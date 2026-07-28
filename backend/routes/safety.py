import json
import re
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from secrets import token_hex
from urllib.parse import urlsplit

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlmodel import select

from app.core.config import settings
from app.services.default_accounts import delete_user_dependencies
from app.services.beta_auth import (
    get_beta_access_enabled,
    get_beta_registration_token_record,
    mark_beta_access_token_used,
)
from app.services.supabase_client import get_supabase_auth_client, get_supabase_client
from app.services.supabase_storage import remove_file
from database.models import (
    BetaAccessToken,
    CandidateProfile,
    PasswordResetVerification,
    RegistrationVerification,
    User,
    get_session,
)

router = APIRouter()

ACCESS_COOKIE_NAME = settings.supabase_access_cookie_name
REFRESH_COOKIE_NAME = settings.supabase_refresh_cookie_name
PUBLIC_ACCOUNT_TYPES = {"candidate", "employer"}


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
        "subscription_jobs_used": user.subscription_jobs_used or 0,
        "has_active_subscription": has_active_subscription,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }


def hash_password(password: str) -> str:
    return sha256(password.encode()).hexdigest()


def is_secure_request(request: Request) -> bool:
    forwarded_proto = request.headers.get("x-forwarded-proto", "").split(",")[0].strip()
    return request.url.scheme == "https" or forwarded_proto == "https"


def normalize_origin(value: str | None) -> str | None:
    if not value:
        return None
    parsed = urlsplit(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")


def is_local_origin(origin: str) -> bool:
    hostname = urlsplit(origin).hostname or ""
    return hostname in {"localhost", "127.0.0.1", "::1"}


def get_supabase_email_redirect_to(request: Request) -> str | None:
    allowed_origins = {
        origin
        for origin in (normalize_origin(item) for item in settings.cors_origins)
        if origin
    }
    request_origin = normalize_origin(request.headers.get("origin"))
    if request_origin and request_origin in allowed_origins:
        return request_origin

    for origin in allowed_origins:
        if not is_local_origin(origin):
            return origin

    return None


def get_supabase_session(response):
    session = getattr(response, "session", None)
    if not session or not getattr(session, "access_token", None) or not getattr(session, "refresh_token", None):
        error("invalid_token", 401)
    return session


def set_supabase_session_cookies(response: Response, request: Request, session) -> None:
    access_max_age = int(getattr(session, "expires_in", None) or 3600)
    set_supabase_token_cookies(
        response,
        request,
        session.access_token,
        session.refresh_token,
        access_max_age,
    )


def set_supabase_token_cookies(
    response: Response,
    request: Request,
    access_token: str,
    refresh_token: str,
    access_max_age: int = 3600,
) -> None:
    response.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=access_token,
        max_age=access_max_age,
        httponly=True,
        secure=is_secure_request(request),
        samesite="lax",
        path="/api",
    )
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=30 * 24 * 60 * 60,
        httponly=True,
        secure=is_secure_request(request),
        samesite="lax",
        path="/api",
    )


def clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        httponly=True,
        samesite="lax",
        path="/api",
    )


def clear_access_cookie(response: Response) -> None:
    response.delete_cookie(
        key=ACCESS_COOKIE_NAME,
        httponly=True,
        samesite="lax",
        path="/api",
    )


def normalize_email(value: str | None) -> str:
    return (value or "").strip().lower()


def get_supabase_user_from_access_token(access_token: str):
    try:
        auth_response = get_supabase_auth_client().auth.get_user(access_token)
    except Exception:
        error("invalid_token", 401)

    auth_user = getattr(auth_response, "user", None)
    if not auth_user or not normalize_email(getattr(auth_user, "email", None)):
        error("invalid_token", 401)
    return auth_user


def refresh_supabase_session_from_token(refresh_token: str):
    try:
        return get_supabase_auth_client().auth.refresh_session(refresh_token)
    except Exception:
        error("invalid_token", 401)


def raise_supabase_email_error() -> None:
    error("supabase_email_delivery_failed", 500)


def send_supabase_signup_email(payload: dict, redirect_to: str | None, resend: bool = False) -> None:
    auth_client = get_supabase_auth_client()
    options = {
        "data": {
            "full_name": payload["full_name"],
            "phone": payload["phone"],
            "account_type": payload["account_type"],
        },
    }
    if redirect_to:
        options["email_redirect_to"] = redirect_to

    try:
        if resend:
            auth_client.auth.resend(
                {
                    "type": "signup",
                    "email": payload["email"],
                    "options": {"email_redirect_to": redirect_to} if redirect_to else {},
                }
            )
            return

        auth_client.auth.sign_up(
            {
                "email": payload["email"],
                "password": payload["password"],
                "options": options,
            }
        )
    except Exception:
        raise_supabase_email_error()


