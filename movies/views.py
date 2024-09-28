# 표준 라이브러리

# 서드파티 라이브러리
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Django 기능 및 프로젝트 관련
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from .models import Movie, Ranking, Rating
from .serializers import BoxofficeSerializer, MovieSerializer


class MovieListApiView(APIView):
    def get(self, request):
        today_movie = Ranking.objects.last().crawling_date
        movies = Ranking.objects.filter(crawling_date=today_movie)
        serializer = BoxofficeSerializer(movies, many=True)
        return Response(serializer.data)


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
        score = request.data.get('evaluate')

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
