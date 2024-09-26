from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from .serializers import UserCreateSerializer


# Create your views here
class UserCreateAPIView(CreateAPIView):
    queryset = None
    serializer_class = UserCreateSerializer
