from hashlib import sha256

from sqlmodel import Session, select

from app.core.config import settings
from database.models import CandidateProfile, Job, JobApplication, Message, User, engine


DEFAULT_EMPLOYER_KIND = "employer"
DEFAULT_CANDIDATE_KIND = "candidate"
LEGACY_EMAILS_BY_KIND = {
    DEFAULT_EMPLOYER_KIND: {"employer@cvhold.local"},
    DEFAULT_CANDIDATE_KIND: {"candidate@cvhold.local"},
}


def hash_password(password: str) -> str:
    return sha256(password.encode()).hexdigest()


def split_full_name(full_name: str) -> tuple[str, str]:
    normalized_parts = [part for part in full_name.strip().split() if part]
    if not normalized_parts:
        return "", ""
    if len(normalized_parts) == 1:
        return normalized_parts[0], ""
    return normalized_parts[0], " ".join(normalized_parts[1:])


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


def _ensure_candidate_profile(session: Session, user: User) -> None:
    first_name, last_name = split_full_name(user.full_name or "")
    profile = session.exec(
        select(CandidateProfile).where(CandidateProfile.user_id == user.id)
    ).first()

    if profile:
        profile.first_name = first_name
        profile.last_name = last_name
        profile.phone = user.phone
        return

    session.add(
        CandidateProfile(
            user_id=user.id,
            first_name=first_name,
            last_name=last_name,
            phone=user.phone,
        )
    )


def _upsert_default_candidate(session: Session, email: str, password: str) -> None:
    _delete_default_users_of_kind(session, DEFAULT_CANDIDATE_KIND, keep_email=email)

    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        user = User(
            full_name="Default Candidate",
            email=email,
            phone=None,
            hashed_password=hash_password(password),
            account_type="candidate",
            is_default_account=True,
            default_account_kind=DEFAULT_CANDIDATE_KIND,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
    else:
        user.full_name = user.full_name or "Default Candidate"
        user.account_type = "candidate"
        user.is_default_account = True
        user.default_account_kind = DEFAULT_CANDIDATE_KIND
        user.hashed_password = hash_password(password)
        user.company_name = None
        user.company_logo_url = None
        user.company_country = None
        user.company_industry = None
        user.company_registration_number = None

    _ensure_candidate_profile(session, user)


def _upsert_default_employer(session: Session, email: str, password: str) -> None:
    _delete_default_users_of_kind(session, DEFAULT_EMPLOYER_KIND, keep_email=email)

    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        user = User(
            full_name="Default Employer",
            email=email,
            phone=None,
            hashed_password=hash_password(password),
            account_type="employer",
            is_default_account=True,
            default_account_kind=DEFAULT_EMPLOYER_KIND,
            company_name="CVHOLD Employer",
            company_country="latvia",
            company_industry="administrative-work",
        )
        session.add(user)
        return

    user.full_name = user.full_name or "Default Employer"
    user.account_type = "employer"
    user.is_default_account = True
    user.default_account_kind = DEFAULT_EMPLOYER_KIND
    user.hashed_password = hash_password(password)
    user.company_name = user.company_name or "CVHOLD Employer"
    user.company_country = user.company_country or "latvia"
    user.company_industry = user.company_industry or "administrative-work"


def sync_default_accounts() -> None:
    employer_email = settings.default_employer_login
    employer_password = settings.default_employer_password
    candidate_email = settings.default_candidate_login
    candidate_password = settings.default_candidate_password

    with Session(engine) as session:
        if employer_email and employer_password:
            _upsert_default_employer(session, employer_email, employer_password)
        else:
            _delete_default_users_of_kind(session, DEFAULT_EMPLOYER_KIND)

        if candidate_email and candidate_password:
            _upsert_default_candidate(session, candidate_email, candidate_password)
        else:
            _delete_default_users_of_kind(session, DEFAULT_CANDIDATE_KIND)

        session.commit()
