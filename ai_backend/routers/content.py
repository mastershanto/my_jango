from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from ai_backend.schemas import (
    DescriptionResponse,
    ProductDescriptionRequest,
    ProductTagsRequest,
    TagsResponse,
)
from services.config import get_ai_settings
from services.ml_service import (
    generate_product_description_local,
    generate_product_tags_local,
)
from services.openai_service import (
    generate_product_description_openai,
    generate_product_tags_openai,
)

router = APIRouter(prefix="/ai", tags=["content-generation"])


@router.post("/openai/description", response_model=DescriptionResponse)
def openai_description(request: ProductDescriptionRequest) -> DescriptionResponse:
    settings = get_ai_settings()
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OpenAI API key not configured.",
        )

    description = generate_product_description_openai(
        request.product_name,
        request.category,
        request.price,
    )
    return DescriptionResponse(description=description, model_used=settings.openai_model)


@router.post("/openai/tags", response_model=TagsResponse)
def openai_tags(request: ProductTagsRequest) -> TagsResponse:
    settings = get_ai_settings()
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OpenAI API key not configured.",
        )

    tags = generate_product_tags_openai(request.product_name, request.description)
    return TagsResponse(tags=tags, model_used=settings.openai_model)


@router.post("/local/description", response_model=DescriptionResponse)
def local_description(request: ProductDescriptionRequest) -> DescriptionResponse:
    description = generate_product_description_local(
        request.product_name,
        request.category,
        request.price,
    )
    return DescriptionResponse(description=description, model_used="distilgpt2")


@router.post("/local/tags", response_model=TagsResponse)
def local_tags(request: ProductTagsRequest) -> TagsResponse:
    tags = generate_product_tags_local(request.product_name)
    return TagsResponse(tags=tags, model_used="distilgpt2")
