# Generated by Django 5.1.1 on 2024-10-19 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0006_alter_product_consumer"),
    ]

    operations = [
        migrations.AddField(
            model_name="purchasedproduct",
            name="quantity",
            field=models.IntegerField(default=1),
        ),
    ]