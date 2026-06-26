# MVP API Contract

## Scope
Целевой MVP-контракт для синхронизации Frontend Agent и Backend Agent.

- Backend target stack: `FastAPI + Pydantic v2 + SQLAlchemy 2.0 + Alembic`
- Frontend target stack: `Vue 3 + <script setup lang="ts"> + Pinia + Vite`
- Auth transport: `Authorization: Bearer <jwt>`
- Base URL: `http://localhost:8000`
- Time fields: ISO 8601 UTC string

## Shared Schemas

### ErrorResponse
```py
class ErrorDetail(BaseModel):
    error: str | None = None
    key: str | None = None

class ErrorResponse(BaseModel):
    detail: ErrorDetail | str
```

### UserOut
```py
class UserOut(BaseModel):
    id: int
    email: EmailStr
    account_type: Literal["user", "employer", "admin"]
    created_at: datetime
    updated_at: datetime
```

### JobOut
```py
class JobOut(BaseModel):
    id: int
    title: str
    status: Literal["pending", "approved", "rejected"]
    company: str
    location: str
    description: str | None
    salary: str | None
    logo: str | None
    user_id: int
    created_at: datetime
    updated_at: datetime
```

### CandidateProfileOut
```py
class CandidateProfileOut(BaseModel):
    first_name: str
    last_name: str
    phone: str
    summary: str
    current_role: str
    skills: str
    sectors: list[str]
    languages: list[str]
    licenses: list[str]
    mobility: str
    preferred_mobility: str
    work_permit: str
    availability: str
    resume_name: str
    resume_url: str
    avatar_url: str
```

### JobApplicationOut
```py
class JobApplicationOut(BaseModel):
    id: int
    job_id: int
    phone: str
    email: EmailStr
    username: str | None
    name: str
    surname: str
    nationality: str | None
    message: str | None
    created_at: datetime
```

### EmployerResponseOut
```py
class EmployerResponseOut(BaseModel):
    id: int
    job_id: int
    job_title: str
    job_company: str
    job_location: str
    job_salary: str
    job_logo: str
    job_description: str
    phone: str
    email: EmailStr
    username: str | None
    name: str
    surname: str
    nationality: str | None
    message: str | None
    created_at: datetime
```

### CandidateApplicationOut
```py
class CandidateApplicationOut(BaseModel):
    id: int
    job_id: int
    job_title: str
    job_company: str
    job_location: str
    job_salary: str
    job_logo: str
    job_status: Literal["pending", "approved", "rejected"]
    message: str | None
    phone: str
    email: EmailStr
    name: str
    surname: str
    nationality: str | None
    created_at: datetime
```

## Auth Endpoints

### `POST /create_account`
Request Schema:
```py
class CreateAccountRequest(BaseModel):
    email: EmailStr
    password: constr(min_length=8)
    account_type: Literal["user", "employer"] = "user"
```

Response Schema:
```py
class CreateAccountResponse(BaseModel):
    status: Literal["ok"]
    user_id: int
```

### `POST /login`
Request Schema:
```py
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
```

Response Schema:
```py
class LoginResponse(BaseModel):
    status: Literal["ok"]
    token: str
```

### `GET /get_me`
Request Schema:
- No body
- Header: `Authorization: Bearer <jwt>`

Response Schema:
- `UserOut`

## Public Jobs Endpoints

### `GET /api/get_jobs`
Request Schema:
- No body

Response Schema:
```py
list[JobOut]
```

### `GET /api/jobs/{job_id}`
Request Schema:
- Path: `job_id: int`

Response Schema:
- `JobOut`

## Employer Jobs Endpoints

### `POST /api/create_job`
Content-Type: `multipart/form-data`

Request Schema:
```py
class CreateJobForm(BaseModel):
    title: str
    company: str
    salary: str
    location: str
    description: str
    logo_url: str | None = None
```
Files:
```py
logo: UploadFile | None
```

Response Schema:
- `JobOut`

### `GET /api/my_jobs`
Request Schema:
- No body
- Header: `Authorization: Bearer <jwt>`

Response Schema:
```py
list[JobOut]
```

### `PUT /api/jobs/{job_id}`
Content-Type: `multipart/form-data`

Request Schema:
```py
class UpdateJobForm(BaseModel):
    title: str
    company: str
    salary: str
    location: str
    description: str
    logo_url: str | None = None
```
Files:
```py
logo: UploadFile | None
```

Response Schema:
- `JobOut`

### `DELETE /api/jobs/{job_id}`
Request Schema:
- Path: `job_id: int`

Response Schema:
- HTTP `204 No Content`

## Candidate Applications Endpoints

### `POST /api/apply`
Request Schema:
```py
class ApplyToJobRequest(BaseModel):
    job_id: int
    username: str | None = None
    email: EmailStr
    phone: str
    name: str
    surname: str
    nationality: str | None = None
    message: str | None = None
```

Response Schema:
```py
class ApplyToJobResponse(BaseModel):
    status: Literal["ok"]
```

### `GET /api/my_applications`
Request Schema:
- No body
- Header: `Authorization: Bearer <jwt>`

Response Schema:
```py
list[CandidateApplicationOut]
```

## Candidate Profile Endpoints

### `GET /api/profile`
Request Schema:
- No body
- Header: `Authorization: Bearer <jwt>`

Response Schema:
- `CandidateProfileOut`

### `PUT /api/profile`
Content-Type: `multipart/form-data`

Request Schema:
```py
class UpdateProfileForm(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    summary: str | None = None
    current_role: str | None = None
    skills: str | None = None
    sectors_json: str | None = None
    languages_json: str | None = None
    licenses_json: str | None = None
    mobility: str | None = None
    preferred_mobility: str | None = None
    work_permit: str | None = None
    availability: str | None = None
```
Files:
```py
avatar: UploadFile | None
resume: UploadFile | None
```

Response Schema:
- `CandidateProfileOut`

## Employer Responses Endpoints

### `GET /api/responses`
Request Schema:
- No body
- Header: `Authorization: Bearer <jwt>`

Response Schema:
```py
list[EmployerResponseOut]
```

### `DELETE /api/responses/{response_id}`
Request Schema:
- Path: `response_id: int`

Response Schema:
- HTTP `204 No Content`

## Admin Moderation Endpoints

### `GET /api/moderation/jobs`
Request Schema:
- No body
- Header: `Authorization: Bearer <jwt>`

Response Schema:
```py
list[JobOut]
```

### `PATCH /api/moderation/jobs/{job_id}/approve`
Request Schema:
- Path: `job_id: int`

Response Schema:
- `JobOut`

### `PATCH /api/moderation/jobs/{job_id}/reject`
Request Schema:
- Path: `job_id: int`

Response Schema:
- `JobOut`

## Notes For Agents

1. Текущая локальная реализация уже покрывает большую часть этого контракта, но пока не соответствует целевому стеку полностью.
2. На backend сейчас используется `sqlmodel + sqlite + sync session`; на следующих шагах нужно привести к `SQLAlchemy 2.0 async + Alembic`.
3. На frontend сейчас код в основном на `.js`; на следующих шагах нужно мигрировать на `TypeScript + Pinia + script setup`.
