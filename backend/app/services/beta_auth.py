import base64
import hashlib
import hmac
from secrets import compare_digest

from fastapi import Request
from sqlmodel import Session
from sqlmodel import select

from app.core.config import settings
from database.models import BetaAccessSetting, BetaAccessToken, engine


DB_BETA_USERNAME = "beta-db"
BETA_ACCESS_SETTING_ID = 1


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


def get_beta_access_enabled() -> bool:
    with Session(engine) as session:
        setting = session.get(BetaAccessSetting, BETA_ACCESS_SETTING_ID)
        if setting:
            return bool(setting.enabled)
    return _get_active_db_token_count() > 0


def set_beta_access_enabled(enabled: bool) -> bool:
    with Session(engine) as session:
        setting = session.get(BetaAccessSetting, BETA_ACCESS_SETTING_ID)
        if not setting:
            setting = BetaAccessSetting(id=BETA_ACCESS_SETTING_ID)
        setting.enabled = bool(enabled)
        session.add(setting)
        session.commit()
        session.refresh(setting)
        return bool(setting.enabled)


def is_beta_auth_enabled() -> bool:
    return get_beta_access_enabled()


def get_beta_access_token_record(access_token: str) -> BetaAccessToken | None:
    normalized_token = (access_token or "").strip()
    if not is_beta_auth_enabled():
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
    return f"{username}:{issued_at}:{token_id or 0}:{token_hash}".encode("utf-8")


def create_beta_access_token(token: BetaAccessToken | None = None) -> str:
    if not token:
        raise ValueError("beta token is required")

    issued_at = 0
    username = DB_BETA_USERNAME
    token_id = token.id
    token_hash = token.token_hash
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
    else:
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
