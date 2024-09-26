import re
from rest_framework import serializers
from .models import User


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
            if attrs["age"] < 0:
                raise serializers.ValidationError(
                    {"age": "나이는 0세 이상 입력 가능합니다."}
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
