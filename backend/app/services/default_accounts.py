from hashlib import sha256

from sqlmodel import Session, select

from app.core.config import settings
from database.models import CandidateProfile, Job, JobApplication, Message, User, engine


DEFAULT_EMPLOYER_KIND = "employer"
DEFAULT_CANDIDATE_KIND = "candidate"
DEFAULT_ADMIN_KIND = "admin"
LEGACY_EMAILS_BY_KIND = {
    DEFAULT_EMPLOYER_KIND: {"employer@cvhold.local"},
    DEFAULT_CANDIDATE_KIND: {"candidate@cvhold.local"},
    DEFAULT_ADMIN_KIND: set(),
}


def hash_password(password: str) -> str:
    return sha256(password.encode()).hexdigest()


def _delete_user_dependencies(session: Session, user: User) -> None:
    profile = session.exec(
        select(CandidateProfile).where(CandidateProfile.user_id == user.id)
    ).first()
    if profile:
        session.delete(profile)

    user_applications = session.exec(
        select(JobApplication).where(JobApplication.applicant_user_id == user.id)
    ).all()
    application_ids = {application.id for application in user_applications if application.id is not None}

    user_jobs = session.exec(select(Job).where(Job.user_id == user.id)).all()
    job_ids = {job.id for job in user_jobs if job.id is not None}

    if job_ids:
        related_job_applications = session.exec(
            select(JobApplication).where(JobApplication.job_id.in_(job_ids))
        ).all()
        application_ids.update(
            application.id for application in related_job_applications if application.id is not None
        )
        for application in related_job_applications:
            session.delete(application)

    if application_ids:
        related_messages = session.exec(
            select(Message).where(Message.application_id.in_(application_ids))
        ).all()
        for message in related_messages:
            session.delete(message)

    direct_messages = session.exec(
        select(Message).where(
            (Message.sender_user_id == user.id) | (Message.recipient_user_id == user.id)
        )
    ).all()
    for message in direct_messages:
        session.delete(message)

    for application in user_applications:
        session.delete(application)

    for job in user_jobs:
        session.delete(job)


def _delete_user(session: Session, user: User | None) -> None:
    if not user:
        return

    _delete_user_dependencies(session, user)
    session.delete(user)


def _delete_default_users_of_kind(session: Session, account_kind: str, keep_email: str | None = None) -> None:
    users = session.exec(
        select(User).where(User.default_account_kind == account_kind)
    ).all()
    for user in users:
        if keep_email and user.email == keep_email:
            continue
        _delete_user(session, user)

    legacy_emails = LEGACY_EMAILS_BY_KIND.get(account_kind, set())
    for legacy_email in legacy_emails:
        if keep_email and legacy_email == keep_email:
            continue
        legacy_user = session.exec(select(User).where(User.email == legacy_email)).first()
        _delete_user(session, legacy_user)


def _upsert_default_admin(session: Session, email: str, password: str) -> None:
    _delete_default_users_of_kind(session, DEFAULT_ADMIN_KIND, keep_email=email)

    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        session.add(
            User(
                full_name="CVHOLD Admin",
                email=email,
                phone=None,
                hashed_password=hash_password(password),
                account_type="admin",
                is_default_account=True,
                default_account_kind=DEFAULT_ADMIN_KIND,
            )
        )
        return

    user.full_name = user.full_name or "CVHOLD Admin"
    user.account_type = "admin"
    user.is_default_account = True
    user.default_account_kind = DEFAULT_ADMIN_KIND
    user.hashed_password = hash_password(password)


def sync_default_accounts() -> None:
    admin_email = settings.default_admin_login
    admin_password = settings.default_admin_password

    with Session(engine) as session:
        _delete_default_users_of_kind(session, DEFAULT_EMPLOYER_KIND)
        _delete_default_users_of_kind(session, DEFAULT_CANDIDATE_KIND)

        if admin_email and admin_password:
            _upsert_default_admin(session, admin_email, admin_password)
        else:
            _delete_default_users_of_kind(session, DEFAULT_ADMIN_KIND)

        session.commit()
