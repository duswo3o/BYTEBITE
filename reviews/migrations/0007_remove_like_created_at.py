# Generated by Django 4.2 on 2024-09-28 08:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("reviews", "0006_like"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="like",
            name="created_at",
        ),
    ]
