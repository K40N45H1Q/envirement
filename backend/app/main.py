from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.models.user import User  # noqa: F401
from app.services.default_accounts import sync_default_accounts
from routes.jobs import router as legacy_jobs_router
from routes.profile import router as legacy_profile_router
from routes.admin import router as legacy_admin_router
from routes.safety import router as legacy_safety_router
from routes.payments import router as legacy_payments_router


def create_app() -> FastAPI:
    sync_default_accounts()

    app = FastAPI(title=settings.app_name, debug=settings.app_debug)

    @app.on_event("startup")
    async def ensure_database_ready() -> None:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api")
    app.include_router(legacy_safety_router, prefix="/api")
    app.include_router(legacy_admin_router, prefix="/api")
    app.include_router(legacy_payments_router, prefix="/api")
    app.include_router(legacy_jobs_router, prefix="/api")
    app.include_router(legacy_profile_router, prefix="/api")
    return app


app = create_app()
