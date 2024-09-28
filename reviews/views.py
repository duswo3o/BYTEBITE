# 서드파티 라이브러리
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

# Django 기능 및 프로젝트 관련
from .models import Review, Comment
from .serializers import ReviewSerializer, CommentSerializer
from .permissions import IsAuthorOrReadOnly
from movies.models import Movie


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.action in ["retrieve", "list"]:
            permission_classes = [AllowAny]
        elif self.action == "create":
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthorOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if self.action in ["retrieve", "update", "destroy"]:
            review_id = self.kwargs.get("pk")
            return self.queryset.filter(id=review_id)

        movie_id = self.kwargs.get("movie_pk")
        if movie_id:
            return self.queryset.filter(movie_id=movie_id)

        return self.queryset

    def perform_create(self, serializer):
        movie_id = self.kwargs.get("movie_pk")
        movie = Movie.objects.get(pk=movie_id)
        serializer.save(author=self.request.user, movie=movie)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [AllowAny]
        elif self.action == "create":
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthorOrReadOnly]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        review_id = self.kwargs.get("review_pk")
        serializer.save(review_id=review_id, author=self.request.user)

    def get_queryset(self):
        review_id = self.kwargs.get("review_pk")
        return self.queryset.filter(review_id=review_id)
