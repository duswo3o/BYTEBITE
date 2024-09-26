from rest_framework import viewsets
from .models import Reviews
from .serializers import ReviewsSerializer
from rest_framework.permissions import AllowAny


class ReviewsViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Reviews.objects.all()
    serializer_class = ReviewsSerializer

    def perform_create(self, serializer):
        # serializer.save(author=self.request.user)
        # 인증되지 않은 사용자는 author를 None으로 설정
        if self.request.user.is_anonymous:
            serializer.save(author=None)  # 또는 기본값으로 임시 사용자 설정
        else:
            serializer.save(author=self.request.user)
