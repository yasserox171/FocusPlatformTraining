"""Celery Tasks — تنفيذ مراحل الـ AI Pipeline في الخلفية

المسار: I1 → R1 → I2 → R2 → DuplicateCheck → I3 → R3 → (انتظار المستخدم) → R4 → I4 → R5
"""
import uuid

from app.database import SessionLocal
from app.models import AIPipelineJob, AIPipelineJobStatus, User
from app.services.ai_pipeline import (
    duplicate_check,
    i2_search,
    i3_analysis,
    i4_generation,
    r1_validation,
    r5_upload,
)
from app.tasks.celery_app import celery_app


def _fail(db, job: AIPipelineJob, error: str):
    job.status = AIPipelineJobStatus.failed
    job.error_message = error
    db.commit()


@celery_app.task(name="pipeline.run_until_user")
def run_pipeline_until_user(job_id: str):
    """R1 → I2 → R2 → DuplicateCheck → I3 → R3 ثم يتوقف بانتظار جواب المستخدم"""
    db = SessionLocal()
    try:
        job = db.get(AIPipelineJob, uuid.UUID(job_id))
        if job is None:
            return

        # R1 — تقييم وضوح الـ Prompt
        job.status = AIPipelineJobStatus.validating
        db.commit()
        try:
            validation = r1_validation.validate_prompt(job.prompt)
        except Exception:
            # انقطاع الاتصال أو فشل الـ API
            _fail(db, job, "connection_error")
            return
        if not validation.get("clear"):
            _fail(db, job, "prompt_unclear")
            return

        # I2 — البحث
        job.status = AIPipelineJobStatus.searching
        db.commit()
        try:
            results = i2_search.search_sources(
                job.prompt, validation.get("language", "both"), validation.get("topic", "")
            )
        except Exception:
            _fail(db, job, "connection_error")
            return
        job.search_results = results

        # R2 — نقل المصادر إلى I3
        job.status = AIPipelineJobStatus.analyzing
        db.commit()

        # I3 — التحليل والتصنيف
        try:
            analysis = i3_analysis.analyze_sources(db, job.prompt, results)
        except Exception:
            _fail(db, job, "connection_error")
            return

        # Duplicate Check — تحذير إذا وُجد تشابه > 80%
        warnings = duplicate_check.check_duplicates(db, analysis.get("topics", []))
        analysis["duplicate_warnings"] = warnings
        job.analysis_results = analysis

        # R3 — طلب اختيار المستخدم
        job.user_request = {
            "possible_contents": analysis.get("possible_contents", []),
            "duplicate_warnings": warnings,
        }
        job.status = AIPipelineJobStatus.awaiting_user
        db.commit()
    finally:
        db.close()


@celery_app.task(name="pipeline.generate")
def run_generation(job_id: str):
    """R4 (الجواب مخزّن سلفاً) → I4 → R5"""
    db = SessionLocal()
    try:
        job = db.get(AIPipelineJob, uuid.UUID(job_id))
        if job is None or job.user_answer is None:
            return

        job.status = AIPipelineJobStatus.generating
        db.commit()

        admin = db.get(User, job.initiated_by)
        category_id = None
        if job.analysis_results:
            category_id = (job.analysis_results.get("category") or {}).get("existing_id")

        # I4 — التوليد (لا فيديوهات أبداً)
        try:
            content_ids = i4_generation.generate_contents(
                db, admin, job.search_results, job.analysis_results, job.user_answer, category_id
            )
        except Exception:
            _fail(db, job, "generation_error")
            return

        # R5 — الرفع كـ Drafts
        job.status = AIPipelineJobStatus.uploading
        db.commit()
        r5_upload.finalize_job(db, job, content_ids)
    finally:
        db.close()
