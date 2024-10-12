# Generated by Django 5.1.1 on 2024-10-11 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("content", models.TextField()),
                ("price", models.PositiveIntegerField()),
                ("image", models.URLField(blank=True, max_length=255, null=True)),
            ],
        ),
    ]
