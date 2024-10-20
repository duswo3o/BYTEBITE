from django.contrib.auth import get_user_model

from rest_framework import serializers
from .models import Product

User = get_user_model()


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "nickname"]
