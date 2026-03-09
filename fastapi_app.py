"""Thin entrypoint for the packaged FastAPI application."""

from ai_backend.app import app
from services.config import get_ai_settings


if __name__ == "__main__":
    import uvicorn

    settings = get_ai_settings()

    uvicorn.run(
        "fastapi_app:app",
        host=settings.fastapi_host,
        port=settings.fastapi_port,
        reload=settings.debug,
    )
