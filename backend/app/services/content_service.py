"""بناء المحتوى المتداخل (دورة → وحدات → دروس → فقرات) من schema الإدخال"""
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import (
    ContentItem,
    ContentStatus,
    ContentType,
    Exercise,
    Lesson,
    Paragraph,
    QuizQuestion,
    Unit,
    User,
)
from app.schemas.content import ContentItemCreate, LessonIn


def _build_lesson(lesson_in: LessonIn, *, unit_id=None, content_item_id=None) -> Lesson:
    lesson = Lesson(
        unit_id=unit_id,
        content_item_id=content_item_id,
        title_ar=lesson_in.title_ar,
        title_fr=lesson_in.title_fr,
        order=lesson_in.order,
    )
    for p in lesson_in.paragraphs:
        paragraph = Paragraph(
            type=p.type,
            order=p.order,
            lang_hint=p.lang_hint,
            content_html=p.content_html,
            video_url=p.video_url,
            video_type=p.video_type,
        )
        for q in p.quiz_questions:
            paragraph.quiz_questions.append(
                QuizQuestion(
                    question_text=q.question_text,
                    question_type=q.question_type,
                    options=[o.model_dump() for o in q.options],
                    hint=q.hint,
                    is_final_quiz=q.is_final_quiz,
                )
            )
        for e in p.exercises:
            paragraph.exercises.append(
                Exercise(description=e.description, solution=e.solution, hint=e.hint)
            )
        lesson.paragraphs.append(paragraph)
    return lesson


def create_content_item(
    db: Session,
    payload: ContentItemCreate,
    created_by: User,
    *,
    is_ai_generated: bool = False,
) -> ContentItem:
    item = ContentItem(
        type=payload.type,
        title_ar=payload.title_ar,
        title_fr=payload.title_fr,
        category_id=payload.category_id,
        status=ContentStatus.draft,
        created_by=created_by.id,
        is_ai_generated=is_ai_generated,
        pass_threshold=payload.pass_threshold,
    )
    db.add(item)
    db.flush()

    # الدورة: وحدات → دروس؛ prerequisite بترتيب الوحدة داخل نفس الدورة فقط
    if payload.type == ContentType.course:
        units_by_order: dict[int, Unit] = {}
        for u in payload.units:
            unit = Unit(
                course_id=item.id,
                title_ar=u.title_ar,
                title_fr=u.title_fr,
                order=u.order,
            )
            for l in u.lessons:
                unit.lessons.append(_build_lesson(l))
            db.add(unit)
            db.flush()
            units_by_order[u.order] = unit
        for u in payload.units:
            if u.prerequisite_unit_order is not None:
                prereq = units_by_order.get(u.prerequisite_unit_order)
                if prereq is not None and prereq.order != u.order:
                    units_by_order[u.order].prerequisite_unit_id = prereq.id
    else:
        for l in payload.lessons:
            db.add(_build_lesson(l, content_item_id=item.id))

    db.commit()
    db.refresh(item)
    return item


def publish_content_item(db: Session, item: ContentItem, admin: User) -> ContentItem:
    item.status = ContentStatus.published
    item.published_by = admin.id
    item.published_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(item)
    return item
