from datetime import datetime, timedelta, timezone
from hashlib import sha256
from secrets import token_urlsafe

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import select

from database.models import BetaAccessToken, CandidateProfile, Job, User, get_session
from app.services.beta_auth import (
    get_beta_access_enabled,
    normalize_beta_email,
    set_beta_access_enabled,
)
from routes.safety import get_current_user, serialize_user


router = APIRouter(prefix="/admin", tags=["admin"])
PLAN_IDS = {"basic", "standard", "pro"}
PLAN_JOB_LIMITS = {"basic": 1, "standard": 5, "pro": 20}


def require_admin(user: User) -> User:
    if user.account_type != "admin":
        raise HTTPException(status_code=403, detail={"error": "forbidden"})
    return user


def token_hash(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def serialize_beta_token(token: BetaAccessToken, assigned_user: User | None = None) -> dict:
    user_id = token.assigned_user_id if token.assigned_user_id else None
    return {
        "id": token.id,
        "token": token.token,
        "userId": user_id,
        "assigned_user_id": user_id,
        "assigned_user": serialize_user(assigned_user) if assigned_user else None,
        "created_by_user_id": token.created_by_user_id,
        "email": token.email or "",
        "is_active": token.is_active,
        "used": token.used_at is not None,
        "used_at": token.used_at,
        "usedAt": token.used_at,
        "last_used_at": token.last_used_at,
        "created_at": token.created_at,
        "createdAt": token.created_at,
        "updated_at": token.updated_at,
    }


def serialize_admin_user(user: User, beta_user_ids: set[int], avatar_url: str = "") -> dict:
    return {
        **serialize_user(user),
        "status": "active",
        "has_beta_access": user.id in beta_user_ids,
        "avatar_url": avatar_url,
    }


def serialize_admin_job(job: Job) -> dict:
    return {
        "id": job.id,
        "title": job.title,
        "occupation_id": job.occupation_id or "",
        "company": job.company,
        "status": job.status,
        "rejection_reason": job.rejection_reason or "",
        "quota_consumed": job.quota_consumed,
        "location": job.location,
        "salary": job.salary or "",
        "description": job.description or "",
        "category": job.category or "",
        "employment_type": job.employment_type or "",
        "country_label": job.country_label or "",
        "country_flag_code": job.country_flag_code or "",
        "logo": job.logo or "",
        "banner_url": job.banner_url or "",
        "user_id": job.user_id,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }


def subscription_expires_at() -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=30)


