import secrets
import shutil
from os import path, makedirs, getenv, remove
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Path, UploadFile
from sqlmodel import select

from database.models import Job, JobApplication, User, get_session
from routes.safety import get_current_user

router = APIRouter()

UPLOAD_DIR = getenv("UPLOAD_DIR")
if not UPLOAD_DIR:
    base_dir = path.dirname(path.dirname(path.abspath(__file__)))
    UPLOAD_DIR = path.join(base_dir, "uploads")


def store_logo_file(logo: UploadFile) -> str:
    filename = f"{secrets.token_hex(8)}_{logo.filename}"
    file_path = path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(logo.file, buffer)
    return f"/uploads/{filename}"


@router.post("/create_job")
async def create_job(
    title: str = Form(...),
    salary: str = Form(...),
    location: str = Form(...),
    description: str = Form(...),
    logo: Optional[UploadFile] = File(None),
    logo_url: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    company_name = (current_user.company_name or "").strip()
    if not company_name:
        raise HTTPException(status_code=400, detail={"key": "missing_company_profile"})

    if not logo and not logo_url:
        raise HTTPException(status_code=400, detail={"key": "missing_logo"})

    makedirs(UPLOAD_DIR, exist_ok=True)

    if logo:
        logo_path = store_logo_file(logo)
        current_user.company_logo_url = logo_path
        session.add(current_user)
    else:
        logo_path = logo_url or current_user.company_logo_url or ""

    job_status = "approved" if current_user.account_type == "admin" else "pending"

    job = Job(
        title=title,
        company=company_name,
        salary=salary,
        location=location,
        description=description,
        logo=logo_path,
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


@router.get("/my_jobs", response_model=List[Job])
def get_my_jobs(
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    return session.exec(
        select(Job).where(Job.user_id == current_user.id).order_by(Job.id.desc())
    ).all()


@router.put("/jobs/{job_id}")
async def update_job(
    job_id: int = Path(...),
    title: str = Form(...),
    salary: str = Form(...),
    location: str = Form(...),
    description: str = Form(...),
    logo: Optional[UploadFile] = File(None),
    logo_url: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    company_name = (current_user.company_name or "").strip()
    if not company_name:
        raise HTTPException(status_code=400, detail={"key": "missing_company_profile"})

    job = session.get(Job, job_id)
    if not job or job.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Job not found")

    old_logo = job.logo
    makedirs(UPLOAD_DIR, exist_ok=True)

    if logo:
        new_logo_path = store_logo_file(logo)
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
        current_user.company_logo_url = new_logo_path
        session.add(current_user)
    elif logo_url:
        job.logo = logo_url
        current_user.company_logo_url = logo_url
        session.add(current_user)
    elif current_user.company_logo_url:
        job.logo = current_user.company_logo_url

    job.title = title
    job.company = company_name
    job.salary = salary
    job.location = location
    job.description = description

    if current_user.account_type != "admin" and job.status == "approved":
        job.status = "pending"

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
    if current_user.account_type != "admin":
        raise HTTPException(status_code=403, detail="forbidden")
    return session.exec(
        select(Job).where(Job.status == "pending").order_by(Job.created_at.desc())
    ).all()


@router.patch("/moderation/jobs/{job_id}/approve")
def approve_job(
    job_id: int = Path(...),
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    if current_user.account_type != "admin":
        raise HTTPException(status_code=403, detail="forbidden")
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
    if current_user.account_type != "admin":
        raise HTTPException(status_code=403, detail="forbidden")
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
    )
    session.add(application)
    session.commit()
    session.refresh(application)
    return {"status": "ok"}


@router.get("/responses")
def get_my_job_responses(
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
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
            "location": job.location,
            "salary": job.salary,
            "logo": job.logo,
            "description": job.description,
        }
        for job in my_jobs
    }

    result = []
    for app in applications:
        job_data = job_map.get(app.job_id, {})
        result.append({
            "id": app.id,
            "job_id": app.job_id,
            "job_title": job_data.get("title", ""),
            "job_company": job_data.get("company", ""),
            "job_location": job_data.get("location", ""),
            "job_salary": job_data.get("salary", ""),
            "job_logo": job_data.get("logo", ""),
            "job_description": job_data.get("description", ""),
            "phone": app.phone,
            "email": app.email,
            "username": app.username,
            "name": app.name,
            "surname": app.surname,
            "nationality": app.nationality,
            "message": app.message,
            "created_at": app.created_at,
        })
    return result


@router.delete("/responses/{response_id}", status_code=204)
def delete_response(
    response_id: int = Path(...),
    current_user: User = Depends(get_current_user),
    session=Depends(get_session),
):
    application = session.get(JobApplication, response_id)
    if not application:
        raise HTTPException(status_code=404, detail="not_found")
    job = session.get(Job, application.job_id)
    if not job or job.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="forbidden")
    session.delete(application)
    session.commit()
