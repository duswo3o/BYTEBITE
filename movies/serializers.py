# 서드파티 라이브러리
from rest_framework import serializers

# Django 기능 및 프로젝트 관련
from django.conf import settings
from django.db.models import Avg
from .models import Genre, Movie, Ranking, Staff, Tag


class BoxofficeSerializer(serializers.ModelSerializer):
    poster = serializers.SerializerMethodField()
    movie_pk = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Ranking
        fields = ["title", "rank", "poster", "movie_pk"]

    def get_poster(self, obj):
        if obj.movie_pk and obj.movie_pk.poster:
            return obj.movie_pk.poster

        return f"{settings.STATIC_URL}images/no_image.png"


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["name"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["name"]


class MovieSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    tags = TagSerializer(many=True, read_only=True)
    poster = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = "__all__"

    def get_poster(self, obj):
        if obj.poster:
            return obj.poster

        return f"{settings.STATIC_URL}images/no_image.png"


class AverageGradeSerializer(MovieSerializer):
    average_grade = serializers.FloatField(read_only=True)

    class Meta:
        model = Movie
        fields = ["id", "title", "average_grade", "poster"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        average_score = instance.ratings.aggregate(Avg("score"))["score__avg"] or 0
        representation["average_grade"] = round(average_score, 1)
        return representation


class LikeSerializer(MovieSerializer):
    like = serializers.IntegerField()

    class Meta:
        model = Movie
        fields = ["id", "title", "like", "release_date", "poster"]


class FilmographySerializer(MovieSerializer):
    class Meta:
        model = Movie
        fields = ["id", "title", "poster"]


class StaffSerializer(serializers.ModelSerializer):
    filmographys = FilmographySerializer(many=True, read_only=True)

    class Meta:
        model = Staff
        fields = fields = ["name", "role", "filmographys"]