@router.get("/summary")
def get_admin_summary(
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    require_admin(current_user)
    users = session.exec(select(User)).all()
    tokens = session.exec(select(BetaAccessToken)).all()
    jobs = session.exec(select(Job)).all()

    return {
        "total_users": len(users),
        "candidates": len([user for user in users if user.account_type in {"candidate", "user"}]),
        "employers": len([user for user in users if user.account_type == "employer"]),
        "vacancies": len(jobs),
        "pending_vacancies": len([job for job in jobs if job.status == "pending"]),
        "active_beta_tokens": len([token for token in tokens if token.is_active]),
    }


@router.get("/users")
def get_admin_users(
    account_type: str | None = None,
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    require_admin(current_user)

    query = select(User).order_by(User.created_at.desc())
    if account_type == "candidate":
        query = query.where(User.account_type.in_(["candidate", "user"]))
    elif account_type == "employer":
        query = query.where(User.account_type == "employer")
    elif account_type == "admin":
        query = query.where(User.account_type == "admin")

    users = session.exec(query).all()
    beta_tokens = session.exec(select(BetaAccessToken).where(BetaAccessToken.is_active == True)).all()
    beta_user_ids = {token.assigned_user_id for token in beta_tokens}

    user_ids = [user.id for user in users if user.id is not None]
    profiles = session.exec(
        select(CandidateProfile).where(CandidateProfile.user_id.in_(user_ids))
    ).all() if user_ids else []
    avatars_by_user_id = {
        profile.user_id: profile.avatar_url or ""
        for profile in profiles
    }

    return [
        serialize_admin_user(user, beta_user_ids, avatars_by_user_id.get(user.id, ""))
        for user in users
    ]


@router.patch("/users/{user_id}/subscription")
async def update_user_subscription(
    user_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    require_admin(current_user)
    payload = await request.json()
    user = session.exec(select(User).where(User.id == user_id)).first()

    if not user:
        raise HTTPException(status_code=404, detail={"error": "user_not_found"})

    if user.account_type != "employer":
        raise HTTPException(status_code=400, detail={"error": "employer_account_required"})

    if payload.get("revoke"):
        user.subscription_plan = None
        user.subscription_expires_at = None
        user.subscription_jobs_used = 0
    else:
        plan = str(payload.get("plan") or "").strip().lower()
        if plan not in PLAN_IDS:
            raise HTTPException(status_code=400, detail={"error": "invalid_subscription_plan"})

        user.subscription_plan = plan
        user.subscription_expires_at = subscription_expires_at()
        user.subscription_jobs_used = 0

    session.add(user)
    session.commit()
    session.refresh(user)
    return serialize_admin_user(user, set())


@router.get("/jobs")
def get_admin_jobs(
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    require_admin(current_user)
    jobs = session.exec(select(Job).order_by(Job.created_at.desc())).all()
    return [serialize_admin_job(job) for job in jobs]


@router.get("/moderation/jobs")
def get_admin_moderation_jobs(
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    require_admin(current_user)
    jobs = session.exec(
        select(Job).where(Job.status == "pending").order_by(Job.created_at.desc())
    ).all()
    return [serialize_admin_job(job) for job in jobs]


@router.patch("/moderation/jobs/{job_id}/approve")
def approve_admin_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    require_admin(current_user)
    job = session.exec(select(Job).where(Job.id == job_id)).first()
    if not job:
        raise HTTPException(status_code=404, detail={"error": "job_not_found"})

    employer = session.get(User, job.user_id)
    if employer and employer.account_type == "employer" and not job.quota_consumed:
        expires_at = employer.subscription_expires_at
        if expires_at and expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if (
            employer.subscription_plan not in PLAN_JOB_LIMITS
            or not expires_at
            or expires_at <= datetime.now(timezone.utc)
        ):
            raise HTTPException(status_code=403, detail={"error": "subscription_required"})

        used_jobs = max(int(employer.subscription_jobs_used or 0), 0)
        if used_jobs >= PLAN_JOB_LIMITS[employer.subscription_plan]:
            raise HTTPException(status_code=403, detail={"error": "subscription_job_limit_reached"})

        employer.subscription_jobs_used = used_jobs + 1
        job.quota_consumed = True
        session.add(employer)

    job.status = "approved"
    job.rejection_reason = None
    session.add(job)
    session.commit()
    session.refresh(job)
    return serialize_admin_job(job)


@router.patch("/moderation/jobs/{job_id}/reject")
async def reject_admin_job(
    job_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    require_admin(current_user)
    payload = await request.json()
    reason = str(payload.get("reason") or "").strip()
    if not reason:
        raise HTTPException(status_code=400, detail={"error": "rejection_reason_required"})
    if len(reason) > 500:
        raise HTTPException(status_code=400, detail={"error": "rejection_reason_too_long"})

    job = session.exec(select(Job).where(Job.id == job_id)).first()
    if not job:
        raise HTTPException(status_code=404, detail={"error": "job_not_found"})
    job.status = "rejected"
    job.rejection_reason = reason
    session.add(job)
    session.commit()
    session.refresh(job)
    return serialize_admin_job(job)


@router.delete("/jobs/{job_id}")
def delete_admin_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    require_admin(current_user)
    job = session.exec(select(Job).where(Job.id == job_id)).first()
    if not job:
        raise HTTPException(status_code=404, detail={"error": "job_not_found"})
    session.delete(job)
    session.commit()
    return {"deleted": True, "id": job_id}


@router.get("/beta-tokens")
def get_beta_tokens(
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    require_admin(current_user)
    tokens = session.exec(select(BetaAccessToken).order_by(BetaAccessToken.created_at.desc())).all()
    assigned_user_ids = [token.assigned_user_id for token in tokens if token.assigned_user_id]
    users_by_id = {
        user.id: user
        for user in session.exec(select(User).where(User.id.in_(assigned_user_ids))).all()
    } if assigned_user_ids else {}

    return [
        serialize_beta_token(token, users_by_id.get(token.assigned_user_id))
        for token in tokens
    ]


@router.get("/beta-settings")
def get_beta_settings(
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    return {"enabled": get_beta_access_enabled()}


@router.patch("/beta-settings")
async def update_beta_settings(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    payload = await request.json()
    enabled = set_beta_access_enabled(bool(payload.get("enabled")))
    return {"enabled": enabled}


@router.post("/beta-tokens")
async def create_beta_token(
    request: Request,
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    require_admin(current_user)
    payload = await request.json()
    email = normalize_beta_email(payload.get("email"))
    if not email:
        raise HTTPException(status_code=400, detail={"error": "beta_token_email_required"})

    raw_token = token_urlsafe(24)
    beta_token = BetaAccessToken(
        token=raw_token,
        token_hash=token_hash(raw_token),
        email=email,
        created_by_user_id=current_user.id,
        is_active=True,
    )
    session.add(beta_token)
    session.commit()
    session.refresh(beta_token)

    return {
        **serialize_beta_token(beta_token),
        "token": raw_token,
    }


@router.patch("/beta-tokens/{token_id}")
async def update_beta_token(
    token_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    require_admin(current_user)
    payload = await request.json()
    beta_token = session.exec(select(BetaAccessToken).where(BetaAccessToken.id == token_id)).first()

    if not beta_token:
        raise HTTPException(status_code=404, detail={"error": "beta_token_not_found"})

    if "is_active" in payload:
        beta_token.is_active = bool(payload["is_active"])
    if "email" in payload:
        email = normalize_beta_email(payload.get("email"))
        if not email:
            raise HTTPException(status_code=400, detail={"error": "beta_token_email_required"})
        beta_token.email = email

    session.add(beta_token)
    session.commit()
    session.refresh(beta_token)

    assigned_user = session.exec(select(User).where(User.id == beta_token.assigned_user_id)).first() if beta_token.assigned_user_id else None
    return serialize_beta_token(beta_token, assigned_user)


@router.delete("/beta-tokens/{token_id}")
def delete_beta_token(
    token_id: int,
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    require_admin(current_user)
    beta_token = session.exec(select(BetaAccessToken).where(BetaAccessToken.id == token_id)).first()

    if not beta_token:
        raise HTTPException(status_code=404, detail={"error": "beta_token_not_found"})

    session.delete(beta_token)
    session.commit()
    return {"deleted": True, "id": token_id}
