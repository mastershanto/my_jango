from __future__ import annotations

from typing import Any

from ai_backend.bootstrap import bootstrap_django

bootstrap_django()

from clothstore.models import Product  # noqa: E402


ProductPayload = dict[str, Any]


def serialize_product(product: Product) -> ProductPayload:
    return {
        "id": product.id,
        "name": product.name,
        "slug": product.slug,
        "category": product.category.name,
        "description": product.description or product.short_description,
        "short_description": product.short_description,
        "price": float(product.price),
        "featured": product.featured,
        "available": product.available,
        "stock": product.stock,
    }


def list_available_products(category: str = "") -> list[ProductPayload]:
    queryset = Product.objects.filter(available=True).select_related("category")
    if category:
        queryset = queryset.filter(category__name__iexact=category)
    return [serialize_product(product) for product in queryset]


def get_product_by_name(product_name: str) -> ProductPayload | None:
    product = (
        Product.objects.filter(name__iexact=product_name, available=True)
        .select_related("category")
        .first()
    )
    if product is None:
        return None
    return serialize_product(product)
