import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    role: UserRole
    full_name_ar: str
    full_name_fr: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole = UserRole.learner
    full_name_ar: str
    full_name_fr: str


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None
    full_name_ar: str | None = None
    full_name_fr: str | None = None
    is_active: bool | None = None
