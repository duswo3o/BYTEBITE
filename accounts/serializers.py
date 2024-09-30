import re

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from .models import User
from movies.models import Movie, Rating
from reviews.models import Review, Comment, Like


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, max_length=128)
    confirm_password = serializers.CharField(write_only=True, max_length=128)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "confirm_password",
            "nickname",
            "age",
            "bio",
            "gender",
        ]

    def validate(self, attrs):
        REGEX_EMAIL = "([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
        if not re.fullmatch(REGEX_EMAIL, attrs["email"]):
            raise serializers.ValidationError({"email": "이메일이 올바르지 않습니다."})

        if len(attrs["password"]) < 8:
            raise serializers.ValidationError(
                {"password": "패스워드는 8자 이상 입력되어야 합니다."}
            )

        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"password_confirm": "패스워드가 일치하지 않습니다."}
            )

        if len(attrs["nickname"]) > 20:
            raise serializers.ValidationError(
                {"nickname": "닉네임의 최대 길이는 20자 입니다."}
            )

        if attrs.get("age") is not None:
            if attrs["age"] < 0 or attrs["age"] > 150:
                raise serializers.ValidationError(
                    {"age": "나이는 0세 이상 150세 이하로 입력 가능합니다."}
                )

        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            nickname=validated_data.get("nickname"),
            gender=validated_data.get("gender"),
            age=validated_data.get("age"),
            bio=validated_data.get("bio"),
        )

        return user


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["old_password", "new_password", "confirm_password"]

    def validate_old_password(self, value):
        """기존 비밀번호를 바르게 입력하였는지 확인합니다.
        기존 패스워드와 입력한 old_password가 다르다면 에러 메세지를 출력하고
        일차한다면 패스워드를 리턴합니다."""

        user = self.context
        if not user.check_password(value):
            raise serializers.ValidationError(
                {"error": "기존 패스워드가 일치하지 않습니다."}
            )
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"error": "새로운 패스워드와 확인 패스워드가 일치하지 않습니다."}
            )

        if attrs["old_password"] == attrs["new_password"]:
            raise serializers.ValidationError(
                {"error": "기존 패스워드와 변경하려는 패스워드가 동일합니다."}
            )

        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data["new_password"])
        instance.save()
        return instance


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "nickname",
            "gender",
            "age",
            "bio",
        ]

    def validate_age(self, value):
        if (value < 0) or (value > 150):
            raise serializers.ValidationError(
                {"error": "나이는 0세 이상 150세 이하로 입력 가능합니다."}
            )
        return value


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ["title"]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["movie", "content"]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["review", "content"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["nickname"]


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ["movie", "score"]


class LikedReviewSerializer(serializers.ModelSerializer):
    review = ReviewSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ["review"]

    def to_representation(self, instance):
        # 부모 클래스의 to_representation() 호출
        representation = super().to_representation(instance)

        # review가 None이거나 직렬화 결과가 비어 있으면 빈 딕셔너리 반환 방지
        if not representation.get("review"):
            return None  # 빈 객체가 아닌 None을 반환하여 리스트에서 제거되도록 처리

        return representation


class LikedCommentSerializer(serializers.ModelSerializer):
    comment = CommentSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ["comment"]

    def to_representation(self, instance):
        # 부모 클래스의 to_representation() 호출
        representation = super().to_representation(instance)

        # comment가 None이거나 직렬화 결과가 비어 있으면 빈 딕셔너리 반환 방지
        if not representation.get("comment"):
            return None  # 빈 객체가 아닌 None을 반환하여 리스트에서 제거되도록 처리

        return representation


class UserProfileSerializer(serializers.ModelSerializer):
    liked_movies = MovieSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    followings = UserSerializer(many=True)
    followings_count = serializers.IntegerField(
        source="followings.count", read_only=True
    )
    followers = UserSerializer(many=True)
    followers_count = serializers.IntegerField(source="followers.count", read_only=True)
    rated_movie = RatingSerializer(many=True, read_only=True, source="ratings")
    # liked_reviews = LikedReviewSerializer(many=True, read_only=True, source="likes")
    # liked_comments = LikedCommentSerializer(many=True, read_only=True, source="likes")
    liked_reviews = serializers.SerializerMethodField()
    liked_comments = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "email",
            "nickname",
            "followings",
            "followings_count",
            "followers",
            "followers_count",
            "gender",
            "age",
            "bio",
            "rated_movie",
            "liked_movies",
            "reviews",
            "liked_reviews",
            "liked_comments",
        ]

    def get_liked_reviews(self, obj):
        # LikedReviewSerializer로 직렬화한 후 유효한 데이터만 필터링
        reviews = LikedReviewSerializer(
            obj.likes.filter(review__isnull=False), many=True
        ).data
        return [
            review for review in reviews if review
        ]  # None 값이 아닌 유효한 리뷰만 반환

    def get_liked_comments(self, obj):
        # LikedCommentSerializer로 직렬화한 후 유효한 데이터만 필터링
        comments = LikedCommentSerializer(
            obj.likes.filter(comment__isnull=False), many=True
        ).data
        return [
            comment for comment in comments if comment
        ]  # None 값이 아닌 유효한 댓글만 반환
