import json
import secrets
import re
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from os import getenv
from pathlib import Path

from dotenv import load_dotenv
import jwt
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlmodel import select

from app.core.config import settings
from app.services.auth_email import (
    AuthEmailError,
    send_registration_code_email,
    send_password_reset_code_email,
)
from database.models import (
    CandidateProfile,
    PasswordResetVerification,
    RegistrationVerification,
    User,
    get_session,
)

load_dotenv()
router = APIRouter()


def get_persistent_secret_key() -> str:
    env_secret = getenv("SECRET_KEY")
    if env_secret:
        return env_secret

    secret_path = Path(__file__).resolve().parent.parent / ".secret_key"
    if secret_path.exists():
        return secret_path.read_text(encoding="utf-8").strip()

    generated_secret = secrets.token_hex(32)
    secret_path.write_text(generated_secret, encoding="utf-8")
    return generated_secret


SECRET_KEY = get_persistent_secret_key()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
PUBLIC_ACCOUNT_TYPES = {"candidate", "employer"}
VERIFICATION_CODE_LENGTH = 6


def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "full_name": user.full_name or "",
        "email": user.email,
        "phone": user.phone or "",
        "account_type": user.account_type,
        "company_name": user.company_name or "",
        "company_logo_url": user.company_logo_url or "",
        "company_country": user.company_country or "",
        "company_industry": user.company_industry or "",
        "company_registration_number": user.company_registration_number or "",
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }


def error(key: str, status: int = 400):
    raise HTTPException(status_code=status, detail={"error": key})


def hash_password(password: str) -> str:
    return sha256(password.encode()).hexdigest()


def hash_verification_code(email: str, code: str) -> str:
    return sha256(f"{normalize_email(email)}:{code}".encode()).hexdigest()


def is_password_strong(password: str) -> bool:
    return (
        len(password) >= 8
        and bool(re.search(r"[A-Z]", password))
        and bool(re.search(r"[a-z]", password))
        and bool(re.search(r"\d", password))
        and bool(re.search(r"[^A-Za-z0-9]", password))
    )


def split_full_name(full_name: str) -> tuple[str, str]:
    normalized_parts = [part for part in full_name.strip().split() if part]
    if not normalized_parts:
        return "", ""
    if len(normalized_parts) == 1:
        return normalized_parts[0], ""
    return normalized_parts[0], " ".join(normalized_parts[1:])


def normalize_email(value: str | None) -> str:
    return (value or "").strip().lower()


def normalize_phone(value: str | None) -> str:
    return re.sub(r"[^\d+]+", "", (value or "").strip())


def normalize_company_name(value: str | None) -> str:
    return " ".join((value or "").strip().lower().split())


