from __future__ import annotations

import json

from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_http_methods

from services import get_ai_client


def _json_body(request: HttpRequest) -> dict:
    return json.loads(request.body or "{}")


@require_http_methods(["POST"])
def generate_description_api(request: HttpRequest) -> JsonResponse:
    data = _json_body(request)
    product_name = data.get("product_name")
    category = data.get("category")
    price = data.get("price")

    if not all([product_name, category, price]):
        return JsonResponse({"error": "Missing required fields."}, status=400)

    with get_ai_client() as client:
        description = client.generate_description(product_name, category, float(price))

    if description is None:
        return JsonResponse({"error": "Failed to generate description."}, status=502)

    return JsonResponse({"description": description})


@require_http_methods(["POST"])
def generate_tags_api(request: HttpRequest) -> JsonResponse:
    data = _json_body(request)
    product_name = data.get("product_name")
    description = data.get("description", "")

    if not product_name:
        return JsonResponse({"error": "product_name required."}, status=400)

    with get_ai_client() as client:
        tags = client.generate_tags(product_name, description)

    if tags is None:
        return JsonResponse({"error": "Failed to generate tags."}, status=502)

    return JsonResponse({"tags": tags})


@require_http_methods(["POST"])
def get_recommendations_api(request: HttpRequest) -> JsonResponse:
    data = _json_body(request)
    user_preference = data.get("user_preference")
    category = data.get("category", "")
    count = int(data.get("count", 5))

    if not user_preference:
        return JsonResponse({"error": "user_preference required."}, status=400)

    with get_ai_client() as client:
        recommendations = client.get_recommendations(user_preference, category, count)

    if recommendations is None:
        return JsonResponse({"error": "Failed to get recommendations."}, status=502)

    return JsonResponse({"recommendations": recommendations, "count": len(recommendations)})


@require_http_methods(["POST"])
def get_similar_products_api(request: HttpRequest) -> JsonResponse:
    data = _json_body(request)
    product_name = data.get("product_name")
    count = int(data.get("count", 3))

    if not product_name:
        return JsonResponse({"error": "product_name required."}, status=400)

    with get_ai_client() as client:
        similar_products = client.get_similar_products(product_name, count)

    if similar_products is None:
        return JsonResponse({"error": "Failed to get similar products."}, status=502)

    return JsonResponse({"similar_products": similar_products})


def ai_service_status(request: HttpRequest) -> JsonResponse:
    with get_ai_client() as client:
        available = client.is_available()
    return JsonResponse({"service": "ai-platform", "available": available})
