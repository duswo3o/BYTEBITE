# Generated by Django 5.1.1 on 2024-10-04 07:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("movies", "0006_ranking_movie_pk"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ranking",
            name="movie_pk",
            field=models.IntegerField(blank=True, unique=True),
        ),
    ]
