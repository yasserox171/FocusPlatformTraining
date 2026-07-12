import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models import (
    ContentStatus,
    ContentType,
    LangHint,
    ParagraphType,
    QuestionType,
    VideoType,
)


class CategoryOut(BaseModel):
    id: uuid.UUID
    name_ar: str
    name_fr: str
    created_by_ai: bool

    model_config = {"from_attributes": True}


class CategoryCreate(BaseModel):
    name_ar: str
    name_fr: str


class QuizOptionIn(BaseModel):
    id: str
    text: str
    is_correct: bool


class QuizQuestionIn(BaseModel):
    question_text: str
    question_type: QuestionType
    options: list[QuizOptionIn]
    hint: str | None = None
    is_final_quiz: bool = False


class ExerciseIn(BaseModel):
    description: str
    solution: str
    hint: str | None = None


class ParagraphIn(BaseModel):
    type: ParagraphType
    order: int = 0
    lang_hint: LangHint = LangHint.auto
    content_html: str | None = None
    video_url: str | None = None
    video_type: VideoType | None = None
    quiz_questions: list[QuizQuestionIn] = []
    exercises: list[ExerciseIn] = []


class LessonIn(BaseModel):
    title_ar: str
    title_fr: str
    order: int = 0
    paragraphs: list[ParagraphIn] = []


class UnitIn(BaseModel):
    title_ar: str
    title_fr: str
    order: int = 0
    prerequisite_unit_order: int | None = None  # يشير لترتيب وحدة سابقة في نفس الدورة
    lessons: list[LessonIn] = []


class ContentItemCreate(BaseModel):
    type: ContentType
    title_ar: str
    title_fr: str
    category_id: uuid.UUID | None = None
    pass_threshold: float = 35.0
    units: list[UnitIn] = []      # للدورات
    lessons: list[LessonIn] = []  # للدروس المستقلة


class ContentItemUpdate(BaseModel):
    title_ar: str | None = None
    title_fr: str | None = None
    category_id: uuid.UUID | None = None
    pass_threshold: float | None = None


class QuizQuestionOut(BaseModel):
    id: uuid.UUID
    question_text: str
    question_type: QuestionType
    options: list
    hint: str | None
    is_final_quiz: bool

    model_config = {"from_attributes": True}


class ExerciseOut(BaseModel):
    id: uuid.UUID
    description: str
    solution: str
    hint: str | None

    model_config = {"from_attributes": True}


class ParagraphOut(BaseModel):
    id: uuid.UUID
    type: ParagraphType
    order: int
    lang_hint: LangHint
    content_html: str | None
    video_url: str | None
    video_type: VideoType | None
    quiz_questions: list[QuizQuestionOut] = []
    exercises: list[ExerciseOut] = []

    model_config = {"from_attributes": True}


class LessonOut(BaseModel):
    id: uuid.UUID
    title_ar: str
    title_fr: str
    order: int
    paragraphs: list[ParagraphOut] = []

    model_config = {"from_attributes": True}


class UnitOut(BaseModel):
    id: uuid.UUID
    title_ar: str
    title_fr: str
    order: int
    prerequisite_unit_id: uuid.UUID | None
    lessons: list[LessonOut] = []

    model_config = {"from_attributes": True}


class ContentItemOut(BaseModel):
    id: uuid.UUID
    type: ContentType
    title_ar: str
    title_fr: str
    category_id: uuid.UUID | None
    status: ContentStatus
    is_ai_generated: bool
    pass_threshold: float
    published_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ContentItemDetail(ContentItemOut):
    units: list[UnitOut] = []
    lessons: list[LessonOut] = []
