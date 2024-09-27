from django.urls import path
from . import views

urlpatterns = [
    path("", views.UserCreateAPIView().as_view()),
    path("signin/", views.UserSigninAPIView().as_view()),
    path("signout/", views.UserSignoutAPIView().as_view()),
]
