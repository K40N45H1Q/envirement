from typing import Optional
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field, create_engine, Session
from sqlalchemy import event


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    hashed_password: str
    account_type: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Job(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    status: str = Field(default="pending")
    company: str
    location: str
    description: Optional[str] = None
    salary: Optional[str] = None
    logo: Optional[str] = None
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
    work_permit: Optional[str] = None
    availability: Optional[str] = None
    resume_name: Optional[str] = None
    resume_url: Optional[str] = None
    avatar_url: Optional[str] = None
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


engine = create_engine("sqlite:///default.db", echo=False)
SQLModel.metadata.create_all(engine)


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


ensure_job_columns()


def get_session():
    with Session(engine) as session:
        yield session
