import json
import re
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from os import getenv
from secrets import randbelow, token_hex

import jwt
from dotenv import get_key, load_dotenv, set_key
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlmodel import select

from app.core.config import settings
from app.services.auth_email import (
    AuthEmailError,
    send_password_reset_code_email,
    send_registration_code_email,
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

ENV_PATH = ".env"
SECRET_KEY = get_key(ENV_PATH, "SECRET_KEY")
if not SECRET_KEY:
    SECRET_KEY = token_hex(32)
    set_key(ENV_PATH, "SECRET_KEY", SECRET_KEY)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
PUBLIC_ACCOUNT_TYPES = {"candidate", "employer"}
VERIFICATION_CODE_LENGTH = 6


def error(key: str, status: int = 400):
    raise HTTPException(status_code=status, detail={"error": key})


async def read_json_object(request: Request) -> dict:
    try:
        data = await request.json()
    except Exception:
        error("invalid_payload")

    if not isinstance(data, dict):
        error("invalid_payload")

    return data


def payload_value(data: dict, snake_key: str, camel_key: str | None = None, default=""):
    if snake_key in data:
        return data.get(snake_key)
    if camel_key and camel_key in data:
        return data.get(camel_key)
    return default


def serialize_user(user: User) -> dict:
    now = datetime.now(timezone.utc)
    expires_at = user.subscription_expires_at
    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    has_active_subscription = bool(user.subscription_plan and expires_at and expires_at > now)

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
        "subscription_plan": user.subscription_plan or "",
        "subscription_expires_at": user.subscription_expires_at,
        "has_active_subscription": has_active_subscription,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }


def hash_password(password: str) -> str:
    return sha256(password.encode()).hexdigest()


def normalize_email(value: str | None) -> str:
    return (value or "").strip().lower()


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
    if not authorization or not authorization.startswith("Bearer "):
        error("unauthorized", 401)

    token = authorization.replace("Bearer ", "", 1)

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
    """
    Принимает оба формата:
    - snake_case: full_name, account_type, company_name
    - camelCase: fullName, accountType, companyName
    Поэтому backend не ломается от текущей модалки.
    """
    account_type = (payload_value(data, "account_type", "accountType", "candidate") or "candidate").strip()

    return {
        "full_name": (payload_value(data, "full_name", "fullName") or "").strip(),
        "email": normalize_email(payload_value(data, "email")),
        "phone": normalize_phone(payload_value(data, "phone")),
        "password": payload_value(data, "password") or "",
        "account_type": account_type,
        "company_name": (payload_value(data, "company_name", "companyName") or "").strip(),
        "company_country": (payload_value(data, "company_country", "companyCountry") or "").strip(),
        "company_industry": (payload_value(data, "company_industry", "companyIndustry") or "").strip(),
        "company_registration_number": (
            payload_value(data, "company_registration_number", "companyRegistrationNumber") or ""
        ).strip(),
    }


def validate_registration_payload(payload: dict) -> None:
    if not payload["email"] or not payload["phone"] or not payload["password"]:
        error("missing_fields")

    if payload["account_type"] == "candidate" and not payload["full_name"]:
        error("missing_fields")

    if not is_password_strong(payload["password"]):
        error("weak_password")

    if payload["account_type"] not in PUBLIC_ACCOUNT_TYPES:
        error("invalid_account_type")

    if payload["account_type"] == "employer":
        if (
            not payload["company_name"]
            or not payload["company_country"]
            or not payload["company_industry"]
            or not payload["company_registration_number"]
        ):
            error("missing_company_fields")


def ensure_registration_is_unique(payload: dict, session) -> None:
    existing_users = session.exec(select(User)).all()

    if any(normalize_email(user.email) == payload["email"] for user in existing_users):
        error("user_exists")

    if any(normalize_phone(user.phone) == payload["phone"] for user in existing_users if user.phone):
        error("phone_exists")

    if payload["account_type"] != "employer":
        return

    normalized_company_name = normalize_company_name(payload.get("company_name"))
    normalized_registration_number = normalize_registration_number(payload.get("company_registration_number"))

    if normalized_company_name and any(
        normalize_company_name(user.company_name) == normalized_company_name
        for user in existing_users
        if user.company_name
    ):
        error("company_name_exists")

    if normalized_registration_number and any(
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
        "company_registration_number": (
            payload["company_registration_number"] if payload["account_type"] == "employer" else None
        ),
    }


