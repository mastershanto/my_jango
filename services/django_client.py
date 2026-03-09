"""
Django client to call FastAPI AI endpoints.
Use this in your Django views to integrate AI features.
"""

import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)

FASTAPI_BASE_URL = "http://127.0.0.1:8001"


class AIServiceClient:
    """Client for calling FastAPI AI services from Django."""

    def __init__(self, base_url: str = FASTAPI_BASE_URL):
        self.base_url = base_url
        self.client = httpx.Client(timeout=30.0)

    def generate_description_openai(
        self, product_name: str, category: str, price: float
    ) -> Optional[str]:
        """Call OpenAI endpoint from Django."""
        try:
            response = self.client.post(
                f"{self.base_url}/ai/openai/description",
                json={
                    "product_name": product_name,
                    "category": category,
                    "price": price,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data.get("description")
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            return None

    def generate_description_local(
        self, product_name: str, category: str, price: float
    ) -> Optional[str]:
        """Call local ML model endpoint from Django."""
        try:
            response = self.client.post(
                f"{self.base_url}/ai/local/description",
                json={
                    "product_name": product_name,
                    "category": category,
                    "price": price,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data.get("description")
        except Exception as e:
            logger.error(f"Local ML model call failed: {str(e)}")
            return None

    def generate_tags_openai(
        self, product_name: str, description: str = ""
    ) -> Optional[list[str]]:
        """Call OpenAI tags endpoint from Django."""
        try:
            response = self.client.post(
                f"{self.base_url}/ai/openai/tags",
                json={"product_name": product_name, "description": description},
            )
            response.raise_for_status()
            data = response.json()
            return data.get("tags")
        except Exception as e:
            logger.error(f"OpenAI tags API call failed: {str(e)}")
            return None

    def generate_tags_local(self, product_name: str) -> Optional[list[str]]:
        """Call local ML model tags endpoint from Django."""
        try:
            response = self.client.post(
                f"{self.base_url}/ai/local/tags",
                json={"product_name": product_name},
            )
            response.raise_for_status()
            data = response.json()
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
            response = self.client.post(
                f"{self.base_url}/ai/openai/recommendations",
                json={
                    "user_preference": user_preference,
                    "category": category,
                    "count": count,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data.get("recommendations")
        except Exception as e:
            logger.error(f"OpenAI recommendations failed: {str(e)}")
            return None

    def get_recommendations_local(
        self, user_preference: str, category: str = "", count: int = 5
    ) -> Optional[list[dict]]:
        """Get product recommendations using local ML."""
        try:
            response = self.client.post(
                f"{self.base_url}/ai/local/recommendations",
                json={
                    "user_preference": user_preference,
                    "category": category,
                    "count": count,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data.get("recommendations")
        except Exception as e:
            logger.error(f"Local ML recommendations failed: {str(e)}")
            return None

    def get_similar_products_openai(
        self, product_name: str, count: int = 3
    ) -> Optional[list[str]]:
        """Get similar products using OpenAI."""
        try:
            response = self.client.post(
                f"{self.base_url}/ai/openai/similar-products",
                json={"product_name": product_name, "count": count},
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"OpenAI similar products failed: {str(e)}")
            return None

    def get_similar_products_local(
        self, product_name: str, count: int = 3
    ) -> Optional[list[dict]]:
        """Get similar products using local ML."""
        try:
            response = self.client.post(
                f"{self.base_url}/ai/local/similar-products",
                json={"product_name": product_name, "count": count},
            )
            response.raise_for_status()
            data = response.json()
            return data.get("recommendations")
        except Exception as e:
            logger.error(f"Local ML similar products failed: {str(e)}")
            return None

    def get_category_recommendations(
        self, category: str, count: int = 5
    ) -> Optional[list[dict]]:
        """Get recommendations based on category."""
        try:
            response = self.client.post(
                f"{self.base_url}/ai/local/category-recommendations",
                json={"category": category, "count": count},
            )
            response.raise_for_status()
            data = response.json()
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


# Singleton instance for convenience
_client_instance = None


def get_ai_client() -> AIServiceClient:
    """Get or create singleton AI service client."""
    global _client_instance
    if _client_instance is None:
        _client_instance = AIServiceClient()
    return _client_instance
