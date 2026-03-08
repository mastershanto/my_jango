from django.db import migrations


def update_products_with_images(apps, schema_editor):
    """Add real free images from Unsplash to existing products."""
    Product = apps.get_model("clothstore", "Product")
    
    # Real Unsplash image URLs for fashion/clothing
    # These are high-quality, free-to-use images
    image_urls = {
        "classic-cotton-shirt": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500&h=500&fit=crop",
        "slim-fit-chino-pant": "https://images.unsplash.com/photo-1473621038104-56f90ad64f94?w=500&h=500&fit=crop",
        "floral-summer-dress": "https://images.unsplash.com/photo-1595777707802-a9e11007e4f0?w=500&h=500&fit=crop",
        "soft-knit-cardigan": "https://images.unsplash.com/photo-1609003734967-4e0457df5d51?w=500&h=500&fit=crop",
        "kids-hoodie-set": "https://images.unsplash.com/photo-1556821552-5f9c5dd8e6f8?w=500&h=500&fit=crop",
        "printed-t-shirt-pack": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500&h=500&fit=crop",
    }
    
    for product in Product.objects.all():
        if product.slug in image_urls:
            product.image_url = image_urls[product.slug]
            product.save(update_fields=["image_url"])


class Migration(migrations.Migration):

    dependencies = [
        ("clothstore", "0003_order_phone_notes"),
    ]

    operations = [
        migrations.RunPython(update_products_with_images, migrations.RunPython.noop),
    ]
