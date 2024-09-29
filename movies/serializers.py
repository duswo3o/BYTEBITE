from rest_framework import serializers
from .models import Movie, Ranking, Staff


class BoxofficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ranking
        fields = ["title", "rank"]


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = "__all__"


class AverageGradeSerializer(serializers.ModelSerializer):
    average_grade = serializers.FloatField()

    class Meta:
        model = Movie
        fields = ["title", "average_grade"]  # 영화 제목과 평균 점수


class LikeSerializer(serializers.ModelSerializer):
    like = serializers.IntegerField()

    class Meta:
        model = Movie
        fields = ["title", "like"]


class FilmographySerializer(MovieSerializer):
    class Meta:
        model = Movie
        fields = ['title']


class StaffSerializer(serializers.ModelSerializer):
    filmographys = FilmographySerializer(many=True, read_only=True)

    class Meta:
        model = Staff
        fields = fields = ['name', 'role', 'filmographys']
