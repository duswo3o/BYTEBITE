from rest_framework import serializers
from .models import Review, Comment, Like, Report


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.nickname")
    review = serializers.PrimaryKeyRelatedField(read_only=True)
    like_count = serializers.SerializerMethodField()
    is_spoiler = serializers.BooleanField(required=False)

    class Meta:
        model = Comment
        fields = [
            "id",
            "review",
            "content",
            "author",
            "created_at",
            "updated_at",
            "like_count",
            "is_spoiler",
        ]

    def get_like_count(self, obj):
        return Like.objects.filter(comment=obj).count()


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.nickname")
    comment_count = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    # comments = CommentSerializer(many=True, read_only=True)
    is_spoiler = serializers.BooleanField(required=False)

    class Meta:
        model = Review
        fields = [
            "id",
            "author",
            "movie",
            "content",
            # "comments",
            "created_at",
            "like_count",
            "comment_count",
            "is_spoiler",
        ]
        read_only_fields = ["author", "movie", "created_at"]

    def get_like_count(self, obj):
        return Like.objects.filter(review=obj).count()

    def get_comment_count(self, obj):
        return Comment.objects.filter(review=obj).count()


class LikeSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.nickname")

    class Meta:
        model = Like
        fields = [
            "id",
            "author",
            "review",
        ]
