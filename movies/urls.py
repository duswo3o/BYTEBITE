from django.urls import path
from movies import views

urlpatterns = [
    path("<int:movie_pk>/", views.MovieAPIView.as_view()),
    path("database/", views.MovieAPIView.as_view()),
]
