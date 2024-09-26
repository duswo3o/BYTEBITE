from rest_framework import serializers
from .models import Reviews


class ReviewsSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")

    class Meta:
        model = Reviews
        fields = "__all__"
