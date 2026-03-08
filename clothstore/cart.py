from decimal import Decimal

from django.http import HttpRequest

from .models import Product


class Cart:
    session_key = "cart"

    def __init__(self, request: HttpRequest) -> None:
        self.session = request.session
        self._cart: dict[str, int] = self.session.get(self.session_key, {})

    def add(self, product_id: int, quantity: int = 1) -> None:
        key = str(product_id)
        self._cart[key] = self._cart.get(key, 0) + quantity
        self.save()

    def update(self, product_id: int, quantity: int) -> None:
        key = str(product_id)
        if quantity <= 0:
            self._cart.pop(key, None)
        else:
            self._cart[key] = quantity
        self.save()

    def remove(self, product_id: int) -> None:
        self._cart.pop(str(product_id), None)
        self.save()

    def clear(self) -> None:
        self.session.pop(self.session_key, None)
        self.session.modified = True
        self._cart = {}

    def save(self) -> None:
        self.session[self.session_key] = self._cart
        self.session.modified = True

    @property
    def items(self) -> list[dict[str, object]]:
        product_ids = [int(product_id) for product_id in self._cart.keys()]
        products = Product.objects.filter(id__in=product_ids)
        product_map = {product.id: product for product in products}
        items: list[dict[str, object]] = []

        for product_id, quantity in self._cart.items():
            product = product_map.get(int(product_id))
            if product is None:
                continue
            line_total = product.price * quantity
            items.append(
                {
                    "product": product,
                    "quantity": quantity,
                    "line_total": line_total,
                }
            )
        return items

    @property
    def count(self) -> int:
        return sum(self._cart.values())

    @property
    def subtotal(self) -> Decimal:
        return sum((item["line_total"] for item in self.items), Decimal("0.00"))
