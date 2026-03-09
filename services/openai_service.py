import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def generate_product_description_openai(product_name: str, category: str, price: float) -> str:
    """Generate product description using OpenAI GPT model."""
    try:
        prompt = f"""Generate a compelling and concise product description for an online clothing store.
        
Product Name: {product_name}
Category: {category}
Price: ${price}

Write a description that is:
- Engaging and persuasive
- 2-3 sentences maximum
- Focuses on style, comfort, and quality
- Suitable for e-commerce listings"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional copywriter for a clothing e-commerce store.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=150,
            temperature=0.7,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        raise Exception(f"OpenAI API error: {str(e)}")


async def generate_product_tags_openai(product_name: str, description: str) -> list[str]:
    """Generate SEO tags for product using OpenAI."""
    try:
        prompt = f"""Generate 5-7 relevant SEO tags for this clothing product.
        
Product Name: {product_name}
Description: {description}

Return only the tags as a comma-separated list, no other text."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an SEO expert for an e-commerce clothing store.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=100,
            temperature=0.5,
        )

        tags_str = response.choices[0].message.content.strip()
        return [tag.strip() for tag in tags_str.split(",")]

    except Exception as e:
        raise Exception(f"OpenAI API error: {str(e)}")
