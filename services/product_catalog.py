from __future__ import annotations

from typing import Any


def _ensure_django_bootstrapped():
    """Bootstrap Django if not already done."""
    try:
        from django.apps import apps
        if not apps.ready:
            from ai_backend.bootstrap import bootstrap_django
            bootstrap_django()
    except (ImportError, RuntimeError):
        pass


def _get_product_model():
    """Lazy load the Product model."""
    _ensure_django_bootstrapped()
    from clothstore.models import Product
    return Product

ProductPayload = dict[str, Any]


def serialize_product(product) -> ProductPayload:
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
    Product = _get_product_model()
    queryset = Product.objects.filter(available=True).select_related("category")
    if category:
        queryset = queryset.filter(category__name__iexact=category)
    return [serialize_product(product) for product in queryset]


def get_product_by_name(product_name: str) -> ProductPayload | None:
    Product = _get_product_model()
    product = (
        Product.objects.filter(name__iexact=product_name, available=True)
        .select_related("category")
        .first()
    )
    if product is None:
        return None
    return serialize_product(product)