def find_supabase_auth_user(email: str):
    try:
        users = get_supabase_client().auth.admin.list_users()
    except Exception:
        return None

    normalized_email = normalize_email(email)
    for auth_user in users:
        if normalize_email(getattr(auth_user, "email", None)) == normalized_email:
            return auth_user
    return None


def find_supabase_auth_user_id(email: str) -> str | None:
    auth_user = find_supabase_auth_user(email)
    return getattr(auth_user, "id", None) if auth_user else None


def send_supabase_magic_link(email: str, redirect_to: str | None) -> None:
    options = {"should_create_user": False}
    if redirect_to:
        options["email_redirect_to"] = redirect_to

    try:
        get_supabase_auth_client().auth.sign_in_with_otp(
            {
                "email": email,
                "options": options,
            }
        )
    except Exception:
        raise_supabase_email_error()


def ensure_supabase_auth_user(user: User, password: str | None = None) -> None:
    auth_password = password or f"{token_hex(32)}A1!"
    metadata = {
        "full_name": user.full_name or "",
        "phone": user.phone or "",
        "account_type": user.account_type,
    }
    auth_user_id = find_supabase_auth_user_id(user.email)
    if auth_user_id:
        return

    try:
        get_supabase_client().auth.admin.create_user(
            {
                "email": user.email,
                "password": auth_password,
                "email_confirm": True,
                "user_metadata": metadata,
            }
        )
    except Exception:
        pass


def send_supabase_password_reset_email(user: User, redirect_to: str | None) -> None:
    ensure_supabase_auth_user(user)
    try:
        if redirect_to:
            get_supabase_auth_client().auth.reset_password_for_email(
                user.email,
                {"redirect_to": redirect_to},
            )
            return
        get_supabase_auth_client().auth.reset_password_for_email(
            user.email,
        )
    except Exception:
        raise_supabase_email_error()


def update_supabase_password(user_id: str | None, password: str) -> None:
    if not user_id:
        raise_supabase_email_error()
    try:
        get_supabase_client().auth.admin.update_user_by_id(user_id, {"password": password})
    except Exception:
        raise_supabase_email_error()


def sign_in_with_supabase(email: str, password: str):
    try:
        return get_supabase_auth_client().auth.sign_in_with_password(
            {
                "email": email,
                "password": password,
            }
        )
    except Exception:
        error("invalid_credentials", 401)


def get_local_user_for_auth_response(auth_response, session) -> User:
    auth_user = getattr(auth_response, "user", None)
    return get_local_user_for_supabase_user(auth_user, session)


def get_local_user_for_supabase_user(auth_user, session) -> User:
    email = normalize_email(getattr(auth_user, "email", None))
    if not email:
        error("invalid_token", 401)

    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        error("user_not_found", 401)
    return user


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
    request: Request,
    response: Response,
    authorization: str | None = Header(None),
    session=Depends(get_session),
) -> User:
    token = request.cookies.get(ACCESS_COOKIE_NAME)
    if not token and authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "", 1)

    refresh_token = request.cookies.get(REFRESH_COOKIE_NAME)

    if not token and not refresh_token:
        error("unauthorized", 401)

    refreshed_session = None

    try:
        if token:
            auth_response = get_supabase_auth_client().auth.get_user(token)
        else:
            auth_response = refresh_supabase_session_from_token(refresh_token)
            refreshed_session = get_supabase_session(auth_response)
    except Exception:
        if not refresh_token:
            error("invalid_token", 401)
        auth_response = refresh_supabase_session_from_token(refresh_token)
        refreshed_session = get_supabase_session(auth_response)

    if refreshed_session:
        set_supabase_token_cookies(
            response,
            request,
            refreshed_session.access_token,
            refreshed_session.refresh_token,
            int(getattr(refreshed_session, "expires_in", None) or 3600),
        )

    auth_user = getattr(auth_response, "user", None)
    email = normalize_email(getattr(auth_user, "email", None))
    if not email:
        error("invalid_token", 401)

    user = session.exec(select(User).where(User.email == email)).first()
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


def complete_pending_registration(email: str, session) -> User:
    user = session.exec(select(User).where(User.email == email)).first()
    if user:
        return user

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
    return user


