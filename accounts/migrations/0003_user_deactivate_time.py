# Generated by Django 4.2 on 2024-09-28 04:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_user_followings"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="deactivate_time",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]