def normalize_registration_number(value: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", "", (value or "").strip().lower())


def require_account_types(user: User, *allowed_types: str) -> User:
    if user.account_type not in allowed_types:
        error("forbidden", 403)
    return user


def get_current_user(
    authorization: str | None = Header(None),
    session=Depends(get_session),
) -> User:
    if not authorization:
        error("unauthorized", 401)
    if not authorization.startswith("Bearer "):
        error("unauthorized", 401)
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
    except Exception:
        error("invalid_token", 401)
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        error("user_not_found", 401)
    return user


def extract_registration_payload(data: dict) -> dict:
    account_type = data.get("account_type", "candidate")
    return {
        "full_name": (data.get("full_name") or "").strip(),
        "email": normalize_email(data.get("email")),
        "phone": normalize_phone(data.get("phone")),
        "password": data.get("password") or "",
        "account_type": account_type,
        "company_name": (data.get("company_name") or "").strip(),
        "company_country": (data.get("company_country") or "").strip(),
        "company_industry": (data.get("company_industry") or "").strip(),
        "company_registration_number": (data.get("company_registration_number") or "").strip(),
    }


def validate_registration_payload(payload: dict) -> None:
    if not payload["full_name"] or not payload["email"] or not payload["phone"] or not payload["password"]:
        error("missing_fields")
    if not is_password_strong(payload["password"]):
        error("weak_password")
    if payload["account_type"] not in PUBLIC_ACCOUNT_TYPES:
        error("invalid_account_type")
    if payload["account_type"] == "employer":
        if not payload["company_name"] or not payload["company_country"] or not payload["company_industry"]:
            error("missing_company_fields")


def ensure_registration_is_unique(payload: dict, session) -> None:
    existing_users = session.exec(select(User)).all()

    if any(normalize_email(user.email) == payload["email"] for user in existing_users):
        error("user_exists")

    if any(normalize_phone(user.phone) == payload["phone"] for user in existing_users if user.phone):
        error("phone_exists")

    if payload["account_type"] != "employer":
        return

    normalized_company_name = normalize_company_name(payload["company_name"])
    normalized_registration_number = normalize_registration_number(payload["company_registration_number"])

    if any(
        normalize_company_name(user.company_name) == normalized_company_name
        for user in existing_users
        if user.company_name
    ):
        error("company_name_exists")

    if payload["company_registration_number"] and any(
        normalize_registration_number(user.company_registration_number) == normalized_registration_number
        for user in existing_users
        if user.company_registration_number
    ):
        error("company_registration_number_exists")


def build_pending_payload(payload: dict) -> dict:
    return {
        "full_name": payload["full_name"],
        "email": payload["email"],
        "phone": payload["phone"],
        "hashed_password": hash_password(payload["password"]),
        "account_type": payload["account_type"],
        "company_name": payload["company_name"] if payload["account_type"] == "employer" else None,
        "company_country": payload["company_country"] if payload["account_type"] == "employer" else None,
        "company_industry": payload["company_industry"] if payload["account_type"] == "employer" else None,
        "company_registration_number": payload["company_registration_number"] if payload["account_type"] == "employer" else None,
    }


def create_user_from_pending_payload(pending_payload: dict, session) -> User:
    user = User(
        full_name=pending_payload["full_name"],
        email=pending_payload["email"],
        phone=pending_payload["phone"],
        account_type=pending_payload["account_type"],
        hashed_password=pending_payload["hashed_password"],
        company_name=pending_payload["company_name"],
        company_country=pending_payload["company_country"],
        company_industry=pending_payload["company_industry"],
        company_registration_number=pending_payload["company_registration_number"],
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    if pending_payload["account_type"] == "candidate":
        first_name, last_name = split_full_name(pending_payload["full_name"])
        session.add(
            CandidateProfile(
                user_id=user.id,
                first_name=first_name,
                last_name=last_name,
                phone=pending_payload["phone"],
            )
        )
        session.commit()

    return user


def ensure_utc_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def upsert_registration_verification(payload: dict, session) -> str:
    verification_code = f"{secrets.randbelow(10 ** VERIFICATION_CODE_LENGTH):0{VERIFICATION_CODE_LENGTH}d}"
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.registration_code_expire_minutes
    )
    pending_payload = build_pending_payload(payload)
    pending_registration = session.exec(
        select(RegistrationVerification).where(RegistrationVerification.email == payload["email"])
    ).first()

    if not pending_registration:
        pending_registration = RegistrationVerification(
            email=payload["email"],
            code_hash=hash_verification_code(payload["email"], verification_code),
            payload_json=json.dumps(pending_payload),
            expires_at=expires_at,
        )
    else:
        pending_registration.code_hash = hash_verification_code(payload["email"], verification_code)
        pending_registration.payload_json = json.dumps(pending_payload)
        pending_registration.expires_at = expires_at
        pending_registration.attempts = 0

    session.add(pending_registration)
    session.commit()
    return verification_code


def upsert_password_reset_verification(email: str, session) -> str:
    verification_code = f"{secrets.randbelow(10 ** VERIFICATION_CODE_LENGTH):0{VERIFICATION_CODE_LENGTH}d}"
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.password_reset_code_expire_minutes
    )
    reset_verification = session.exec(
        select(PasswordResetVerification).where(PasswordResetVerification.email == email)
    ).first()

    if not reset_verification:
        reset_verification = PasswordResetVerification(
            email=email,
            code_hash=hash_verification_code(email, verification_code),
            expires_at=expires_at,
        )
    else:
        reset_verification.code_hash = hash_verification_code(email, verification_code)
        reset_verification.expires_at = expires_at
        reset_verification.attempts = 0

    session.add(reset_verification)
    session.commit()
    return verification_code


@router.post("/request_registration_code")
async def request_registration_code(
    request: Request,
    session=Depends(get_session),
):
    payload = extract_registration_payload(await request.json())
    validate_registration_payload(payload)
    ensure_registration_is_unique(payload, session)
    verification_code = upsert_registration_verification(payload, session)

    try:
        send_registration_code_email(payload["email"], verification_code)
    except AuthEmailError as exc:
        pending_registration = session.exec(
            select(RegistrationVerification).where(RegistrationVerification.email == payload["email"])
        ).first()
        if pending_registration:
            session.delete(pending_registration)
            session.commit()
        error(str(exc), 500)

    return {
        "status": "ok",
        "email": payload["email"],
        "expires_in_minutes": settings.registration_code_expire_minutes,
    }


