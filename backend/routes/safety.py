import secrets
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from os import getenv

import jwt
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlmodel import Session, select

from database.models import User, engine, get_session

router = APIRouter()

SECRET_KEY = getenv("SECRET_KEY") or secrets.token_hex(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
PUBLIC_ACCOUNT_TYPES = {"user", "employer"}
DEFAULT_ADMIN_EMAIL = getenv("DEFAULT_ADMIN_EMAIL", "admin@cvhold.local")
DEFAULT_ADMIN_PASSWORD = getenv("DEFAULT_ADMIN_PASSWORD", "CVHOLD_Admin_2026_Secure!")


def error(key: str, status: int = 400):
    raise HTTPException(status_code=status, detail={"error": key})


def hash_password(password: str) -> str:
    return sha256(password.encode()).hexdigest()


def ensure_default_admin():
    admin_password_hash = hash_password(DEFAULT_ADMIN_PASSWORD)

    with Session(engine) as session:
        admin = session.exec(
            select(User).where(User.email == DEFAULT_ADMIN_EMAIL)
        ).first()

        if not admin:
            admin = User(
                email=DEFAULT_ADMIN_EMAIL,
                account_type="admin",
                hashed_password=admin_password_hash,
            )
            session.add(admin)
            session.commit()
            return

        updated = False

        if admin.account_type != "admin":
            admin.account_type = "admin"
            updated = True

        if admin.hashed_password != admin_password_hash:
            admin.hashed_password = admin_password_hash
            updated = True

        if updated:
            session.add(admin)
            session.commit()


def require_account_types(user: User, *allowed_types: str) -> User:
    if user.account_type not in allowed_types:
        error("forbidden", 403)
    return user


def get_current_user(
    authorization: str = Header(...),
    session=Depends(get_session),
) -> User:
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
    email = data.get("email")
    password = data.get("password")
    account_type = data.get("account_type", "user")

    if not email or not password:
        error("missing_fields")
    if account_type not in PUBLIC_ACCOUNT_TYPES:
        error("invalid_account_type")

    if session.exec(select(User).where(User.email == email)).first():
        error("user_exists")

    user = User(
        email=email,
        account_type=account_type,
        hashed_password=hash_password(password),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

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
