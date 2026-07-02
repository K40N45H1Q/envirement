from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Iterable

import jwt
from fastapi import HTTPException, status
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.user import User


ALGORITHM = "HS256"
PUBLIC_ACCOUNT_TYPES = {"candidate", "employer"}


def auth_error(key: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> HTTPException:
    return HTTPException(status_code=status_code, detail={"error": key})


def hash_password(password: str) -> str:
    return sha256(password.encode()).hexdigest()


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    return jwt.encode(
        {"user_id": user_id, "exp": int(expire.timestamp())},
        settings.jwt_secret_key,
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[ALGORITHM])
    except Exception as exc:
        raise auth_error("invalid_token", status.HTTP_401_UNAUTHORIZED) from exc

    user_id = payload.get("user_id")
    if not isinstance(user_id, int):
        raise auth_error("invalid_token", status.HTTP_401_UNAUTHORIZED)
    return user_id


def require_account_types(user: User, allowed_types: Iterable[str]) -> User:
    if user.account_type not in set(allowed_types):
        raise auth_error("forbidden", status.HTTP_403_FORBIDDEN)
    return user


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    query: Select[tuple[User]] = select(User).where(User.email == email)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    query: Select[tuple[User]] = select(User).where(User.id == user_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def ensure_email_is_available(session: AsyncSession, email: str) -> None:
    existing_user = await get_user_by_email(session, email)
    if existing_user is not None:
        raise auth_error("user_exists")


async def authenticate_user(
    session: AsyncSession,
    email: str,
    password: str,
) -> User:
    user = await get_user_by_email(session, email)
    if user is None or user.hashed_password != hash_password(password):
        raise auth_error("invalid_credentials", status.HTTP_401_UNAUTHORIZED)
    return user
