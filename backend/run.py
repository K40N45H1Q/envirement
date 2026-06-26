from uvicorn import run

from app.core.config import settings
from app.main import app

if __name__ == "__main__":
    run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True,
        log_level="info",
    )
