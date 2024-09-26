from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Ranking
from .serializers import BoxofficeSerializer


# Create your views here.
class MovieListApiView(APIView):
    def get(self, request):
        today_movie = Ranking.objects.last().crawling_date
        movies = Ranking.objects.filter(crawling_date=today_movie)
        serializer = BoxofficeSerializer(movies, many=True)
        return Response(serializer.data)
