from __future__ import annotations

from pydantic import BaseModel, Field


class ProductDescriptionRequest(BaseModel):
    product_name: str = Field(..., min_length=2, max_length=150)
    category: str = Field(..., min_length=2, max_length=100)
    price: float = Field(..., gt=0)


class ProductTagsRequest(BaseModel):
    product_name: str = Field(..., min_length=2, max_length=150)
    description: str = Field(default="", max_length=2000)


class DescriptionResponse(BaseModel):
    description: str
    model_used: str


class TagsResponse(BaseModel):
    tags: list[str]
    model_used: str


class RecommendationItem(BaseModel):
    product_name: str
    category: str
    reasoning: str = ""
    similarity_score: float = 0.0


class RecommendationResponse(BaseModel):
    recommendations: list[RecommendationItem]
    model_used: str


class RecommendationRequest(BaseModel):
    user_preference: str = Field(..., min_length=3, max_length=500)
    category: str = Field(default="", max_length=100)
    count: int = Field(default=5, ge=1, le=12)


class SimilarProductsRequest(BaseModel):
    product_name: str = Field(..., min_length=2, max_length=150)
    count: int = Field(default=3, ge=1, le=12)


class CategoryRequest(BaseModel):
    category: str = Field(..., min_length=2, max_length=100)
    count: int = Field(default=5, ge=1, le=12)
