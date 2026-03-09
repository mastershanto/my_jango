from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from ai_backend.schemas import (
    CategoryRequest,
    RecommendationItem,
    RecommendationRequest,
    RecommendationResponse,
    SimilarProductsRequest,
)
from services.config import get_ai_settings
from services.openai_recommendation_service import (
    get_product_recommendations_openai,
    get_similar_products_openai,
)
from services.product_catalog import get_product_by_name, list_available_products
from services.recommendation_service import (
    get_category_recommendations_local,
    get_product_recommendations_local,
    get_similar_products_local,
)

router = APIRouter(prefix="/ai", tags=["recommendations"])


def _to_items(rows: list[dict]) -> list[RecommendationItem]:
    return [
        RecommendationItem(
            product_name=row.get("product_name", ""),
            category=row.get("category", ""),
            reasoning=row.get("reasoning", ""),
            similarity_score=float(row.get("similarity_score", 0.0) or 0.0),
        )
        for row in rows
    ]


@router.post("/openai/recommendations", response_model=RecommendationResponse)
def openai_recommendations(request: RecommendationRequest) -> RecommendationResponse:
    settings = get_ai_settings()
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OpenAI API key not configured.",
        )

    recommendations = get_product_recommendations_openai(
        request.user_preference,
        category=request.category,
        count=request.count,
    )
    return RecommendationResponse(
        recommendations=_to_items(recommendations),
        model_used=settings.openai_model,
    )


@router.post("/openai/similar-products", response_model=list[str])
def openai_similar_products(request: SimilarProductsRequest) -> list[str]:
    settings = get_ai_settings()
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OpenAI API key not configured.",
        )
    return get_similar_products_openai(request.product_name, request.count)


@router.post("/local/recommendations", response_model=RecommendationResponse)
def local_recommendations(request: RecommendationRequest) -> RecommendationResponse:
    products = list_available_products(request.category)
    recommendations = get_product_recommendations_local(
        request.user_preference,
        products,
        count=request.count,
    )
    return RecommendationResponse(
        recommendations=_to_items(recommendations),
        model_used="distilbert-content-based",
    )


@router.post("/local/similar-products", response_model=RecommendationResponse)
def local_similar_products(request: SimilarProductsRequest) -> RecommendationResponse:
    product = get_product_by_name(request.product_name)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    products = list_available_products(product["category"])
    recommendations = get_similar_products_local(product, products, request.count)
    return RecommendationResponse(
        recommendations=_to_items(recommendations),
        model_used="distilbert-content-based",
    )


@router.post("/local/category-recommendations", response_model=RecommendationResponse)
def local_category_recommendations(request: CategoryRequest) -> RecommendationResponse:
    products = list_available_products(request.category)
    recommendations = get_category_recommendations_local(
        request.category,
        products,
        request.count,
    )
    return RecommendationResponse(
        recommendations=_to_items(recommendations),
        model_used="catalog-ranking",
    )
