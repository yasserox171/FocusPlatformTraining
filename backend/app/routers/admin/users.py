import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ApiKey, User
from app.schemas.auth import UserCreate, UserOut, UserUpdate
from app.security import generate_api_key, hash_password, hash_token, require_admin

router = APIRouter(prefix="/api/admin", tags=["admin:users"])


@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return db.query(User).order_by(User.created_at.desc()).all()


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    email = payload.email.lower()
    if db.query(User).filter(User.email == email).first() is not None:
        raise HTTPException(status_code=409, detail="البريد مستعمل / Email déjà utilisé")
    user = User(
        email=email,
        password_hash=hash_password(payload.password),
        role=payload.role,
        full_name_ar=payload.full_name_ar,
        full_name_fr=payload.full_name_fr,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="مستخدم غير موجود / Utilisateur introuvable")
    data = payload.model_dump(exclude_unset=True)
    if "password" in data:
        user.password_hash = hash_password(data.pop("password"))
    if "email" in data and data["email"] is not None:
        data["email"] = data["email"].lower()
    for field, value in data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


class ApiKeyCreated(BaseModel):
    id: uuid.UUID
    label: str
    # يظهر مرة واحدة فقط عند الإنشاء
    api_key: str


class ApiKeyOut(BaseModel):
    id: uuid.UUID
    label: str
    is_active: bool

    model_config = {"from_attributes": True}


class ApiKeyCreate(BaseModel):
    label: str = ""


@router.get("/api-keys", response_model=list[ApiKeyOut])
def list_api_keys(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return db.query(ApiKey).filter(ApiKey.admin_id == admin.id).all()


@router.post("/api-keys", response_model=ApiKeyCreated, status_code=201)
def create_key(
    payload: ApiKeyCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)
):
    raw = generate_api_key()
    key = ApiKey(admin_id=admin.id, key_hash=hash_token(raw), label=payload.label)
    db.add(key)
    db.commit()
    db.refresh(key)
    return ApiKeyCreated(id=key.id, label=key.label, api_key=raw)


@router.delete("/api-keys/{key_id}", status_code=204)
def revoke_key(
    key_id: uuid.UUID, db: Session = Depends(get_db), admin: User = Depends(require_admin)
):
    key = db.get(ApiKey, key_id)
    if key is None or key.admin_id != admin.id:
        raise HTTPException(status_code=404, detail="مفتاح غير موجود / Clé introuvable")
    key.is_active = False
    db.commit()
