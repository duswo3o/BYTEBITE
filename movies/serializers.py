# 서드파티 라이브러리
from rest_framework import serializers

# Django 기능 및 프로젝트 관련
from django.contrib.auth import get_user_model
from .models import Genre, Movie, Ranking, Staff


class PosterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ["poster"]


class BoxofficeSerializer(serializers.ModelSerializer):
    poster = serializers.CharField(source="movie_pk.poster", read_only=True)
    movie_pk = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Ranking
        fields = ["title", "rank", "poster", "movie_pk"]


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["name"]


class MovieSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)

    class Meta:
        model = Movie
        fields = "__all__"


class AverageGradeSerializer(serializers.ModelSerializer):
    average_grade = serializers.FloatField()

    class Meta:
        model = Movie
        fields = ["id", "title", "average_grade", "poster"]


class LikeSerializer(serializers.ModelSerializer):
    like = serializers.IntegerField()

    class Meta:
        model = Movie
        fields = ["id", "title", "like", "poster"]


class ComingSerializer(serializers.ModelSerializer):
    like = serializers.IntegerField()

    class Meta:
        model = Movie
        fields = ["id", "title", "like", "release_date", "poster"]


class FilmographySerializer(MovieSerializer):
    class Meta:
        model = Movie
        fields = ["title"]


class StaffSerializer(serializers.ModelSerializer):
    filmographys = FilmographySerializer(many=True, read_only=True)

    class Meta:
        model = Staff
        fields = fields = ["name", "role", "filmographys"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["nickname", "bio"]
