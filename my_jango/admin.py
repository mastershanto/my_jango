
from django.contrib import admin

from .models import AppUser, Product


@admin.register(AppUser)
class AppUserAdmin(admin.ModelAdmin):  # type: ignore[misc]
    list_display = [
        "name", "email", "phone", "created_at"
    ]
    list_filter = ["created_at"]
    search_fields = ["name", "email", "phone"]
    readonly_fields = [
        "created_at", "updated_at"
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):  # type: ignore[misc]
    list_display = [
        "title", "price", "stock", "created_at"
    ]
    list_filter = [
        "created_at", "price"
    ]
    search_fields = ["title", "description"]
    readonly_fields = [
        "created_at"
    ]

