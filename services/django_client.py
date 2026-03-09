"""HTTP client used by Django views to call the FastAPI AI service."""

from __future__ import annotations

import logging
import uuid
import time
from typing import Any
from contextlib import contextmanager

import httpx

from .config import get_ai_settings
from .errors import ServiceUnavailableError, CircuitBreakerOpenError

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Simple circuit breaker for fault tolerance."""

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time: float | None = None
        self.is_open = False

    def record_success(self) -> None:
        self.failure_count = 0
        self.is_open = False
        self.last_failure_time = None

    def record_failure(self) -> None:
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.is_open = True

    def can_attempt(self) -> bool:
        if not self.is_open:
            return True
        if self.last_failure_time and (time.time() - self.last_failure_time) > self.timeout:
            self.is_open = False
            self.failure_count = 0
            return True
        return False


def _base_url() -> str:
    try:
        from django.conf import settings as django_settings
        return getattr(django_settings, "AI_SERVICE_BASE_URL", get_ai_settings().django_ai_base_url)
    except Exception:
        return get_ai_settings().django_ai_base_url


class AIServiceClient:
    """Thin HTTP client: Django → FastAPI AI service with resilience."""

    def __init__(self, base_url: str | None = None, max_retries: int = 3) -> None:
        self.base_url = base_url or _base_url()
        self._client = httpx.Client(timeout=get_ai_settings().request_timeout)
        self.max_retries = max_retries
        self.breaker = CircuitBreaker()
        self.request_id = str(uuid.uuid4())

    # ------------------------------------------------------------------
    # Retry logic
    # ------------------------------------------------------------------

    def _post_with_retry(self, path: str, payload: dict[str, Any]) -> Any:
        """POST with exponential backoff retry."""
        if not self.breaker.can_attempt():
            raise CircuitBreakerOpenError()

        last_error: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                resp = self._client.post(
                    f"{self.base_url}{path}",
                    json=payload,
                    headers={"X-Request-ID": self.request_id},
                )
                resp.raise_for_status()
                self.breaker.record_success()
                return resp.json()
            except httpx.HTTPError as exc:
                last_error = exc
                self.breaker.record_failure()
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # exponential backoff
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {exc}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All {self.max_retries} attempts failed: {exc}")

        raise ServiceUnavailableError(f"AI service failed after {self.max_retries} attempts")

    # Kept for backward compatibility and clarity
    def _post(self, path: str, payload: dict[str, Any]) -> Any:
        return self._post_with_retry(path, payload)

    def generate_description(
        self, product_name: str, category: str, price: float
    ) -> str | None:
        try:
            data = self._post(
                "/ai/generate/description",
                {"product_name": product_name, "category": category, "price": price},
            )
            return data.get("description")
        except CircuitBreakerOpenError as exc:
            logger.error(f"Circuit breaker open: {exc.message}")
            return None
        except ServiceUnavailableError as exc:
            logger.error(f"Service unavailable: {exc.message}")
            return None
        except Exception as exc:
            logger.error("generate_description failed: %s", exc, exc_info=True)
            return None

    def generate_tags(
        self, product_name: str, description: str = ""
    ) -> list[str] | None:
        try:
            data = self._post(
                "/ai/generate/tags",
                {"product_name": product_name, "description": description},
            )
            return data.get("tags")
        except (CircuitBreakerOpenError, ServiceUnavailableError) as exc:
            logger.error(f"AI service issue: {exc.message}")
            return None
        except Exception as exc:
            logger.error("generate_tags failed: %s", exc, exc_info=True)
            return None

    # ------------------------------------------------------------------
    # Recommendations
    # ------------------------------------------------------------------

    def get_recommendations(
        self, user_preference: str, category: str = "", count: int = 5
    ) -> list[dict] | None:
        try:
            data = self._post(
                "/ai/recommendations",
                {"user_preference": user_preference, "category": category, "count": count},
            )
            return data.get("recommendations")
        except (CircuitBreakerOpenError, ServiceUnavailableError) as exc:
            logger.error(f"AI service issue: {exc.message}")
            return None
        except Exception as exc:
            logger.error("get_recommendations failed: %s", exc, exc_info=True)
            return None

    def get_similar_products(
        self, product_name: str, count: int = 3
    ) -> list[dict] | None:
        try:
            data = self._post(
                "/ai/similar-products",
                {"product_name": product_name, "count": count},
            )
            return data.get("recommendations")
        except (CircuitBreakerOpenError, ServiceUnavailableError) as exc:
            logger.error(f"AI service issue: {exc.message}")
            return None
        except Exception as exc:
            logger.error("get_similar_products failed: %s", exc, exc_info=True)
            return None

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        """Check if AI service is healthy and circuit breaker is not open."""
        if not self.breaker.can_attempt():
            logger.warning("Circuit breaker is open")
            return False
        try:
            resp = self._client.get(f"{self.base_url}/health", timeout=3.0)
            return resp.status_code == 200
        except Exception as exc:
            logger.error(f"Health check failed: {exc}")
            self.breaker.record_failure()
            return False

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "AIServiceClient":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()


def get_ai_client() -> AIServiceClient:
    """Factory — returns a new client instance with resilience features."""
    return AIServiceClient()


_DEFAULT_BASE_URL_CACHE = None

