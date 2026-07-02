import json
import secrets
import shutil
from os import path, makedirs, getenv, remove
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Path, UploadFile
from sqlmodel import select

from database.models import CandidateProfile, Job, JobApplication, Message, User, get_session
from routes.safety import get_current_user, require_account_types

router = APIRouter()

UPLOAD_DIR = getenv("UPLOAD_DIR")
if not UPLOAD_DIR:
    base_dir = path.dirname(path.dirname(path.abspath(__file__)))
    UPLOAD_DIR = path.join(base_dir, "uploads")


def get_application_context(application_id: int, current_user: User, session):
    application = session.get(JobApplication, application_id)
    if not application:
        raise HTTPException(status_code=404, detail={"key": "application_not_found"})

    job = session.get(Job, application.job_id)
    if not job:
        raise HTTPException(status_code=404, detail={"key": "job_not_found"})

    is_candidate = (
        application.applicant_user_id == current_user.id
        and current_user.account_type == "candidate"
    )
    is_employer = (
        job.user_id == current_user.id
        and current_user.account_type == "employer"
    )
    is_admin = current_user.account_type == "admin"

    if not (is_candidate or is_employer or is_admin):
        raise HTTPException(status_code=403, detail={"key": "forbidden"})

    recipient_user_id = job.user_id if is_candidate else application.applicant_user_id
    return application, job, recipient_user_id, is_candidate


def ensure_chat_access(application: JobApplication, current_user: User, is_candidate: bool):
    if application.chat_approved:
        return

    if is_candidate:
        raise HTTPException(status_code=403, detail={"key": "chat_not_approved"})

    raise HTTPException(status_code=400, detail={"key": "chat_not_approved"})


def parse_json_field(value: Optional[str], fallback):
    if not value:
        return fallback

    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return fallback


