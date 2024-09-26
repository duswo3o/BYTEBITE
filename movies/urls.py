from django.urls import path
from . import views

urlpatterns = [
    path("", views.MovieListApiView().as_view()),
]
