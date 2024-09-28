import re

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from .models import User
from movies.models import Movie
from reviews.models import Review


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
        fields = ["content"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["nickname"]


class UserProfileSerializer(serializers.ModelSerializer):
    liked_movies = MovieSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    followings = UserSerializer(many=True)
    followings_count = serializers.IntegerField(
        source="followings.count", read_only=True
    )
    followers = UserSerializer(many=True)
    followers_count = serializers.IntegerField(source="followers.count", read_only=True)

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
            "liked_movies",
            "reviews",
        ]
