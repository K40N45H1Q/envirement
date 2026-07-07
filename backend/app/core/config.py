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
    access_token_expire_minutes: int
    base_dir: Path
    uploads_dir: Path
    database_url: str
    cors_origins: list[str]
    beta_access_token: str | None
    beta_cookie_name: str
    beta_failed_attempt_limit: int
    default_employer_login: str | None
    default_employer_password: str | None
    default_candidate_login: str | None
    default_candidate_password: str | None


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


def load_settings() -> Settings:
    base_dir = Path(__file__).resolve().parents[2]
    load_dotenv(base_dir / ".env")
    load_dotenv(base_dir.parent / ".env")
    return Settings(
        app_name=os.getenv("APP_NAME", "CVHOLD API"),
        app_env=os.getenv("APP_ENV", "development"),
        app_host=os.getenv("APP_HOST", "0.0.0.0"),
        app_port=int(os.getenv("APP_PORT", "8000")),
        app_debug=parse_bool(os.getenv("APP_DEBUG"), True),
        jwt_secret_key=os.getenv("SECRET_KEY", "change-me-before-production"),
        access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")),
        base_dir=base_dir,
        uploads_dir=base_dir / "uploads",
        database_url=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./default.db"),
        cors_origins=parse_origins(os.getenv("CORS_ORIGINS")),
        beta_access_token=(os.getenv("BETA_ACCESS_TOKEN") or "").strip() or None,
        beta_cookie_name=os.getenv("BETA_COOKIE_NAME", "cvhold_beta_access"),
        beta_failed_attempt_limit=int(os.getenv("BETA_FAILED_ATTEMPT_LIMIT", "3")),
        default_employer_login=(os.getenv("DEFAULT_EMPLOYER_LOGIN") or "").strip().lower() or None,
        default_employer_password=(os.getenv("DEFAULT_EMPLOYER_PASSWORD") or "").strip() or None,
        default_candidate_login=(os.getenv("DEFAULT_CANDIDATE_LOGIN") or "").strip().lower() or None,
        default_candidate_password=(os.getenv("DEFAULT_CANDIDATE_PASSWORD") or "").strip() or None,
    )


settings = load_settings()
