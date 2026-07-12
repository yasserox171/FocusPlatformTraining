import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category, ContentItem, ContentStatus, ContentType, User
from app.schemas.content import (
    CategoryCreate,
    CategoryOut,
    ContentItemCreate,
    ContentItemDetail,
    ContentItemOut,
    ContentItemUpdate,
)
from app.security import require_admin
from app.services.content_service import create_content_item, publish_content_item

router = APIRouter(prefix="/api/admin/content", tags=["admin:content"])


@router.get("", response_model=list[ContentItemOut])
def list_content(
    status: ContentStatus | None = Query(None),
    type: ContentType | None = Query(None),
    category_id: uuid.UUID | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    q = db.query(ContentItem)
    if status is not None:
        q = q.filter(ContentItem.status == status)
    if type is not None:
        q = q.filter(ContentItem.type == type)
    if category_id is not None:
        q = q.filter(ContentItem.category_id == category_id)
    return q.order_by(ContentItem.created_at.desc()).all()


@router.post("", response_model=ContentItemDetail, status_code=201)
def create_content(
    payload: ContentItemCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return create_content_item(db, payload, admin)


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return db.query(Category).order_by(Category.name_ar).all()


@router.post("/categories", response_model=CategoryOut, status_code=201)
def create_category(
    payload: CategoryCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)
):
    category = Category(name_ar=payload.name_ar, name_fr=payload.name_fr)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/{content_id}", response_model=ContentItemDetail)
def get_content(
    content_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(require_admin)
):
    item = db.get(ContentItem, content_id)
    if item is None:
        raise HTTPException(status_code=404, detail="محتوى غير موجود / Contenu introuvable")
    return item


@router.put("/{content_id}", response_model=ContentItemOut)
def update_content(
    content_id: uuid.UUID,
    payload: ContentItemUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    item = db.get(ContentItem, content_id)
    if item is None:
        raise HTTPException(status_code=404, detail="محتوى غير موجود / Contenu introuvable")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.post("/{content_id}/publish", response_model=ContentItemOut)
def publish_content(
    content_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    item = db.get(ContentItem, content_id)
    if item is None:
        raise HTTPException(status_code=404, detail="محتوى غير موجود / Contenu introuvable")
    if item.status == ContentStatus.published:
        raise HTTPException(status_code=400, detail="منشور سلفاً / Déjà publié")
    return publish_content_item(db, item, admin)


@router.delete("/{content_id}", status_code=204)
def delete_content(
    content_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(require_admin)
):
    item = db.get(ContentItem, content_id)
    if item is None:
        raise HTTPException(status_code=404, detail="محتوى غير موجود / Contenu introuvable")
    db.delete(item)
    db.commit()
