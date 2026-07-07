import json
from os import environ
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.beta_router import router as beta_router
from app.core.config import settings
from app.services.beta_ip_security import (
    clear_failed_attempts,
    get_client_ip,
    is_ip_blocked,
    register_failed_attempt_with_state,
)
from app.services.beta_auth import (
    create_beta_access_token,
    has_beta_access,
    is_beta_auth_enabled,
    verify_beta_access_token_value,
)
from app.services.default_accounts import sync_default_accounts
from app.services.request_blackhole import close_blocked_connection
from routes.jobs import router as legacy_jobs_router
from routes.profile import router as legacy_profile_router
from routes.safety import router as legacy_safety_router


class BetaAccessMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http" or not is_beta_auth_enabled():
            await self.app(scope, receive, send)
            return

        path = scope.get("path") or "/"
        method = scope.get("method")
        if method == "OPTIONS":
            await self.app(scope, receive, send)
            return

        from starlette.requests import Request

        request = Request(scope)
        client_ip = get_client_ip(request)
        if is_ip_blocked(client_ip):
            closed = await close_blocked_connection(send)
            if closed:
                return
            response = JSONResponse(
                status_code=404,
                content="Access denied!",
            )
            await response(scope, receive, send)
            return

        if path == "/api/beta-auth/login" and method == "POST":
            body = b""
            more_body = True
            while more_body:
                message = await receive()
                if message["type"] != "http.request":
                    continue
                body += message.get("body", b"")
                more_body = message.get("more_body", False)

            try:
                payload = json.loads(body.decode("utf-8") or "{}")
            except (json.JSONDecodeError, UnicodeDecodeError):
                payload = {}

            access_token = payload.get("access_token") or ""
            if not verify_beta_access_token_value(access_token):
                is_blocked, remaining_attempts = register_failed_attempt_with_state(client_ip)
                if is_blocked:
                    closed = await close_blocked_connection(send)
                    if closed:
                        return
                    response = JSONResponse(status_code=204, content=None)
                    await response(scope, receive, send)
                    return

                response = JSONResponse(
                    status_code=401,
                    content={
                        "detail": {
                            "error": "invalid_beta_credentials",
                            "remaining_attempts": remaining_attempts,
                        }
                    },
                )
                await response(scope, receive, send)
                return

            response = JSONResponse(
                status_code=200,
                content={"status": "ok", "authorized": True},
            )
            clear_failed_attempts(client_ip)
            response.set_cookie(
                key=settings.beta_cookie_name,
                value=create_beta_access_token(),
                httponly=True,
                secure=scope.get("scheme") == "https",
                samesite="lax",
                path="/",
            )
            await response(scope, receive, send)
            return

        public_prefixes = (
            "/api/beta-auth/",
        )

        if any(path.startswith(prefix) for prefix in public_prefixes) or has_beta_access(request):
            await self.app(scope, receive, send)
            return

        response = JSONResponse(
            status_code=401,
            content={"detail": {"error": "beta_auth_required"}},
        )
        await response(scope, receive, send)


def create_app() -> FastAPI:
    sync_default_accounts()

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
    app.include_router(beta_router)
    app.include_router(legacy_safety_router)
    app.include_router(legacy_jobs_router, prefix="/api")
    app.include_router(legacy_profile_router, prefix="/api")
    return app


fastapi_app = create_app()
app = BetaAccessMiddleware(fastapi_app)
