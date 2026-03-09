from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from ai_backend.schemas import (
    DescriptionResponse,
    ProductDescriptionRequest,
    ProductTagsRequest,
    TagsResponse,
)
from services.config import get_ai_settings
from services import openai_service

router = APIRouter(prefix="/ai", tags=["content-generation"])


@router.post("/generate/description", response_model=DescriptionResponse)
def generate_description(request: ProductDescriptionRequest) -> DescriptionResponse:
    settings = get_ai_settings()
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OpenAI API key not configured.",
        )
    description = openai_service.generate_product_description_openai(
        request.product_name,
        request.category,
        request.price,
    )
    return DescriptionResponse(description=description, model_used=settings.openai_model)


@router.post("/generate/tags", response_model=TagsResponse)
def generate_tags(request: ProductTagsRequest) -> TagsResponse:
    settings = get_ai_settings()
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OpenAI API key not configured.",
        )
    tags = openai_service.generate_product_tags_openai(request.product_name, request.description)
    return TagsResponse(tags=tags, model_used=settings.openai_model)
