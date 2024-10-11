from django.urls import path
from . import views

urlpatterns = [
    path("", views.ProductAPIView().as_view()),
    path("payments/", views.PaymentAPIView().as_view()),
]
