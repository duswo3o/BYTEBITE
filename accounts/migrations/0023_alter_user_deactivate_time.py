# Generated by Django 5.1.1 on 2024-10-12 07:55

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0022_alter_user_deactivate_time"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="deactivate_time",
            field=models.DateTimeField(
                blank=True,
                default=datetime.datetime(2024, 10, 13, 1, 55, 54, 553307),
                null=True,
            ),
        ),
    ]
