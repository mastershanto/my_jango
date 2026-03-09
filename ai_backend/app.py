from __future__ import annotations

import os
import uuid
from datetime import datetime

# Ensure Django settings are configured before any other imports
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from ai_backend.routers import content_router, recommendation_router
from ai_backend.responses import ErrorResponse, HealthCheckResponse, StatusResponse
from services.config import get_ai_settings
from services.errors import AIServiceError
from services.logging_config import setup_logging

logger = setup_logging(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("AI Platform starting up")
    yield
    logger.info("AI Platform shutting down")


def create_app() -> FastAPI:
    settings = get_ai_settings()

    application = FastAPI(
        title="Cloth Store AI Platform",
        description="Production-grade AI service with resilience for Django storefront.",
        version="2.0.0",
        lifespan=lifespan,
    )

    # Add request ID middleware
    @application.middleware("http")
    async def add_request_id(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global exception handlers
    @application.exception_handler(AIServiceError)
    async def ai_service_error_handler(request: Request, exc: AIServiceError):
        logger.error(f"AIServiceError: {exc.message}", extra={"error_code": exc.error_code})
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=exc.error_code,
                message=exc.message,
                status=exc.status_code,
                details=exc.details,
                request_id=getattr(request.state, "request_id", None),
            ).model_dump(),
        )

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"Validation error: {exc}")
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                error="VALIDATION_ERROR",
                message="Invalid request parameters",
                status=422,
                details={"validation_errors": exc.errors()},
                request_id=getattr(request.state, "request_id", None),
            ).model_dump(),
        )

    @application.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="INTERNAL_SERVER_ERROR",
                message="An unexpected error occurred",
                status=500,
                request_id=getattr(request.state, "request_id", None),
            ).model_dump(),
        )

    application.include_router(content_router)
    application.include_router(recommendation_router)

    @application.get("/health", response_model=HealthCheckResponse, tags=["platform"])
    def health_check() -> HealthCheckResponse:
        return HealthCheckResponse(
            status="healthy",
            service="cloth-store-ai-platform",
            timestamp=datetime.utcnow().isoformat(),
        )

    @application.get("/status", response_model=StatusResponse, tags=["platform"])
    def status_check() -> StatusResponse:
        # In future, could check database, cache, etc.
        return StatusResponse(
            service="cloth-store-ai-platform",
            status="operational",
            ai_service_available=True,
        )

    @application.get("/", tags=["platform"])
    def root() -> dict[str, object]:
        return {
            "message": "Cloth Store AI Platform",
            "version": "2.0.0",
            "debug": settings.debug,
            "docs_url": "/docs",
            "services": ["content-generation", "recommendations"],
        }

    return application


app = create_app()
