# Generated by Django 5.1.1 on 2024-10-10 03:15

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0008_alter_user_deactivate_time"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="deactivate_time",
            field=models.DateTimeField(
                blank=True,
                default=datetime.datetime(2024, 10, 10, 21, 15, 6, 300521),
                null=True,
            ),
        ),
    ]
