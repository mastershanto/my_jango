"""Custom exception types for graceful error handling."""

from typing import Optional


class AIServiceError(Exception):
    """Base exception for AI service errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[dict] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict:
        return {
            "error": self.error_code,
            "message": self.message,
            "status": self.status_code,
            "details": self.details,
        }


class ServiceUnavailableError(AIServiceError):
    """Raised when FastAPI service is unavailable."""

    def __init__(self, message: str = "AI service is currently unavailable"):
        super().__init__(
            message=message,
            status_code=503,
            error_code="SERVICE_UNAVAILABLE",
        )


class ValidationError(AIServiceError):
    """Raised when input validation fails."""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class CircuitBreakerOpenError(AIServiceError):
    """Raised when circuit breaker is open."""

    def __init__(self):
        super().__init__(
            message="Service temporarily unavailable — too many failures",
            status_code=503,
            error_code="CIRCUIT_BREAKER_OPEN",
        )
