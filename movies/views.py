import requests
import time
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Movie, Ranking
from .serializers import BoxofficeSerializer, MovieSerializer


class MovieListApiView(APIView):
    def get(self, request):
        today_movie = Ranking.objects.last().crawling_date
        movies = Ranking.objects.filter(crawling_date=today_movie)
        serializer = BoxofficeSerializer(movies, many=True)
        return Response(serializer.data)


class MovieAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Movie, pk=pk)

    # 영화 상세페이지 조회
    def get(self, request, movie_pk):
        movie = self.get_object(movie_pk)
        serializer = MovieSerializer(movie)
        return Response(serializer.data)

    # 영화 보고싶어요, 관심없어요.
    def post(self, request, movie_pk):
        movie = self.get_object(movie_pk)
        
        # 추천
        if request.data.get('evaluate') == 'recommendation':
            movie.non_recommendation.remove(request.user)

            if movie.recommendation.filter(pk=request.user.pk).exists():
                movie.recommendation.remove(request.user)
                return Response({"detail": "추천이 취소되었습니다."}, status=status.HTTP_200_OK)
            else:
                movie.recommendation.add(request.user)
                movie.save()
                return Response({"detail": "이 기사를 추천합니다."}, status=status.HTTP_200_OK)
        # 비추천
        else:
            movie.recommendation.remove(request.user)

            if movie.non_recommendation.filter(pk=request.user.pk).exists():
                movie.non_recommendation.remove(request.user)
                return Response({"detail": "비추천이 취소되었습니다."}, status=status.HTTP_200_OK)
            else:
                movie.non_recommendation.add(request.user)
                movie.save()
                return Response({"detail": "이 기사를 비추천합니다."}, status=status.HTTP_200_OK)


class MovieDataBaseAPIView(APIView):
    """데이터베이스 최신화 요청 클래스

    현재 버전에서는 테스트용 데이터가 필요하기 때문에 개발자가 원하는 시점에
    요청을 보내서 DB를 업데이트 할 수 있도록 함.
    추후에는 삭제 또는 수정될 예정입니다.
    """
    API_URL = "http://api.koreafilm.or.kr/openapi-data2/wisenut/search_api/search_json2.jsp?collection=kmdb_new2"

    def post(self, request):
        start_count = 0
        total_data = []

        while True:
            params = {
                "ServiceKey": settings.KMDB_API_KEY,
                "listCount": 100,
                "startCount": start_count,
                "detail": "N",
            }

            response = requests.get(self.API_URL, params=params)

            if response.status_code == 200:
                data = response.json()["Data"][0]["Result"]
                total_data.extend(data)

                if len(data) < 1000:
                    break
                # 아래의 break문을 주석처리 하면 KMDb의 모든 데이터를 가져오게 됩니다.
                break

                start_count += 1000

                time.sleep(3)

            else:
                return Response(
                    {"error": "API에 접속에 실패했습니다."},
                    status=status.HTTP_400_BAD_REQUEST
                    )

        save_to_database(total_data)
        return Response(
            {"message": f"{len(total_data)}개의 영화 데이터가 저장되었습니다."},
            status=status.HTTP_200_OK
            )


def save_to_database(total_data):
    for item in total_data:
        movie_cd = item["movieSeq"]
        title = item["title"]
        # genre = item['genre']
        runtime = item["runtime"] if item["runtime"] else None
        rating = item["rating"] if item["rating"] else None
        plot = item["plots"]["plot"][0]["plotText"]

        movie, created = Movie.objects.update_or_create(
            movie_cd=movie_cd,
            defaults={
                "title": title,
                # 'genre': genre,
                "runtime": runtime,
                "grade": rating,
                "plot": plot,
                }
            )
