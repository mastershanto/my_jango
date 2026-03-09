from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db.models import Q

from clothstore.models import Product
from services import get_ai_client


class Command(BaseCommand):
    help = "Generate AI descriptions for products without one."

    def add_arguments(self, parser) -> None:
        parser.add_argument("--model", choices=["local", "openai"], default="local")
        parser.add_argument("--batch", type=int, default=10)
        parser.add_argument("--all", action="store_true")

    def handle(self, *args, **options) -> None:
        model = options["model"]
        batch_size = options["batch"]
        queryset = Product.objects.filter(Q(description__isnull=True) | Q(description=""))
        products = queryset if options["all"] else queryset[:batch_size]

        with get_ai_client() as client:
            for product in products:
                description = (
                    client.generate_description_openai(
                        product.name,
                        product.category.name,
                        float(product.price),
                    )
                    if model == "openai"
                    else client.generate_description_local(
                        product.name,
                        product.category.name,
                        float(product.price),
                    )
                )
                if description:
                    product.description = description
                    product.save(update_fields=["description"])
                    self.stdout.write(self.style.SUCCESS(f"Updated {product.name}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Skipped {product.name}"))
