import hashlib

from sqlmodel import Session
from sqlmodel import select

from database.models import BetaAccessSetting, BetaAccessToken, engine


BETA_ACCESS_SETTING_ID = 1


def _hash_token(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalize_beta_email(value: str | None) -> str:
    return (value or "").strip().lower()


def _get_active_db_token_count() -> int:
    with Session(engine) as session:
        try:
            tokens = session.exec(
                select(BetaAccessToken).where(BetaAccessToken.is_active == True)
            ).all()
        except Exception:
            return 0
    return len(tokens)


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


def get_beta_registration_token_record(access_token: str, email: str) -> BetaAccessToken | None:
    normalized_token = (access_token or "").strip()
    normalized_email = normalize_beta_email(email)
    if not is_beta_auth_enabled():
        return None
    if not normalized_token or not normalized_email:
        return None

    with Session(engine) as session:
        result = session.exec(
            select(BetaAccessToken).where(
                BetaAccessToken.token_hash == _hash_token(normalized_token),
                BetaAccessToken.is_active == True,
                BetaAccessToken.email == normalized_email,
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
