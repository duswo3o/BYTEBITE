# 서드파티 라이브러리
from rest_framework import viewsets, permissions, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

# Django 기능 및 프로젝트 관련
from .models import Review, Comment, Like
from .serializers import ReviewSerializer, CommentSerializer, LikeSerializer
from .permissions import IsAuthorOrReadOnly
from movies.models import Movie
from openai import OpenAI
import os
from dotenv import load_dotenv
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)


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
                return Response({"message": "좋아요 취소"}, status=status.HTTP_200_OK)

            like = Like.objects.create(user=request.user, review=review)
            serializer = LikeSerializer(like)
            return Response({"message": "좋아요!"}, status=status.HTTP_201_CREATED)

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
                return Response({"message": "좋아요 취소"}, status=status.HTTP_200_OK)

            like = Like.objects.create(user=request.user, comment=comment)
            serializer = LikeSerializer(like)
            return Response({"message": "좋아요!"}, status=status.HTTP_201_CREATED)

        return Response(
            {"error": "리뷰 또는 코멘트 ID가 필요합니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )


@csrf_exempt
@require_http_methods(["POST"])
def transform_review(request):
    data = json.loads(request.body)
    content = data.get("content")
    style = data.get("style", "기본")  # 기본 스타일

    # 말투에 따라 다른 시스템 메시지 설정
    system_messages = {
        "조선시대": "조선시대 말투로 변경해줘. 100~200자 사이로 변경해.",
        "평론가": "너는 입력된 내용을 비유와 은유를 섞어서 평론가처럼 바꿔줘. 100~200자 사이로 변경해.",
        "Mz": "이모지 섞어서 요즘 mz세대 말투로 변경해줘 100~200자 사이로 변경해.",
        "기본": "기본",
    }

    system_message = system_messages.get(style, "기본")

    # OpenAI API 호출
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": system_message,
            },
            {"role": "user", "content": content},
        ],
    )

    transformed_content = completion.choices[0].message.content
    return JsonResponse({"transformedContent": transformed_content})
