from django.db import models
from django.contrib.auth import get_user_model


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class Movie(models.Model):
    movie_cd = models.IntegerField(unique=True)
    title = models.CharField(max_length=50)
    # genre = 추후 논의 필요
    # avg_rating = 추후 논의 필요
    runtime = models.IntegerField(null=True, blank=True)
    grade = models.CharField(null=True, blank=True, max_length=50)
    plot = models.TextField(blank=True)
    like_users = models.ManyToManyField(
        get_user_model(),
        related_name="movies",
        blank=True,
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="movies",
        blank=True,
    )

    def __str__(self):
        return self.title
