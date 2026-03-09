"""HTTP client used by Django views to call the FastAPI AI service."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from .config import get_ai_settings

logger = logging.getLogger(__name__)


def _base_url() -> str:
    try:
        from django.conf import settings as django_settings
        return getattr(django_settings, "AI_SERVICE_BASE_URL", get_ai_settings().django_ai_base_url)
    except Exception:
        return get_ai_settings().django_ai_base_url


class AIServiceClient:
    """Thin HTTP client: Django → FastAPI AI service."""

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = base_url or _base_url()
        self._client = httpx.Client(timeout=get_ai_settings().request_timeout)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _post(self, path: str, payload: dict[str, Any]) -> Any:
        resp = self._client.post(f"{self.base_url}{path}", json=payload)
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # Content generation
    # ------------------------------------------------------------------

    def generate_description(
        self, product_name: str, category: str, price: float
    ) -> str | None:
        try:
            data = self._post(
                "/ai/generate/description",
                {"product_name": product_name, "category": category, "price": price},
            )
            return data.get("description")
        except Exception as exc:
            logger.error("generate_description failed: %s", exc)
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
        except Exception as exc:
            logger.error("generate_tags failed: %s", exc)
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
        except Exception as exc:
            logger.error("get_recommendations failed: %s", exc)
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
        except Exception as exc:
            logger.error("get_similar_products failed: %s", exc)
            return None

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        try:
            resp = self._client.get(f"{self.base_url}/health", timeout=3.0)
            return resp.status_code == 200
        except Exception:
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
    """Factory — returns a new client instance."""
    return AIServiceClient()


_DEFAULT_BASE_URL_CACHE = None

