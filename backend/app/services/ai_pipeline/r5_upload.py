"""R5 — رفع المحتوى المولّد كـ Draft وإنهاء الـ Job

المحتوى أُنشئ سلفاً كـ Drafts في I4؛ هنا نُحدّث الـ Job إلى done
ونسجّل الـ IDs — الأدمين يراجع ثم يضغط "نشر / Publier".
"""
from sqlalchemy.orm import Session

from app.models import AIPipelineJob, AIPipelineJobStatus


def finalize_job(db: Session, job: AIPipelineJob, content_ids: list[str]) -> AIPipelineJob:
    job.generated_content_ids = content_ids
    job.status = AIPipelineJobStatus.done
    db.commit()
    db.refresh(job)
    return job
