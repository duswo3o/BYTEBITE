from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path("", views.UserAPIView().as_view()),
    path("signin/", views.UserSigninAPIView().as_view()),
    path("activate/<uidb64>/<str:token>/", views.UserActivate.as_view()),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("signout/", views.UserSignoutAPIView().as_view()),
    path("password/", views.UserChangePasswordAPIView().as_view()),
    path("<int:pk>/", views.UserProfileAPIView().as_view()),
    path("<int:user_pk>/follow/", views.UserFollowAPIView().as_view()),
    path("delete_user/", views.delete_user),
    path("payment/", views.PaymentAPIView().as_view()),
]
