"""
Django URLs configuration for FastAPI AI integration.

Add this to your clothstore/urls.py to enable AI API endpoints.
"""

from django.urls import path
from EXAMPLES_DJANGO_INTEGRATION import (
    ai_service_status,
    generate_description_api,
    generate_tags_api,
    get_recommendations_api,
    get_similar_products_api,
    category_recommendations_api,
    product_recommendations_page,
)

app_name = "ai"

urlpatterns = [
    # AI Service endpoints
    path(
        "api/generate-description/",
        generate_description_api,
        name="generate_description",
    ),
    path("api/generate-tags/", generate_tags_api, name="generate_tags"),
    path("api/status/", ai_service_status, name="ai_status"),
    
    # Recommendation endpoints
    path(
        "api/recommendations/",
        get_recommendations_api,
        name="get_recommendations",
    ),
    path(
        "api/similar-products/",
        get_similar_products_api,
        name="similar_products",
    ),
    path(
        "api/category-recommendations/",
        category_recommendations_api,
        name="category_recommendations",
    ),
    
    # Pages
    path(
        "recommendations/",
        product_recommendations_page,
        name="recommendations_page",
    ),
]


# To include these URLs in your main Django project, add to config/urls.py:
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("clothstore.urls")),
    path("ai/", include("ai_urls")),  # Add this line
]
"""
