from os import environ
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import settings
from routes.jobs import router as legacy_jobs_router
from routes.profile import router as legacy_profile_router
from routes.safety import router as legacy_safety_router


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, debug=settings.app_debug)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    uploads_dir = Path(settings.uploads_dir)
    uploads_dir.mkdir(parents=True, exist_ok=True)
    environ["UPLOAD_DIR"] = str(uploads_dir)

    app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
    app.include_router(api_router, prefix="/api")
    app.include_router(legacy_safety_router)
    app.include_router(legacy_jobs_router, prefix="/api")
    app.include_router(legacy_profile_router, prefix="/api")
    return app


app = create_app()
