from __future__ import annotations

from functools import lru_cache

from transformers import pipeline


@lru_cache(maxsize=1)
def get_text_generator():
    return pipeline(
        "text-generation",
        model="distilgpt2",
        device=-1,
    )


def generate_product_description_local(
    product_name: str,
    category: str,
    price: float,
) -> str:
    """Generate product description using a local text model."""
    prompt = (
        f"Product: {product_name}\n"
        f"Category: {category}\n"
        f"Price: ${price}\n"
        "Description:"
    )
    result = get_text_generator()(
        prompt,
        max_length=120,
        num_return_sequences=1,
        temperature=0.7,
        top_p=0.95,
        do_sample=True,
    )
    generated_text = result[0]["generated_text"]
    description = generated_text.replace(prompt, "").strip()
    if description:
        return description
    return (
        f"{product_name} is a quality {category.lower()} option designed for comfort, "
        f"style, and everyday wear at ${price}."
    )


def generate_product_tags_local(product_name: str) -> list[str]:
    """Generate tags using a local text model."""
    prompt = f"Generate concise product tags for {product_name}:"
    result = get_text_generator()(
        prompt,
        max_length=60,
        num_return_sequences=1,
        temperature=0.4,
    )
    generated_text = result[0]["generated_text"]
    tags_part = generated_text.replace(prompt, "").strip()
    tags = [tag.strip() for tag in tags_part.split(",") if 2 < len(tag.strip()) < 24]
    if tags:
        return tags[:7]
    return ["clothing", product_name.lower(), "fashion", "apparel", "style"]
