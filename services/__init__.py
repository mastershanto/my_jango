"""AI services: OpenAI integrations + HTTP client for Django → FastAPI calls."""

from .config import AISettings, get_ai_settings
from .django_client import AIServiceClient, get_ai_client
from .openai_service import (
    generate_product_description_openai,
    generate_product_tags_openai,
)
from .openai_recommendation_service import (
    get_product_recommendations_openai,
    get_similar_products_openai,
    get_recommendation_reasoning_openai,
)

__all__ = [
    "AIServiceClient",
    "AISettings",
    "get_ai_client",
    "get_ai_settings",
    "generate_product_description_openai",
    "generate_product_tags_openai",
    "get_product_recommendations_openai",
    "get_similar_products_openai",
    "get_recommendation_reasoning_openai",
]
