from typing import Any, Dict

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

from .models import AppUser, Product


def profile(request: HttpRequest) -> HttpResponse:
    """Display user profile page."""
    users: list[AppUser] = AppUser.objects.all()[:5]
    context: Dict[str, Any] = {
        "users": users,
        "page_title": "User Profiles"
    }
    return render(request, 'home.html', context)


def deshboard(request: HttpRequest) -> HttpResponse:
    """Display dashboard with product stats."""
    products: list[Product] = Product.objects.all()
    in_stock: int = Product.objects.filter(stock__gt=0).count()
    total_value: float = sum(float(p.price * p.stock) for p in products)
    
    context: Dict[str, Any] = {
        "products": products,
        "in_stock_count": in_stock,
        "total_products": len(products),
        "inventory_value": total_value,
        "page_title": "Dashboard"
    }
    return render(request, 'dashboard.html', context)


def about(request: HttpRequest) -> HttpResponse:
    """Display about page."""
    context: Dict[str, Any] = {"page_title": "About Us"}
    return render(request, 'about.html', context)
