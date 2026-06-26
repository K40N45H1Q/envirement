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


def get_session():
    with Session(engine) as session:
        yield session
