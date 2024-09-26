from rest_framework import serializers
from .models import Ranking


class BoxofficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ranking
        fields = ["title", "rank"]
