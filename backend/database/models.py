from typing import Optional
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field, create_engine, Session
from sqlalchemy import event


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: Optional[str] = None
    email: str
    phone: Optional[str] = None
    hashed_password: str
    account_type: str
    is_default_account: bool = Field(default=False)
    default_account_kind: Optional[str] = None
    company_name: Optional[str] = None
    company_logo_url: Optional[str] = None
    company_country: Optional[str] = None
    company_industry: Optional[str] = None
    company_registration_number: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Job(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    status: str = Field(default="pending")
    company: str
    category: Optional[str] = None
    location: str
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    required_from: Optional[str] = None
    remote_allowed: bool = Field(default=False)
    education_level: Optional[str] = None
    country_key: Optional[str] = None
    country_label: Optional[str] = None
    country_flag_code: Optional[str] = None
    description: Optional[str] = None
    salary: Optional[str] = None
    logo: Optional[str] = None
    banner_url: Optional[str] = None
    languages_json: Optional[str] = None
    licenses_json: Optional[str] = None
    has_housing: bool = Field(default=False)
    has_transport: bool = Field(default=False)
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class JobApplication(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: int = Field(foreign_key="job.id")
    applicant_user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    phone: str
    email: str
    username: Optional[str] = None
    name: str
    surname: str
    nationality: Optional[str] = None
    message: Optional[str] = None
    chat_approved: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    application_id: int = Field(foreign_key="jobapplication.id", index=True)
    sender_user_id: int = Field(foreign_key="user.id", index=True)
    recipient_user_id: int = Field(foreign_key="user.id", index=True)
    body: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CandidateProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    summary: Optional[str] = None
    current_role: Optional[str] = None
    skills: Optional[str] = None
    sectors_json: Optional[str] = None
    languages_json: Optional[str] = None
    licenses_json: Optional[str] = None
    mobility: Optional[str] = None
    preferred_mobility: Optional[str] = None
    salary_expectation: Optional[str] = None
    preferred_employment_type: Optional[str] = None
    education_level: Optional[str] = None
    remote_ready: bool = Field(default=False)
    work_permit: Optional[str] = None
    availability: Optional[str] = None
    resume_name: Optional[str] = None
    resume_url: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BetaBlockedIP(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ip_address: str = Field(index=True, unique=True)
    failed_attempts: int = Field(default=0)
    is_blocked: bool = Field(default=False)
    blocked_at: Optional[datetime] = None
    last_failed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BetaAccessToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    token: str = Field(default="")
    token_hash: str = Field(index=True, unique=True)
    assigned_user_id: int = Field(foreign_key="user.id", index=True)
    created_by_user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    note: Optional[str] = None
    is_active: bool = Field(default=True)
    used_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BetaAccessSetting(SQLModel, table=True):
    id: Optional[int] = Field(default=1, primary_key=True)
    enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RegistrationVerification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    code_hash: str
    payload_json: str
    expires_at: datetime
    attempts: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PasswordResetVerification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    code_hash: str
    expires_at: datetime
    attempts: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


@event.listens_for(User, "before_update")
def update_user_timestamp(mapper, connection, target):
    target.updated_at = datetime.now(timezone.utc)


@event.listens_for(Job, "before_update")
def update_job_timestamp(mapper, connection, target):
    target.updated_at = datetime.now(timezone.utc)


@event.listens_for(CandidateProfile, "before_update")
def update_candidate_profile_timestamp(mapper, connection, target):
    target.updated_at = datetime.now(timezone.utc)


@event.listens_for(BetaBlockedIP, "before_update")
def update_beta_blocked_ip_timestamp(mapper, connection, target):
    target.updated_at = datetime.now(timezone.utc)


@event.listens_for(BetaAccessToken, "before_update")
def update_beta_access_token_timestamp(mapper, connection, target):
    target.updated_at = datetime.now(timezone.utc)


@event.listens_for(BetaAccessSetting, "before_update")
def update_beta_access_setting_timestamp(mapper, connection, target):
    target.updated_at = datetime.now(timezone.utc)


@event.listens_for(RegistrationVerification, "before_update")
def update_registration_verification_timestamp(mapper, connection, target):
    target.updated_at = datetime.now(timezone.utc)


@event.listens_for(PasswordResetVerification, "before_update")
def update_password_reset_verification_timestamp(mapper, connection, target):
    target.updated_at = datetime.now(timezone.utc)


engine = create_engine("sqlite:///default.db", echo=False)
SQLModel.metadata.create_all(engine)


def ensure_beta_access_token_columns():
    with engine.begin() as connection:
        columns = {
            row[1]
            for row in connection.exec_driver_sql("PRAGMA table_info(betaaccesstoken)").fetchall()
        }

        if "token" not in columns:
            connection.exec_driver_sql(
                "ALTER TABLE betaaccesstoken ADD COLUMN token VARCHAR NOT NULL DEFAULT ''"
            )


ensure_beta_access_token_columns()


def ensure_job_columns():
    with engine.begin() as connection:
        columns = {
            row[1]
            for row in connection.exec_driver_sql("PRAGMA table_info(job)").fetchall()
        }

        if "has_housing" not in columns:
            connection.exec_driver_sql(
                "ALTER TABLE job ADD COLUMN has_housing BOOLEAN NOT NULL DEFAULT 0"
            )

        if "has_transport" not in columns:
            connection.exec_driver_sql(
                "ALTER TABLE job ADD COLUMN has_transport BOOLEAN NOT NULL DEFAULT 0"
            )

        if "languages_json" not in columns:
            connection.exec_driver_sql(
                "ALTER TABLE job ADD COLUMN languages_json VARCHAR"
            )

        if "licenses_json" not in columns:
            connection.exec_driver_sql(
                "ALTER TABLE job ADD COLUMN licenses_json VARCHAR"
            )

        if "country_key" not in columns:
            connection.exec_driver_sql(
                "ALTER TABLE job ADD COLUMN country_key VARCHAR"
            )

        if "country_label" not in columns:
            connection.exec_driver_sql(
                "ALTER TABLE job ADD COLUMN country_label VARCHAR"
            )

        if "country_flag_code" not in columns:
            connection.exec_driver_sql(
                "ALTER TABLE job ADD COLUMN country_flag_code VARCHAR"
            )

        if "employment_type" not in columns:
            connection.exec_driver_sql(
                "ALTER TABLE job ADD COLUMN employment_type VARCHAR"
            )

        if "experience_level" not in columns:
            connection.exec_driver_sql(
                "ALTER TABLE job ADD COLUMN experience_level VARCHAR"
            )

        if "category" not in columns:
            connection.exec_driver_sql(
                "ALTER TABLE job ADD COLUMN category VARCHAR"
            )

        if "required_from" not in columns:
            connection.exec_driver_sql(
                "ALTER TABLE job ADD COLUMN required_from VARCHAR"
            )

        if "remote_allowed" not in columns:
            connection.exec_driver_sql(
                "ALTER TABLE job ADD COLUMN remote_allowed BOOLEAN NOT NULL DEFAULT 0"
            )

        if "education_level" not in columns:
            connection.exec_driver_sql(
                "ALTER TABLE job ADD COLUMN education_level VARCHAR"
            )

        if "banner_url" not in columns:
            connection.exec_driver_sql(
                "ALTER TABLE job ADD COLUMN banner_url VARCHAR"
            )


def ensure_user_columns():
    with engine.begin() as connection:
        columns = {
            row[1]
            for row in connection.exec_driver_sql("PRAGMA table_info(user)").fetchall()
        }

        additions = {
            "full_name": "ALTER TABLE user ADD COLUMN full_name VARCHAR",
            "is_default_account": "ALTER TABLE user ADD COLUMN is_default_account BOOLEAN NOT NULL DEFAULT 0",
            "default_account_kind": "ALTER TABLE user ADD COLUMN default_account_kind VARCHAR",
            "company_name": "ALTER TABLE user ADD COLUMN company_name VARCHAR",
            "company_logo_url": "ALTER TABLE user ADD COLUMN company_logo_url VARCHAR",
            "company_country": "ALTER TABLE user ADD COLUMN company_country VARCHAR",
            "company_industry": "ALTER TABLE user ADD COLUMN company_industry VARCHAR",
            "company_registration_number": "ALTER TABLE user ADD COLUMN company_registration_number VARCHAR",
            "phone": "ALTER TABLE user ADD COLUMN phone VARCHAR",
        }

        for column, statement in additions.items():
            if column not in columns:
                connection.exec_driver_sql(statement)


ensure_job_columns()
ensure_user_columns()


def ensure_application_columns():
    with engine.begin() as connection:
        columns = {
            row[1]
            for row in connection.exec_driver_sql("PRAGMA table_info(jobapplication)").fetchall()
        }

        if "chat_approved" not in columns:
            connection.exec_driver_sql(
                "ALTER TABLE jobapplication ADD COLUMN chat_approved BOOLEAN NOT NULL DEFAULT 0"
            )


ensure_application_columns()


def ensure_candidate_profile_columns():
    with engine.begin() as connection:
        columns = {
            row[1]
            for row in connection.exec_driver_sql("PRAGMA table_info(candidateprofile)").fetchall()
        }

        additions = {
            "salary_expectation": "ALTER TABLE candidateprofile ADD COLUMN salary_expectation VARCHAR",
            "preferred_employment_type": "ALTER TABLE candidateprofile ADD COLUMN preferred_employment_type VARCHAR",
            "education_level": "ALTER TABLE candidateprofile ADD COLUMN education_level VARCHAR",
            "remote_ready": "ALTER TABLE candidateprofile ADD COLUMN remote_ready BOOLEAN NOT NULL DEFAULT 0",
        }

        for column, statement in additions.items():
            if column not in columns:
                connection.exec_driver_sql(statement)


ensure_candidate_profile_columns()


def get_session():
    with Session(engine) as session:
        yield session
