import enum
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ContentType(str, enum.Enum):
    lesson = "lesson"
    course = "course"
    exercise = "exercise"
    quiz = "quiz"


class ContentStatus(str, enum.Enum):
    draft = "draft"
    published = "published"


class ParagraphType(str, enum.Enum):
    text = "text"
    video = "video"
    quiz = "quiz"
    exercise = "exercise"


class LangHint(str, enum.Enum):
    ar = "ar"
    fr = "fr"
    auto = "auto"


class VideoType(str, enum.Enum):
    youtube = "youtube"
    direct = "direct"


class QuestionType(str, enum.Enum):
    mcq = "mcq"
    yes_no = "yes_no"


class ContentItem(Base):
    """الجدول الرئيسي للمحتويات — دروس، دورات، تمارين، كويزات"""

    __tablename__ = "content_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type: Mapped[ContentType] = mapped_column(Enum(ContentType), nullable=False)
    title_ar: Mapped[str] = mapped_column(String(500), nullable=False)
    title_fr: Mapped[str] = mapped_column(String(500), nullable=False)
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("categories.id"), nullable=True)
    status: Mapped[ContentStatus] = mapped_column(
        Enum(ContentStatus), default=ContentStatus.draft, nullable=False
    )
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"), nullable=True)
    published_by: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"), nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_ai_generated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # نسبة النجاح للكويز النهائي — قابلة للتخصيص per دورة (افتراضي 35%)
    pass_threshold: Mapped[float] = mapped_column(Float, default=35.0, nullable=False)
    # مدة التكوين بالساعات — تظهر على الشهادة (0 = غير محددة)
    duration_hours: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    category = relationship("Category")
    units: Mapped[list["Unit"]] = relationship(
        back_populates="course", cascade="all, delete-orphan", order_by="Unit.order"
    )
    lessons: Mapped[list["Lesson"]] = relationship(
        back_populates="content_item", cascade="all, delete-orphan", order_by="Lesson.order"
    )


class Unit(Base):
    """وحدات الدورة التكوينية"""

    __tablename__ = "units"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_items.id"), nullable=False)
    title_ar: Mapped[str] = mapped_column(String(500), nullable=False)
    title_fr: Mapped[str] = mapped_column(String(500), nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # Prerequisite — بين الوحدات داخل نفس الدورة فقط
    prerequisite_unit_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("units.id"), nullable=True
    )

    course: Mapped[ContentItem] = relationship(back_populates="units")
    lessons: Mapped[list["Lesson"]] = relationship(
        back_populates="unit", cascade="all, delete-orphan", order_by="Lesson.order"
    )
    prerequisite_unit: Mapped[Optional["Unit"]] = relationship(remote_side="Unit.id")


class Lesson(Base):
    """دروس داخل وحدة (unit_id) أو مستقلة (content_item_id)"""

    __tablename__ = "lessons"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    unit_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("units.id"), nullable=True)
    content_item_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("content_items.id"), nullable=True
    )
    title_ar: Mapped[str] = mapped_column(String(500), nullable=False)
    title_fr: Mapped[str] = mapped_column(String(500), nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    unit: Mapped[Optional[Unit]] = relationship(back_populates="lessons")
    content_item: Mapped[Optional[ContentItem]] = relationship(back_populates="lessons")
    paragraphs: Mapped[list["Paragraph"]] = relationship(
        back_populates="lesson", cascade="all, delete-orphan", order_by="Paragraph.order"
    )


class Paragraph(Base):
    """الفقرات — اللبنات الأساسية للمحتوى"""

    __tablename__ = "paragraphs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lesson_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lessons.id"), nullable=False)
    type: Mapped[ParagraphType] = mapped_column(Enum(ParagraphType), nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lang_hint: Mapped[LangHint] = mapped_column(Enum(LangHint), default=LangHint.auto, nullable=False)
    # للنص
    content_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # للفيديو — YouTube URL أو رابط مباشر (لا رفع ملفات فيديو للخادم)
    video_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    video_type: Mapped[Optional[VideoType]] = mapped_column(Enum(VideoType), nullable=True)

    lesson: Mapped[Lesson] = relationship(back_populates="paragraphs")
    quiz_questions: Mapped[list["QuizQuestion"]] = relationship(
        back_populates="paragraph", cascade="all, delete-orphan"
    )
    exercises: Mapped[list["Exercise"]] = relationship(
        back_populates="paragraph", cascade="all, delete-orphan"
    )


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paragraph_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("paragraphs.id"), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[QuestionType] = mapped_column(Enum(QuestionType), nullable=False)
    # [{id, text, is_correct}]
    options: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    hint: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # هل هو الكويز النهائي للدورة؟ (شرط شهادة الكفاءة)
    is_final_quiz: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    paragraph: Mapped[Paragraph] = relationship(back_populates="quiz_questions")


class Exercise(Base):
    """تمرين — لا تقييم أبداً: عرض + حل + تلميح فقط"""

    __tablename__ = "exercises"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paragraph_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("paragraphs.id"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    # الحل الكامل — يُخفى حتى يضغط المتعلم
    solution: Mapped[str] = mapped_column(Text, nullable=False)
    hint: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    paragraph: Mapped[Paragraph] = relationship(back_populates="exercises")
