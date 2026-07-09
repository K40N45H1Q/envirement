import base64
import hashlib
import hmac
from secrets import compare_digest

from fastapi import Request
from sqlmodel import Session
from sqlmodel import select

from app.core.config import settings
from database.models import BetaAccessToken, engine


LEGACY_BETA_USERNAME = "beta"
DB_BETA_USERNAME = "beta-db"


def _hash_token(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _get_active_db_token_count() -> int:
    with engine.connect() as connection:
        try:
            row = connection.exec_driver_sql(
                "SELECT COUNT(*) FROM betaaccesstoken WHERE is_active = 1"
            ).fetchone()
        except Exception:
            return 0
    return int(row[0] or 0) if row else 0


def is_beta_auth_enabled() -> bool:
    return bool(settings.beta_access_token) or _get_active_db_token_count() > 0


def get_expected_beta_access_token() -> str:
    return (settings.beta_access_token or "").strip()


def verify_beta_access_token_value(access_token: str) -> bool:
    normalized_token = (access_token or "").strip()
    if settings.beta_access_token and compare_digest(normalized_token, get_expected_beta_access_token()):
        return True
    return get_beta_access_token_record(normalized_token) is not None


def get_beta_access_token_record(access_token: str) -> BetaAccessToken | None:
    normalized_token = (access_token or "").strip()
    if not is_beta_auth_enabled():
        return None

    if settings.beta_access_token and compare_digest(normalized_token, get_expected_beta_access_token()):
        return None

    with Session(engine) as session:
        result = session.exec(
            select(BetaAccessToken).where(
                BetaAccessToken.token_hash == _hash_token(normalized_token),
                BetaAccessToken.is_active == True,
            )
        )
        return result.first()


def mark_beta_access_token_used(token: BetaAccessToken | None) -> None:
    if not token or not token.id:
        return

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    with Session(engine) as session:
        db_token = session.get(BetaAccessToken, token.id)
        if not db_token or not db_token.is_active:
            return

        if db_token.used_at is None:
            db_token.used_at = now
        db_token.last_used_at = now
        session.add(db_token)
        session.commit()


def _signature_payload(username: str, issued_at: int, token_id: int | None = None, token_hash: str = "") -> bytes:
    access_token_hash = hashlib.sha256(get_expected_beta_access_token().encode("utf-8")).hexdigest()
    return f"{username}:{issued_at}:{access_token_hash}:{token_id or 0}:{token_hash}".encode("utf-8")


def create_beta_access_token(token: BetaAccessToken | None = None) -> str:
    issued_at = 0
    username = DB_BETA_USERNAME if token else LEGACY_BETA_USERNAME
    token_id = token.id if token else None
    token_hash = token.token_hash if token else ""
    payload = _signature_payload(username, issued_at, token_id, token_hash)
    signature = hmac.new(
        settings.jwt_secret_key.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()
    raw_token = f"{username}:{issued_at}:{token_id or 0}:{token_hash}:{signature}".encode("utf-8")
    return base64.urlsafe_b64encode(raw_token).decode("utf-8")


def validate_beta_access_token(token: str | None) -> bool:
    if not is_beta_auth_enabled():
        return True
    if not token:
        return False

    try:
        decoded = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
        parts = decoded.split(":", 4)
        if len(parts) != 5:
            return False

        username, issued_at_raw, token_id_raw, token_hash, provided_signature = parts
        issued_at = int(issued_at_raw)
        token_id = int(token_id_raw)
    except Exception:
        return False

    if issued_at != 0:
        return False

    if username == DB_BETA_USERNAME:
        with Session(engine) as session:
            result = session.exec(
                select(BetaAccessToken).where(
                    BetaAccessToken.id == token_id,
                    BetaAccessToken.token_hash == token_hash,
                    BetaAccessToken.is_active == True,
                )
            )
            token = result.first()

        if not token:
            return False
    elif username != LEGACY_BETA_USERNAME:
        return False

    expected_signature = hmac.new(
        settings.jwt_secret_key.encode("utf-8"),
        _signature_payload(username, issued_at, token_id, token_hash),
        hashlib.sha256,
    ).hexdigest()

    return compare_digest(provided_signature, expected_signature)


def has_beta_access(request: Request) -> bool:
    if not is_beta_auth_enabled():
        return True
    return validate_beta_access_token(request.cookies.get(settings.beta_cookie_name))
