from __future__ import annotations

import os

# Ensure Django settings are configured before any other imports
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ai_backend.routers import content_router, recommendation_router
from services.config import get_ai_settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


def create_app() -> FastAPI:
    settings = get_ai_settings()

    application = FastAPI(
        title="Cloth Store AI Platform",
        description="Production-style AI service for Django storefront integrations.",
        version="2.0.0",
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(content_router)
    application.include_router(recommendation_router)

    @application.get("/health", tags=["platform"])
    def health_check() -> dict[str, str]:
        return {"status": "healthy", "service": "cloth-store-ai-platform"}

    @application.get("/", tags=["platform"])
    def root() -> dict[str, object]:
        return {
            "message": "Cloth Store AI Platform",
            "debug": settings.debug,
            "docs_url": "/docs",
            "services": ["content-generation", "recommendations"],
        }

    return application


app = create_app()
