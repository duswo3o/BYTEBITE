from rest_framework import serializers
from .models import Ranking, Movie


class BoxofficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ranking
        fields = ["title", "rank"]


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = "__all__"