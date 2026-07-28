import json
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, Path, Request, Response, UploadFile
from sqlmodel import select

from database.models import CandidateProfile, Job, JobApplication, Message, User, get_session
from app.services.matchscore import ALGORITHM_VERSION, parse_date, score_candidate
from app.services.supabase_storage import remove_file, upload_file
from routes.safety import ACCESS_COOKIE_NAME, REFRESH_COOKIE_NAME, get_current_user, require_account_types

router = APIRouter()
PLAN_JOB_LIMITS = {
    "basic": 1,
    "standard": 5,
    "pro": 20,
}

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


def store_upload_file(upload: UploadFile) -> str:
    return upload_file(upload, "jobs")


def remove_upload_file(upload_url: Optional[str]) -> None:
    remove_file(upload_url)


def store_resume_file(upload: UploadFile) -> str:
    filename = (upload.filename or "").strip()
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail={"key": "resume_must_be_pdf"})

    return store_upload_file(upload)


def has_active_subscription(user: User) -> bool:
    expires_at = user.subscription_expires_at
    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return bool(user.subscription_plan in PLAN_JOB_LIMITS and expires_at and expires_at > datetime.now(timezone.utc))


def ensure_active_employer_subscription(user: User) -> None:
    if user.account_type == "admin":
        return

    if not has_active_subscription(user):
        raise HTTPException(status_code=403, detail={"key": "subscription_required"})


def get_optional_current_user(
    request: Request,
    response: Response,
    authorization: str | None = Header(None),
    session=Depends(get_session),
) -> User | None:
    if not authorization and not request.cookies.get(ACCESS_COOKIE_NAME) and not request.cookies.get(REFRESH_COOKIE_NAME):
        return None
    try:
        return get_current_user(request=request, response=response, authorization=authorization, session=session)
    except HTTPException:
        return None


def ensure_employer_plan_allows_job(user: User, session) -> None:
    ensure_active_employer_subscription(user)
    if user.account_type == "admin":
        return

    job_limit = PLAN_JOB_LIMITS[user.subscription_plan]
    used_jobs_count = max(int(user.subscription_jobs_used or 0), 0)

    if used_jobs_count >= job_limit:
        raise HTTPException(status_code=403, detail={"key": "subscription_job_limit_reached"})


