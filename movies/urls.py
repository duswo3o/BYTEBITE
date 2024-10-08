from django.urls import path
from movies import views

urlpatterns = [
    path("", views.MovieListApiView().as_view()),
    path("search/", views.MovieSearchAPIView.as_view()),
    path("<int:movie_pk>/", views.MovieDetailAPIView.as_view()),
    path("<int:movie_pk>/score/", views.MovieScoreAPIView.as_view()),
]