@router.post("/create_job")
async def create_job(
    title: str = Form(...),
    company: str = Form(...),
    salary: str = Form(...),
    category: Optional[str] = Form(None),
    employment_type: Optional[str] = Form(None),
    country_key: str = Form(...),
    country_label: str = Form(...),
    country_flag_code: str = Form(...),
    location: str = Form(...),
    description: str = Form(...),
    languages_json: Optional[str] = Form(None),
    licenses_json: Optional[str] = Form(None),
    has_housing: bool = Form(False),
    has_transport: bool = Form(False),
    logo: Optional[UploadFile] = File(None),
    logo_url: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    require_account_types(current_user, "employer", "admin")

    makedirs(UPLOAD_DIR, exist_ok=True)

    if logo:
        filename = f"{secrets.token_hex(8)}_{logo.filename}"
        file_path = path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(logo.file, buffer)
        logo_path = f"/uploads/{filename}"
    else:
        logo_path = logo_url or ""

    job_status = "approved"

    job = Job(
        title=title,
        company=company,
        salary=salary,
        category=category,
        employment_type=employment_type,
        country_key=country_key,
        country_label=country_label,
        country_flag_code=country_flag_code,
        location=location,
        description=description,
        logo=logo_path,
        languages_json=languages_json,
        licenses_json=licenses_json,
        has_housing=has_housing,
        has_transport=has_transport,
        user_id=current_user.id,
        status=job_status,
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


@router.get("/get_jobs", response_model=List[Job])
def get_jobs(session=Depends(get_session)):
    return session.exec(
        select(Job).where(Job.status == "approved").order_by(Job.id.desc())
    ).all()


@router.get("/jobs/{job_id}", response_model=Job)
def get_job(job_id: int = Path(...), session=Depends(get_session)):
    job = session.get(Job, job_id)
    if not job or job.status != "approved":
        raise HTTPException(status_code=404, detail={"key": "job_not_found"})
    return job


@router.get("/my_jobs", response_model=List[Job])
def get_my_jobs(
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    require_account_types(current_user, "employer", "admin")

    return session.exec(
        select(Job).where(Job.user_id == current_user.id).order_by(Job.id.desc())
    ).all()


@router.put("/jobs/{job_id}")
async def update_job(
    job_id: int = Path(...),
    title: str = Form(...),
    company: str = Form(...),
    salary: str = Form(...),
    category: Optional[str] = Form(None),
    employment_type: Optional[str] = Form(None),
    country_key: str = Form(...),
    country_label: str = Form(...),
    country_flag_code: str = Form(...),
    location: str = Form(...),
    description: str = Form(...),
    languages_json: Optional[str] = Form(None),
    licenses_json: Optional[str] = Form(None),
    has_housing: bool = Form(False),
    has_transport: bool = Form(False),
    logo: Optional[UploadFile] = File(None),
    logo_url: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    require_account_types(current_user, "employer", "admin")

    job = session.get(Job, job_id)
    if not job or job.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Job not found")

    old_logo = job.logo
    makedirs(UPLOAD_DIR, exist_ok=True)

    if logo:
        filename = f"{secrets.token_hex(8)}_{logo.filename}"
        file_path = path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(logo.file, buffer)
        new_logo_path = f"/uploads/{filename}"
        if old_logo and old_logo.startswith("/uploads/"):
            try:
                full_old_path = path.join(
                    path.dirname(path.dirname(path.abspath(__file__))),
                    old_logo.lstrip("/")
                )
                if path.exists(full_old_path):
                    remove(full_old_path)
            except Exception:
                pass
        job.logo = new_logo_path
    elif logo_url:
        job.logo = logo_url

    job.title = title
    job.company = company
    job.salary = salary
    job.category = category
    job.employment_type = employment_type
    job.country_key = country_key
    job.country_label = country_label
    job.country_flag_code = country_flag_code
    job.location = location
    job.description = description
    job.languages_json = languages_json
    job.licenses_json = licenses_json
    job.has_housing = has_housing
    job.has_transport = has_transport

    job.status = "approved"

    session.add(job)
    session.commit()
    session.refresh(job)
    return job


@router.delete("/jobs/{job_id}", status_code=204)
async def delete_job(
    job_id: int = Path(...),
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    require_account_types(current_user, "employer", "admin")

    job = session.get(Job, job_id)
    if not job or job.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.logo and job.logo.startswith("/uploads/"):
        try:
            full_path = path.join(
                path.dirname(path.dirname(path.abspath(__file__))),
                job.logo.lstrip("/")
            )
            if path.exists(full_path):
                remove(full_path)
        except Exception:
            pass
    session.delete(job)
    session.commit()


@router.get("/moderation/jobs", response_model=List[Job])
def get_pending_jobs(
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    require_account_types(current_user, "admin")

    return session.exec(
        select(Job).where(Job.status == "pending").order_by(Job.created_at.desc())
    ).all()


@router.patch("/moderation/jobs/{job_id}/approve")
def approve_job(
    job_id: int = Path(...),
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    require_account_types(current_user, "admin")

    job = session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="not_found")
    job.status = "approved"
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


@router.patch("/moderation/jobs/{job_id}/reject")
def reject_job(
    job_id: int = Path(...),
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    require_account_types(current_user, "admin")

    job = session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="not_found")
    job.status = "rejected"
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


@router.post("/apply")
async def apply_to_job(
    request_data: dict,
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    require_account_types(current_user, "candidate")

    job_id = request_data.get("job_id")
    phone = request_data.get("phone")
    email = request_data.get("email")
    username = request_data.get("username")
    name = request_data.get("name")
    surname = request_data.get("surname")
    nationality = request_data.get("nationality")
    message = request_data.get("message")

    if not job_id or not phone or not email or not name or not surname:
        raise HTTPException(status_code=400, detail={"key": "missing_fields"})

    job = session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail={"key": "job_not_found"})
    if job.status != "approved":
        raise HTTPException(status_code=400, detail={"key": "job_not_available"})
    existing_application = session.exec(
        select(JobApplication).where(
            JobApplication.job_id == job_id,
            JobApplication.applicant_user_id == current_user.id,
        )
    ).first()
    if existing_application:
        raise HTTPException(status_code=400, detail={"key": "duplicate_application"})

    application = JobApplication(
        job_id=job_id,
        applicant_user_id=current_user.id,
        phone=phone,
        email=email,
        username=username,
        name=name,
        surname=surname,
        nationality=nationality,
        message=message,
        chat_approved=False,
    )
    session.add(application)
    session.commit()
    session.refresh(application)
    return {"status": "ok", "application_id": application.id}


@router.get("/responses")
def get_my_job_responses(
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    require_account_types(current_user, "employer", "admin")

    my_jobs = session.exec(
        select(Job).where(Job.user_id == current_user.id)
    ).all()
    job_ids = [job.id for job in my_jobs]
    if not job_ids:
        return []

    applications = session.exec(
        select(JobApplication)
        .where(JobApplication.job_id.in_(job_ids))
        .order_by(JobApplication.created_at.desc())
    ).all()

    job_map = {
        job.id: {
            "title": job.title,
            "company": job.company,
            "category": job.category,
            "country_key": job.country_key,
            "country_label": job.country_label,
            "country_flag_code": job.country_flag_code,
            "location": job.location,
            "salary": job.salary,
            "logo": job.logo,
            "description": job.description,
            "languages": parse_json_field(job.languages_json, []),
            "licenses": parse_json_field(job.licenses_json, []),
        }
        for job in my_jobs
    }

    applicant_ids = [
        app.applicant_user_id
        for app in applications
        if app.applicant_user_id is not None
    ]
    profiles = session.exec(
        select(CandidateProfile).where(CandidateProfile.user_id.in_(set(applicant_ids)))
    ).all() if applicant_ids else []
    profile_map = {profile.user_id: profile for profile in profiles}

    result = []
    for app in applications:
        job_data = job_map.get(app.job_id, {})
        profile = profile_map.get(app.applicant_user_id)
        result.append({
            "id": app.id,
            "job_id": app.job_id,
            "job_title": job_data.get("title", ""),
            "job_company": job_data.get("company", ""),
            "job_country_key": job_data.get("country_key", ""),
            "job_country_label": job_data.get("country_label", ""),
            "job_country_flag_code": job_data.get("country_flag_code", ""),
            "job_location": job_data.get("location", ""),
            "job_salary": job_data.get("salary", ""),
            "job_logo": job_data.get("logo", ""),
            "job_description": job_data.get("description", ""),
            "job_languages": job_data.get("languages", []),
            "job_licenses": job_data.get("licenses", []),
            "phone": app.phone,
            "email": app.email,
            "username": app.username,
            "name": app.name,
            "surname": app.surname,
            "nationality": app.nationality,
            "message": app.message,
            "chat_approved": app.chat_approved,
            "candidate_current_role": profile.current_role if profile else "",
            "candidate_summary": profile.summary if profile else "",
            "candidate_skills": profile.skills if profile else "",
            "candidate_work_permit": profile.work_permit if profile else "",
            "candidate_availability": profile.availability if profile else "",
            "candidate_resume_url": profile.resume_url if profile else "",
            "candidate_avatar_url": profile.avatar_url if profile else "",
            "candidate_languages": parse_json_field(profile.languages_json, []) if profile else [],
            "candidate_licenses": parse_json_field(profile.licenses_json, []) if profile else [],
            "candidate_sectors": parse_json_field(profile.sectors_json, []) if profile else [],
            "created_at": app.created_at,
        })
    return result


@router.patch("/responses/{response_id}/approve-chat")
def approve_response_chat(
    response_id: int = Path(...),
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    require_account_types(current_user, "employer", "admin")

    application = session.get(JobApplication, response_id)
    if not application:
        raise HTTPException(status_code=404, detail={"key": "application_not_found"})

    job = session.get(Job, application.job_id)
    if not job or job.user_id != current_user.id:
        raise HTTPException(status_code=403, detail={"key": "forbidden"})

    application.chat_approved = True
    session.add(application)
    session.commit()
    session.refresh(application)

    return {"status": "ok", "application_id": application.id, "chat_approved": True}


@router.get("/messages/conversations")
def get_message_conversations(
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    candidate_applications = []
    if current_user.account_type == "candidate":
        candidate_applications = session.exec(
            select(JobApplication).where(
                JobApplication.applicant_user_id == current_user.id,
                JobApplication.chat_approved == True,
            )
        ).all()

    employer_applications = []
    if current_user.account_type in {"employer", "admin"}:
        employer_jobs = session.exec(
            select(Job).where(Job.user_id == current_user.id)
        ).all()
        employer_job_ids = [job.id for job in employer_jobs]
        employer_applications = session.exec(
            select(JobApplication).where(
                JobApplication.job_id.in_(employer_job_ids),
                JobApplication.chat_approved == True,
            )
        ).all() if employer_job_ids else []

    applications_map = {
        application.id: application
        for application in [*candidate_applications, *employer_applications]
    }
    if not applications_map:
        return []

    job_ids = list({application.job_id for application in applications_map.values()})
    jobs = session.exec(select(Job).where(Job.id.in_(job_ids))).all()
    jobs_map = {job.id: job for job in jobs}

    applicant_ids = [
        application.applicant_user_id
        for application in applications_map.values()
        if application.applicant_user_id is not None
    ]
    users = session.exec(select(User).where(User.id.in_(set(applicant_ids)))).all() if applicant_ids else []
    users_map = {user.id: user for user in users}

    messages = session.exec(
        select(Message)
        .where(Message.application_id.in_(list(applications_map.keys())))
        .order_by(Message.created_at.desc())
    ).all()

    latest_message_by_application = {}
    for message in messages:
        latest_message_by_application.setdefault(message.application_id, message)

    conversations = []
    for application in applications_map.values():
        job = jobs_map.get(application.job_id)
        if not job:
            continue

        is_candidate = (
            application.applicant_user_id == current_user.id
            and current_user.account_type == "candidate"
        )
        candidate = users_map.get(application.applicant_user_id)
        latest_message = latest_message_by_application.get(application.id)

        conversations.append({
            "application_id": application.id,
            "job_id": application.job_id,
            "job_title": job.title,
            "job_company": job.company,
            "job_location": job.location,
            "counterparty_name": (
                job.company if is_candidate
                else f"{application.name} {application.surname}".strip() or "Кандидат"
            ),
            "counterparty_email": (
                application.email if is_candidate
                else getattr(candidate, "email", application.email)
            ),
            "last_message": latest_message.body if latest_message else application.message or "Диалог еще не начат",
            "last_message_at": latest_message.created_at if latest_message else application.created_at,
            "created_at": application.created_at,
        })

    conversations.sort(
        key=lambda item: item["last_message_at"] or item["created_at"],
        reverse=True,
    )
    return conversations


@router.get("/messages/{application_id}")
def get_messages(
    application_id: int = Path(...),
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    application, job, _, is_candidate = get_application_context(application_id, current_user, session)
    ensure_chat_access(application, current_user, is_candidate)
    messages = session.exec(
        select(Message)
        .where(Message.application_id == application_id)
        .order_by(Message.created_at.asc())
    ).all()

    thread = []
    if application.message:
        thread.append({
            "id": f"application-{application.id}",
            "body": application.message,
            "created_at": application.created_at,
            "sender_role": "candidate",
            "is_own": is_candidate,
            "sender_name": f"{application.name} {application.surname}".strip() or "Кандидат",
        })

    for message in messages:
        sender_role = "candidate" if message.sender_user_id == application.applicant_user_id else "employer"
        thread.append({
            "id": message.id,
            "body": message.body,
            "created_at": message.created_at,
            "sender_role": sender_role,
            "is_own": message.sender_user_id == current_user.id,
            "sender_name": (
                f"{application.name} {application.surname}".strip()
                if sender_role == "candidate"
                else job.company
            ),
        })

    return {
        "application_id": application.id,
        "job_id": job.id,
        "job_title": job.title,
        "job_company": job.company,
        "job_location": job.location,
        "messages": thread,
    }


@router.post("/messages/{application_id}")
async def send_message(
    application_id: int = Path(...),
    request_data: dict | None = None,
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    application, job, recipient_user_id, is_candidate = get_application_context(application_id, current_user, session)
    ensure_chat_access(application, current_user, is_candidate)

    body = ((request_data or {}).get("body") or "").strip()
    if not body:
        raise HTTPException(status_code=400, detail={"key": "missing_message_body"})
    if recipient_user_id is None:
        raise HTTPException(status_code=400, detail={"key": "conversation_not_available"})

    message = Message(
        application_id=application.id,
        sender_user_id=current_user.id,
        recipient_user_id=recipient_user_id,
        body=body,
    )
    session.add(message)
    session.commit()
    session.refresh(message)

    return {
        "id": message.id,
        "body": message.body,
        "created_at": message.created_at,
        "sender_role": "candidate" if is_candidate else "employer",
        "is_own": True,
        "sender_name": (
            f"{application.name} {application.surname}".strip()
            if is_candidate
            else job.company
        ),
    }


@router.delete("/messages/{application_id}", status_code=204)
def delete_conversation(
    application_id: int = Path(...),
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    application, _, _, _ = get_application_context(application_id, current_user, session)
    messages = session.exec(
        select(Message).where(Message.application_id == application.id)
    ).all()

    for message in messages:
        session.delete(message)

    session.delete(application)
    session.commit()


@router.delete("/responses/{response_id}", status_code=204)
def delete_response(
    response_id: int = Path(...),
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    require_account_types(current_user, "employer", "admin")

    application = session.get(JobApplication, response_id)
    if not application:
        raise HTTPException(status_code=404, detail="not_found")
    job = session.get(Job, application.job_id)
    if not job or job.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="forbidden")
    session.delete(application)
    session.commit()
