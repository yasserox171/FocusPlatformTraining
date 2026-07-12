import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Category,
    ContentItem,
    ContentStatus,
    ContentType,
    LearnerProgress,
    Unit,
    User,
)
from app.security import require_learner
from app.services.progress_service import (
    completed_paragraph_ids,
    course_progress_percent,
    unit_accessible,
    unit_completed,
)

router = APIRouter(prefix="/api/learner", tags=["learner:content"])


def _item_summary(item: ContentItem, progress: float | None = None) -> dict:
    out = {
        "id": str(item.id),
        "type": item.type.value,
        "title_ar": item.title_ar,
        "title_fr": item.title_fr,
        "category_id": str(item.category_id) if item.category_id else None,
        "published_at": item.published_at.isoformat() if item.published_at else None,
    }
    if progress is not None:
        out["progress"] = progress
    return out


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), learner: User = Depends(require_learner)):
    """الأشرطة الثلاثة: محتوياتي / الأحدث / حسب الفئة"""
    published = db.query(ContentItem).filter(ContentItem.status == ContentStatus.published)

    # محتوياتي / Mes contenus — المحتويات التي بدأها المتعلم
    started_ids = {
        r.content_item_id
        for r in db.query(LearnerProgress.content_item_id)
        .filter(LearnerProgress.learner_id == learner.id)
        .distinct()
        .all()
    }
    my_contents = [i for i in published.all() if i.id in started_ids]

    # الأحدث / Récents
    recents = (
        db.query(ContentItem)
        .filter(ContentItem.status == ContentStatus.published)
        .order_by(ContentItem.published_at.desc())
        .limit(12)
        .all()
    )

    # حسب الفئة / Par catégorie
    categories = db.query(Category).all()
    by_category = []
    for cat in categories:
        items = (
            db.query(ContentItem)
            .filter(
                ContentItem.status == ContentStatus.published,
                ContentItem.category_id == cat.id,
            )
            .limit(12)
            .all()
        )
        if items:
            by_category.append(
                {
                    "category": {"id": str(cat.id), "name_ar": cat.name_ar, "name_fr": cat.name_fr},
                    "items": [_item_summary(i) for i in items],
                }
            )

    def with_progress(item: ContentItem) -> dict:
        p = (
            course_progress_percent(db, learner, item)
            if item.type == ContentType.course
            else None
        )
        return _item_summary(item, p)

    return {
        "my_contents": [with_progress(i) for i in my_contents],
        "recents": [with_progress(i) for i in recents],
        "by_category": by_category,
    }


@router.get("/course/{course_id}")
def course_detail(
    course_id: uuid.UUID, db: Session = Depends(get_db), learner: User = Depends(require_learner)
):
    course = db.get(ContentItem, course_id)
    if course is None or course.status != ContentStatus.published:
        raise HTTPException(status_code=404, detail="محتوى غير موجود / Contenu introuvable")

    done_paragraphs = completed_paragraph_ids(db, learner, course.id)

    def lesson_out(lesson) -> dict:
        return {
            "id": str(lesson.id),
            "title_ar": lesson.title_ar,
            "title_fr": lesson.title_fr,
            "order": lesson.order,
            "paragraphs": [
                {
                    "id": str(p.id),
                    "type": p.type.value,
                    "order": p.order,
                    "lang_hint": p.lang_hint.value,
                    "content_html": p.content_html,
                    "video_url": p.video_url,
                    "video_type": p.video_type.value if p.video_type else None,
                    "completed": p.id in done_paragraphs,
                    "quiz_questions": [
                        {
                            "id": str(q.id),
                            "question_text": q.question_text,
                            "question_type": q.question_type.value,
                            # لا نُسرّب is_correct — يُكشف عبر زر "الجواب الصحيح"
                            "options": [
                                {"id": o.get("id"), "text": o.get("text")} for o in (q.options or [])
                            ],
                            "hint": q.hint,
                            "is_final_quiz": q.is_final_quiz,
                        }
                        for q in p.quiz_questions
                    ],
                    "exercises": [
                        {
                            "id": str(e.id),
                            "description": e.description,
                            "hint": e.hint,
                            # الحل يُجلب عبر endpoint منفصل عند الضغط
                        }
                        for e in p.exercises
                    ],
                }
                for p in lesson.paragraphs
            ],
        }

    units_out = []
    for unit in sorted(course.units, key=lambda u: u.order):
        units_out.append(
            {
                "id": str(unit.id),
                "title_ar": unit.title_ar,
                "title_fr": unit.title_fr,
                "order": unit.order,
                "prerequisite_unit_id": str(unit.prerequisite_unit_id)
                if unit.prerequisite_unit_id
                else None,
                "accessible": unit_accessible(db, learner, unit),
                "completed": unit_completed(db, learner, unit),
                "lessons": [lesson_out(l) for l in unit.lessons],
            }
        )

    return {
        **_item_summary(course, course_progress_percent(db, learner, course)),
        "pass_threshold": course.pass_threshold,
        "units": units_out,
        "lessons": [lesson_out(l) for l in course.lessons],
    }


@router.get("/unit/{unit_id}/access")
def unit_access(
    unit_id: uuid.UUID, db: Session = Depends(get_db), learner: User = Depends(require_learner)
):
    """تحقق Prerequisites — هل يمكن للمتعلم الوصول لهذه الوحدة؟"""
    unit = db.get(Unit, unit_id)
    if unit is None:
        raise HTTPException(status_code=404, detail="وحدة غير موجودة / Unité introuvable")
    accessible = unit_accessible(db, learner, unit)
    return {
        "unit_id": str(unit.id),
        "accessible": accessible,
        "prerequisite_unit_id": str(unit.prerequisite_unit_id)
        if unit.prerequisite_unit_id
        else None,
        "message": None
        if accessible
        else "أكمل الوحدة السابقة أولاً / Complétez d'abord l'unité précédente",
    }