def ensure_utc_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def upsert_registration_verification(payload: dict, session) -> bool:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.registration_code_expire_minutes
    )
    pending_payload = build_pending_payload(payload)

    pending_registration = session.exec(
        select(RegistrationVerification).where(RegistrationVerification.email == payload["email"])
    ).first()

    is_existing_registration = bool(pending_registration)

    if not pending_registration:
        pending_registration = RegistrationVerification(
            email=payload["email"],
            code_hash="supabase",
            payload_json=json.dumps(pending_payload),
            expires_at=expires_at,
            attempts=0,
        )
    else:
        pending_registration.code_hash = "supabase"
        pending_registration.payload_json = json.dumps(pending_payload)
        pending_registration.expires_at = expires_at
        pending_registration.attempts = 0

    session.add(pending_registration)
    session.commit()
    return is_existing_registration


def upsert_password_reset_verification(email: str, session) -> None:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.password_reset_code_expire_minutes
    )

    reset_verification = session.exec(
        select(PasswordResetVerification).where(PasswordResetVerification.email == email)
    ).first()

    if not reset_verification:
        reset_verification = PasswordResetVerification(
            email=email,
            code_hash="supabase",
            expires_at=expires_at,
            attempts=0,
        )
    else:
        reset_verification.code_hash = "supabase"
        reset_verification.expires_at = expires_at
        reset_verification.attempts = 0

    session.add(reset_verification)
    session.commit()


@router.post("/request_registration_link")
async def request_registration_link(
    request: Request,
    session=Depends(get_session),
):
    data = await read_json_object(request)
    payload = extract_registration_payload(data)

    validate_registration_payload(payload)
    ensure_registration_is_unique(payload, session)

    if get_beta_access_enabled():
        error("beta_registration_closed", 403)

    is_existing_registration = upsert_registration_verification(payload, session)
    existing_auth_user = find_supabase_auth_user(payload["email"])

    try:
        redirect_to = get_supabase_email_redirect_to(request)
        if existing_auth_user and getattr(existing_auth_user, "email_confirmed_at", None):
            send_supabase_magic_link(payload["email"], redirect_to)
        else:
            send_supabase_signup_email(
                payload,
                redirect_to,
                resend=is_existing_registration or bool(existing_auth_user),
            )
    except HTTPException:
        pending_registration = session.exec(
            select(RegistrationVerification).where(RegistrationVerification.email == payload["email"])
        ).first()
        if pending_registration:
            session.delete(pending_registration)
            session.commit()
        raise
    return {
        "status": "ok",
        "email": payload["email"],
        "expires_in_minutes": settings.registration_code_expire_minutes,
    }


@router.get("/registration_options")
def get_registration_options():
    return {
        "beta_access_required": get_beta_access_enabled(),
    }


@router.post("/request_password_reset_link")
async def request_password_reset_link(
    request: Request,
    session=Depends(get_session),
):
    data = await read_json_object(request)
    email = normalize_email(data.get("email"))

    if not email:
        error("missing_reset_email")

    user = session.exec(select(User).where(User.email == email)).first()
    if user:
        try:
            upsert_password_reset_verification(email, session)
            send_supabase_password_reset_email(user, get_supabase_email_redirect_to(request))
        except HTTPException:
            reset_verification = session.exec(
                select(PasswordResetVerification).where(PasswordResetVerification.email == email)
            ).first()
            if reset_verification:
                session.delete(reset_verification)
                session.commit()
            raise

    return {
        "status": "ok",
        "email": email,
        "expires_in_minutes": settings.password_reset_code_expire_minutes,
    }


@router.post("/auth/email-link")
async def complete_email_link_auth(
    request: Request,
    session=Depends(get_session),
):
    data = await read_json_object(request)
    access_token = data.get("access_token") or data.get("accessToken") or ""
    refresh_token = data.get("refresh_token") or data.get("refreshToken") or ""
    auth_type = data.get("type") or ""

    if not access_token or not refresh_token:
        error("missing_auth_tokens", 401)

    try:
        access_max_age = int(data.get("expires_in") or data.get("expiresIn") or 3600)
    except (TypeError, ValueError):
        access_max_age = 3600

    try:
        auth_user = get_supabase_user_from_access_token(access_token)
    except HTTPException as exc:
        if exc.status_code != 401:
            raise
        auth_response = refresh_supabase_session_from_token(refresh_token)
        auth_user = getattr(auth_response, "user", None)
        refreshed_session = get_supabase_session(auth_response)
        access_token = refreshed_session.access_token
        refresh_token = refreshed_session.refresh_token
        access_max_age = int(getattr(refreshed_session, "expires_in", None) or access_max_age)

    email = normalize_email(getattr(auth_user, "email", None))
    if not email:
        error("invalid_token", 401)

    if auth_type in {"signup", "email", "magiclink"}:
        user = complete_pending_registration(email, session)
    else:
        user = get_local_user_for_supabase_user(auth_user, session)

    response = JSONResponse(jsonable_encoder({
        "status": "ok",
        "type": auth_type,
        "user": serialize_user(user),
    }))
    set_supabase_token_cookies(response, request, access_token, refresh_token, access_max_age)
    return response


