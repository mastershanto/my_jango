"""Local recommendation services backed by embeddings and catalog metadata."""

from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
# Load a simple pretrained model for text similarity
try:
    tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
    model = AutoModel.from_pretrained("distilbert-base-uncased")
    model.eval()
except Exception:
    tokenizer = None
    model = None


def _get_text_embedding(text: str) -> np.ndarray:
    """Get embedding for text using DistilBERT."""
    if tokenizer is None or model is None:
        # Fallback: simple keyword-based scoring
        return np.array([len(text)])

    try:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
        with torch.no_grad():
            outputs = model(**inputs)

        # Use mean pooling of last hidden state
        last_hidden = outputs.last_hidden_state
        embeddings = torch.mean(last_hidden, dim=1)

        return embeddings[0].numpy()
    except Exception:
        return np.array([len(text)])


def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors."""
    if len(vec1) == 0 or len(vec2) == 0:
        return 0.0

    dot_product = np.dot(vec1, vec2)
    norm_product = np.linalg.norm(vec1) * np.linalg.norm(vec2)

    if norm_product == 0:
        return 0.0

    return dot_product / norm_product


def get_product_recommendations_local(
    user_preference: str, products: list[dict], count: int = 5
) -> list[dict]:
    """
    Get product recommendations using local ML based on user preferences.

    Args:
        user_preference: Description of what user is looking for
        products: List of available products with 'name', 'category', 'description'
        count: Number of recommendations to return

    Returns:
        List of recommended products with similarity scores
    """
    if not products:
        return []

    user_embedding = _get_text_embedding(user_preference.lower())
    scored_products = []
    for product in products:
        product_text = (
            f"{product.get('name', '')} "
            f"{product.get('category', '')} "
            f"{product.get('description', '')}"
        )
        product_embedding = _get_text_embedding(product_text.lower())
        similarity = _cosine_similarity(user_embedding, product_embedding)
        category_bonus = 0.1 if product.get("category", "").lower() in user_preference.lower() else 0.0
        scored_products.append({"product": product, "score": similarity + category_bonus})

    sorted_products = sorted(scored_products, key=lambda item: item["score"], reverse=True)
    return [
        {
            "product_name": item["product"].get("name", "Unknown"),
            "category": item["product"].get("category", "Unknown"),
            "description": item["product"].get("description", ""),
            "similarity_score": round(item["score"], 3),
            "reasoning": f"Matches your preference for {user_preference}",
        }
        for item in sorted_products[:count]
    ]


def get_similar_products_local(
    product: dict, products: list[dict], count: int = 3
) -> list[dict]:
    """
    Find similar products based on a given product.
    Uses content-based filtering.
    """
    if not products:
        return []

    target_text = f"{product.get('name', '')} {product.get('category', '')} {product.get('description', '')}"
    target_embedding = _get_text_embedding(target_text.lower())
    similarity_scores = []

    for other_product in products:
        if other_product.get("id") == product.get("id"):
            continue
        other_text = f"{other_product.get('name', '')} {other_product.get('category', '')} {other_product.get('description', '')}"
        other_embedding = _get_text_embedding(other_text.lower())
        similarity = _cosine_similarity(target_embedding, other_embedding)
        category_bonus = 0.15 if other_product.get("category", "").lower() == product.get("category", "").lower() else 0.0
        similarity_scores.append({"product": other_product, "score": similarity + category_bonus})

    sorted_similar = sorted(similarity_scores, key=lambda item: item["score"], reverse=True)
    return [
        {
            "product_name": item["product"].get("name", "Unknown"),
            "category": item["product"].get("category", "Unknown"),
            "similarity_score": round(item["score"], 3),
            "reasoning": "Similar style and category",
        }
        for item in sorted_similar[:count]
    ]


def get_category_recommendations_local(
    category: str, products: list[dict], count: int = 5
) -> list[dict]:
    """
    Get recommendations based on category.
    Returns popular/featured products from that category.
    """
    category_products = [
        product for product in products if product.get("category", "").lower() == category.lower()
    ]
    if not category_products:
        return []
    sorted_products = sorted(
        category_products,
        key=lambda product: (product.get("featured", False), float(product.get("price", 0))),
        reverse=True,
    )
    return [
        {
            "product_name": product.get("name", "Unknown"),
            "category": product.get("category", "Unknown"),
            "price": float(product.get("price", 0)),
            "reasoning": f"Popular in {category}",
        }
        for product in sorted_products[:count]
    ]


def get_trending_products_local(
    products: list[dict], count: int = 5
) -> list[dict]:
    """
    Get trending products (highest rated, most featured).
    """
    sorted_products = sorted(
        products,
        key=lambda product: (
            product.get("featured", False),
            -abs(float(product.get("price", 0)) - 50),
        ),
        reverse=True,
    )
    return [
        {
            "product_name": product.get("name", "Unknown"),
            "category": product.get("category", "Unknown"),
            "price": float(product.get("price", 0)),
            "featured": product.get("featured", False),
            "reasoning": "Trending now",
        }
        for product in sorted_products[:count]
    ]
