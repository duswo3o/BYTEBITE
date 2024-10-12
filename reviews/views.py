# 표준 라이브러리
import os
import json

# 서드파티 라이브러리
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import permissions, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Django 기능 및 프로젝트 관련
from .models import Review, Comment, Like, Report
from movies.models import Movie
from .permissions import IsAuthorOrReadOnly, IsActiveAndNotSuspended
from .serializers import (
    CommentSerializer,
    ReviewSerializer,
    LikeSerializer,
)
from .sentiment_analysis import predict
from openai import OpenAI
from dotenv import load_dotenv

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
            permission_classes = [IsActiveAndNotSuspended]
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
        review = serializer.validated_data.get("content")
        is_positive = predict(review)
        serializer.save(
            author=self.request.user,
            movie=movie,
            is_positive=is_positive,
        )


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [AllowAny]
        elif self.action == "create":
            permission_classes = [IsActiveAndNotSuspended]
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
    permission_classes = [IsActiveAndNotSuspended]

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


class ReportAPIView(APIView):
    permission_classes = [IsActiveAndNotSuspended]

    def post(self, request, **kwargs):
        review_id = kwargs.get("review_id")
        comment_id = kwargs.get("comment_id")
        reporter = request.user

        if review_id:
            review = get_object_or_404(Review, id=review_id)
            report = Report.objects.filter(reporter=reporter, review=review).first()
            if report:
                return Response(
                    {"message": "이미 신고한 리뷰입니다"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            report = Report.objects.create(reporter=reporter, review=review)
            report_count = Report.objects.filter(review=review).count()
            writer = review.author

            # 작성자에게 경고 이메일 전송
            if report_count == 5:
                send_mail(
                    subject="popcorngeek에서 작성한 리뷰가 신고되었습니다.",
                    message=f"귀하의 리뷰('{review.movie}')가 {report_count}회 신고되었습니다.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[writer.email],
                    fail_silently=False,
                )

            # 작성자에게 리뷰 삭제 이메일 전송
            elif report_count >= 10:
                review.delete()
                send_mail(
                    subject="popcorngeek에서 작성한 리뷰가 지속적으로 신고되어 삭제되었습니다.",
                    message=f"귀하의 리뷰('{review.movie}')가 {report_count}회 신고되어 삭제되었습니다.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[writer.email],
                    fail_silently=False,
                )
                writer.admonition += 1
                if writer.admonition >= 5:
                    writer.is_suspended = True
                    writer.suspended_time = timezone.now()
                    send_mail(
                        subject="popcorngeek에서 귀하의 계정이 정지되었습니다.",
                        message="popcoengeek에서 귀하는 경고가 누적되어 계정이 정지되었습니다.",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[writer.email],
                        fail_silently=False,
                    )
                review.author.save()

            return Response(
                {"message": "해당 리뷰가 신고 완료되었습니다."},
                status=status.HTTP_200_OK,
            )

        elif comment_id:
            comment = get_object_or_404(Comment, id=comment_id)
            report = Report.objects.filter(reporter=reporter, comment=comment).first()
            if report:
                return Response(
                    {"message": "이미 신고한 댓글입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            report = Report.objects.create(reporter=reporter, comment=comment)
            report_count = Report.objects.filter(comment=comment).count()
            writer = comment.author

            # 작성자에게 경고 이메일 전송
            if report_count == 5:
                send_mail(
                    subject="popcorngeek에서 작성한 리뷰가 신고되었습니다.",
                    message=f"귀하의 댓글('{comment.content[10:]}...')가 {report_count}회 신고되었습니다.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[writer.email],
                    fail_silently=False,
                )

            # 작성자에게 댓글 삭제 이메일 전송
            elif report_count >= 10:
                comment.delete()
                send_mail(
                    subject="popcorngeek에서 작성한 리뷰가 지속적으로 신고되어 삭제되었습니다.",
                    message=f"귀하의 댓글('{comment.content[10:]}...')가 {report_count}회 신고되어 삭제되었습니다.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[writer.email],
                    fail_silently=False,
                )
                writer.admonition += 1
                if writer.admonition >= 5:  # 테스트용 2회
                    writer.is_suspended = True
                    writer.suspended_time = timezone.now()
                    send_mail(
                        subject="popcorngeek에서 귀하의 계정이 정지되었습니다.",
                        message="popcoengeek에서 귀하는 경고가 누적되어 계정이 정지되었습니다.",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[writer.email],
                        fail_silently=False,
                    )
                comment.author.save()

            return Response(
                {"message": "해당 댓글이 신고 완료되었습니다."},
                status=status.HTTP_200_OK,
            )
