# Generated by Django 5.1.1 on 2024-10-08 00:59

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_alter_user_deactivate_time"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="deactivate_time",
            field=models.DateTimeField(
                blank=True,
                default=datetime.datetime(2024, 10, 8, 18, 59, 17, 794182),
                null=True,
            ),
        ),
    ]