@router.post("/request_password_reset_code")
async def request_password_reset_code(
    request: Request,
    session=Depends(get_session),
):
    data = await request.json()
    email = normalize_email(data.get("email"))

    if not email:
        error("missing_reset_email")

    user = session.exec(select(User).where(User.email == email)).first()
    if user:
        verification_code = upsert_password_reset_verification(email, session)
        try:
            send_password_reset_code_email(email, verification_code)
        except AuthEmailError as exc:
            reset_verification = session.exec(
                select(PasswordResetVerification).where(PasswordResetVerification.email == email)
            ).first()
            if reset_verification:
                session.delete(reset_verification)
                session.commit()
            error(str(exc), 500)

    return {
        "status": "ok",
        "email": email,
        "expires_in_minutes": settings.password_reset_code_expire_minutes,
    }


@router.post("/confirm_password_reset")
async def confirm_password_reset(
    request: Request,
    session=Depends(get_session),
):
    data = await request.json()
    email = normalize_email(data.get("email"))
    code = (data.get("code") or "").strip()
    new_password = data.get("new_password") or ""

    if not email or not code or not new_password:
        error("missing_reset_fields")
    if not is_password_strong(new_password):
        error("weak_password")

    reset_verification = session.exec(
        select(PasswordResetVerification).where(PasswordResetVerification.email == email)
    ).first()

    if not reset_verification:
        error("password_reset_session_not_found", 404)

    now = datetime.now(timezone.utc)
    if ensure_utc_datetime(reset_verification.expires_at) < now:
        session.delete(reset_verification)
        session.commit()
        error("password_reset_code_expired", 410)

    if reset_verification.code_hash != hash_verification_code(email, code):
        reset_verification.attempts += 1
        session.add(reset_verification)
        session.commit()
        error("invalid_password_reset_code")

    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        session.delete(reset_verification)
        session.commit()
        return {"status": "ok"}

    user.hashed_password = hash_password(new_password)
    session.add(user)
    session.delete(reset_verification)
    session.commit()
    return {"status": "ok"}


@router.post("/verify_registration_code")
async def verify_registration_code(
    request: Request,
    session=Depends(get_session),
):
    data = await request.json()
    email = normalize_email(data.get("email"))
    code = (data.get("code") or "").strip()

    if not email or not code:
        error("missing_verification_fields")

    pending_registration = session.exec(
        select(RegistrationVerification).where(RegistrationVerification.email == email)
    ).first()

    if not pending_registration:
        error("verification_session_not_found", 404)

    now = datetime.now(timezone.utc)
    if ensure_utc_datetime(pending_registration.expires_at) < now:
        session.delete(pending_registration)
        session.commit()
        error("verification_code_expired", 410)

    if pending_registration.code_hash != hash_verification_code(email, code):
        pending_registration.attempts += 1
        session.add(pending_registration)
        session.commit()
        error("invalid_verification_code")

    pending_payload = json.loads(pending_registration.payload_json)
    validate_registration_payload(
        {
            **pending_payload,
            "password": "verified",
            "company_name": pending_payload.get("company_name") or "",
            "company_country": pending_payload.get("company_country") or "",
            "company_industry": pending_payload.get("company_industry") or "",
            "company_registration_number": pending_payload.get("company_registration_number") or "",
        }
    )
    ensure_registration_is_unique(
        {
            **pending_payload,
            "password": "verified",
            "company_name": pending_payload.get("company_name") or "",
            "company_country": pending_payload.get("company_country") or "",
            "company_industry": pending_payload.get("company_industry") or "",
            "company_registration_number": pending_payload.get("company_registration_number") or "",
        },
        session,
    )

    user = create_user_from_pending_payload(pending_payload, session)
    session.delete(pending_registration)
    session.commit()
    return {"status": "ok", "user_id": user.id}


@router.post("/create_account")
async def create_account():
    error("email_verification_required", 403)


@router.post("/login")
async def login(
    request: Request,
    session=Depends(get_session),
):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        error("missing_fields")

    hashed = hash_password(password)
    normalized_email = normalize_email(email)
    user = session.exec(select(User).where(User.email == normalized_email)).first()

    if not user or user.hashed_password != hashed:
        error("invalid_credentials")

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    token = jwt.encode(
        {"user_id": user.id, "exp": int(expire.timestamp())},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return {"status": "ok", "token": token}


@router.get("/get_me")
def get_me(current_user: User = Depends(get_current_user)):
    return serialize_user(current_user)
