from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    ReviewViewSet,
    CommentViewSet,
    LikeViewSet,
    SentimentAPIView,
    transform_review,
    ReportAPIView,
)

urlpatterns = [
    path(
        "<int:movie_pk>/",
        ReviewViewSet.as_view({"get": "list", "post": "create"}),  # 리뷰 생성
        name="reviews-create",
    ),
    path(
        "detail/<int:pk>/",
        ReviewViewSet.as_view(
            {"get": "retrieve", "put": "update", "delete": "destroy"}
        ),  # 특정 리뷰 조회, 수정, 삭제
        name="reviews-detail",
    ),
    path(
        "<int:review_pk>/comments/",
        CommentViewSet.as_view({"get": "list", "post": "create"}),
        name="comments-list",
    ),
    path(
        "<int:review_pk>/comments/<int:pk>/",
        CommentViewSet.as_view(
            {"get": "retrieve", "put": "update", "delete": "destroy"}
        ),
        name="comments-detail",
    ),
    path(
        "likes/review/<int:review_id>/",
        LikeViewSet.as_view({"post": "create"}),
        name="like-review-create",
    ),
    path(
        "likes/comment/<int:comment_id>/",
        LikeViewSet.as_view({"post": "create"}),
        name="like-comment-create",
    ),
    path("transform-review/", transform_review, name="transform_review"),
    path("report/review/<int:review_id>/", ReportAPIView.as_view()),
    path("report/comment/<int:comment_id>/", ReportAPIView.as_view()),
    path("sentiment/<int:movie_pk>/", SentimentAPIView.as_view()),
]
