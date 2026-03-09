"""OpenAI-backed recommendation services."""

from __future__ import annotations

from .openai_service import get_openai_client
from .config import get_ai_settings
from .product_catalog import list_available_products


def get_product_recommendations_openai(
    user_preference: str, category: str = "", count: int = 5
) -> list[dict]:
    """Get product recommendations grounded in the live product catalog."""
    settings = get_ai_settings()
    catalog_rows = list_available_products(category)
    catalog_text = "\n".join(
        f"- {row['name']} | {row['category']} | ${row['price']} | {row['short_description']}"
        for row in catalog_rows[:50]
    )
    prompt = f"""You are a fashion recommendation expert.

User preference: {user_preference}
Requested category: {category or 'any'}
Available products:
{catalog_text}

Pick the best {count} products from the available products only.
Return one recommendation per line in this exact format:
[Product Name] | [Category] | [Reasoning]"""

    response = get_openai_client().chat.completions.create(
        model=settings.openai_model,
        messages=[
            {
                "role": "system",
                "content": "Only recommend from the provided catalog.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=500,
        temperature=0.4,
    )
    recommendations_text = response.choices[0].message.content or ""
    return _parse_recommendations(recommendations_text.strip())


def get_recommendation_reasoning_openai(
    product_name: str, user_preference: str
) -> str:
    """Get detailed recommendation reasoning."""
    settings = get_ai_settings()
    prompt = f"""Explain in 2-3 sentences why {product_name} matches this preference: {user_preference}."""
    response = get_openai_client().chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": "You are a fashion recommendation expert."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=120,
        temperature=0.5,
    )
    content = response.choices[0].message.content or ""
    return content.strip()


def get_similar_products_openai(product_name: str, count: int = 3) -> list[str]:
    """Get similar products from the live product catalog."""
    settings = get_ai_settings()
    catalog_text = "\n".join(
        f"- {row['name']} | {row['category']} | {row['short_description']}"
        for row in list_available_products()[:50]
    )
    prompt = f"""Using the catalog below, return {count} products similar to {product_name}.

Catalog:
{catalog_text}

Return only product names, one per line."""
    response = get_openai_client().chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": "Only return names from the catalog."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=120,
        temperature=0.3,
    )
    content = response.choices[0].message.content or ""
    return [line.strip("- ").strip() for line in content.split("\n") if line.strip()][:count]


def _parse_recommendations(text: str) -> list[dict]:
    """Parse recommendation text into structured format."""
    recommendations = []

    for line in text.split("\n"):
        line = line.strip()
        if not line or line.startswith("```"):
            continue

        # Remove leading bullet points or numbers
        if line.startswith(("- ", "* ", "+ ")):
            line = line[2:]

        # Parse format: [Product] | [Category] | [Reasoning]
        if "|" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3:
                product_name = parts[0].replace("[", "").replace("]", "").strip()
                category = parts[1].replace("[", "").replace("]", "").strip()
                reasoning = parts[2].replace("[", "").replace("]", "").strip()

                if product_name and category:
                    recommendations.append({
                        "product_name": product_name,
                        "category": category,
                        "reasoning": reasoning,
                    })

    return recommendations
