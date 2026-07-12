"""المصادقة والصلاحيات — JWT (access + refresh) + bcrypt + API Key"""
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import ApiKey, User, UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: uuid.UUID, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "role": role, "type": "access", "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(user_id: uuid.UUID) -> tuple[str, datetime]:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    token = secrets.token_urlsafe(48)
    payload = {"sub": str(user_id), "jti": token, "type": "refresh", "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM), expire


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="جلسة غير صالحة / Session invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="جلسة غير صالحة / Session invalide")
    user = db.get(User, uuid.UUID(payload["sub"]))
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="حساب غير مفعّل / Compte inactif")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="صلاحيات غير كافية / Accès refusé")
    return user


def require_learner(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.learner:
        raise HTTPException(status_code=403, detail="صلاحيات غير كافية / Accès refusé")
    return user


def generate_api_key() -> str:
    return f"fpt_{secrets.token_urlsafe(32)}"


def require_api_key(
    x_api_key: str = Header(..., alias="X-API-Key"), db: Session = Depends(get_db)
) -> User:
    """التحقق من مفتاح API — للإدراج التلقائي عبر /api/v1/content/import"""
    key = db.query(ApiKey).filter(
        ApiKey.key_hash == hash_token(x_api_key), ApiKey.is_active.is_(True)
    ).first()
    if key is None:
        raise HTTPException(status_code=401, detail="مفتاح API غير صالح / Clé API invalide")
    admin = db.get(User, key.admin_id)
    if admin is None or not admin.is_active or admin.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="صلاحيات غير كافية / Accès refusé")
    return admin
