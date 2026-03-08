from django.contrib import admin

from .models import Category, Order, OrderItem, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ("name", "slug", "created_at")
	prepopulated_fields = {"slug": ("name",)}
	search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ("name", "category", "price", "stock", "available", "featured")
	list_filter = ("category", "available", "featured")
	list_editable = ("price", "stock", "available", "featured")
	prepopulated_fields = {"slug": ("name",)}
	search_fields = ("name", "fabric", "short_description")


class OrderItemInline(admin.TabularInline):
	model = OrderItem
	extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ("id", "customer_name", "customer_email", "phone", "city", "status", "created_at")
	list_filter = ("status", "created_at")
	search_fields = ("customer_name", "customer_email", "phone", "city")
	inlines = [OrderItemInline]
