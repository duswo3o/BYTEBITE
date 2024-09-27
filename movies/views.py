# 표준 라이브러리
import time

# 서드파티 라이브러리
import requests
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Django 기능 및 프로젝트 관련
from django.conf import settings
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from .models import Genre, Movie, Ranking, Staff
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
    @method_decorator(permission_classes([IsAuthenticated]))
    def post(self, request, movie_pk):
        movie = self.get_object(movie_pk)

        # 보고싶어요
        if request.data.get("like") == "like":
            movie.dislike_users.remove(request.user)

            if movie.like_users.filter(pk=request.user.pk).exists():
                movie.like_users.remove(request.user)
                return Response(
                    {"detail": "보고싶어요를 해제합니다."},
                    status=status.HTTP_200_OK
                    )
            else:
                movie.like_users.add(request.user)
                movie.save()
                return Response(
                    {"detail": "이 영화가 보고싶어요."},
                    status=status.HTTP_200_OK
                    )
        # 관심없어요
        else:
            movie.like_users.remove(request.user)

            if movie.dislike_users.filter(pk=request.user.pk).exists():
                movie.dislike_users.remove(request.user)
                return Response(
                    {"detail": "관심없어요를 해제합니다."},
                    status=status.HTTP_200_OK
                    )
            else:
                movie.dislike_users.add(request.user)
                movie.save()
                return Response(
                    {"detail": "이 영화가 관심없어요."},
                    status=status.HTTP_200_OK
                    )


class MovieDataBaseAPIView(APIView):
    """데이터베이스 최신화 요청 클래스

    현재 버전에서는 테스트용 데이터가 필요하기 때문에 개발자가 원하는 시점에
    요청을 보내서 DB를 업데이트 할 수 있도록 함.
    추후에는 삭제 또는 수정할 예정입니다.
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
        runtime = item["runtime"] if item["runtime"] else None
        rating = item["rating"] if item["rating"] else None
        plot = item["plots"]["plot"][0]["plotText"]

        genres = item["genre"].split(",")
        genre_objects = []

        for genre_name in genres:
            genre_name = genre_name.strip()
            genre, created = Genre.objects.get_or_create(name=genre_name)
            genre_objects.append(genre)

        movie, created = Movie.objects.update_or_create(
            movie_cd=movie_cd,
            defaults={
                "title": title,
                "runtime": runtime,
                "grade": rating,
                "plot": plot,
                }
            )

        movie.genre.set(genre_objects)

        directors = item["directors"]["director"]
        actors = item["actors"]["actor"]

        # 스태프 로직(추후에 함수화)
        create_staff(movie, directors, actors)

        movie.save()


def create_staff(movie, directors, actors):
    staffs = []

    for director in directors:
        staffs.append(
            {"name_cd": director["directorId"],
                "name": director["directorNm"],
                "role": "director"}
            )

    for actor in actors:
        staffs.append(
            {"name_cd": actor["actorId"],
                "name": actor["actorNm"],
                "role": "actor"}
            )

    for staff in staffs:
        name_cd = staff.get("name_cd")
        name_cd = int(name_cd) if name_cd else None

        name = staff.get("name")
        role = staff.get("role")

        try:
            if name_cd is not None:
                staff, created = Staff.objects.get_or_create(
                    name_cd=name_cd,
                    defaults={"name": name, "role": role}
                    )
            else:
                staff, created = Staff.objects.get_or_create(
                    name=name,
                    role=role
                    )

            movie.staffs.add(staff)

        except IntegrityError:
            pass
