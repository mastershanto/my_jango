"""
AI Services package for integrating OpenAI and local ML models.
"""

from .django_client import AIServiceClient, get_ai_client
from .ml_service import generate_product_description_local, generate_product_tags_local
from .openai_service import (
    generate_product_description_openai,
    generate_product_tags_openai,
)
from .openai_recommendation_service import (
    get_product_recommendations_openai,
    get_similar_products_openai,
    get_recommendation_reasoning_openai,
)
from .recommendation_service import (
    get_product_recommendations_local,
    get_similar_products_local,
    get_category_recommendations_local,
    get_trending_products_local,
)

__all__ = [
    "AIServiceClient",
    "get_ai_client",
    "generate_product_description_openai",
    "generate_product_tags_openai",
    "generate_product_description_local",
    "generate_product_tags_local",
    "get_product_recommendations_openai",
    "get_similar_products_openai",
    "get_recommendation_reasoning_openai",
    "get_product_recommendations_local",
    "get_similar_products_local",
    "get_category_recommendations_local",
    "get_trending_products_local",
]
