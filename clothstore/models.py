from decimal import Decimal

from django.db import models
from django.urls import reverse


class Category(models.Model):
	"""Groups products to keep the storefront simple and organized."""

	name = models.CharField(max_length=100)
	slug = models.SlugField(unique=True)
	description = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["name"]
		verbose_name_plural = "Categories"

	def __str__(self) -> str:
		return self.name


class Product(models.Model):
	"""Simple cloth product model for learning ecommerce basics."""

	category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
	name = models.CharField(max_length=150)
	slug = models.SlugField(unique=True)
	short_description = models.CharField(max_length=220)
	description = models.TextField()
	fabric = models.CharField(max_length=100)
	price = models.DecimalField(max_digits=10, decimal_places=2)
	stock = models.PositiveIntegerField(default=0)
	available = models.BooleanField(default=True)
	featured = models.BooleanField(default=False)
	image_url = models.URLField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-featured", "name"]

	def __str__(self) -> str:
		return self.name

	def get_absolute_url(self) -> str:
		return reverse("clothstore:product_detail", kwargs={"slug": self.slug})

	@property
	def is_in_stock(self) -> bool:
		return self.available and self.stock > 0

	@property
	def stock_label(self) -> str:
		if self.stock == 0:
			return "Out of stock"
		if self.stock <= 5:
			return "Only a few left"
		return "In stock"


class Order(models.Model):
	"""A lightweight order model to demonstrate model relationships."""

	class Status(models.TextChoices):
		PENDING = "pending", "Pending"
		PROCESSING = "processing", "Processing"
		SHIPPED = "shipped", "Shipped"

	customer_name = models.CharField(max_length=120)
	customer_email = models.EmailField()
	phone = models.CharField(max_length=20, blank=True)
	city = models.CharField(max_length=120)
	address = models.CharField(max_length=255)
	notes = models.TextField(blank=True)
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self) -> str:
		return f"Order #{self.pk} - {self.customer_name}"

	@property
	def reference_code(self) -> str:
		return f"CS-{self.pk:05d}"

	@property
	def total_amount(self) -> Decimal:
		return sum((item.line_total for item in self.items.all()), Decimal("0.00"))


class OrderItem(models.Model):
	"""Connects an order with one or more products."""

	order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
	product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="order_items")
	quantity = models.PositiveIntegerField(default=1)
	price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

	class Meta:
		ordering = ["product__name"]

	def __str__(self) -> str:
		return f"{self.quantity} x {self.product.name}"

	@property
	def line_total(self) -> Decimal:
		return self.price_at_purchase * self.quantity
