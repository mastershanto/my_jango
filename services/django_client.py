"""Django-side client for the FastAPI AI platform."""

from __future__ import annotations

import logging
from typing import Any, Optional

import httpx

from django.conf import settings

from .config import get_ai_settings

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = getattr(settings, "AI_SERVICE_BASE_URL", get_ai_settings().django_ai_base_url)


class AIServiceClient:
    """Client for calling FastAPI AI services from Django."""

    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        self.base_url = base_url
        self.client = httpx.Client(timeout=get_ai_settings().request_timeout)

    def _post(self, path: str, payload: dict[str, Any]) -> Any:
        response = self.client.post(f"{self.base_url}{path}", json=payload)
        response.raise_for_status()
        return response.json()

    def generate_description_openai(
        self, product_name: str, category: str, price: float
    ) -> Optional[str]:
        """Call OpenAI endpoint from Django."""
        try:
            data = self._post(
                "/ai/openai/description",
                {
                    "product_name": product_name,
                    "category": category,
                    "price": price,
                },
            )
            return data.get("description")
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            return None

    def generate_description_local(
        self, product_name: str, category: str, price: float
    ) -> Optional[str]:
        """Call local ML model endpoint from Django."""
        try:
            data = self._post(
                "/ai/local/description",
                {
                    "product_name": product_name,
                    "category": category,
                    "price": price,
                },
            )
            return data.get("description")
        except Exception as e:
            logger.error(f"Local ML model call failed: {str(e)}")
            return None

    def generate_tags_openai(
        self, product_name: str, description: str = ""
    ) -> Optional[list[str]]:
        """Call OpenAI tags endpoint from Django."""
        try:
            data = self._post(
                "/ai/openai/tags",
                {"product_name": product_name, "description": description},
            )
            return data.get("tags")
        except Exception as e:
            logger.error(f"OpenAI tags API call failed: {str(e)}")
            return None

    def generate_tags_local(self, product_name: str) -> Optional[list[str]]:
        """Call local ML model tags endpoint from Django."""
        try:
            data = self._post("/ai/local/tags", {"product_name": product_name})
            return data.get("tags")
        except Exception as e:
            logger.error(f"Local ML tags call failed: {str(e)}")
            return None

    # Recommendation methods
    def get_recommendations_openai(
        self, user_preference: str, category: str = "", count: int = 5
    ) -> Optional[list[dict]]:
        """Get product recommendations using OpenAI."""
        try:
            data = self._post(
                "/ai/openai/recommendations",
                {
                    "user_preference": user_preference,
                    "category": category,
                    "count": count,
                },
            )
            return data.get("recommendations")
        except Exception as e:
            logger.error(f"OpenAI recommendations failed: {str(e)}")
            return None

    def get_recommendations_local(
        self, user_preference: str, category: str = "", count: int = 5
    ) -> Optional[list[dict]]:
        """Get product recommendations using local ML."""
        try:
            data = self._post(
                "/ai/local/recommendations",
                {
                    "user_preference": user_preference,
                    "category": category,
                    "count": count,
                },
            )
            return data.get("recommendations")
        except Exception as e:
            logger.error(f"Local ML recommendations failed: {str(e)}")
            return None

    def get_similar_products_openai(
        self, product_name: str, count: int = 3
    ) -> Optional[list[str]]:
        """Get similar products using OpenAI."""
        try:
            data = self._post(
                "/ai/openai/similar-products",
                {"product_name": product_name, "count": count},
            )
            return data
        except Exception as e:
            logger.error(f"OpenAI similar products failed: {str(e)}")
            return None

    def get_similar_products_local(
        self, product_name: str, count: int = 3
    ) -> Optional[list[dict]]:
        """Get similar products using local ML."""
        try:
            data = self._post(
                "/ai/local/similar-products",
                {"product_name": product_name, "count": count},
            )
            return data.get("recommendations")
        except Exception as e:
            logger.error(f"Local ML similar products failed: {str(e)}")
            return None

    def get_category_recommendations(
        self, category: str, count: int = 5
    ) -> Optional[list[dict]]:
        """Get recommendations based on category."""
        try:
            data = self._post(
                "/ai/local/category-recommendations",
                {"category": category, "count": count},
            )
            return data.get("recommendations")
        except Exception as e:
            logger.error(f"Category recommendations failed: {str(e)}")
            return None

    def is_service_available(self) -> bool:
        """Check if FastAPI service is running."""
        try:
            response = self.client.get(f"{self.base_url}/health", timeout=5.0)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"FastAPI service not available: {str(e)}")
            return False

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def get_ai_client() -> AIServiceClient:
    """Return a fresh AI service client."""
    return AIServiceClient()
