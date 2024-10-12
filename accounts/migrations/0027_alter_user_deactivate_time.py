# Generated by Django 5.1.1 on 2024-10-12 08:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0026_alter_user_deactivate_time"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="deactivate_time",
            field=models.DateTimeField(
                blank=True,
                default=datetime.datetime(2024, 10, 13, 2, 23, 32, 596126),
                null=True,
            ),
        ),
    ]
