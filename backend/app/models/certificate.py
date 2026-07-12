import enum
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CertificateType(str, enum.Enum):
    attendance = "attendance"  # شهادة حضور
    competency = "competency"  # شهادة كفاءة


class Certificate(Base):
    __tablename__ = "certificates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    learner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_items.id"), nullable=False)
    type: Mapped[CertificateType] = mapped_column(Enum(CertificateType), nullable=False)
    serial_number: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    # رابط صفحة التحقق العامة /verify/{serial_number}
    qr_code_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    pdf_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    # بيانات القالب (القالب سيوفره ياسر لاحقاً)
    template_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    learner = relationship("User")
    course = relationship("ContentItem")
