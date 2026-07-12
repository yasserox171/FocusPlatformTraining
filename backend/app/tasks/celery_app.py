from celery import Celery

from app.config import settings

celery_app = Celery(
    "focus_platform",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.pipeline_tasks"],
)
celery_app.conf.task_track_started = True
