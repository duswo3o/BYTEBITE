# Generated by Django 5.1.1 on 2024-10-04 07:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("movies", "0005_remove_movie_rating_rating"),
    ]

    operations = [
        migrations.AddField(
            model_name="ranking",
            name="movie_pk",
            field=models.IntegerField(default=0, unique=True),
            preserve_default=False,
        ),
    ]
