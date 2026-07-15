"""إعدادات التطبيق — تُقرأ من متغيرات البيئة (.env)"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    DATABASE_URL: str = "postgresql://user:pass@localhost/focus_platform"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # JWT
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Claude API
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-sonnet-5"

    # Storage
    UPLOAD_DIR: str = "./uploads"
    CERTIFICATES_DIR: str = "./certificates"

    # App
    APP_URL: str = "http://localhost:3000"
    API_URL: str = "http://localhost:8000"

    # Email (اختياري)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 0
    SMTP_USER: str = ""
    SMTP_PASS: str = ""

    # الكويز النهائي — نسبة النجاح الافتراضية (قابلة للتخصيص per دورة)
    DEFAULT_PASS_THRESHOLD: float = 35.0


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
