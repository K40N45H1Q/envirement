from os import environ, makedirs, path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from uvicorn import run

from routes.jobs import router as jobs_router
from routes.profile import router as profile_router
from routes.safety import ensure_default_admin, router as safety_router

BASE_DIR = path.dirname(path.abspath(__file__))
UPLOAD_DIR = path.join(BASE_DIR, "uploads")

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

environ["UPLOAD_DIR"] = UPLOAD_DIR
ensure_default_admin()

app.include_router(safety_router)
app.include_router(jobs_router, prefix="/api")
app.include_router(profile_router, prefix="/api")

if __name__ == "__main__":
    run(
        "run:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
