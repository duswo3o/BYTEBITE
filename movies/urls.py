from django.urls import path
from movies import views

urlpatterns = [
    path("database/", views.MovieAPIView.as_view()),
]
