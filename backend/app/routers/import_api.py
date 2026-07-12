"""الإدراج التلقائي عبر API Key — POST /api/v1/content/import

Header: X-API-Key
المحتوى يُنشأ كـ Draft للمراجعة (بدون فيديو مرفوع — روابط فقط).
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas.content import ContentItemCreate, ContentItemOut
from app.security import require_api_key
from app.services.content_service import create_content_item

router = APIRouter(prefix="/api/v1/content", tags=["import"])


@router.post("/import", response_model=ContentItemOut, status_code=201)
def import_content(
    payload: ContentItemCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_api_key),
):
    return create_content_item(db, payload, admin)
