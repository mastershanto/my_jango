from __future__ import annotations

from functools import lru_cache

from openai import OpenAI

from .config import get_ai_settings


@lru_cache(maxsize=1)
def get_openai_client() -> OpenAI:
    settings = get_ai_settings()
    if not settings.openai_api_key:
        raise ValueError("OpenAI API key is not configured.")
    return OpenAI(api_key=settings.openai_api_key)


def generate_product_description_openai(
    product_name: str,
    category: str,
    price: float,
) -> str:
    """Generate product description using OpenAI."""
    settings = get_ai_settings()
    prompt = f"""Generate a compelling and concise product description for an online clothing store.

Product Name: {product_name}
Category: {category}
Price: ${price}

Write a description that is:
- Engaging and persuasive
- 2-3 sentences maximum
- Focused on style, comfort, and quality
- Suitable for an e-commerce listing"""

    response = get_openai_client().chat.completions.create(
        model=settings.openai_model,
        messages=[
            {
                "role": "system",
                "content": "You are a senior e-commerce copywriter for a fashion brand.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=180,
        temperature=0.7,
    )
    content = response.choices[0].message.content or ""
    return content.strip()


def generate_product_tags_openai(product_name: str, description: str) -> list[str]:
    """Generate SEO tags for a product using OpenAI."""
    settings = get_ai_settings()
    prompt = f"""Generate 5-7 concise SEO tags for this clothing product.

Product Name: {product_name}
Description: {description}

Return only a comma-separated list."""

    response = get_openai_client().chat.completions.create(
        model=settings.openai_model,
        messages=[
            {
                "role": "system",
                "content": "You are an SEO specialist for a fashion storefront.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=100,
        temperature=0.4,
    )
    content = response.choices[0].message.content or ""
    return [tag.strip() for tag in content.split(",") if tag.strip()]
