# Generated by Django 4.2 on 2024-09-27 02:15

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("reviews", "0003_comments_updated_at_alter_comments_author"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Comments",
            new_name="Comment",
        ),
        migrations.RenameModel(
            old_name="Reviews",
            new_name="Review",
        ),
    ]