@router.post("/auth/recovery-password")
async def update_recovery_password(
    request: Request,
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    data = await read_json_object(request)
    new_password = data.get("new_password") or data.get("newPassword") or ""
    if not new_password:
        error("missing_reset_fields")

    if not is_password_strong(new_password):
        error("weak_password")

    auth_user_id = find_supabase_auth_user_id(current_user.email)
    update_supabase_password(auth_user_id, new_password)
    current_user.hashed_password = hash_password(new_password)
    session.add(current_user)
    reset_verification = session.exec(
        select(PasswordResetVerification).where(PasswordResetVerification.email == current_user.email)
    ).first()
    if reset_verification:
        session.delete(reset_verification)
    session.commit()

    auth_response = sign_in_with_supabase(current_user.email, new_password)
    user = get_local_user_for_auth_response(auth_response, session)

    response = JSONResponse(jsonable_encoder({
        "status": "ok",
        "user": serialize_user(user),
    }))
    set_supabase_session_cookies(response, request, get_supabase_session(auth_response))
    return response


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

    if get_beta_access_enabled():
        beta_token = get_beta_registration_token_record(password, email)
        if not beta_token:
            error("invalid_beta_credentials", 401)

        user = session.exec(select(User).where(User.email == email)).first()
        if not user:
            user = User(
                full_name=email,
                email=email,
                phone="",
                account_type="candidate",
                hashed_password=hash_password(password),
            )
            session.add(user)
            session.commit()
            session.refresh(user)

        auth_user_id = find_supabase_auth_user_id(email)
        if auth_user_id:
            update_supabase_password(auth_user_id, password)
        else:
            ensure_supabase_auth_user(user, password)

        auth_response = sign_in_with_supabase(email, password)
        mark_beta_access_token_used(beta_token)
    else:
        auth_response = sign_in_with_supabase(email, password)

    user = get_local_user_for_auth_response(auth_response, session)

    response = JSONResponse(jsonable_encoder({
        "status": "ok",
        "user": serialize_user(user),
    }))
    set_supabase_session_cookies(response, request, get_supabase_session(auth_response))
    return response


@router.post("/refresh")
def refresh_session(
    request: Request,
    session=Depends(get_session),
):
    refresh_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not refresh_token:
        error("refresh_token_missing", 401)

    auth_response = refresh_supabase_session_from_token(refresh_token)

    user = get_local_user_for_auth_response(auth_response, session)

    response = JSONResponse(jsonable_encoder({
        "status": "ok",
        "user": serialize_user(user),
    }))
    set_supabase_session_cookies(response, request, get_supabase_session(auth_response))
    return response


@router.post("/logout")
def logout_session():
    response = JSONResponse({"status": "ok"})
    clear_access_cookie(response)
    clear_refresh_cookie(response)
    return response


@router.get("/get_me")
def get_me(current_user: User = Depends(get_current_user)):
    return serialize_user(current_user)


@router.delete("/account")
def delete_account(
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    if current_user.account_type == "admin":
        error("admin_account_deletion_forbidden", 403)

    beta_tokens = session.exec(
        select(BetaAccessToken).where(
            (BetaAccessToken.assigned_user_id == current_user.id)
            | (BetaAccessToken.created_by_user_id == current_user.id)
        )
    ).all()
    for beta_token in beta_tokens:
        if beta_token.assigned_user_id == current_user.id:
            beta_token.assigned_user_id = None
        if beta_token.created_by_user_id == current_user.id:
            beta_token.created_by_user_id = None
        session.add(beta_token)

    registration = session.exec(
        select(RegistrationVerification).where(RegistrationVerification.email == current_user.email)
    ).first()
    if registration:
        session.delete(registration)

    password_reset = session.exec(
        select(PasswordResetVerification).where(PasswordResetVerification.email == current_user.email)
    ).first()
    if password_reset:
        session.delete(password_reset)

    upload_urls = delete_user_dependencies(session, current_user)
    session.delete(current_user)
    session.commit()

    for upload_url in upload_urls:
        remove_file(upload_url)

    response = JSONResponse({"status": "ok", "deleted": True})
    clear_access_cookie(response)
    clear_refresh_cookie(response)
    return response
