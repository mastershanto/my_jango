from django.contrib import messages
from django.db import transaction
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .cart import Cart
from .forms import CheckoutForm, OrderLookupForm
from .models import Category, Order, Product


def store_home(request: HttpRequest) -> HttpResponse:
	categories = Category.objects.annotate(product_count=Count("products"))
	featured_products = Product.objects.filter(featured=True, available=True)[:4]
	new_arrivals = Product.objects.filter(available=True)[:6]
	affordable_products = Product.objects.filter(available=True).order_by("price")[:4]

	context = {
		"categories": categories,
		"featured_products": featured_products,
		"new_arrivals": new_arrivals,
		"affordable_products": affordable_products,
		"total_products": Product.objects.count(),
		"total_categories": Category.objects.count(),
		"total_orders": Order.objects.count(),
	}
	return render(request, "clothstore/home.html", context)


def product_list(request: HttpRequest, category_slug: str | None = None) -> HttpResponse:
	categories = Category.objects.all()
	selected_category = None
	query = request.GET.get("q", "").strip()
	products = Product.objects.filter(available=True).select_related("category")

	if category_slug is not None:
		selected_category = get_object_or_404(Category, slug=category_slug)
		products = products.filter(category=selected_category)

	if query:
		products = products.filter(name__icontains=query)

	context = {
		"categories": categories,
		"products": products,
		"selected_category": selected_category,
		"query": query,
	}
	return render(request, "clothstore/product_list.html", context)


def product_detail(request: HttpRequest, slug: str) -> HttpResponse:
	product = get_object_or_404(Product.objects.select_related("category"), slug=slug)
	related_products = Product.objects.filter(category=product.category, available=True).exclude(pk=product.pk)[:3]

	context = {
		"product": product,
		"related_products": related_products,
	}
	return render(request, "clothstore/product_detail.html", context)


def cart_detail(request: HttpRequest) -> HttpResponse:
	cart = Cart(request)
	context = {
		"cart_items": cart.items,
		"cart_count": cart.count,
		"cart_subtotal": cart.subtotal,
	}
	return render(request, "clothstore/cart_detail.html", context)


def cart_add(request: HttpRequest, product_id: int) -> HttpResponse:
	product = get_object_or_404(Product, pk=product_id, available=True)
	try:
		quantity = max(int(request.POST.get("quantity", 1)), 1)
	except (TypeError, ValueError):
		quantity = 1
	quantity = min(quantity, product.stock)
	cart = Cart(request)
	cart.add(product_id=product.id, quantity=quantity)
	messages.success(request, f"Added {product.name} to cart.")
	return redirect(request.POST.get("next") or product.get_absolute_url())


def cart_update(request: HttpRequest, product_id: int) -> HttpResponse:
	product = get_object_or_404(Product, pk=product_id)
	try:
		quantity = max(int(request.POST.get("quantity", 1)), 0)
	except (TypeError, ValueError):
		quantity = 1
	quantity = min(quantity, product.stock)
	cart = Cart(request)
	cart.update(product_id=product.id, quantity=quantity)
	messages.success(request, f"Updated {product.name} quantity.")
	return redirect("clothstore:cart_detail")


def cart_remove(request: HttpRequest, product_id: int) -> HttpResponse:
	product = get_object_or_404(Product, pk=product_id)
	cart = Cart(request)
	cart.remove(product_id=product.id)
	messages.success(request, f"Removed {product.name} from cart.")
	return redirect("clothstore:cart_detail")


@transaction.atomic
def checkout(request: HttpRequest) -> HttpResponse:
	cart = Cart(request)

	if cart.count == 0:
		messages.info(request, "Your cart is empty. Add products before checkout.")
		return redirect("clothstore:product_list")

	if request.method == "POST":
		form = CheckoutForm(request.POST)
		if form.is_valid():
			product_ids = [item["product"].id for item in cart.items]
			locked_products = {
				product.id: product
				for product in Product.objects.select_for_update().filter(id__in=product_ids)
			}

			for item in cart.items:
				product = locked_products[item["product"].id]
				if product.stock < item["quantity"]:
					form.add_error(None, f"Not enough stock for {product.name}. Available quantity: {product.stock}.")
					return render(
						request,
						"clothstore/checkout.html",
						{
							"form": form,
							"cart_items": cart.items,
							"cart_subtotal": cart.subtotal,
						},
					)

			order = Order.objects.create(**form.cleaned_data)

			for item in cart.items:
				product = locked_products[item["product"].id]
				order.items.create(
					product=product,
					quantity=item["quantity"],
					price_at_purchase=item["product"].price,
				)
				product.stock -= item["quantity"]
				if product.stock == 0:
					product.available = False
				product.save(update_fields=["stock", "available"])

			cart.clear()
			messages.success(request, "Your order was placed successfully.")
			return redirect("clothstore:order_success", order_id=order.id)
	else:
		form = CheckoutForm()

	context = {
		"form": form,
		"cart_items": cart.items,
		"cart_subtotal": cart.subtotal,
	}
	return render(request, "clothstore/checkout.html", context)


def order_success(request: HttpRequest, order_id: int) -> HttpResponse:
	order = get_object_or_404(Order.objects.prefetch_related("items__product"), pk=order_id)
	return render(request, "clothstore/order_success.html", {"order": order})


def order_lookup(request: HttpRequest) -> HttpResponse:
	form = OrderLookupForm(request.POST or None)
	orders = None

	if request.method == "POST" and form.is_valid():
		orders = Order.objects.filter(customer_email=form.cleaned_data["email"]).prefetch_related("items__product")

	context = {
		"form": form,
		"orders": orders,
	}
	return render(request, "clothstore/order_lookup.html", context)


def order_demo(request: HttpRequest) -> HttpResponse:
	demo_order = Order.objects.prefetch_related("items__product").first()

	context = {
		"demo_order": demo_order,
	}
	return render(request, "clothstore/order_demo.html", context)
