from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from ai_backend.schemas import (
    RecommendationItem,
    RecommendationRequest,
    RecommendationResponse,
    SimilarProductsRequest,
)
from services.config import get_ai_settings
from services import openai_recommendation_service

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


@router.post("/recommendations", response_model=RecommendationResponse)
def recommendations(request: RecommendationRequest) -> RecommendationResponse:
    settings = get_ai_settings()
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OpenAI API key not configured.",
        )
    recs = openai_recommendation_service.get_product_recommendations_openai(
        request.user_preference,
        category=request.category,
        count=request.count,
    )
    return RecommendationResponse(
        recommendations=_to_items(recs),
        model_used=settings.openai_model,
    )


@router.post("/similar-products", response_model=RecommendationResponse)
def similar_products(request: SimilarProductsRequest) -> RecommendationResponse:
    settings = get_ai_settings()
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OpenAI API key not configured.",
        )
    similar = openai_recommendation_service.get_similar_products_openai(
        request.product_name, request.count
    )
    # get_similar_products_openai returns list[str] — wrap as RecommendationItems
    items = [
        RecommendationItem(product_name=name, category="", reasoning="", similarity_score=0.0)
        for name in (similar or [])
    ]
    return RecommendationResponse(
        recommendations=items,
        model_used=settings.openai_model,
    )
