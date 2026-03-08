from typing import Sequence, Union, Callable, Any

from django.contrib import admin
from .models import User, Product


@admin.register(User)
class UserAdmin(admin.ModelAdmin[User]):
    list_display: Sequence[Union[str, Callable[[User], Any]]] = [
        "name", "email", "phone", "created_at"
    ]
    list_filter: Sequence[
        Union[
            str,
            type[admin.ListFilter],
            tuple[str, type[admin.ListFilter]],
        ]
    ] = ["created_at"]
    search_fields: Sequence[str] = ["name", "email", "phone"]
    readonly_fields: Sequence[Union[str, Callable[[User], Any]]] = [
        "created_at", "updated_at"
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin[Product]):
    list_display: Sequence[Union[str, Callable[[Product], Any]]] = [
        "title", "price", "stock", "created_at",
    ]
    list_filter: Sequence[
        Union[
            str,
            type[admin.ListFilter],
            tuple[str, type[admin.ListFilter]],
        ]
    ] = ["created_at", "price"]
    search_fields: Sequence[str] = ["title", "description"]
    readonly_fields: Sequence[Union[str, Callable[[Product], Any]]] = [
        "created_at",
    ]
