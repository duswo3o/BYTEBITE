from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path("", views.UserAPIView().as_view()),
    path("signin/", views.UserSigninAPIView().as_view()),
    path("kakao/login/", views.KakaoLoginView.as_view(), name="kakao_login"),
    path("kakao/callback/", views.KakaoCallbackView.as_view(), name="kakao_callback"),
    path("activate/<uidb64>/<str:token>/", views.UserActivate.as_view()),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("signout/", views.UserSignoutAPIView().as_view()),
    path("password/", views.UserChangePasswordAPIView().as_view()),
    path("<int:pk>/", views.UserProfileAPIView().as_view()),
    path("<int:user_pk>/follow/", views.UserFollowAPIView().as_view()),
]
