from ipaddress import ip_address
from datetime import datetime, timezone

from sqlmodel import Session, select

from app.core.config import settings
from database.models import BetaBlockedIP, engine


def normalize_ip(ip_address: str | None) -> str:
    ip = (ip_address or "").strip().lower()
    if not ip:
        return "unknown"

    if "," in ip:
        ip = ip.split(",", 1)[0].strip()

    if ip.startswith("::ffff:"):
        ip = ip.removeprefix("::ffff:")

    if ip == "::1":
        return "127.0.0.1"

    return ip


def is_public_ip(ip_value: str | None) -> bool:
    normalized_ip = normalize_ip(ip_value)
    if normalized_ip in {"unknown", ""}:
        return False

    try:
        parsed_ip = ip_address(normalized_ip)
    except ValueError:
        return False

    return not (
        parsed_ip.is_private
        or parsed_ip.is_loopback
        or parsed_ip.is_link_local
        or parsed_ip.is_multicast
        or parsed_ip.is_reserved
        or parsed_ip.is_unspecified
    )


def get_public_ip_from_headers(request) -> str | None:
    headers = request.headers
    header_candidates = [
        headers.get("cf-connecting-ip"),
        headers.get("true-client-ip"),
        headers.get("fly-client-ip"),
        headers.get("x-client-ip"),
        headers.get("x-forwarded-for"),
        headers.get("x-real-ip"),
    ]

    for candidate in header_candidates:
        if not candidate:
            continue

        for raw_ip in str(candidate).split(","):
            normalized_ip = normalize_ip(raw_ip)
            if is_public_ip(normalized_ip):
                return normalized_ip

    return None


def get_client_ip(request) -> str:
    public_ip = get_public_ip_from_headers(request)
    if public_ip:
        return public_ip

    fallback_ip = normalize_ip(request.client.host if request.client else "unknown")
    if settings.app_env == "development":
        return fallback_ip

    return "unknown"


def get_ip_record(ip_address: str) -> BetaBlockedIP | None:
    normalized_ip = normalize_ip(ip_address)
    with Session(engine) as session:
        return session.exec(
            select(BetaBlockedIP).where(BetaBlockedIP.ip_address == normalized_ip)
        ).first()


def is_ip_blocked(ip_address: str) -> bool:
    record = get_ip_record(ip_address)
    return bool(record and record.is_blocked)


def register_failed_attempt(ip_address: str) -> bool:
    normalized_ip = normalize_ip(ip_address)
    now = datetime.now(timezone.utc)

    with Session(engine) as session:
        record = session.exec(
            select(BetaBlockedIP).where(BetaBlockedIP.ip_address == normalized_ip)
        ).first()

        if not record:
            record = BetaBlockedIP(
                ip_address=normalized_ip,
                failed_attempts=1,
                last_failed_at=now,
            )
            session.add(record)
        else:
            record.failed_attempts += 1
            record.last_failed_at = now

        if record.failed_attempts >= settings.beta_failed_attempt_limit:
            record.is_blocked = True
            record.blocked_at = now

        session.commit()
        session.refresh(record)
        return record.is_blocked


def register_failed_attempt_with_state(ip_address: str) -> tuple[bool, int]:
    normalized_ip = normalize_ip(ip_address)
    now = datetime.now(timezone.utc)

    with Session(engine) as session:
        record = session.exec(
            select(BetaBlockedIP).where(BetaBlockedIP.ip_address == normalized_ip)
        ).first()

        if not record:
            record = BetaBlockedIP(
                ip_address=normalized_ip,
                failed_attempts=1,
                last_failed_at=now,
            )
            session.add(record)
        else:
            record.failed_attempts += 1
            record.last_failed_at = now

        if record.failed_attempts >= settings.beta_failed_attempt_limit:
            record.is_blocked = True
            record.blocked_at = now

        session.commit()
        session.refresh(record)

        remaining_attempts = max(settings.beta_failed_attempt_limit - record.failed_attempts, 0)
        return record.is_blocked, remaining_attempts


def clear_failed_attempts(ip_address: str) -> None:
    normalized_ip = normalize_ip(ip_address)
    with Session(engine) as session:
        record = session.exec(
            select(BetaBlockedIP).where(BetaBlockedIP.ip_address == normalized_ip)
        ).first()

        if not record:
            return

        session.delete(record)
        session.commit()
