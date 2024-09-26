from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ReviewsViewSet

router = DefaultRouter()
router.register(r"reviews", ReviewsViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
