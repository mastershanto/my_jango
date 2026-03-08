from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("clothstore", "0002_seed_store_data"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="notes",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="order",
            name="phone",
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
