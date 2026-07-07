import base64
import hashlib
import hmac
from secrets import compare_digest

from fastapi import Request

from app.core.config import settings


def is_beta_auth_enabled() -> bool:
    return bool(settings.beta_access_token)


def get_expected_beta_access_token() -> str:
    return (settings.beta_access_token or "").strip()


def verify_beta_access_token_value(access_token: str) -> bool:
    if not is_beta_auth_enabled():
        return True
    return compare_digest((access_token or "").strip(), get_expected_beta_access_token())


def _signature_payload(username: str, issued_at: int) -> bytes:
    access_token_hash = hashlib.sha256(get_expected_beta_access_token().encode("utf-8")).hexdigest()
    return f"{username}:{issued_at}:{access_token_hash}".encode("utf-8")


def create_beta_access_token() -> str:
    issued_at = 0
    username = "beta"
    payload = _signature_payload(username, issued_at)
    signature = hmac.new(
        settings.jwt_secret_key.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()
    raw_token = f"{username}:{issued_at}:{signature}".encode("utf-8")
    return base64.urlsafe_b64encode(raw_token).decode("utf-8")


def validate_beta_access_token(token: str | None) -> bool:
    if not is_beta_auth_enabled():
        return True
    if not token:
        return False

    try:
        decoded = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
        username, issued_at_raw, provided_signature = decoded.split(":", 2)
        issued_at = int(issued_at_raw)
    except Exception:
        return False

    if username != "beta" or issued_at != 0:
        return False

    expected_signature = hmac.new(
        settings.jwt_secret_key.encode("utf-8"),
        _signature_payload(username, issued_at),
        hashlib.sha256,
    ).hexdigest()

    return compare_digest(provided_signature, expected_signature)


def has_beta_access(request: Request) -> bool:
    if not is_beta_auth_enabled():
        return True
    return validate_beta_access_token(request.cookies.get(settings.beta_cookie_name))
