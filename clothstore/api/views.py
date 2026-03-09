from __future__ import annotations

import json
import logging

from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_http_methods

from services import get_ai_client
from services.errors import AIServiceError

logger = logging.getLogger(__name__)


def _json_body(request: HttpRequest) -> dict:
    return json.loads(request.body or "{}")


def _error_response(message: str, status: int = 500, error_code: str = "ERROR") -> JsonResponse:
    """Standard error response format."""
    return JsonResponse(
        {
            "error": error_code,
            "message": message,
            "status": status,
        },
        status=status,
    )


@require_http_methods(["POST"])
def generate_description_api(request: HttpRequest) -> JsonResponse:
    try:
        data = _json_body(request)
        product_name = data.get("product_name", "").strip()
        category = data.get("category", "").strip()
        price = data.get("price")

        if not all([product_name, category, price]):
            return _error_response(
                "Missing required fields: product_name, category, price",
                status=400,
                error_code="VALIDATION_ERROR",
            )

        try:
            price = float(price)
        except (ValueError, TypeError):
            return _error_response("price must be a valid number", status=400, error_code="VALIDATION_ERROR")

        with get_ai_client() as client:
            description = client.generate_description(product_name, category, price)

        if description is None:
            logger.warning(f"Failed to generate description for {product_name}")
            return _error_response("Failed to generate description", status=502, error_code="AI_SERVICE_ERROR")

        return JsonResponse({"description": description, "product": product_name})
    except Exception as exc:
        logger.error(f"generate_description_api error: {exc}", exc_info=True)
        return _error_response("Internal server error", status=500, error_code="INTERNAL_ERROR")


@require_http_methods(["POST"])
def generate_tags_api(request: HttpRequest) -> JsonResponse:
    try:
        data = _json_body(request)
        product_name = data.get("product_name", "").strip()
        description = data.get("description", "").strip()

        if not product_name:
            return _error_response("product_name is required", status=400, error_code="VALIDATION_ERROR")

        with get_ai_client() as client:
            tags = client.generate_tags(product_name, description)

        if tags is None:
            logger.warning(f"Failed to generate tags for {product_name}")
            return _error_response("Failed to generate tags", status=502, error_code="AI_SERVICE_ERROR")

        return JsonResponse({"tags": tags, "product": product_name})
    except Exception as exc:
        logger.error(f"generate_tags_api error: {exc}", exc_info=True)
        return _error_response("Internal server error", status=500, error_code="INTERNAL_ERROR")


@require_http_methods(["POST"])
def get_recommendations_api(request: HttpRequest) -> JsonResponse:
    try:
        data = _json_body(request)
        user_preference = data.get("user_preference", "").strip()
        category = data.get("category", "").strip()
        count = int(data.get("count", 5))

        if not user_preference:
            return _error_response("user_preference is required", status=400, error_code="VALIDATION_ERROR")

        if count < 1 or count > 50:
            return _error_response("count must be between 1 and 50", status=400, error_code="VALIDATION_ERROR")

        with get_ai_client() as client:
            recommendations = client.get_recommendations(user_preference, category, count)

        if recommendations is None:
            logger.warning(f"Failed to get recommendations for preference: {user_preference}")
            return _error_response("Failed to get recommendations", status=502, error_code="AI_SERVICE_ERROR")

        return JsonResponse({
            "recommendations": recommendations,
            "count": len(recommendations),
            "user_preference": user_preference,
        })
    except ValueError as exc:
        logger.warning(f"Invalid count parameter: {exc}")
        return _error_response("count must be a valid integer", status=400, error_code="VALIDATION_ERROR")
    except Exception as exc:
        logger.error(f"get_recommendations_api error: {exc}", exc_info=True)
        return _error_response("Internal server error", status=500, error_code="INTERNAL_ERROR")


@require_http_methods(["POST"])
def get_similar_products_api(request: HttpRequest) -> JsonResponse:
    try:
        data = _json_body(request)
        product_name = data.get("product_name", "").strip()
        count = int(data.get("count", 3))

        if not product_name:
            return _error_response("product_name is required", status=400, error_code="VALIDATION_ERROR")

        if count < 1 or count > 50:
            return _error_response("count must be between 1 and 50", status=400, error_code="VALIDATION_ERROR")

        with get_ai_client() as client:
            similar_products = client.get_similar_products(product_name, count)

        if similar_products is None:
            logger.warning(f"Failed to get similar products for: {product_name}")
            return _error_response("Failed to get similar products", status=502, error_code="AI_SERVICE_ERROR")

        return JsonResponse({
            "similar_products": similar_products,
            "count": len(similar_products),
            "base_product": product_name,
        })
    except ValueError as exc:
        logger.warning(f"Invalid count parameter: {exc}")
        return _error_response("count must be a valid integer", status=400, error_code="VALIDATION_ERROR")
    except Exception as exc:
        logger.error(f"get_similar_products_api error: {exc}", exc_info=True)
        return _error_response("Internal server error", status=500, error_code="INTERNAL_ERROR")


def ai_service_status(request: HttpRequest) -> JsonResponse:
    """Check if AI service is available."""
    try:
        with get_ai_client() as client:
            available = client.is_available()
        return JsonResponse({
            "service": "ai-platform",
            "available": available,
            "status": "operational" if available else "degraded",
        })
    except Exception as exc:
        logger.error(f"ai_service_status error: {exc}", exc_info=True)
        return JsonResponse({
            "service": "ai-platform",
            "available": False,
            "status": "error",
        }, status=500)
