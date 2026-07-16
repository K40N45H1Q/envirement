import json
import secrets
import shutil
from datetime import date
from os import getenv, path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlmodel import select

from database.models import CandidateProfile, Job, JobApplication, get_session
from app.services.matching import parse_date
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
            "residence": "",
            "phone": "",
            "summary": "",
            "current_role": "",
            "desired_occupation_id": "",
            "desired_occupation_label": "",
            "skills": "",
            "skill_ids": [],
            "sectors": [],
            "languages": [],
            "licenses": [],
            "mobility": "",
            "preferred_mobility": "",
            "salary_expectation": "",
            "preferred_employment_type": "",
            "education_level": "",
            "remote_ready": False,
            "work_permit": "",
            "availability": "",
            "resume_name": "",
            "resume_url": "",
            "avatar_url": "",
            "resume_data": {},
        }

    return {
        "first_name": profile.first_name or "",
        "last_name": profile.last_name or "",
        "residence": profile.residence or "",
        "phone": profile.phone or "",
        "summary": profile.summary or "",
        "current_role": profile.current_role or "",
        "desired_occupation_id": profile.desired_occupation_id or "",
        "desired_occupation_label": profile.desired_occupation_label or "",
        "skills": profile.skills or "",
        "skill_ids": parse_json_field(profile.skill_ids_json, []),
        "sectors": parse_json_field(profile.sectors_json, []),
        "languages": parse_json_field(profile.languages_json, []),
        "licenses": parse_json_field(profile.licenses_json, []),
        "mobility": profile.mobility or "",
        "preferred_mobility": profile.preferred_mobility or "",
        "salary_expectation": profile.salary_expectation or "",
        "preferred_employment_type": profile.preferred_employment_type or "",
        "education_level": profile.education_level or "",
        "remote_ready": bool(profile.remote_ready),
        "work_permit": profile.work_permit or "",
        "availability": profile.availability or "",
        "resume_name": profile.resume_name or "",
        "resume_url": profile.resume_url or "",
        "avatar_url": profile.avatar_url or "",
        "resume_data": parse_json_field(profile.resume_data_json, {}),
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
    residence: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    summary: Optional[str] = Form(None),
    current_role: Optional[str] = Form(None),
    desired_occupation_id: Optional[str] = Form(None),
    desired_occupation_label: Optional[str] = Form(None),
    skills: Optional[str] = Form(None),
    skill_ids_json: Optional[str] = Form(None),
    sectors_json: Optional[str] = Form(None),
    languages_json: Optional[str] = Form(None),
    licenses_json: Optional[str] = Form(None),
    mobility: Optional[str] = Form(None),
    preferred_mobility: Optional[str] = Form(None),
    salary_expectation: Optional[str] = Form(None),
    preferred_employment_type: Optional[str] = Form(None),
    education_level: Optional[str] = Form(None),
    remote_ready: bool = Form(False),
    work_permit: Optional[str] = Form(None),
    availability: Optional[str] = Form(None),
    resume_data_json: Optional[str] = Form(None),
    avatar: Optional[UploadFile] = File(None),
    resume: Optional[UploadFile] = File(None),
    current_user=Depends(get_current_user),
    session=Depends(get_session),
):
    availability = (availability or '').strip()
    availability_date = parse_date(availability)
    if availability and availability != 'Immediate' and (
        not availability_date or availability_date < date.today()
    ):
        raise HTTPException(status_code=400, detail={"key": "invalid_availability"})

    profile = session.exec(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    ).first()
    if not profile:
        profile = CandidateProfile(user_id=current_user.id)

    avatar_url, _ = save_upload(avatar, "avatar")
    resume_url, resume_name = save_upload(resume, "resume")

    profile.first_name = first_name
    profile.last_name = last_name
    profile.residence = residence
    profile.phone = phone
    profile.summary = summary
    profile.current_role = current_role
    profile.desired_occupation_id = desired_occupation_id
    profile.desired_occupation_label = desired_occupation_label
    profile.skills = skills
    profile.skill_ids_json = skill_ids_json
    profile.sectors_json = sectors_json
    profile.languages_json = languages_json
    profile.licenses_json = licenses_json
    profile.mobility = mobility
    profile.preferred_mobility = preferred_mobility
    profile.salary_expectation = salary_expectation
    profile.preferred_employment_type = preferred_employment_type
    profile.education_level = education_level
    profile.remote_ready = remote_ready
    profile.work_permit = work_permit
    profile.availability = availability or None
    profile.resume_data_json = resume_data_json

    if avatar_url:
        profile.avatar_url = avatar_url
    if resume_url:
        profile.resume_url = resume_url
    if resume_name:
        profile.resume_name = resume_name

    current_user.full_name = " ".join(
        part.strip() for part in (first_name, last_name) if part and part.strip()
    ) or None
    current_user.phone = phone

    session.add(profile)
    session.add(current_user)
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
            "job_occupation_id": job.occupation_id or "",
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
            "match_score": application.match_score,
            "match_label": application.match_label,
            "match_analysis": parse_json_field(application.match_json, None),
            "created_at": application.created_at,
        })
    return result
