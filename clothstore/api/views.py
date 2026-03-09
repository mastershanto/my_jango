from __future__ import annotations

import json

from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
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
    use_openai = data.get("use_openai", False)

    if not all([product_name, category, price]):
        return JsonResponse({"error": "Missing required fields."}, status=400)

    with get_ai_client() as client:
        description = (
            client.generate_description_openai(product_name, category, price)
            if use_openai
            else client.generate_description_local(product_name, category, price)
        )

    if description is None:
        return JsonResponse({"error": "Failed to generate description."}, status=502)

    return JsonResponse({
        "description": description,
        "provider": "openai" if use_openai else "local",
    })


@require_http_methods(["POST"])
def generate_tags_api(request: HttpRequest) -> JsonResponse:
    data = _json_body(request)
    product_name = data.get("product_name")
    description = data.get("description", "")
    use_openai = data.get("use_openai", False)

    if not product_name:
        return JsonResponse({"error": "product_name required."}, status=400)

    with get_ai_client() as client:
        tags = (
            client.generate_tags_openai(product_name, description)
            if use_openai
            else client.generate_tags_local(product_name)
        )

    if tags is None:
        return JsonResponse({"error": "Failed to generate tags."}, status=502)

    return JsonResponse({"tags": tags, "provider": "openai" if use_openai else "local"})


@require_http_methods(["POST"])
def get_recommendations_api(request: HttpRequest) -> JsonResponse:
    data = _json_body(request)
    user_preference = data.get("user_preference")
    category = data.get("category", "")
    count = int(data.get("count", 5))
    use_openai = data.get("use_openai", False)

    if not user_preference:
        return JsonResponse({"error": "user_preference required."}, status=400)

    with get_ai_client() as client:
        recommendations = (
            client.get_recommendations_openai(user_preference, category, count)
            if use_openai
            else client.get_recommendations_local(user_preference, category, count)
        )

    if recommendations is None:
        return JsonResponse({"error": "Failed to get recommendations."}, status=502)

    return JsonResponse({
        "recommendations": recommendations,
        "provider": "openai" if use_openai else "local",
        "count": len(recommendations),
    })


@require_http_methods(["POST"])
def get_similar_products_api(request: HttpRequest) -> JsonResponse:
    data = _json_body(request)
    product_name = data.get("product_name")
    count = int(data.get("count", 3))
    use_openai = data.get("use_openai", False)

    if not product_name:
        return JsonResponse({"error": "product_name required."}, status=400)

    with get_ai_client() as client:
        similar_products = (
            client.get_similar_products_openai(product_name, count)
            if use_openai
            else client.get_similar_products_local(product_name, count)
        )

    if similar_products is None:
        return JsonResponse({"error": "Failed to get similar products."}, status=502)

    return JsonResponse({
        "similar_products": similar_products,
        "provider": "openai" if use_openai else "local",
    })


@require_http_methods(["GET", "POST"])
def category_recommendations_api(request: HttpRequest) -> JsonResponse:
    if request.method == "GET":
        category = request.GET.get("category", "")
        count = int(request.GET.get("count", 5))
    else:
        data = _json_body(request)
        category = data.get("category", "")
        count = int(data.get("count", 5))

    if not category:
        return JsonResponse({"error": "category required."}, status=400)

    with get_ai_client() as client:
        recommendations = client.get_category_recommendations(category, count)

    if recommendations is None:
        return JsonResponse({"error": "Failed to get category recommendations."}, status=502)

    return JsonResponse({
        "category": category,
        "recommendations": recommendations,
        "provider": "local",
    })


def ai_service_status(request: HttpRequest) -> JsonResponse:
    with get_ai_client() as client:
        available = client.is_service_available()
    return JsonResponse({"service": "ai-platform", "available": available})


def product_recommendations_page(request: HttpRequest):
    return render(
        request,
        "clothstore/recommendations.html",
        {"categories": ["Tops", "Bottoms", "Outerwear", "Footwear", "Accessories"]},
    )
