from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


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
    release_date = models.DateField(null=True, blank=True)
    poster = models.URLField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.title


class Ranking(models.Model):
    title = models.CharField(max_length=255)
    rank = models.PositiveIntegerField()
    crawling_date = models.DateField()
    movie_pk = models.ForeignKey(
        Movie, on_delete=models.CASCADE, related_name="ranking", blank=True, null=True
    )

    def __str__(self):
        return self.title


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="ratings")
    score = models.FloatField()

    class Meta:
        unique_together = ("user", "movie")

    def __str__(self):
        return f"{self.user} rated {self.movie} as {self.score}"
