import os
from pathlib import Path

from pydantic import BaseModel, ConfigDict
from dotenv import load_dotenv


class Settings(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    app_name: str
    app_env: str
    app_host: str
    app_port: int
    app_debug: bool
    jwt_secret_key: str
    base_dir: Path
    uploads_dir: Path
    database_url: str
    database_sync_url: str
    database_async_url: str
    supabase_url: str | None
    supabase_publishable_key: str | None
    supabase_secret_key: str | None
    supabase_access_cookie_name: str
    supabase_refresh_cookie_name: str
    cors_origins: list[str]
    default_admin_login: str | None
    default_admin_password: str | None
    registration_code_expire_minutes: int
    password_reset_code_expire_minutes: int
    stripe_secret_key: str | None
    stripe_publishable_key: str | None
    stripe_webhook_secret: str | None


def parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def parse_origins(value: str | None) -> list[str]:
    if not value:
        return [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
        ]
    return [item.strip() for item in value.split(",") if item.strip()]


def make_database_sync_url(value: str) -> str:
    if value.startswith("sqlite+aiosqlite://"):
        return value.replace("sqlite+aiosqlite://", "sqlite://", 1)
    if value.startswith("postgres://"):
        return value.replace("postgres://", "postgresql+psycopg://", 1)
    if value.startswith("postgresql://"):
        return value.replace("postgresql://", "postgresql+psycopg://", 1)
    if value.startswith("postgresql+asyncpg://"):
        return value.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
    return value


def make_database_async_url(value: str) -> str:
    if value.startswith("sqlite://"):
        return value.replace("sqlite://", "sqlite+aiosqlite://", 1)
    if value.startswith("postgres://"):
        return value.replace("postgres://", "postgresql+asyncpg://", 1)
    if value.startswith("postgresql://"):
        return value.replace("postgresql://", "postgresql+asyncpg://", 1)
    if value.startswith("postgresql+psycopg://"):
        return value.replace("postgresql+psycopg://", "postgresql+asyncpg://", 1)
    return value


def load_settings() -> Settings:
    base_dir = Path(__file__).resolve().parents[2]
    load_dotenv(base_dir / ".env")
    load_dotenv(base_dir.parent / ".env")
    database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./default.db")
    return Settings(
        app_name=os.getenv("APP_NAME", "CVHOLD API"),
        app_env=os.getenv("APP_ENV", "development"),
        app_host=os.getenv("APP_HOST", "0.0.0.0"),
        app_port=int(os.getenv("APP_PORT", "8000")),
        app_debug=parse_bool(os.getenv("APP_DEBUG"), True),
        jwt_secret_key=os.getenv("SECRET_KEY", "change-me-before-production"),
        base_dir=base_dir,
        uploads_dir=base_dir / "uploads",
        database_url=database_url,
        database_sync_url=make_database_sync_url(database_url),
        database_async_url=make_database_async_url(database_url),
        supabase_url=(os.getenv("SUPABASE_URL") or "").strip() or None,
        supabase_publishable_key=(os.getenv("SUPABASE_PUBLISHABLE_KEY") or "").strip() or None,
        supabase_secret_key=(os.getenv("SUPABASE_SECRET_KEY") or "").strip() or None,
        supabase_access_cookie_name=os.getenv("ACCESS_COOKIE_NAME", "cvhold_supabase_access_token"),
        supabase_refresh_cookie_name=os.getenv("REFRESH_COOKIE_NAME", "cvhold_supabase_refresh_token"),
        cors_origins=parse_origins(os.getenv("CORS_ORIGINS")),
        default_admin_login=(os.getenv("DEFAULT_ADMIN_LOGIN") or "admin@cvhold.com").strip().lower() or None,
        default_admin_password=(os.getenv("DEFAULT_ADMIN_PASSWORD") or "CVHOLD-Admin-2026!n7Qp#4Lz").strip() or None,
        registration_code_expire_minutes=int(os.getenv("REGISTRATION_CODE_EXPIRE_MINUTES", "10")),
        password_reset_code_expire_minutes=int(os.getenv("PASSWORD_RESET_CODE_EXPIRE_MINUTES", "10")),
        stripe_secret_key=(os.getenv("STRIPE_SECRET_KEY") or "").strip() or None,
        stripe_publishable_key=(os.getenv("STRIPE_PUBLISHABLE_KEY") or "").strip() or None,
        stripe_webhook_secret=(os.getenv("STRIPE_WEBHOOK_SECRET") or "").strip() or None,
    )


settings = load_settings()
