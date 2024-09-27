# Generated by Django 4.2 on 2024-09-27 07:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("movies", "0002_staff_alter_movie_title"),
    ]

    operations = [
        migrations.AddField(
            model_name="movie",
            name="staffs",
            field=models.ManyToManyField(
                blank=True, related_name="filmographys", to="movies.staff"
            ),
        ),
        migrations.AlterField(
            model_name="genre",
            name="name",
            field=models.CharField(blank=True, max_length=30, unique=True),
        ),
        migrations.AlterField(
            model_name="staff",
            name="name_cd",
            field=models.IntegerField(blank=True, unique=True),
        ),
        migrations.AlterField(
            model_name="tag",
            name="name",
            field=models.CharField(blank=True, max_length=30, unique=True),
        ),
    ]
