import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RefreshToken, User
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse, UserOut
from app.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    hash_token,
    verify_password,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _issue_tokens(user: User, db: Session) -> TokenResponse:
    access = create_access_token(user.id, user.role.value)
    refresh, expires_at = create_refresh_token(user.id)
    db.add(RefreshToken(user_id=user.id, token_hash=hash_token(refresh), expires_at=expires_at))
    db.commit()
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="بيانات دخول خاطئة / Identifiants incorrects")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="حساب معطّل / Compte désactivé")
    return _issue_tokens(user, db)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    data = decode_token(payload.refresh_token)
    if data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="جلسة غير صالحة / Session invalide")
    stored = db.query(RefreshToken).filter(
        RefreshToken.token_hash == hash_token(payload.refresh_token),
        RefreshToken.revoked.is_(False),
    ).first()
    if stored is None or stored.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="انتهت الجلسة / Session expirée")
    user = db.get(User, uuid.UUID(data["sub"]))
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="حساب غير مفعّل / Compte inactif")
    stored.revoked = True
    return _issue_tokens(user, db)


@router.post("/logout")
def logout(payload: RefreshRequest, db: Session = Depends(get_db)):
    stored = db.query(RefreshToken).filter(
        RefreshToken.token_hash == hash_token(payload.refresh_token)
    ).first()
    if stored is not None:
        stored.revoked = True
        db.commit()
    return {"message": "تم تسجيل الخروج / Déconnecté"}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
