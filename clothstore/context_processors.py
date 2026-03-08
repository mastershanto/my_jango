from .cart import Cart


def cart_summary(request):
    cart = Cart(request)
    return {
        "global_cart_count": cart.count,
        "global_cart_total": cart.subtotal,
    }
