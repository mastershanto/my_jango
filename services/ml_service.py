from transformers import pipeline

# Load text generation model (runs locally, no API key needed)
text_generator = pipeline(
    "text-generation",
    model="distilgpt2",  # Lightweight model suitable for CPU
    device=-1,  # Use CPU (-1) or GPU (0 if available)
)


async def generate_product_description_local(
    product_name: str, category: str, price: float
) -> str:
    """Generate product description using local ML model."""
    try:
        prompt = f"Product: {product_name} in {category} category priced at ${price}. Description: This is a"

        result = text_generator(
            prompt,
            max_length=100,
            num_return_sequences=1,
            temperature=0.7,
            top_p=0.95,
            do_sample=True,
        )

        generated_text = result[0]["generated_text"]
        # Remove the prompt from the generated text
        description = generated_text.replace(prompt, "").strip()

        if not description:
            description = f"High-quality {product_name} in {category}. Perfect for any occasion. Priced at ${price}."

        return description

    except Exception as e:
        raise Exception(f"Local ML model error: {str(e)}")


async def generate_product_tags_local(product_name: str) -> list[str]:
    """Generate tags using local ML model."""
    try:
        prompt = f"Generate keywords for: {product_name}. Tags:"

        result = text_generator(
            prompt,
            max_length=50,
            num_return_sequences=1,
            temperature=0.5,
        )

        generated_text = result[0]["generated_text"]
        # Extract tags
        tags_part = generated_text.replace(prompt, "").strip()

        # Simple extraction of tag-like words
        tags = [
            word.strip()
            for word in tags_part.split(",")
            if len(word.strip()) > 2 and len(word.strip()) < 20
        ]

        if not tags:
            tags = [
                "clothing",
                product_name.lower(),
                "apparel",
                "fashion",
                "wear",
            ]

        return tags[:7]

    except Exception as e:
        raise Exception(f"Local ML model error: {str(e)}")
