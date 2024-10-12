from django.urls import path
from . import views

urlpatterns = [
    path("", views.ProductAPIView().as_view()),
    path("<int:product_pk>/", views.ProductDetailAPIView().as_view()),
    path("payments/", views.PaymentAPIView().as_view()),
    path("login_user/", views.LoginUserAPIView().as_view()),
]
