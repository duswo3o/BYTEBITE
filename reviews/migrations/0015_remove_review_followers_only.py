# Generated by Django 5.1.1 on 2024-10-18 07:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("reviews", "0014_review_followers_only_review_private"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="review",
            name="followers_only",
        ),
    ]
