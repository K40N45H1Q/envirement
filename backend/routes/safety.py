import secrets
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from os import getenv

import jwt
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlmodel import Session, select

from database.models import (
    CandidateProfile,
    Job,
    JobApplication,
    Message,
    User,
    engine,
    get_session,
)

router = APIRouter()

SECRET_KEY = getenv("SECRET_KEY") or secrets.token_hex(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
PUBLIC_ACCOUNT_TYPES = {"user", "employer"}
DEFAULT_ADMIN_EMAIL = getenv("DEFAULT_ADMIN_EMAIL", "admin@cvhold.local")
DEFAULT_ADMIN_PASSWORD = getenv("DEFAULT_ADMIN_PASSWORD", "CVHOLD_Admin_2026_Secure!")
DEFAULT_EMPLOYER_EMAIL = getenv("DEFAULT_EMPLOYER_EMAIL", "employer@cvhold.local")
DEFAULT_EMPLOYER_PASSWORD = getenv("DEFAULT_EMPLOYER_PASSWORD", "CVHOLD_Employer_2026_Secure!")
DEFAULT_CANDIDATE_EMAIL = getenv("DEFAULT_CANDIDATE_EMAIL", "candidate@cvhold.local")
DEFAULT_CANDIDATE_PASSWORD = getenv("DEFAULT_CANDIDATE_PASSWORD", "CVHOLD_Candidate_2026_Secure!")


def error(key: str, status: int = 400):
    raise HTTPException(status_code=status, detail={"error": key})


def hash_password(password: str) -> str:
    return sha256(password.encode()).hexdigest()


def ensure_default_admin():
    with Session(engine) as session:
        default_accounts = [
            {
                "email": DEFAULT_ADMIN_EMAIL,
                "account_type": "admin",
                "hashed_password": hash_password(DEFAULT_ADMIN_PASSWORD),
            },
            {
                "email": DEFAULT_EMPLOYER_EMAIL,
                "account_type": "employer",
                "hashed_password": hash_password(DEFAULT_EMPLOYER_PASSWORD),
            },
            {
                "email": DEFAULT_CANDIDATE_EMAIL,
                "account_type": "user",
                "hashed_password": hash_password(DEFAULT_CANDIDATE_PASSWORD),
            },
        ]

        changed = False

        for account_data in default_accounts:
            user = session.exec(
                select(User).where(User.email == account_data["email"])
            ).first()

            if not user:
                session.add(User(**account_data))
                changed = True
                continue

            updated = False

            if user.account_type != account_data["account_type"]:
                user.account_type = account_data["account_type"]
                updated = True

            if user.hashed_password != account_data["hashed_password"]:
                user.hashed_password = account_data["hashed_password"]
                updated = True

            if updated:
                session.add(user)
                changed = True

        if changed:
            session.commit()


def ensure_mvp_seed_data():
    with Session(engine) as session:
        employer = session.exec(
            select(User).where(User.email == DEFAULT_EMPLOYER_EMAIL)
        ).first()
        candidate = session.exec(
            select(User).where(User.email == DEFAULT_CANDIDATE_EMAIL)
        ).first()

        if not employer or not candidate:
            return

        profile = session.exec(
            select(CandidateProfile).where(CandidateProfile.user_id == candidate.id)
        ).first()
        if not profile:
            profile = CandidateProfile(
                user_id=candidate.id,
                first_name="Ivan",
                last_name="Ivanov",
                phone="+49 152 12345678",
                summary=(
                    "Experienced industrial technician and welder with long-term project "
                    "experience across Germany, Latvia, and the Netherlands."
                ),
                current_role="Industrial Technician / MIG-MAG Welder",
                skills="MIG/MAG, монтаж, электрика, turbines, maintenance, CE driving",
                sectors_json=(
                    '["Энергетика", "Производство", "Строительство"]'
                ),
                languages_json=(
                    '[{"name":"Русский","level":"C2"},{"name":"English","level":"B2"},{"name":"Deutsch","level":"A2"}]'
                ),
                licenses_json='["B", "C", "CE", "VCA"]',
                mobility="EU mobility",
                preferred_mobility="Germany / Latvia / Netherlands",
                work_permit="EU citizen",
                availability="Immediate",
                resume_name="ivan-ivanov-cv.pdf",
                resume_url="https://example.com/resume/ivan-ivanov-cv.pdf",
                avatar_url="https://i.pravatar.cc/320?img=12",
            )
            session.add(profile)

        seeded_jobs = [
            {
                "title": "Wind Turbine Service Technician",
                "company": "Enercom SIA",
                "salary": "2 500 - 3 500 EUR",
                "location": "Riga, Latvia",
                "description": (
                    "Maintenance of wind turbines, preventive inspections, work at height, "
                    "service trips across the Baltics, accommodation support and company transport."
                ),
                "logo": "https://images.unsplash.com/photo-1466611653911-95081537e5b7?auto=format&fit=crop&w=320&q=80",
            },
            {
                "title": "HV Electrician",
                "company": "Enercom SIA",
                "salary": "2 200 - 2 800 EUR",
                "location": "Liepaja, Latvia",
                "description": (
                    "High-voltage cable work, switchgear servicing, commissioning, shift work, "
                    "safety procedures, transport to project sites included."
                ),
                "logo": "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?auto=format&fit=crop&w=320&q=80",
            },
            {
                "title": "MIG/MAG Welder",
                "company": "SteelBuild GmbH",
                "salary": "3 200 - 3 800 EUR",
                "location": "Berlin, Germany",
                "description": (
                    "Welding of metal constructions, reading technical drawings, quality control, "
                    "official employment, accommodation support."
                ),
                "logo": "https://images.unsplash.com/photo-1517048676732-d65bc937f952?auto=format&fit=crop&w=320&q=80",
            },
            {
                "title": "Blade Repair Technician",
                "company": "Nordex Baltic",
                "salary": "2 900 - 3 400 EUR",
                "location": "Tallinn, Estonia",
                "description": (
                    "Composite repairs on wind turbine blades, inspection reports, rope access "
                    "preferred, project-based rotations."
                ),
                "logo": "https://images.unsplash.com/photo-1509395176047-4a66953fd231?auto=format&fit=crop&w=320&q=80",
            },
            {
                "title": "Driver CE",
                "company": "LogiMove Europe",
                "salary": "3 000 - 3 300 EUR",
                "location": "Warsaw, Poland",
                "description": (
                    "International transport routes, modern fleet, stable contract, company transport "
                    "card, housing support during onboarding."
                ),
                "logo": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=320&q=80",
            },
        ]

        jobs_by_title = {
            (job.title, job.company): job
            for job in session.exec(
                select(Job).where(Job.user_id == employer.id)
            ).all()
        }

        created_jobs = []
        for job_data in seeded_jobs:
            job = jobs_by_title.get((job_data["title"], job_data["company"]))
            if not job:
                job = Job(
                    **job_data,
                    user_id=employer.id,
                    status="approved",
                )
                session.add(job)
                session.flush()
            else:
                job.status = "approved"
                job.salary = job_data["salary"]
                job.location = job_data["location"]
                job.description = job_data["description"]
                job.logo = job_data["logo"]
                session.add(job)
            created_jobs.append(job)

        session.commit()

        jobs_by_title = {
            (job.title, job.company): job
            for job in session.exec(
                select(Job).where(Job.user_id == employer.id)
            ).all()
        }

        seeded_applications = [
            {
                "job_key": ("Wind Turbine Service Technician", "Enercom SIA"),
                "phone": "+49 152 12345678",
                "email": DEFAULT_CANDIDATE_EMAIL,
                "username": DEFAULT_CANDIDATE_EMAIL,
                "name": "Ivan",
                "surname": "Ivanov",
                "nationality": "Latvia",
                "message": "Ready to relocate to Latvia within two weeks and start turbine service work immediately.",
                "messages": [
                    ("employer", "Thanks, your profile looks relevant. Are you available for a first call tomorrow?"),
                    ("candidate", "Yes, I am available after 10:00 and can also share certificates during the call."),
                ],
            },
            {
                "job_key": ("HV Electrician", "Enercom SIA"),
                "phone": "+49 152 12345678",
                "email": DEFAULT_CANDIDATE_EMAIL,
                "username": DEFAULT_CANDIDATE_EMAIL,
                "name": "Ivan",
                "surname": "Ivanov",
                "nationality": "Latvia",
                "message": "Worked on industrial electrical systems and can join rotating site work.",
                "messages": [
                    ("employer", "We also have a shift schedule on coastal sites. Would that work for you?"),
                    ("candidate", "Yes, shift work is fine. I already have VCA and experience with site safety procedures."),
                ],
            },
            {
                "job_key": ("MIG/MAG Welder", "SteelBuild GmbH"),
                "phone": "+49 152 12345678",
                "email": DEFAULT_CANDIDATE_EMAIL,
                "username": DEFAULT_CANDIDATE_EMAIL,
                "name": "Ivan",
                "surname": "Ivanov",
                "nationality": "Latvia",
                "message": "More than eight years of welding experience and technical drawing reading.",
                "messages": [
                    ("employer", "Your welding background matches well. Please confirm your earliest start date."),
                    ("candidate", "Earliest start date is next Monday. I can travel with my own car if needed."),
                ],
            },
        ]

        existing_applications = {
            (application.job_id, application.applicant_user_id): application
            for application in session.exec(
                select(JobApplication).where(
                    JobApplication.applicant_user_id == candidate.id
                )
            ).all()
        }

        for item in seeded_applications:
            job = jobs_by_title.get(item["job_key"])
            if not job:
                continue

            application = existing_applications.get((job.id, candidate.id))
            if not application:
                application = JobApplication(
                    job_id=job.id,
                    applicant_user_id=candidate.id,
                    phone=item["phone"],
                    email=item["email"],
                    username=item["username"],
                    name=item["name"],
                    surname=item["surname"],
                    nationality=item["nationality"],
                    message=item["message"],
                )
                session.add(application)
                session.flush()

            existing_messages = session.exec(
                select(Message).where(Message.application_id == application.id)
            ).all()
            existing_bodies = {message.body for message in existing_messages}

            for sender_role, body in item["messages"]:
                if body in existing_bodies:
                    continue
                sender_user_id = employer.id if sender_role == "employer" else candidate.id
                recipient_user_id = candidate.id if sender_role == "employer" else employer.id
                session.add(
                    Message(
                        application_id=application.id,
                        sender_user_id=sender_user_id,
                        recipient_user_id=recipient_user_id,
                        body=body,
                    )
                )

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
