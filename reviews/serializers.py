from rest_framework import serializers
from .models import Review, Comment, Like


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.nickname")

    class Meta:
        model = Review
        fields = ["id", "author", "movie", "content", "created_at"]
        read_only_fields = ["author", "movie", "created_at"]


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.nickname")
    review = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "review", "content", "author", "created_at", "updated_at"]


class LikeSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="author.nickname")
    class Meta:
        model = Like
        fields = ['id', 'user', 'review',]
