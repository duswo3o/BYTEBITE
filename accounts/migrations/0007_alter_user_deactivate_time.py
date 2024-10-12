import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0006_alter_user_deactivate_time"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="deactivate_time",
            field=models.DateTimeField(
                blank=True,
                null=True,
            ),
        ),
    ]
