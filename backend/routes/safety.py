import secrets
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from os import getenv
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


SECRET_KEY = getenv("SECRET_KEY") or secrets.token_hex(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
PUBLIC_ACCOUNT_TYPES = {"candidate", "employer"}
DEFAULT_ADMIN_EMAIL = getenv("DEFAULT_ADMIN_EMAIL", "admin@cvhold.local")
DEFAULT_ADMIN_PASSWORD = getenv("DEFAULT_ADMIN_PASSWORD", "CVHOLD_Admin_2026_Secure!")
DEFAULT_EMPLOYER_EMAIL = getenv("DEFAULT_EMPLOYER_EMAIL", "employer@cvhold.local")
DEFAULT_EMPLOYER_PASSWORD = getenv("DEFAULT_EMPLOYER_PASSWORD", "CVHOLD_Employer_2026_Secure!")
DEFAULT_CANDIDATE_EMAIL = getenv("DEFAULT_CANDIDATE_EMAIL", "candidate@cvhold.local")
DEFAULT_CANDIDATE_PASSWORD = getenv("DEFAULT_CANDIDATE_PASSWORD", "CVHOLD_Candidate_2026_Secure!")


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


def ensure_default_admin():
    with Session(engine) as session:
        default_accounts = [
            {
                "email": DEFAULT_ADMIN_EMAIL,
                "account_type": "admin",
                "hashed_password": hash_password(DEFAULT_ADMIN_PASSWORD),
            },
            {
                "email": DEFAULT_EMPLOYER_EMAIL,
                "account_type": "employer",
                "hashed_password": hash_password(DEFAULT_EMPLOYER_PASSWORD),
            },
            {
                "email": DEFAULT_CANDIDATE_EMAIL,
                "account_type": "candidate",
                "hashed_password": hash_password(DEFAULT_CANDIDATE_PASSWORD),
            },
        ]

        changed = False

        for account_data in default_accounts:
            user = session.exec(
                select(User).where(User.email == account_data["email"])
            ).first()

            if not user:
                session.add(User(**account_data))
                changed = True
                continue

            updated = False

            if user.account_type != account_data["account_type"]:
                user.account_type = account_data["account_type"]
                updated = True

            if user.hashed_password != account_data["hashed_password"]:
                user.hashed_password = account_data["hashed_password"]
                updated = True

            if updated:
                session.add(user)
                changed = True

        if changed:
            session.commit()

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
    email = (data.get("email") or "").strip().lower()
    phone = (data.get("phone") or "").strip()
    password = data.get("password")
    account_type = data.get("account_type", "candidate")
    company_name = data.get("company_name")
    company_country = data.get("company_country")
    company_industry = data.get("company_industry")
    company_registration_number = data.get("company_registration_number")

    if not full_name or not email or not phone or not password:
        error("missing_fields")
    if account_type not in PUBLIC_ACCOUNT_TYPES:
        error("invalid_account_type")
    if account_type == "employer":
        if not company_name or not company_country or not company_industry:
            error("missing_company_fields")

    if session.exec(select(User).where(User.email == email)).first():
        error("user_exists")

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
    user = session.exec(select(User).where(User.email == email)).first()

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
    return current_user