def normalize_pending_payload(raw_payload: dict) -> dict:
    """
    Pending payload хранится уже без обычного password, только с hashed_password.
    Здесь нельзя заново вызывать validate_registration_payload(), иначе будет ошибка weak_password.
    """
    account_type = payload_value(raw_payload, "account_type", "accountType", "candidate") or "candidate"
    password_hash = payload_value(raw_payload, "hashed_password", "hashedPassword")

    # На случай старых pending-записей, где случайно лежал plaintext password.
    if not password_hash and raw_payload.get("password"):
        password_hash = hash_password(raw_payload["password"])

    pending_payload = {
        "full_name": (payload_value(raw_payload, "full_name", "fullName") or "").strip(),
        "email": normalize_email(payload_value(raw_payload, "email")),
        "phone": normalize_phone(payload_value(raw_payload, "phone")),
        "hashed_password": password_hash or "",
        "account_type": account_type,
        "company_name": payload_value(raw_payload, "company_name", "companyName") or None,
        "company_country": payload_value(raw_payload, "company_country", "companyCountry") or None,
        "company_industry": payload_value(raw_payload, "company_industry", "companyIndustry") or None,
        "company_registration_number": (
            payload_value(raw_payload, "company_registration_number", "companyRegistrationNumber") or None
        ),
    }

    if pending_payload["account_type"] != "employer":
        pending_payload["company_name"] = None
        pending_payload["company_country"] = None
        pending_payload["company_industry"] = None
        pending_payload["company_registration_number"] = None

    return pending_payload


def validate_pending_payload(pending_payload: dict) -> None:
    if (
        not pending_payload["email"]
        or not pending_payload["phone"]
        or not pending_payload["hashed_password"]
    ):
        error("invalid_registration_payload")

    if pending_payload["account_type"] not in PUBLIC_ACCOUNT_TYPES:
        error("invalid_account_type")

    if pending_payload["account_type"] == "candidate" and not pending_payload["full_name"]:
        error("invalid_registration_payload")

    if pending_payload["account_type"] == "employer":
        if (
            not pending_payload["company_name"]
            or not pending_payload["company_country"]
            or not pending_payload["company_industry"]
            or not pending_payload["company_registration_number"]
        ):
            error("missing_company_fields")


def pending_payload_to_unique_check_payload(pending_payload: dict) -> dict:
    return {
        "email": pending_payload["email"],
        "phone": pending_payload["phone"],
        "account_type": pending_payload["account_type"],
        "company_name": pending_payload.get("company_name") or "",
        "company_registration_number": pending_payload.get("company_registration_number") or "",
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
    session.flush()
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
        session.flush()

    return user


def ensure_utc_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def upsert_registration_verification(payload: dict, session) -> str:
    verification_code = f"{randbelow(10 ** VERIFICATION_CODE_LENGTH):0{VERIFICATION_CODE_LENGTH}d}"
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
            attempts=0,
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
    verification_code = f"{randbelow(10 ** VERIFICATION_CODE_LENGTH):0{VERIFICATION_CODE_LENGTH}d}"
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
            attempts=0,
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
    data = await read_json_object(request)
    payload = extract_registration_payload(data)

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


@router.post("/verify_registration_code")
async def verify_registration_code(
    request: Request,
    session=Depends(get_session),
):
    data = await read_json_object(request)

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

    try:
        raw_pending_payload = json.loads(pending_registration.payload_json)
    except Exception:
        session.delete(pending_registration)
        session.commit()
        error("invalid_registration_payload")

    pending_payload = normalize_pending_payload(raw_pending_payload)
    validate_pending_payload(pending_payload)
    ensure_registration_is_unique(pending_payload_to_unique_check_payload(pending_payload), session)

    user = create_user_from_pending_payload(pending_payload, session)
    session.delete(pending_registration)
    session.commit()
    session.refresh(user)

    return {
        "status": "ok",
        "user_id": user.id,
        "user": serialize_user(user),
    }


@router.post("/request_password_reset_code")
async def request_password_reset_code(
    request: Request,
    session=Depends(get_session),
):
    data = await read_json_object(request)
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
    data = await read_json_object(request)

    email = normalize_email(data.get("email"))
    code = (data.get("code") or "").strip()
    new_password = data.get("new_password") or data.get("newPassword") or ""

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


@router.post("/create_account")
async def create_account():
    error("email_verification_required", 403)


@router.post("/login")
async def login(
    request: Request,
    session=Depends(get_session),
):
    data = await read_json_object(request)

    email = normalize_email(data.get("email"))
    password = data.get("password") or ""

    if not email or not password:
        error("missing_fields")

    hashed = hash_password(password)
    user = session.exec(select(User).where(User.email == email)).first()

    if not user or user.hashed_password != hashed:
        error("invalid_credentials")

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = jwt.encode(
        {"user_id": user.id, "exp": int(expire.timestamp())},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return {
        "status": "ok",
        "token": token,
        "user": serialize_user(user),
    }


@router.get("/get_me")
def get_me(current_user: User = Depends(get_current_user)):
    return serialize_user(current_user)
