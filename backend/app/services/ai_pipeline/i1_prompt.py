"""I1 — واجهة الـ Prompt: إنشاء AIPipelineJob وإطلاق المسار"""
from sqlalchemy.orm import Session

from app.models import AIPipelineJob, AIPipelineJobStatus, User


def start_pipeline_job(db: Session, prompt: str, admin: User) -> AIPipelineJob:
    job = AIPipelineJob(
        prompt=prompt,
        status=AIPipelineJobStatus.validating,
        initiated_by=admin.id,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job
