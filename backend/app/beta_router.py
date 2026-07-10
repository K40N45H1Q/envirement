from json import JSONDecodeError

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.services.beta_ip_security import (
    clear_failed_attempts,
    get_client_ip,
    register_failed_attempt_with_state,
)
from app.services.beta_auth import (
    create_beta_access_token,
    get_beta_access_token_record,
    has_beta_access,
    is_beta_auth_enabled,
    mark_beta_access_token_used,
)


router = APIRouter(prefix="/api/beta-auth", tags=["beta-auth"])


def _set_beta_cookie(response: Response, request: Request, token: str) -> None:
    response.set_cookie(
        key=settings.beta_cookie_name,
        value=token,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="lax",
        path="/",
    )


def _clear_beta_cookie(response: Response, request: Request) -> None:
    response.delete_cookie(
        key=settings.beta_cookie_name,
        path="/",
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="lax",
    )


@router.get("/status")
async def beta_auth_status(request: Request) -> dict[str, bool]:
    return {
        "enabled": is_beta_auth_enabled(),
        "authorized": has_beta_access(request),
    }


@router.post("/login")
async def beta_auth_login(request: Request) -> Response:
    try:
        payload = await request.json()
    except (JSONDecodeError, UnicodeDecodeError):
        payload = {}

    access_token = payload.get("access_token") or ""
    client_ip = get_client_ip(request)

    beta_token = get_beta_access_token_record(access_token)

    if not beta_token:
        is_blocked, remaining_attempts = register_failed_attempt_with_state(client_ip)
        if is_blocked:
            return JSONResponse(
                status_code=401,
                content={
                    "detail": {
                        "error": "invalid_beta_credentials",
                        "remaining_attempts": 0,
                        "blocked": True,
                    }
                },
            )
        return JSONResponse(
            status_code=401,
            content={
                "detail": {
                    "error": "invalid_beta_credentials",
                    "remaining_attempts": remaining_attempts,
                }
            },
        )

    response = JSONResponse(
        status_code=200,
        content={"status": "ok", "authorized": True},
    )
    clear_failed_attempts(client_ip)
    mark_beta_access_token_used(beta_token)
    _set_beta_cookie(response, request, create_beta_access_token(beta_token))
    return response


@router.post("/logout")
async def beta_auth_logout(request: Request) -> Response:
    response = JSONResponse(
        status_code=200,
        content={"status": "ok", "authorized": False},
    )
    _clear_beta_cookie(response, request)
    return response
