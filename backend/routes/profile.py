import json
import secrets
import shutil
from os import getenv, path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlmodel import select

from database.models import CandidateProfile, Job, JobApplication, get_session
from routes.safety import get_current_user

router = APIRouter()

UPLOAD_DIR = getenv("UPLOAD_DIR")
if not UPLOAD_DIR:
    base_dir = path.dirname(path.dirname(path.abspath(__file__)))
    UPLOAD_DIR = path.join(base_dir, "uploads")


def save_upload(file: Optional[UploadFile], prefix: str):
    if not file:
        return None, None

    filename = f"{prefix}_{secrets.token_hex(8)}_{file.filename}"
    file_path = path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return f"/uploads/{filename}", file.filename


def parse_json_field(value: Optional[str], fallback):
    if not value:
        return fallback
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return fallback


def serialize_profile(profile: Optional[CandidateProfile]):
    if not profile:
        return {
            "first_name": "",
            "last_name": "",
            "phone": "",
            "summary": "",
            "current_role": "",
            "skills": "",
            "sectors": [],
            "languages": [],
            "licenses": [],
            "mobility": "",
            "preferred_mobility": "",
            "work_permit": "",
            "availability": "",
            "resume_name": "",
            "resume_url": "",
            "avatar_url": "",
        }

    return {
        "first_name": profile.first_name or "",
        "last_name": profile.last_name or "",
        "phone": profile.phone or "",
        "summary": profile.summary or "",
        "current_role": profile.current_role or "",
        "skills": profile.skills or "",
        "sectors": parse_json_field(profile.sectors_json, []),
        "languages": parse_json_field(profile.languages_json, []),
        "licenses": parse_json_field(profile.licenses_json, []),
        "mobility": profile.mobility or "",
        "preferred_mobility": profile.preferred_mobility or "",
        "work_permit": profile.work_permit or "",
        "availability": profile.availability or "",
        "resume_name": profile.resume_name or "",
        "resume_url": profile.resume_url or "",
        "avatar_url": profile.avatar_url or "",
    }


@router.get("/profile")
def get_profile(current_user=Depends(get_current_user), session=Depends(get_session)):
    profile = session.exec(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    ).first()
    return serialize_profile(profile)


@router.put("/profile")
async def update_profile(
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    summary: Optional[str] = Form(None),
    current_role: Optional[str] = Form(None),
    skills: Optional[str] = Form(None),
    sectors_json: Optional[str] = Form(None),
    languages_json: Optional[str] = Form(None),
    licenses_json: Optional[str] = Form(None),
    mobility: Optional[str] = Form(None),
    preferred_mobility: Optional[str] = Form(None),
    work_permit: Optional[str] = Form(None),
    availability: Optional[str] = Form(None),
    avatar: Optional[UploadFile] = File(None),
    resume: Optional[UploadFile] = File(None),
    current_user=Depends(get_current_user),
    session=Depends(get_session),
):
    profile = session.exec(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    ).first()
    if not profile:
        profile = CandidateProfile(user_id=current_user.id)

    avatar_url, _ = save_upload(avatar, "avatar")
    resume_url, resume_name = save_upload(resume, "resume")

    profile.first_name = first_name
    profile.last_name = last_name
    profile.phone = phone
    profile.summary = summary
    profile.current_role = current_role
    profile.skills = skills
    profile.sectors_json = sectors_json
    profile.languages_json = languages_json
    profile.licenses_json = licenses_json
    profile.mobility = mobility
    profile.preferred_mobility = preferred_mobility
    profile.work_permit = work_permit
    profile.availability = availability

    if avatar_url:
        profile.avatar_url = avatar_url
    if resume_url:
        profile.resume_url = resume_url
    if resume_name:
        profile.resume_name = resume_name

    session.add(profile)
    session.commit()
    session.refresh(profile)
    return serialize_profile(profile)


@router.get("/my_applications")
def get_my_applications(current_user=Depends(get_current_user), session=Depends(get_session)):
    applications = session.exec(
        select(JobApplication)
        .where(JobApplication.applicant_user_id == current_user.id)
        .order_by(JobApplication.created_at.desc())
    ).all()

    if not applications:
        return []

    jobs = session.exec(
        select(Job).where(Job.id.in_([application.job_id for application in applications]))
    ).all()
    jobs_map = {job.id: job for job in jobs}

    result = []
    for application in applications:
        job = jobs_map.get(application.job_id)
        if not job:
            continue
        result.append({
            "id": application.id,
            "job_id": application.job_id,
            "job_title": job.title,
            "job_company": job.company,
            "job_location": job.location,
            "job_salary": job.salary,
            "job_logo": job.logo,
            "job_status": job.status,
            "message": application.message,
            "phone": application.phone,
            "email": application.email,
            "name": application.name,
            "surname": application.surname,
            "nationality": application.nationality,
            "chat_approved": application.chat_approved,
            "created_at": application.created_at,
        })
    return result
