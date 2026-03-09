"""
OpenAI Product Recommendation Service
Uses OpenAI to generate personalized product recommendations based on user preferences.
"""

import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def get_product_recommendations_openai(
    user_preference: str, category: str = "", count: int = 5
) -> list[dict]:
    """
    Get product recommendations using OpenAI based on user preferences.
    
    Args:
        user_preference: Description of what user is looking for (e.g., "casual summer outfit")
        category: Optional category filter (e.g., "Tops", "Bottoms")
        count: Number of recommendations to return (default: 5)
    
    Returns:
        List of product recommendations with name, category, and reasoning
    """
    try:
        category_context = f" in the {category} category" if category else ""
        
        prompt = f"""You are a fashion expert for an online clothing store.
Based on the user's preference, recommend {count} specific clothing products{category_context}.

User's Preference: {user_preference}

For each recommendation, provide:
1. Product name (be specific, like "Blue Denim Jacket" not just "Jacket")
2. Category (e.g., Tops, Bottoms, Outerwear, Accessories)
3. Brief reasoning (1-2 sentences why it matches their preference)

Format each recommendation as:
- [Product Name] | [Category] | [Reasoning]

Provide exactly {count} recommendations, one per line."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful fashion assistant for an online clothing store. Provide specific product recommendations.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
            temperature=0.7,
        )

        recommendations_text = response.choices[0].message.content.strip()
        recommendations = _parse_recommendations(recommendations_text)

        return recommendations

    except Exception as e:
        raise Exception(f"OpenAI recommendation error: {str(e)}")


async def get_recommendation_reasoning_openai(
    product_name: str, user_preference: str
) -> str:
    """
    Get detailed reasoning why a product is recommended for a user.
    """
    try:
        prompt = f"""Explain in 2-3 sentences why the "{product_name}" is a perfect match for someone 
looking for: {user_preference}

Focus on style, comfort, and practical benefits."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a fashion expert providing personalized recommendations.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=150,
            temperature=0.7,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        raise Exception(f"OpenAI reasoning error: {str(e)}")


async def get_similar_products_openai(product_name: str, count: int = 3) -> list[str]:
    """
    Get similar product recommendations based on a product name.
    """
    try:
        prompt = f"""Recommend {count} similar clothing products to "{product_name}".
Return only product names, one per line, without numbering or explanations."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a fashion expert for an online clothing store.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=150,
            temperature=0.6,
        )

        products_text = response.choices[0].message.content.strip()
        products = [p.strip() for p in products_text.split("\n") if p.strip()]

        return products[:count]

    except Exception as e:
        raise Exception(f"OpenAI similar products error: {str(e)}")


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
