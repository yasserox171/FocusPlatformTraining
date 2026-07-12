"""منطق التقدم — Progress Bar + Prerequisites + اكتمال الدورة"""
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import (
    ContentItem,
    LearnerProgress,
    Lesson,
    Paragraph,
    ProgressStatus,
    Unit,
    User,
)


def _course_paragraph_ids(db: Session, course: ContentItem) -> list[uuid.UUID]:
    """كل paragraphs الدورة: عبر units → lessons، أو lessons مستقلة"""
    ids: list[uuid.UUID] = []
    unit_ids = [u.id for u in db.query(Unit).filter(Unit.course_id == course.id).all()]
    lessons = db.query(Lesson).filter(
        (Lesson.unit_id.in_(unit_ids)) | (Lesson.content_item_id == course.id)
    ).all() if unit_ids else db.query(Lesson).filter(Lesson.content_item_id == course.id).all()
    lesson_ids = [l.id for l in lessons]
    if lesson_ids:
        ids = [
            p.id for p in db.query(Paragraph.id).filter(Paragraph.lesson_id.in_(lesson_ids)).all()
        ]
    return ids


def completed_paragraph_ids(db: Session, learner: User, content_item_id: uuid.UUID) -> set:
    rows = db.query(LearnerProgress.paragraph_id).filter(
        LearnerProgress.learner_id == learner.id,
        LearnerProgress.content_item_id == content_item_id,
        LearnerProgress.paragraph_id.isnot(None),
        LearnerProgress.status == ProgressStatus.completed,
    ).all()
    return {r.paragraph_id for r in rows}


def course_progress_percent(db: Session, learner: User, course: ContentItem) -> float:
    """progress% = (paragraphs_completed / total_paragraphs) * 100"""
    all_ids = _course_paragraph_ids(db, course)
    if not all_ids:
        return 0.0
    done = completed_paragraph_ids(db, learner, course.id)
    completed = len([pid for pid in all_ids if pid in done])
    return round(completed / len(all_ids) * 100, 1)


def unit_completed(db: Session, learner: User, unit: Unit) -> bool:
    """الوحدة مكتملة إذا كانت كل paragraphs دروسها مكتملة"""
    lesson_ids = [l.id for l in unit.lessons]
    if not lesson_ids:
        return True
    paragraph_ids = [
        p.id for p in db.query(Paragraph.id).filter(Paragraph.lesson_id.in_(lesson_ids)).all()
    ]
    if not paragraph_ids:
        return True
    done = completed_paragraph_ids(db, learner, unit.course_id)
    return all(pid in done for pid in paragraph_ids)


def unit_accessible(db: Session, learner: User, unit: Unit) -> bool:
    """الوحدة متاحة إذا لا prerequisite أو الـ prerequisite مكتمل"""
    if unit.prerequisite_unit_id is None:
        return True
    prereq = db.get(Unit, unit.prerequisite_unit_id)
    if prereq is None:
        return True
    return unit_completed(db, learner, prereq)


def mark_paragraph_completed(
    db: Session, learner: User, content_item_id: uuid.UUID, paragraph: Paragraph
) -> LearnerProgress:
    lesson = paragraph.lesson
    row = db.query(LearnerProgress).filter(
        LearnerProgress.learner_id == learner.id,
        LearnerProgress.content_item_id == content_item_id,
        LearnerProgress.paragraph_id == paragraph.id,
    ).first()
    if row is None:
        row = LearnerProgress(
            learner_id=learner.id,
            content_item_id=content_item_id,
            unit_id=lesson.unit_id,
            lesson_id=lesson.id,
            paragraph_id=paragraph.id,
        )
        db.add(row)
    row.status = ProgressStatus.completed
    row.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(row)
    return row


def course_completed(db: Session, learner: User, course: ContentItem) -> bool:
    """إكمال جميع الوحدات (كل paragraphs في كل lessons في كل units)"""
    all_ids = _course_paragraph_ids(db, course)
    if not all_ids:
        return False
    done = completed_paragraph_ids(db, learner, course.id)
    return all(pid in done for pid in all_ids)


def upsert_course_completion(db: Session, learner: User, course: ContentItem) -> None:
    """سجل إكمال على مستوى الدورة (بدون unit/lesson/paragraph)"""
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
    if row.status != ProgressStatus.completed:
        row.status = ProgressStatus.completed
        row.completed_at = datetime.now(timezone.utc)
    db.commit()
