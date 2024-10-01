# 서드파티 라이브러리
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Django 기능 및 프로젝트 관련
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from .models import Movie, Ranking, Rating, Staff
from .serializers import (
    AverageGradeSerializer,
    BoxofficeSerializer,
    LikeSerializer,
    MovieSerializer,
    StaffSerializer,
    UserSerializer,
    )


# 메인페이지
class MovieListApiView(APIView):
    def get(self, request):
        # 박스오피스 순 출력
        today_movie = Ranking.objects.last().crawling_date
        movies = Ranking.objects.filter(crawling_date=today_movie)

        boxoffice_serializer = BoxofficeSerializer(movies, many=True)

        # 평균 평점 순 출력
        graded_movies = Movie.objects.annotate(
            average_grade=Avg("ratings__score")
            ).order_by("-average_grade")[:10]

        graded_serializer = AverageGradeSerializer(graded_movies, many=True)

        # 좋아요 많은 순 출력
        liked_movies = Movie.objects.annotate(
            like_count=models.Count("like_users"),
            dislike_count=models.Count("dislike_users")
        ).annotate(
            like=models.F("like_count") - models.F("dislike_count")
        ).order_by("-like")[:10]

        liked_serializer = LikeSerializer(liked_movies, many=True)

        response_data = {
            "boxoffice_movies": boxoffice_serializer.data,
            "graded_movies": graded_serializer.data,
            "liked_movies": liked_serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class MovieSearchAPIView(APIView):
    # 검색
    def get(self, request):
        # 검색할 데이터 종류(영화, 영화인, 회원)
        search_type = request.GET.get("search_type")
        # 검색 키워드
        search_keyword = request.GET.get("search_keyword")

        if not search_keyword:
            return Response(
                {'error': '검색어를 제공해야 합니다.'},
                status=status.HTTP_400_BAD_REQUEST
                )

        # 영화 검색(제목, 장르, 줄거리)
        if search_type == 'movies':
            search_data = Movie.objects.filter(
                Q(title__icontains=search_keyword) |
                Q(genre__name__icontains=search_keyword) |
                Q(plot__icontains=search_keyword)
                ).distinct()

            serializer_class = MovieSerializer

        # 영화인 검색(이름)
        elif search_type == 'staff':
            search_data = Staff.objects.filter(name__icontains=search_keyword)

            serializer_class = StaffSerializer

        # 회원 검색(닉네임)
        else:
            search_data = get_user_model().objects.filter(
                nickname__icontains=search_keyword
                )

            serializer_class = UserSerializer

        serializer = serializer_class(search_data, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class MovieDetailAPIView(APIView):
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


# 평점
class MovieScoreAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, movie_pk):
        movie = get_object_or_404(Movie, pk=movie_pk)
        score = request.data.get("evaluate")

        Rating.objects.filter(user=request.user, movie=movie).delete()

        if score == 0 or score > 5:
            return Response(
                {"detail": "이 영화의 평가를 취소합니다."},
                status=status.HTTP_200_OK
                )
        else:
            score = int(score * 10) / 10
            Rating.objects.create(user=request.user, movie=movie, score=score)

            return Response(
                {"detail": f"이 영화의 점수를 {score}로 평가합니다."},
                status=status.HTTP_200_OK
                )
