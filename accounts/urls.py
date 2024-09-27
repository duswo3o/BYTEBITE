from django.urls import path
from . import views

urlpatterns = [
    path("", views.UserAPIView().as_view()),
    path("signin/", views.UserSigninAPIView().as_view()),
    path("signout/", views.UserSignoutAPIView().as_view()),
    path("password/", views.UserChangePasswordAPIView().as_view()),
    # path("withdraw/", views.UserAPIView.as_view()),
]
