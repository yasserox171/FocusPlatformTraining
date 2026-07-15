import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    CertificateType,
    ContentItem,
    ContentStatus,
    ContentType,
    Exercise,
    Paragraph,
    QuizQuestion,
    User,
)
from app.security import require_learner
from app.services.certificate_service import issue_certificate
from app.services.progress_service import (
    course_completed,
    course_progress_percent,
    mark_paragraph_completed,
    unit_accessible,
    upsert_course_completion,
)

router = APIRouter(prefix="/api/learner", tags=["learner:progress"])
logger = logging.getLogger(__name__)


class ProgressUpdate(BaseModel):
    content_item_id: uuid.UUID
    paragraph_id: uuid.UUID


@router.post("/progress")
def update_progress(
    payload: ProgressUpdate,
    db: Session = Depends(get_db),
    learner: User = Depends(require_learner),
):
    """تحديث التقدم — إكمال فقرة؛ يمنح شهادة الحضور تلقائياً عند إكمال الدورة"""
    item = db.get(ContentItem, payload.content_item_id)
    if item is None or item.status != ContentStatus.published:
        raise HTTPException(status_code=404, detail="محتوى غير موجود / Contenu introuvable")
    paragraph = db.get(Paragraph, payload.paragraph_id)
    if paragraph is None:
        raise HTTPException(status_code=404, detail="فقرة غير موجودة / Paragraphe introuvable")

    # Prerequisites: منع إكمال فقرة في وحدة مقفلة
    if paragraph.lesson.unit_id is not None:
        unit = paragraph.lesson.unit
        if not unit_accessible(db, learner, unit):
            raise HTTPException(
                status_code=403,
                detail="أكمل الوحدة السابقة أولاً / Complétez d'abord l'unité précédente",
            )

    mark_paragraph_completed(db, learner, item.id, paragraph)

    certificate_awarded = None
    progress = None
    if item.type == ContentType.course:
        progress = course_progress_percent(db, learner, item)
        # شهادة الحضور: إكمال جميع الوحدات — لا يُشترط أي نقطة
        if course_completed(db, learner, item):
            upsert_course_completion(db, learner, item)
            try:
                cert = issue_certificate(db, learner, item, CertificateType.attendance)
                certificate_awarded = {
                    "id": str(cert.id),
                    "type": cert.type.value,
                    "serial_number": cert.serial_number,
                }
            except Exception:
                # فشل توليد PDF (مثلاً مكتبات WeasyPrint غير مثبتة) لا يجب أن يُسقط الطلب
                logger.exception("Attendance certificate issuance failed for course %s", item.id)

    return {
        "status": "completed",
        "progress": progress,
        "certificate_awarded": certificate_awarded,
    }


class QuizSubmission(BaseModel):
    # {question_id: selected_option_id}
    answers: dict[str, str]


@router.get("/exercise/{exercise_id}/solution")
def exercise_solution(
    exercise_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(require_learner)
):
    """كشف الحل — يُجلب فقط عند ضغط المتعلم على زر الحل"""
    exercise = db.get(Exercise, exercise_id)
    if exercise is None:
        raise HTTPException(status_code=404, detail="تمرين غير موجود / Exercice introuvable")
    return {"solution": exercise.solution}


@router.get("/quiz/{question_id}/answer")
def quiz_correct_answer(
    question_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(require_learner)
):
    """زر "الجواب الصحيح / Bonne réponse" — للكويزات التدريبية"""
    q = db.get(QuizQuestion, question_id)
    if q is None:
        raise HTTPException(status_code=404, detail="سؤال غير موجود / Question introuvable")
    correct = [o.get("id") for o in (q.options or []) if o.get("is_correct")]
    return {"correct_option_ids": correct}


@router.post("/quiz/{course_id}/submit")
def submit_final_quiz(
    course_id: uuid.UUID,
    payload: QuizSubmission,
    db: Session = Depends(get_db),
    learner: User = Depends(require_learner),
):
    """تقديم الكويز النهائي — محاولات غير محدودة؛ النجاح يمنح شهادة كفاءة"""
    course = db.get(ContentItem, course_id)
    if course is None or course.type != ContentType.course:
        raise HTTPException(status_code=404, detail="دورة غير موجودة / Formation introuvable")

    # كل أسئلة الكويز النهائي للدورة
    questions = (
        db.query(QuizQuestion)
        .join(Paragraph, QuizQuestion.paragraph_id == Paragraph.id)
        .filter(QuizQuestion.is_final_quiz.is_(True))
        .all()
    )
    course_questions = [
        q
        for q in questions
        if q.paragraph.lesson is not None
        and (
            (q.paragraph.lesson.unit is not None and q.paragraph.lesson.unit.course_id == course.id)
            or q.paragraph.lesson.content_item_id == course.id
        )
    ]
    if not course_questions:
        raise HTTPException(
            status_code=400, detail="لا كويز نهائي لهذه الدورة / Pas de quiz final"
        )

    correct_count = 0
    results = []
    for q in course_questions:
        selected = payload.answers.get(str(q.id))
        correct_ids = [o.get("id") for o in (q.options or []) if o.get("is_correct")]
        is_correct = selected in correct_ids
        if is_correct:
            correct_count += 1
        results.append(
            {"question_id": str(q.id), "correct": is_correct, "correct_option_ids": correct_ids}
        )

    score = round(correct_count / len(course_questions) * 100, 1)
    passed = score >= course.pass_threshold

    # تسجيل المحاولة (غير محدودة)
    from app.models import LearnerProgress, ProgressStatus

    row = db.query(LearnerProgress).filter(
        LearnerProgress.learner_id == learner.id,
        LearnerProgress.content_item_id == course.id,
        LearnerProgress.unit_id.is_(None),
        LearnerProgress.lesson_id.is_(None),
        LearnerProgress.paragraph_id.is_(None),
    ).first()
    if row is None:
        row = LearnerProgress(learner_id=learner.id, content_item_id=course.id)
        db.add(row)
    row.attempts += 1
    row.quiz_score = max(score, row.quiz_score or 0)
    if row.status == ProgressStatus.not_started:
        row.status = ProgressStatus.in_progress
    db.commit()

    certificate_awarded = None
    if passed:
        try:
            cert = issue_certificate(db, learner, course, CertificateType.competency)
            certificate_awarded = {
                "id": str(cert.id),
                "type": cert.type.value,
                "serial_number": cert.serial_number,
            }
        except Exception:
            # فشل توليد PDF (مثلاً مكتبات WeasyPrint غير مثبتة) لا يجب أن يُسقط الطلب
            logger.exception("Competency certificate issuance failed for course %s", course_id)

    return {
        "score": score,
        "pass_threshold": course.pass_threshold,
        "passed": passed,
        "attempts": row.attempts,
        "results": results,
        "certificate_awarded": certificate_awarded,
        "message": "مبروك! / Félicitations !"
        if passed
        else "حاول مجدداً، أنت قريب! / Réessayez, vous y êtes presque !",
    }
