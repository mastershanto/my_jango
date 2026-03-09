"""
Example: Using FastAPI AI services in Django views.
Copy these patterns to your actual views.py to enable AI features.
"""

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods

from clothstore.models import Product
from services import get_ai_client


def product_detail_with_ai(request, product_id):
    """
    Example product detail view that generates AI description on the fly.
    """
    product = get_object_or_404(Product, id=product_id)

    # Generate AI description if not already present
    if not product.description:
        with get_ai_client() as client:
            # Try OpenAI first, fallback to local model
            description = client.generate_description_openai(
                product.name, product.category.name, product.price
            )

            if not description:
                description = client.generate_description_local(
                    product.name, product.category.name, product.price
                )

            # Optionally save to database
            if description:
                product.description = description
                product.save()

    context = {"product": product}
    return render(request, "clothstore/product_detail.html", context)


@require_http_methods(["POST"])
def generate_description_api(request):
    """
    API endpoint to generate product description.
    Call this from JavaScript: POST /api/generate-description/
    """
    import json

    try:
        data = json.loads(request.body)
        product_name = data.get("product_name")
        category = data.get("category")
        price = data.get("price")
        use_openai = data.get("use_openai", False)

        if not all([product_name, category, price]):
            return JsonResponse(
                {"error": "Missing required fields"},
                status=400,
            )

        with get_ai_client() as client:
            if use_openai:
                description = client.generate_description_openai(
                    product_name, category, price
                )
                model = "OpenAI"
            else:
                description = client.generate_description_local(
                    product_name, category, price
                )
                model = "Local ML"

            if description:
                return JsonResponse(
                    {"description": description, "model": model}
                )
            else:
                return JsonResponse(
                    {"error": "Failed to generate description"},
                    status=500,
                )

    except Exception as e:
        return JsonResponse(
            {"error": str(e)},
            status=500,
        )


@require_http_methods(["POST"])
def generate_tags_api(request):
    """
    API endpoint to generate product tags.
    Call this from JavaScript: POST /api/generate-tags/
    """
    import json

    try:
        data = json.loads(request.body)
        product_name = data.get("product_name")
        description = data.get("description", "")
        use_openai = data.get("use_openai", False)

        if not product_name:
            return JsonResponse(
                {"error": "product_name required"},
                status=400,
            )

        with get_ai_client() as client:
            if use_openai:
                tags = client.generate_tags_openai(product_name, description)
                model = "OpenAI"
            else:
                tags = client.generate_tags_local(product_name)
                model = "Local ML"

            if tags:
                return JsonResponse(
                    {"tags": tags, "model": model}
                )
            else:
                return JsonResponse(
                    {"error": "Failed to generate tags"},
                    status=500,
                )

    except Exception as e:
        return JsonResponse(
            {"error": str(e)},
            status=500,
        )


def ai_service_status(request):
    """
    Check if FastAPI AI service is running.
    """
    with get_ai_client() as client:
        is_available = client.is_service_available()

    return JsonResponse(
        {
            "service": "AI Service",
            "status": "running" if is_available else "offline",
            "available": is_available,
        }
    )


# Product Recommendation Examples


@require_http_methods(["POST"])
def get_recommendations_api(request):
    """
    API endpoint to get product recommendations.
    Call this from JavaScript: POST /api/recommendations/
    
    Request body:
    {
        "user_preference": "I want a casual summer outfit",
        "category": "Tops",  # optional
        "count": 5,
        "use_openai": true
    }
    """
    import json

    try:
        data = json.loads(request.body)
        user_preference = data.get("user_preference")
        category = data.get("category", "")
        count = data.get("count", 5)
        use_openai = data.get("use_openai", False)

        if not user_preference:
            return JsonResponse(
                {"error": "user_preference required"},
                status=400,
            )

        with get_ai_client() as client:
            if use_openai:
                recommendations = client.get_recommendations_openai(
                    user_preference, category, count
                )
                model = "OpenAI GPT-3.5"
            else:
                recommendations = client.get_recommendations_local(
                    user_preference, category, count
                )
                model = "Local ML"

            if recommendations:
                return JsonResponse(
                    {
                        "recommendations": recommendations,
                        "model": model,
                        "count": len(recommendations),
                    }
                )
            else:
                return JsonResponse(
                    {"error": "Failed to get recommendations"},
                    status=500,
                )

    except Exception as e:
        return JsonResponse(
            {"error": str(e)},
            status=500,
        )


@require_http_methods(["POST"])
def get_similar_products_api(request):
    """
    API endpoint to get similar products.
    Call this from JavaScript: POST /api/similar-products/
    
    Request body:
    {
        "product_name": "Blue Denim Jacket",
        "count": 3,
        "use_openai": true
    }
    """
    import json

    try:
        data = json.loads(request.body)
        product_name = data.get("product_name")
        count = data.get("count", 3)
        use_openai = data.get("use_openai", False)

        if not product_name:
            return JsonResponse(
                {"error": "product_name required"},
                status=400,
            )

        with get_ai_client() as client:
            if use_openai:
                similar = client.get_similar_products_openai(product_name, count)
                model = "OpenAI GPT-3.5"
            else:
                similar = client.get_similar_products_local(product_name, count)
                model = "Local ML"

            if similar:
                return JsonResponse(
                    {
                        "similar_products": similar,
                        "model": model,
                    }
                )
            else:
                return JsonResponse(
                    {"error": "Failed to get similar products"},
                    status=500,
                )

    except Exception as e:
        return JsonResponse(
            {"error": str(e)},
            status=500,
        )


@require_http_methods(["GET", "POST"])
def category_recommendations_api(request):
    """
    API endpoint to get category-based recommendations.
    
    GET: /api/category-recommendations/?category=Tops&count=5
    """
    try:
        if request.method == "GET":
            category = request.GET.get("category", "Tops")
            count = int(request.GET.get("count", 5))
        else:
            import json
            data = json.loads(request.body)
            category = data.get("category", "Tops")
            count = data.get("count", 5)

        with get_ai_client() as client:
            recommendations = client.get_category_recommendations(category, count)

            if recommendations:
                return JsonResponse(
                    {
                        "category": category,
                        "recommendations": recommendations,
                        "model": "Local ML Category Filter",
                    }
                )
            else:
                return JsonResponse(
                    {"error": f"No products found in category {category}"},
                    status=404,
                )

    except Exception as e:
        return JsonResponse(
            {"error": str(e)},
            status=500,
        )


def product_recommendations_page(request):
    """
    Example page showing product recommendations.
    """
    categories = ["Tops", "Bottoms", "Outerwear", "Footwear", "Accessories"]
    
    context = {
        "categories": categories,
        "title": "Smart Recommendations",
    }
    
    return render(request, "clothstore/recommendations.html", context)
