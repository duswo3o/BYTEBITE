# Generated by Django 4.2 on 2024-09-27 09:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("movies", "0003_movie_staffs_alter_genre_name_alter_staff_name_cd_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="movie",
            old_name="avg_rating",
            new_name="rating",
        ),
    ]
