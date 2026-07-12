import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AIPipelineJob, AIPipelineJobStatus, User
from app.security import require_admin
from app.services.ai_pipeline.i1_prompt import start_pipeline_job

router = APIRouter(prefix="/api/admin/pipeline", tags=["admin:pipeline"])


class PipelineStart(BaseModel):
    prompt: str


class PipelineAnswer(BaseModel):
    # R4 — المحتويات المختارة من قائمة R3
    selected_contents: list[dict]


def _job_out(job: AIPipelineJob) -> dict:
    return {
        "id": str(job.id),
        "prompt": job.prompt,
        "status": job.status.value,
        "search_results": job.search_results,
        "analysis_results": job.analysis_results,
        "user_request": job.user_request,
        "user_answer": job.user_answer,
        "generated_content_ids": job.generated_content_ids,
        "error_message": job.error_message,
        "created_at": job.created_at.isoformat(),
        "updated_at": job.updated_at.isoformat(),
    }


@router.post("/start", status_code=201)
def start_pipeline(
    payload: PipelineStart, db: Session = Depends(get_db), admin: User = Depends(require_admin)
):
    """I1 — إطلاق الـ Pipeline"""
    prompt = payload.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=422, detail="الـ Prompt فارغ / Prompt vide")
    job = start_pipeline_job(db, prompt, admin)
    from app.tasks.pipeline_tasks import run_pipeline_until_user

    run_pipeline_until_user.delay(str(job.id))
    return _job_out(job)


@router.get("")
def list_jobs(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    jobs = db.query(AIPipelineJob).order_by(AIPipelineJob.created_at.desc()).limit(50).all()
    return [_job_out(j) for j in jobs]


@router.get("/{job_id}/status")
def job_status(job_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    job = db.get(AIPipelineJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="مهمة غير موجودة / Tâche introuvable")
    return _job_out(job)


@router.post("/{job_id}/answer")
def answer_job(
    job_id: uuid.UUID,
    payload: PipelineAnswer,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """R4 — جواب المستخدم: اختيار المحتويات المطلوب توليدها"""
    job = db.get(AIPipelineJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="مهمة غير موجودة / Tâche introuvable")
    if job.status != AIPipelineJobStatus.awaiting_user:
        raise HTTPException(status_code=400, detail="المهمة ليست بانتظار الجواب / Tâche non en attente")
    if not payload.selected_contents:
        raise HTTPException(status_code=422, detail="لا اختيار / Aucune sélection")
    job.user_answer = {"selected_contents": payload.selected_contents}
    db.commit()
    from app.tasks.pipeline_tasks import run_generation

    run_generation.delay(str(job.id))
    return _job_out(job)
