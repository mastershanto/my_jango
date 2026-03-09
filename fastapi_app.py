"""
FastAPI application for AI-powered features integrated with Django.
Run this separately from Django with: uvicorn fastapi_app:app --reload --port 8001
"""

import os
from contextlib import asynccontextmanager

import django
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Import services
from services.ml_service import (
    generate_product_description_local,
    generate_product_tags_local,
)
from services.openai_service import (
    generate_product_description_openai,
    generate_product_tags_openai,
)
from services.openai_recommendation_service import (
    get_product_recommendations_openai,
    get_similar_products_openai,
    get_recommendation_reasoning_openai,
)
from services.recommendation_service import (
    get_product_recommendations_local,
    get_similar_products_local,
    get_category_recommendations_local,
    get_trending_products_local,
)


# Pydantic models for request/response
class ProductDescriptionRequest(BaseModel):
    product_name: str
    category: str
    price: float


class ProductTagsRequest(BaseModel):
    product_name: str
    description: str = ""


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
    user_preference: str
    category: str = ""
    count: int = 5


class SimilarProductsRequest(BaseModel):
    product_name: str
    count: int = 3


class CategoryRequest(BaseModel):
    category: str
    count: int = 5


# Lifespan event for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("FastAPI server starting...")
    yield
    # Shutdown
    print("FastAPI server shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Cloth Store AI Service",
    description="AI-powered API for product descriptions and tagging",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware for Django integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Check if API is running."""
    return {"status": "healthy", "service": "Cloth Store AI Service"}


# OpenAI endpoints
@app.post(
    "/ai/openai/description", response_model=DescriptionResponse, tags=["OpenAI"]
)
async def generate_description_openai(request: ProductDescriptionRequest):
    """Generate product description using OpenAI GPT model."""
    try:
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key not configured. Set OPENAI_API_KEY in .env",
            )

        description = await generate_product_description_openai(
            request.product_name, request.category, request.price
        )

        return DescriptionResponse(description=description, model_used="OpenAI GPT-3.5")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai/openai/tags", response_model=TagsResponse, tags=["OpenAI"])
async def generate_tags_openai(request: ProductTagsRequest):
    """Generate SEO tags using OpenAI."""
    try:
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key not configured. Set OPENAI_API_KEY in .env",
            )

        tags = await generate_product_tags_openai(
            request.product_name, request.description
        )

        return TagsResponse(tags=tags, model_used="OpenAI GPT-3.5")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Local ML Model endpoints
@app.post(
    "/ai/local/description",
    response_model=DescriptionResponse,
    tags=["Local ML Model"],
)
async def generate_description_local(request: ProductDescriptionRequest):
    """Generate product description using local ML model (no API key needed)."""
    try:
        description = await generate_product_description_local(
            request.product_name, request.category, request.price
        )

        return DescriptionResponse(
            description=description, model_used="Local DistilGPT-2"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai/local/tags", response_model=TagsResponse, tags=["Local ML Model"])
async def generate_tags_local(request: ProductTagsRequest):
    """Generate tags using local ML model (no API key needed)."""
    try:
        tags = await generate_product_tags_local(request.product_name)

        return TagsResponse(tags=tags, model_used="Local DistilGPT-2")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# OpenAI Recommendation endpoints
@app.post(
    "/ai/openai/recommendations",
    response_model=RecommendationResponse,
    tags=["OpenAI Recommendations"],
)
async def recommend_products_openai(request: RecommendationRequest):
    """Get product recommendations using OpenAI based on user preferences."""
    try:
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key not configured. Set OPENAI_API_KEY in .env",
            )

        recommendations = await get_product_recommendations_openai(
            request.user_preference, request.category, request.count
        )

        # Convert to response format
        items = [
            RecommendationItem(
                product_name=rec.get("product_name", ""),
                category=rec.get("category", ""),
                reasoning=rec.get("reasoning", ""),
            )
            for rec in recommendations
        ]

        return RecommendationResponse(
            recommendations=items, model_used="OpenAI GPT-3.5"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/ai/openai/similar-products",
    response_model=list[str],
    tags=["OpenAI Recommendations"],
)
async def similar_products_openai(request: SimilarProductsRequest):
    """Get similar products using OpenAI."""
    try:
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key not configured. Set OPENAI_API_KEY in .env",
            )

        products = await get_similar_products_openai(
            request.product_name, request.count
        )

        return products

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Local ML Model Recommendation endpoints
@app.post(
    "/ai/local/recommendations",
    response_model=RecommendationResponse,
    tags=["Local ML Recommendations"],
)
async def recommend_products_local(request: RecommendationRequest):
    """Get product recommendations using local ML based on user preferences."""
    try:
        # For demo, create sample products. In production, fetch from Django DB
        sample_products = [
            {
                "id": 1,
                "name": "Blue Denim Jacket",
                "category": "Outerwear",
                "description": "Classic blue denim jacket perfect for layering",
                "price": 89.99,
                "featured": True,
            },
            {
                "id": 2,
                "name": "White T-Shirt",
                "category": "Tops",
                "description": "Simple white cotton t-shirt",
                "price": 19.99,
            },
            {
                "id": 3,
                "name": "Black Jeans",
                "category": "Bottoms",
                "description": "Comfortable black denim jeans",
                "price": 59.99,
                "featured": True,
            },
            {
                "id": 4,
                "name": "Summer T-Shirt",
                "category": "Tops",
                "description": "Lightweight summer t-shirt",
                "price": 24.99,
            },
            {
                "id": 5,
                "name": "Casual Sneakers",
                "category": "Footwear",
                "description": "Comfortable casual sneakers",
                "price": 79.99,
            },
        ]

        recommendations = await get_product_recommendations_local(
            request.user_preference, sample_products, request.count
        )

        # Convert to response format
        items = [
            RecommendationItem(
                product_name=rec.get("product_name", ""),
                category=rec.get("category", ""),
                reasoning=rec.get("reasoning", ""),
                similarity_score=rec.get("similarity_score", 0),
            )
            for rec in recommendations
        ]

        return RecommendationResponse(
            recommendations=items, model_used="Local DistilBERT + ML"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/ai/local/similar-products",
    response_model=RecommendationResponse,
    tags=["Local ML Recommendations"],
)
async def similar_products_local(request: SimilarProductsRequest):
    """Get similar products using local ML."""
    try:
        # Sample product to find similar items for
        base_product = {"name": request.product_name, "category": "General"}

        # Sample products database
        products = [
            {
                "id": 1,
                "name": "Blue Denim Jacket",
                "category": "Outerwear",
                "description": "Classic blue denim jacket",
            },
            {
                "id": 2,
                "name": "Black Denim Jacket",
                "category": "Outerwear",
                "description": "Black denim jacket",
            },
            {
                "id": 3,
                "name": "Leather Jacket",
                "category": "Outerwear",
                "description": "Classic leather jacket",
            },
        ]

        similar = await get_similar_products_local(base_product, products, request.count)

        # Convert to response format
        items = [
            RecommendationItem(
                product_name=s.get("product_name", ""),
                category=s.get("category", ""),
                reasoning=s.get("reasoning", ""),
                similarity_score=s.get("similarity_score", 0),
            )
            for s in similar
        ]

        return RecommendationResponse(
            recommendations=items, model_used="Local DistilBERT + ML"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/ai/local/category-recommendations",
    response_model=RecommendationResponse,
    tags=["Local ML Recommendations"],
)
async def category_recommendations(request: CategoryRequest):
    """Get recommendations based on category."""
    try:
        # Sample products
        products = [
            {"id": 1, "name": "Blue Denim Jacket", "category": "Outerwear", "price": 89.99, "featured": True},
            {"id": 2, "name": "Black Denim Jacket", "category": "Outerwear", "price": 79.99},
            {"id": 3, "name": "White T-Shirt", "category": "Tops", "price": 19.99, "featured": True},
            {"id": 4, "name": "Summer T-Shirt", "category": "Tops", "price": 24.99},
        ]

        recommendations = await get_category_recommendations_local(
            request.category, products, request.count
        )

        items = [
            RecommendationItem(
                product_name=rec.get("product_name", ""),
                category=rec.get("category", ""),
                reasoning=rec.get("reasoning", ""),
            )
            for rec in recommendations
        ]

        return RecommendationResponse(
            recommendations=items, model_used="Local ML Category Filter"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """FastAPI root endpoint with documentation."""
    return {
        "message": "Cloth Store AI Service API",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "endpoints": {
            "health": "/health",
            "openai_description": "POST /ai/openai/description",
            "openai_tags": "POST /ai/openai/tags",
            "openai_recommendations": "POST /ai/openai/recommendations",
            "openai_similar": "POST /ai/openai/similar-products",
            "local_description": "POST /ai/local/description",
            "local_tags": "POST /ai/local/tags",
            "local_recommendations": "POST /ai/local/recommendations",
            "local_similar": "POST /ai/local/similar-products",
            "local_category": "POST /ai/local/category-recommendations",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "fastapi_app:app",
        host=os.getenv("FASTAPI_HOST", "127.0.0.1"),
        port=int(os.getenv("FASTAPI_PORT", 8001)),
        reload=True,
    )
