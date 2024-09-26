from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ReviewsViewSet, CommentsViewSet

router = DefaultRouter()
router.register(r"", ReviewsViewSet, basename="reviews")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "<int:review_pk>/comments/",
        CommentsViewSet.as_view({"get": "list", "post": "create"}),
        name="comments-list",
    ),
    path(
        "<int:review_pk>/comments/<int:pk>/",
        CommentsViewSet.as_view(
            {"get": "retrieve", "put": "update", "delete": "destroy"}
        ),
        name="comments-detail",
    ),
]
