from fastapi import APIRouter


api_router = APIRouter()


@api_router.get("/health", tags=["system"])
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@api_router.get("/bootstrap-status", tags=["system"])
async def bootstrap_status() -> dict[str, str]:
    return {
        "status": "ok",
        "mode": "hybrid",
        "detail": "New app foundation is active and legacy MVP routes are mounted for continuity.",
    }
