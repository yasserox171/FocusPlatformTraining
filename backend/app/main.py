from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, import_api, public
from app.routers.admin import analytics as admin_analytics
from app.routers.admin import content as admin_content
from app.routers.admin import pipeline as admin_pipeline
from app.routers.admin import users as admin_users
from app.routers.learner import certificates as learner_certificates
from app.routers.learner import content as learner_content
from app.routers.learner import progress as learner_progress

app = FastAPI(
    title="Focus Platform Training",
    description="منصة تكوينية داخلية — مركز Focus، سافي، المغرب",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.APP_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(public.router)
app.include_router(import_api.router)
app.include_router(admin_content.router)
app.include_router(admin_users.router)
app.include_router(admin_analytics.router)
app.include_router(admin_pipeline.router)
app.include_router(learner_content.router)
app.include_router(learner_progress.router)
app.include_router(learner_certificates.router)


@app.get("/health")
def health():
    return {"status": "ok"}
