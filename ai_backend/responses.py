"""Common response models for consistent API structure."""

from pydantic import BaseModel, Field
from typing import Any, Optional


class ErrorResponse(BaseModel):
    """Standard error response format."""

    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    status: int = Field(..., description="HTTP status code")
    details: Optional[dict[str, Any]] = Field(None, description="Additional error details")
    request_id: Optional[str] = Field(None, description="Request correlation ID")


class HealthCheckResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status: healthy or degraded")
    service: str = Field(..., description="Service name")
    timestamp: str = Field(..., description="ISO timestamp")


class StatusResponse(BaseModel):
    """Service status response with circuit breaker info."""

    service: str
    status: str
    ai_service_available: bool
    version: str = "2.0.0"
