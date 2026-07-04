from uvicorn import run

from app.core.config import settings
from pathlib import Path

if __name__ == "__main__":
    backend_dir = Path(__file__).resolve().parent
    run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True,
        reload_dirs=[str(backend_dir)],
        log_level="info",
    )
