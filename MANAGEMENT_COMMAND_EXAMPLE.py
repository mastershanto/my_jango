"""
Django Management Command: Generate AI descriptions for existing products

Usage:
    python manage.py generate_ai_descriptions

Options:
    --model=local       Use local ML model (default)
    --model=openai      Use OpenAI API
    --batch=10          Process 10 products at a time
    --all               Process all products without descriptions

Place this file in: clothstore/management/commands/generate_ai_descriptions.py
Create directories if they don't exist: mkdir -p clothstore/management/commands
"""

from django.core.management.base import BaseCommand
from django.db.models import Q

from clothstore.models import Product
from services import get_ai_client


class Command(BaseCommand):
    help = "Generate AI descriptions for products using FastAPI"

    def add_arguments(self, parser):
        parser.add_argument(
            "--model",
            type=str,
            choices=["local", "openai"],
            default="local",
            help="Which model to use (default: local)",
        )

        parser.add_argument(
            "--batch",
            type=int,
            default=10,
            help="Number of products to process (default: 10)",
        )

        parser.add_argument(
            "--all",
            action="store_true",
            help="Process all products without descriptions",
        )

    def handle(self, *args, **options):
        model = options["model"]
        batch_size = options["batch"]
        process_all = options["all"]

        self.stdout.write(
            self.style.SUCCESS(f"🤖 Starting AI description generation ({model})...")
        )
        self.stdout.write("")

        # Get products without descriptions
        if process_all:
            products = Product.objects.filter(Q(description__isnull=True) | Q(description=""))
        else:
            products = Product.objects.filter(Q(description__isnull=True) | Q(description=""))[
                :batch_size
            ]

        total = products.count()

        if total == 0:
            self.stdout.write(self.style.WARNING("ℹ️  No products found to process"))
            return

        self.stdout.write(f"📝 Processing {total} products...\n")

        processed = 0
        failed = 0

        with get_ai_client() as client:
            for idx, product in enumerate(products, 1):
                try:
                    self.stdout.write(
                        f"[{idx}/{total}] {product.name}... ",
                        ending="",
                    )

                    # Generate description based on chosen model
                    if model == "openai":
                        description = client.generate_description_openai(
                            product.name,
                            product.category.name,
                            float(product.price),
                        )
                    else:  # local
                        description = client.generate_description_local(
                            product.name,
                            product.category.name,
                            float(product.price),
                        )

                    if description:
                        product.description = description
                        product.save()

                        self.stdout.write(
                            self.style.SUCCESS("✅"),
                        )
                        processed += 1
                    else:
                        self.stdout.write(
                            self.style.ERROR("❌ (no description generated)"),
                        )
                        failed += 1

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"❌ Error: {str(e)[:50]}..."),
                    )
                    failed += 1

        # Summary
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(f"✅ Successfully processed: {processed} products")
        self.stdout.write(f"❌ Failed: {failed} products")
        self.stdout.write(f"📊 Total: {total} products")
        self.stdout.write(self.style.SUCCESS("=" * 60))


# Create the directories if needed
# mkdir -p clothstore/management/commands
# touch clothstore/management/__init__.py
# touch clothstore/management/commands/__init__.py
