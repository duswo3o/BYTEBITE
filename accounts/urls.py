from django.urls import path
from . import views

urlpatterns = [
    path("", views.UserCreateAPIView().as_view()),
]
