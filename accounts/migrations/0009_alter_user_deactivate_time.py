<<<<<<< HEAD
# Generated by Django 5.1.1 on 2024-10-10 04:10
=======
# Generated by Django 5.1.1 on 2024-10-10 03:15
>>>>>>> 64c6e279ba2e78c28eed69cc942be7de59d4a809

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
<<<<<<< HEAD
        ("accounts", "0008_merge_20241009_0328"),
=======
        ("accounts", "0008_alter_user_deactivate_time"),
>>>>>>> 64c6e279ba2e78c28eed69cc942be7de59d4a809
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="deactivate_time",
            field=models.DateTimeField(
                blank=True,
<<<<<<< HEAD
                default=datetime.datetime(2024, 10, 10, 22, 10, 19, 989712),
=======
                default=datetime.datetime(2024, 10, 10, 21, 15, 6, 300521),
>>>>>>> 64c6e279ba2e78c28eed69cc942be7de59d4a809
                null=True,
            ),
        ),
    ]
