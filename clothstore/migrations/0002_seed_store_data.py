from decimal import Decimal

from django.db import migrations



def seed_store_data(apps, schema_editor):
    Category = apps.get_model("clothstore", "Category")
    Product = apps.get_model("clothstore", "Product")
    Order = apps.get_model("clothstore", "Order")
    OrderItem = apps.get_model("clothstore", "OrderItem")

    men = Category.objects.create(
        name="Men",
        slug="men",
        description="Shirts, trousers, and smart-casual basics for men.",
    )
    women = Category.objects.create(
        name="Women",
        slug="women",
        description="Elegant dresses, tops, and everyday fashion for women.",
    )
    kids = Category.objects.create(
        name="Kids",
        slug="kids",
        description="Soft and comfortable outfits designed for active kids.",
    )

    products = [
        Product(
            category=men,
            name="Classic Cotton Shirt",
            slug="classic-cotton-shirt",
            short_description="A clean office-ready shirt for daily wear.",
            description="This cotton shirt is easy to style with jeans or formal pants and is perfect for a first ecommerce demo product.",
            fabric="Cotton",
            price=Decimal("29.99"),
            stock=25,
            available=True,
            featured=True,
        ),
        Product(
            category=men,
            name="Slim Fit Chino Pant",
            slug="slim-fit-chino-pant",
            short_description="Comfortable chino pants with a modern fit.",
            description="A versatile pair of chinos that works for study, office, or weekend wear.",
            fabric="Twill",
            price=Decimal("34.50"),
            stock=18,
            available=True,
            featured=False,
        ),
        Product(
            category=women,
            name="Floral Summer Dress",
            slug="floral-summer-dress",
            short_description="Lightweight printed dress with a relaxed feel.",
            description="A simple dress example that helps learners see category-to-product relationships in Django.",
            fabric="Rayon",
            price=Decimal("42.00"),
            stock=14,
            available=True,
            featured=True,
        ),
        Product(
            category=women,
            name="Soft Knit Cardigan",
            slug="soft-knit-cardigan",
            short_description="Layer-friendly cardigan for cool evenings.",
            description="Soft knit fabric and easy styling make this a good sample product for the storefront.",
            fabric="Wool Blend",
            price=Decimal("38.75"),
            stock=10,
            available=True,
            featured=False,
        ),
        Product(
            category=kids,
            name="Kids Hoodie Set",
            slug="kids-hoodie-set",
            short_description="Warm hoodie and jogger set for active days.",
            description="A simple kidswear sample product that demonstrates stock and price fields.",
            fabric="Fleece",
            price=Decimal("31.20"),
            stock=12,
            available=True,
            featured=True,
        ),
        Product(
            category=kids,
            name="Printed T-Shirt Pack",
            slug="printed-t-shirt-pack",
            short_description="Colorful two-piece t-shirt pack.",
            description="A beginner-friendly example of a lower-priced product with short and full descriptions.",
            fabric="Cotton Jersey",
            price=Decimal("19.90"),
            stock=30,
            available=True,
            featured=False,
        ),
    ]

    Product.objects.bulk_create(products)

    featured_shirt = Product.objects.get(slug="classic-cotton-shirt")
    floral_dress = Product.objects.get(slug="floral-summer-dress")

    order = Order.objects.create(
        customer_name="Amina Rahman",
        customer_email="amina@example.com",
        city="Dhaka",
        address="21 Learning Street",
        status="processing",
    )

    OrderItem.objects.create(order=order, product=featured_shirt, quantity=2, price_at_purchase=featured_shirt.price)
    OrderItem.objects.create(order=order, product=floral_dress, quantity=1, price_at_purchase=floral_dress.price)


class Migration(migrations.Migration):

    dependencies = [
        ("clothstore", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_store_data, migrations.RunPython.noop),
    ]
