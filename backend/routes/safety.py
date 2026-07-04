import secrets
import re
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from os import getenv
from pathlib import Path
from dotenv import load_dotenv
import jwt
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlmodel import Session, select

from database.models import (
    CandidateProfile,
    Job,
    JobApplication,
    Message,
    User,
    engine,
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


@router.post("/create_account")
async def create_account(
    request: Request,
    session=Depends(get_session),
):
    data = await request.json()
    full_name = (data.get("full_name") or "").strip()
    email = normalize_email(data.get("email"))
    phone = normalize_phone(data.get("phone"))
    password = data.get("password")
    account_type = data.get("account_type", "candidate")
    company_name = (data.get("company_name") or "").strip()
    company_country = data.get("company_country")
    company_industry = data.get("company_industry")
    company_registration_number = (data.get("company_registration_number") or "").strip()

    if not full_name or not email or not phone or not password:
        error("missing_fields")
    if account_type not in PUBLIC_ACCOUNT_TYPES:
        error("invalid_account_type")
    if account_type == "employer":
        if not company_name or not company_country or not company_industry:
            error("missing_company_fields")

    if session.exec(select(User).where(User.email == email)).first():
        error("user_exists")

    existing_users = session.exec(select(User)).all()

    if any(normalize_phone(user.phone) == phone for user in existing_users if user.phone):
        error("phone_exists")

    if account_type == "employer":
        normalized_company_name = normalize_company_name(company_name)
        normalized_registration_number = normalize_registration_number(company_registration_number)

        if any(
            normalize_company_name(user.company_name) == normalized_company_name
            for user in existing_users
            if user.company_name
        ):
            error("company_name_exists")

        if company_registration_number and any(
            normalize_registration_number(user.company_registration_number) == normalized_registration_number
            for user in existing_users
            if user.company_registration_number
        ):
            error("company_registration_number_exists")

    user = User(
        full_name=full_name,
        email=email,
        phone=phone,
        account_type=account_type,
        hashed_password=hash_password(password),
        company_name=company_name if account_type == "employer" else None,
        company_country=company_country if account_type == "employer" else None,
        company_industry=company_industry if account_type == "employer" else None,
        company_registration_number=(
            company_registration_number if account_type == "employer" else None
        ),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    if account_type == "candidate":
        first_name, last_name = split_full_name(full_name)
        session.add(
            CandidateProfile(
                user_id=user.id,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
            )
        )
        session.commit()

    return {"status": "ok", "user_id": user.id}


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
