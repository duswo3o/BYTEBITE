# 서드파티 라이브러리
from rest_framework import viewsets, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

# Django 기능 및 프로젝트 관련
from .models import Review, Comment, Like
from .serializers import ReviewSerializer, CommentSerializer, LikeSerializer
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


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        review_id = kwargs.get("review_id")
        comment_id = kwargs.get("comment_id")

        if review_id:
            try:
                review = Review.objects.get(id=review_id)
            except Review.DoesNotExist:
                return Response(
                    {"error": "리뷰를 찾을 수 없습니다"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            existing_like = Like.objects.filter(
                user=request.user, review=review
            ).first()
            if existing_like:
                existing_like.delete()
                return Response(
                    {"message": "좋아요 취소"}, status=status.HTTP_204_NO_CONTENT
                )

            like = Like.objects.create(user=request.user, review=review)
            serializer = LikeSerializer(like)
            return Response({"message": "좋아요"}, status=status.HTTP_201_CREATED)

        elif comment_id:
            try:
                comment = Comment.objects.get(id=comment_id)
            except Comment.DoesNotExist:
                return Response(
                    {"error": "코멘트를 찾을 수 없습니다"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            existing_like = Like.objects.filter(
                user=request.user, comment=comment
            ).first()
            if existing_like:
                existing_like.delete()
                return Response(
                    {"message": "좋아요 취소"}, status=status.HTTP_204_NO_CONTENT
                )

            like = Like.objects.create(user=request.user, comment=comment)
            serializer = LikeSerializer(like)
            return Response({"message": "좋아요"}, status=status.HTTP_201_CREATED)

        return Response(
            {"error": "리뷰 또는 코멘트 ID가 필요합니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )
