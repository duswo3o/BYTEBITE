# Generated by Django 4.2 on 2024-09-26 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("movies", "0003_alter_movie_like_users"),
    ]

    operations = [
        migrations.AlterField(
            model_name="movie",
            name="runtime",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
