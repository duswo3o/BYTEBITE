from django.urls import path
from movies import views

urlpatterns = [
    path("", views.MovieListApiView().as_view()),
    path("<int:movie_pk>/", views.MovieAPIView.as_view()),
    path("database/", views.MovieDataBaseAPIView.as_view()),
]
