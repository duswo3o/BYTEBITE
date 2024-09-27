from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Ranking(models.Model):
    title = models.CharField(max_length=255)
    rank = models.PositiveIntegerField()
    crawling_date = models.DateField()

    def __str__(self):
        return self.title


class Staff(models.Model):
    name_cd = models.IntegerField(unique=True, blank=True)
    name = models.CharField(max_length=50)
    role = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True, blank=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=30, unique=True, blank=True)

    def __str__(self):
        return self.name


class Movie(models.Model):
    movie_cd = models.IntegerField(unique=True)
    title = models.CharField(max_length=255)
    genre = models.ManyToManyField(
        Genre,
        related_name="movies",
        blank=True,
    )
    avg_rating = models.ManyToManyField(
        User,
        related_name="evaluated_movies",
        blank=True,
    )
    runtime = models.IntegerField(null=True, blank=True)
    grade = models.CharField(null=True, blank=True, max_length=50)
    plot = models.TextField(blank=True)
    like_users = models.ManyToManyField(
        User,
        related_name="liked_movies",
        blank=True,
    )
    dislike_users = models.ManyToManyField(
        User,
        related_name="disliked_movies",
        blank=True,
    )
    staffs = models.ManyToManyField(
        Staff,
        related_name="filmographys",
        blank=True,
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="movies",
        blank=True,
    )

    def __str__(self):
        return self.title
