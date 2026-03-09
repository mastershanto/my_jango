from django.urls import path

from . import views

app_name = "clothstore_ai"

urlpatterns = [
    path("api/generate-description/", views.generate_description_api, name="generate_description"),
    path("api/generate-tags/", views.generate_tags_api, name="generate_tags"),
    path("api/recommendations/", views.get_recommendations_api, name="get_recommendations"),
    path("api/similar-products/", views.get_similar_products_api, name="similar_products"),
    path("api/status/", views.ai_service_status, name="ai_status"),
]
