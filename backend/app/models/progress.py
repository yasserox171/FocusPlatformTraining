import enum
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ProgressStatus(str, enum.Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"


class LearnerProgress(Base):
    __tablename__ = "learner_progress"
    __table_args__ = (
        UniqueConstraint(
            "learner_id", "content_item_id", "unit_id", "lesson_id", "paragraph_id",
            name="uq_learner_progress_scope",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    learner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    content_item_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("content_items.id"), nullable=False, index=True
    )
    unit_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("units.id"), nullable=True)
    lesson_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("lessons.id"), nullable=True)
    paragraph_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("paragraphs.id"), nullable=True)
    status: Mapped[ProgressStatus] = mapped_column(
        Enum(ProgressStatus), default=ProgressStatus.not_started, nullable=False
    )
    # للكويز النهائي فقط
    quiz_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    # عدد محاولات الكويز — غير محدودة
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    learner = relationship("User")
    content_item = relationship("ContentItem")


class AIPipelineJobStatus(str, enum.Enum):
    pending = "pending"
    validating = "validating"
    searching = "searching"
    analyzing = "analyzing"
    awaiting_user = "awaiting_user"
    generating = "generating"
    uploading = "uploading"
    done = "done"
    failed = "failed"


class AIPipelineJob(Base):
    __tablename__ = "ai_pipeline_jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[AIPipelineJobStatus] = mapped_column(
        Enum(AIPipelineJobStatus), default=AIPipelineJobStatus.pending, nullable=False
    )
    initiated_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    search_results: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    analysis_results: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    user_request: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)  # R3 request
    user_answer: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)  # R4 answer
    generated_content_ids: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    initiator = relationship("User")
