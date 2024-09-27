from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ReviewViewSet, CommentViewSet

router = DefaultRouter()
router.register(r"", ReviewViewSet, basename="review")

urlpatterns = [
    path("", include(router.urls)),
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
]
