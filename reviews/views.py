# 표준 라이브러리
import json

# 서드파티 라이브러리
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
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
    SentimentSerializer,
)
from .sentiment_analysis import predict
from .tasks import send_email
from openai import OpenAI

client = OpenAI(api_key=settings.OPENAI_API_KEY)


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
        report_type = request.data.get("report_type")
        review_id = kwargs.get("review_id")
        comment_id = kwargs.get("comment_id")
        reporter = request.user

        if report_type == "spoiler":
            if review_id:
                return self.handle_spoiler_report(review_id, reporter, is_review=True)
            elif comment_id:
                return self.handle_spoiler_report(comment_id, reporter, is_review=False)
        else:
            if review_id:
                return self.handle_report(review_id, reporter, is_review=True)
            elif comment_id:
                return self.handle_report(comment_id, reporter, is_review=False)

        return Response(
            {"message": "신고 타입 또는 대상이 잘못되었습니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def handle_spoiler_report(self, object_id, reporter, is_review=True):
        obj = self.get_review_or_comment(object_id, is_review)
        report = Report.objects.filter(
            reporter=reporter,
            review=obj if is_review else None,
            comment=None if is_review else obj,
            report_type="spoiler",
        ).first()

        if report:
            return Response(
                {"message": "이미 신고한 리뷰/댓글입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        Report.objects.create(
            reporter=reporter,
            review=obj if is_review else None,
            comment=None if is_review else obj,
            report_type="spoiler",
        )
        report_count = Report.objects.filter(
            review=obj if is_review else None,
            comment=None if is_review else obj,
            report_type="spoiler",
        ).count()

        if report_count == 7:
            obj.is_spoiler = True
            obj.save()
            send_email.delay(
                subject="popcorngeek에서 작성한 리뷰가 스포방지 처리 되었습니다.",
                message=f"귀하의 리뷰/댓글이 {report_count}회 신고되어 스포방지 처리 되었습니다.",
                recipient=obj.author.email,
            )
            Report.objects.filter(
                review=obj if is_review else None, comment=None if is_review else obj
            ).delete()

        return Response(
            {
                "message": f"해당 {'리뷰' if is_review else '댓글'}가 신고 완료되었습니다."
            },
            status=status.HTTP_200_OK,
        )

    def handle_report(self, object_id, reporter, is_review=True):
        obj = self.get_review_or_comment(object_id, is_review)
        report = Report.objects.filter(
            reporter=reporter,
            review=obj if is_review else None,
            comment=None if is_review else obj,
        ).first()

        if report:
            return Response(
                {"message": "이미 신고한 리뷰/댓글입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        Report.objects.create(
            reporter=reporter,
            review=obj if is_review else None,
            comment=None if is_review else obj,
        )
        report_count = Report.objects.filter(
            review=obj if is_review else None, comment=None if is_review else obj
        ).count()

        # 경고 및 삭제 로직
        if report_count == 5:
            send_email.delay(
                subject=f"popcorngeek에서 작성한 {'리뷰' if is_review else '댓글'}가 신고되었습니다.",
                message=f"귀하의 {'리뷰' if is_review else '댓글'}가 {report_count}회 신고되었습니다.",
                recipient=obj.author.email,
            )
        elif report_count >= 10:
            obj.delete()
            send_email.delay(
                subject=f"popcorngeek에서 작성한 {'리뷰' if is_review else '댓글'}가 지속적으로 신고되어 삭제되었습니다.",
                message=f"귀하의 {'리뷰' if is_review else '댓글'}가 {report_count}회 신고되어 삭제되었습니다.",
                recipient=obj.author.email,
            )
            self.handle_user_admonition(obj.author)

        return Response(
            {
                "message": f"해당 {'리뷰' if is_review else '댓글'}가 신고 완료되었습니다."
            },
            status=status.HTTP_200_OK,
        )

    def handle_user_admonition(self, writer):
        writer.admonition += 1
        if writer.admonition >= 5:
            writer.is_suspended = True
            writer.suspended_time = timezone.now()
            send_email.delay(
                subject="popcorngeek에서 귀하의 계정이 정지되었습니다.",
                message="popcorngeek에서 귀하는 경고가 누적되어 계정이 정지되었습니다.",
                recipient=writer.email,
            )
        writer.save()

    def get_review_or_comment(self, object_id, is_review=True):
        if is_review:
            return get_object_or_404(Review, id=object_id)
        return get_object_or_404(Comment, id=object_id)


class SentimentAPIView(APIView):
    def get(self, request, movie_pk):
        positive = (
            Review.objects.filter(movie=movie_pk, is_positive=1)
            .annotate(like_count=models.Count("review_likes"))
            .order_by("-like_count")[:3]
        )
        negative = (
            Review.objects.filter(movie=movie_pk, is_positive=0)
            .annotate(like_count=models.Count("review_likes"))
            .order_by("-like_count")[:3]
        )

        positive_serializer = SentimentSerializer(positive, many=True)
        negative_serializer = SentimentSerializer(negative, many=True)

        sentiment = {
            "positive_review": positive_serializer.data,
            "negative_review": negative_serializer.data,
        }

        return Response(sentiment, status=status.HTTP_200_OK)
