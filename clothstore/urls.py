from django.urls import path

from . import views

app_name = "clothstore"

urlpatterns = [
    path("", views.store_home, name="home"),
    path("products/", views.product_list, name="product_list"),
    path("category/<slug:category_slug>/", views.product_list, name="category_products"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/update/<int:product_id>/", views.cart_update, name="cart_update"),
    path("cart/remove/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("orders/success/<int:order_id>/", views.order_success, name="order_success"),
    path("orders/lookup/", views.order_lookup, name="order_lookup"),
    path("orders/demo/", views.order_demo, name="order_demo"),
]
