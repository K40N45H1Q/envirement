from datetime import datetime, timezone
from hashlib import sha256
from secrets import token_urlsafe

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import select

from database.models import BetaAccessToken, Job, User, get_session
from routes.safety import get_current_user, serialize_user


router = APIRouter(prefix="/admin", tags=["admin"])


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
        "note": token.note or "",
        "is_active": token.is_active,
        "used": token.used_at is not None,
        "used_at": token.used_at,
        "usedAt": token.used_at,
        "last_used_at": token.last_used_at,
        "created_at": token.created_at,
        "createdAt": token.created_at,
        "updated_at": token.updated_at,
    }


def serialize_admin_user(user: User, beta_user_ids: set[int]) -> dict:
    return {
        **serialize_user(user),
        "status": "active",
        "has_beta_access": user.id in beta_user_ids,
    }


def serialize_admin_job(job: Job) -> dict:
    return {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "status": job.status,
        "location": job.location,
        "salary": job.salary or "",
        "user_id": job.user_id,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
    }


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

    return [serialize_admin_user(user, beta_user_ids) for user in users]


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
    job.status = "approved"
    session.add(job)
    session.commit()
    session.refresh(job)
    return serialize_admin_job(job)


@router.patch("/moderation/jobs/{job_id}/reject")
def reject_admin_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    require_admin(current_user)
    job = session.exec(select(Job).where(Job.id == job_id)).first()
    if not job:
        raise HTTPException(status_code=404, detail={"error": "job_not_found"})
    job.status = "rejected"
    session.add(job)
    session.commit()
    session.refresh(job)
    return serialize_admin_job(job)


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


@router.post("/beta-tokens")
async def create_beta_token(
    request: Request,
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    require_admin(current_user)
    payload = await request.json()
    note = str(payload.get("note") or "").strip() or None

    raw_token = token_urlsafe(24)
    beta_token = BetaAccessToken(
        token=raw_token,
        token_hash=token_hash(raw_token),
        assigned_user_id=0,
        created_by_user_id=current_user.id,
        note=note,
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
    if "note" in payload:
        beta_token.note = str(payload.get("note") or "").strip() or None

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
