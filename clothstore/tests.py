from django.test import TestCase
from django.urls import reverse

from .models import Category, Order, Product


class ClothStoreViewTests(TestCase):
	def setUp(self) -> None:
		category = Category.objects.create(name="Test Men", slug="test-men")
		self.product = Product.objects.create(
			category=category,
			name="Test Shirt",
			slug="test-shirt",
			short_description="A simple test product.",
			description="Used for testing the product detail view.",
			fabric="Cotton",
			price="20.00",
			stock=5,
			available=True,
			featured=True,
		)

	def test_home_page_loads(self) -> None:
		response = self.client.get(reverse("clothstore:home"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Learn Django by building a cloth store")

	def test_product_list_page_loads(self) -> None:
		response = self.client.get(reverse("clothstore:product_list"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.product.name)

	def test_product_detail_page_loads(self) -> None:
		response = self.client.get(reverse("clothstore:product_detail", args=[self.product.slug]))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.product.description)

	def test_add_to_cart_and_view_cart(self) -> None:
		self.client.post(reverse("clothstore:cart_add", args=[self.product.id]), {"quantity": 2})
		response = self.client.get(reverse("clothstore:cart_detail"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.product.name)
		self.assertContains(response, "Checkout")

	def test_checkout_creates_order(self) -> None:
		starting_count = Order.objects.count()
		self.client.post(reverse("clothstore:cart_add", args=[self.product.id]), {"quantity": 2})
		response = self.client.post(
			reverse("clothstore:checkout"),
			{
				"customer_name": "Test Customer",
				"customer_email": "customer@example.com",
				"phone": "0123456789",
				"city": "Dhaka",
				"address": "Test Address",
				"notes": "Please call before delivery.",
			},
		)
		self.assertEqual(response.status_code, 302)
		self.assertEqual(Order.objects.count(), starting_count + 1)
		order = Order.objects.get(customer_email="customer@example.com")
		self.assertIsNotNone(order)
		self.assertEqual(order.items.count(), 1)

	def test_order_lookup_finds_customer_orders(self) -> None:
		order = Order.objects.create(
			customer_name="Test Customer",
			customer_email="customer@example.com",
			city="Dhaka",
			address="Street 1",
		)
		order.items.create(product=self.product, quantity=1, price_at_purchase=self.product.price)
		response = self.client.post(reverse("clothstore:order_lookup"), {"email": "customer@example.com"})
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, order.customer_name)