@router.post("/create_job")
async def create_job(
    title: str = Form(...),
    occupation_id: Optional[str] = Form(None),
    company: Optional[str] = Form(None),
    salary: str = Form(...),
    category: Optional[str] = Form(None),
    employment_type: Optional[str] = Form(None),
    experience_level: Optional[str] = Form(None),
    required_from: Optional[str] = Form(None),
    remote_allowed: bool = Form(False),
    education_level: Optional[str] = Form(None),
    country_key: str = Form(...),
    country_label: str = Form(...),
    country_flag_code: str = Form(...),
    location: str = Form(...),
    description: str = Form(...),
    languages_json: Optional[str] = Form(None),
    licenses_json: Optional[str] = Form(None),
    skills_json: Optional[str] = Form(None),
    has_housing: bool = Form(False),
    has_transport: bool = Form(False),
    logo: Optional[UploadFile] = File(None),
    logo_url: Optional[str] = Form(None),
    banner: Optional[UploadFile] = File(None),
    banner_url: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    require_account_types(current_user, "employer", "admin")

    if not (occupation_id or "").strip():
        raise HTTPException(status_code=400, detail={"key": "occupation_required"})
    if required_from and not parse_date(required_from):
        raise HTTPException(status_code=400, detail={"key": "invalid_required_from"})

    company_name = (current_user.company_name or "").strip() or (company or "").strip()
    if not company_name:
        raise HTTPException(status_code=400, detail={"key": "missing_company_profile"})
    if company_name != (current_user.company_name or "").strip():
        current_user.company_name = company_name
        session.add(current_user)
    ensure_employer_plan_allows_job(current_user, session)

    if logo:
        logo_path = store_upload_file(logo)
        current_user.company_logo_url = logo_path
        session.add(current_user)
    else:
        logo_path = logo_url or current_user.company_logo_url or ""

    banner_path = store_upload_file(banner) if banner else (banner_url or "")

    job_status = "approved" if current_user.account_type == "admin" else "pending"

    job = Job(
        title=title,
        occupation_id=occupation_id,
        company=company_name,
        salary=salary,
        category=category,
        employment_type=employment_type,
        experience_level=experience_level,
        required_from=required_from,
        remote_allowed=remote_allowed,
        education_level=education_level,
        country_key=country_key,
        country_label=country_label,
        country_flag_code=country_flag_code,
        location=location,
        description=description,
        logo=logo_path,
        banner_url=banner_path,
        languages_json=languages_json,
        licenses_json=licenses_json,
        skills_json=skills_json,
        has_housing=has_housing,
        has_transport=has_transport,
        user_id=current_user.id,
        status=job_status,
        quota_consumed=current_user.account_type == "admin",
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
def get_job(
    job_id: int = Path(...),
    session=Depends(get_session),
    current_user: User | None = Depends(get_optional_current_user),
):
    job = session.get(Job, job_id)
    can_view_unpublished = current_user is not None and current_user.account_type == "admin"
    if not job or (job.status != "approved" and not can_view_unpublished):
        raise HTTPException(status_code=404, detail={"key": "job_not_found"})
    return job


@router.get("/jobs/{job_id}/match")
def get_job_match(
    job_id: int = Path(...),
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    require_account_types(current_user, "candidate")
    job = session.get(Job, job_id)
    if not job or job.status != "approved":
        raise HTTPException(status_code=404, detail={"key": "job_not_found"})
    profile = session.exec(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    ).first()
    return score_candidate(profile or {}, job)


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
    occupation_id: Optional[str] = Form(None),
    company: Optional[str] = Form(None),
    salary: str = Form(...),
    category: Optional[str] = Form(None),
    employment_type: Optional[str] = Form(None),
    experience_level: Optional[str] = Form(None),
    required_from: Optional[str] = Form(None),
    remote_allowed: bool = Form(False),
    education_level: Optional[str] = Form(None),
    country_key: str = Form(...),
    country_label: str = Form(...),
    country_flag_code: str = Form(...),
    location: str = Form(...),
    description: str = Form(...),
    languages_json: Optional[str] = Form(None),
    licenses_json: Optional[str] = Form(None),
    skills_json: Optional[str] = Form(None),
    has_housing: bool = Form(False),
    has_transport: bool = Form(False),
    logo: Optional[UploadFile] = File(None),
    logo_url: Optional[str] = Form(None),
    banner: Optional[UploadFile] = File(None),
    banner_url: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    require_account_types(current_user, "employer", "admin")
    ensure_active_employer_subscription(current_user)

    if not (occupation_id or "").strip():
        raise HTTPException(status_code=400, detail={"key": "occupation_required"})
    if required_from and not parse_date(required_from):
        raise HTTPException(status_code=400, detail={"key": "invalid_required_from"})

    company_name = (current_user.company_name or "").strip() or (company or "").strip()
    if not company_name:
        raise HTTPException(status_code=400, detail={"key": "missing_company_profile"})
    if company_name != (current_user.company_name or "").strip():
        current_user.company_name = company_name
        session.add(current_user)

    job = session.get(Job, job_id)
    if not job or job.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Job not found")

    old_logo = job.logo
    old_banner = job.banner_url
    if logo:
        new_logo_path = store_upload_file(logo)
        remove_upload_file(old_logo)
        job.logo = new_logo_path
        current_user.company_logo_url = new_logo_path
        session.add(current_user)
    elif logo_url:
        job.logo = logo_url
        current_user.company_logo_url = logo_url
        session.add(current_user)
    elif current_user.company_logo_url:
        job.logo = current_user.company_logo_url

    if banner:
        new_banner_path = store_upload_file(banner)
        remove_upload_file(old_banner)
        job.banner_url = new_banner_path
    elif banner_url:
        if old_banner and old_banner != banner_url:
            remove_upload_file(old_banner)
        job.banner_url = banner_url

    job.title = title
    job.occupation_id = occupation_id
    job.company = company_name
    job.salary = salary
    job.category = category
    job.employment_type = employment_type
    job.experience_level = experience_level
    job.required_from = required_from
    job.remote_allowed = remote_allowed
    job.education_level = education_level
    job.country_key = country_key
    job.country_label = country_label
    job.country_flag_code = country_flag_code
    job.location = location
    job.description = description
    job.languages_json = languages_json
    job.licenses_json = licenses_json
    job.skills_json = skills_json
    job.has_housing = has_housing
    job.has_transport = has_transport

    job.status = "approved" if current_user.account_type == "admin" else "pending"

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
    ensure_active_employer_subscription(current_user)

    job = session.get(Job, job_id)
    if not job or job.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Job not found")

    remove_upload_file(job.logo)
    remove_upload_file(job.banner_url)
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
    request: Request,
    job_id: Optional[int] = Form(None),
    phone: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    username: Optional[str] = Form(None),
    name: Optional[str] = Form(None),
    surname: Optional[str] = Form(None),
    nationality: Optional[str] = Form(None),
    message: Optional[str] = Form(None),
    resume: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    require_account_types(current_user, "candidate")

    content_type = request.headers.get("content-type", "")
    resume_upload = resume if getattr(resume, "filename", None) else None

    if "multipart/form-data" not in content_type:
        request_data = await request.json()
        try:
            job_id = int(request_data.get("job_id"))
        except (TypeError, ValueError):
            job_id = None
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

    profile = session.exec(
        select(CandidateProfile).where(CandidateProfile.user_id == current_user.id)
    ).first()
    match_result = score_candidate(profile or {}, job)
    if match_result["excluded"]:
        raise HTTPException(status_code=400, detail={"key": "outside_professional_area"})

    resume_url = None
    resume_name = None
    if resume_upload:
        resume_url = store_resume_file(resume_upload)
        resume_name = resume_upload.filename

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
        resume_name=resume_name,
        resume_url=resume_url,
        chat_approved=False,
        match_score=match_result["score"],
        match_label=match_result["label"],
        match_algorithm_version=ALGORITHM_VERSION,
        match_json=json.dumps(match_result, ensure_ascii=False),
        matched_at=datetime.now(timezone.utc),
    )
    session.add(application)
    session.commit()
    session.refresh(application)
    return {"status": "ok", "application_id": application.id, "match_analysis": match_result}


@router.get("/responses")
def get_my_job_responses(
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    require_account_types(current_user, "employer", "admin")
    ensure_active_employer_subscription(current_user)

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

    my_jobs_by_id = {job.id: job for job in my_jobs}
    job_map = {
        job.id: {
            "title": job.title,
            "occupation_id": job.occupation_id,
            "company": job.company,
            "category": job.category,
            "employment_type": job.employment_type,
            "experience_level": job.experience_level,
            "required_from": job.required_from,
            "remote_allowed": job.remote_allowed,
            "education_level": job.education_level,
            "country_key": job.country_key,
            "country_label": job.country_label,
            "country_flag_code": job.country_flag_code,
            "location": job.location,
            "salary": job.salary,
            "logo": job.logo,
            "banner_url": job.banner_url,
            "description": job.description,
            "languages": parse_json_field(job.languages_json, []),
            "licenses": parse_json_field(job.licenses_json, []),
            "skills": parse_json_field(job.skills_json, []),
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
        match_analysis = parse_json_field(app.match_json, None)
        if not isinstance(match_analysis, dict) or match_analysis.get("algorithm_version") != ALGORITHM_VERSION:
            match_analysis = score_candidate(profile or {}, my_jobs_by_id.get(app.job_id, {}))
        if match_analysis.get("excluded"):
            continue
        result.append({
            "id": app.id,
            "job_id": app.job_id,
            "job_title": job_data.get("title", ""),
            "job_occupation_id": job_data.get("occupation_id", ""),
            "job_company": job_data.get("company", ""),
            "job_category": job_data.get("category", ""),
            "job_employment_type": job_data.get("employment_type", ""),
            "job_experience_level": job_data.get("experience_level", ""),
            "job_required_from": job_data.get("required_from", ""),
            "job_remote_allowed": bool(job_data.get("remote_allowed", False)),
            "job_education_level": job_data.get("education_level", ""),
            "job_country_key": job_data.get("country_key", ""),
            "job_country_label": job_data.get("country_label", ""),
            "job_country_flag_code": job_data.get("country_flag_code", ""),
            "job_location": job_data.get("location", ""),
            "job_salary": job_data.get("salary", ""),
            "job_logo": job_data.get("logo", ""),
            "job_banner_url": job_data.get("banner_url", ""),
            "job_description": job_data.get("description", ""),
            "job_languages": job_data.get("languages", []),
            "job_licenses": job_data.get("licenses", []),
            "job_skills": job_data.get("skills", []),
            "phone": app.phone,
            "email": app.email,
            "username": app.username,
            "name": app.name,
            "surname": app.surname,
            "nationality": app.nationality,
            "message": app.message,
            "candidate_resume_name": app.resume_name or (profile.resume_name if profile else ""),
            "candidate_resume_url": app.resume_url or (profile.resume_url if profile else ""),
            "candidate_has_site_cv": bool(
                profile and parse_json_field(profile.resume_data_json, {})
            ),
            "chat_approved": app.chat_approved,
            "candidate_current_role": profile.current_role if profile else "",
            "candidate_summary": profile.summary if profile else "",
            "candidate_skills": profile.skills if profile else "",
            "candidate_skill_ids": parse_json_field(profile.skill_ids_json, []) if profile else [],
            "candidate_education_level": profile.education_level if profile else "",
            "candidate_salary_expectation": profile.salary_expectation if profile else "",
            "candidate_preferred_employment_type": profile.preferred_employment_type if profile else "",
            "candidate_remote_ready": bool(profile.remote_ready) if profile else False,
            "candidate_work_permit": profile.work_permit if profile else "",
            "candidate_availability": profile.availability if profile else "",
            "candidate_avatar_url": profile.avatar_url if profile else "",
            "candidate_languages": parse_json_field(profile.languages_json, []) if profile else [],
            "candidate_licenses": parse_json_field(profile.licenses_json, []) if profile else [],
            "candidate_sectors": parse_json_field(profile.sectors_json, []) if profile else [],
            "match_analysis": match_analysis,
            "match_score": match_analysis.get("score") or 0,
            "match_label": match_analysis.get("label", "weak"),
            "created_at": app.created_at,
        })
    return sorted(result, key=lambda item: item["match_score"], reverse=True)


@router.get("/responses/{response_id}/cv")
def get_response_cv(
    response_id: int,
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    require_account_types(current_user, "employer", "admin")
    ensure_active_employer_subscription(current_user)
    application, _, _, _ = get_application_context(response_id, current_user, session)
    profile = session.exec(
        select(CandidateProfile).where(
            CandidateProfile.user_id == application.applicant_user_id
        )
    ).first()
    resume_data = parse_json_field(profile.resume_data_json, {}) if profile else {}
    if not profile or not resume_data:
        raise HTTPException(status_code=404, detail={"key": "candidate_cv_not_found"})

    return {
        "first_name": profile.first_name or application.name or "",
        "last_name": profile.last_name or application.surname or "",
        "email": application.email or "",
        "residence": profile.residence or "",
        "phone": profile.phone or application.phone or "",
        "summary": profile.summary or "",
        "current_role": profile.current_role or "",
        "skills": profile.skills or "",
        "sectors": parse_json_field(profile.sectors_json, []),
        "languages": parse_json_field(profile.languages_json, []),
        "licenses": parse_json_field(profile.licenses_json, []),
        "avatar_url": profile.avatar_url or "",
        "resume_data": resume_data,
    }


@router.patch("/responses/{response_id}/approve-chat")
def approve_response_chat(
    response_id: int = Path(...),
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    require_account_types(current_user, "employer", "admin")
    ensure_active_employer_subscription(current_user)

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
            "job_occupation_id": job.occupation_id or "",
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
    ensure_active_employer_subscription(current_user)

    application = session.get(JobApplication, response_id)
    if not application:
        raise HTTPException(status_code=404, detail="not_found")
    job = session.get(Job, application.job_id)
    if not job or job.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="forbidden")
    remove_upload_file(application.resume_url)
    session.delete(application)
    session.commit()
