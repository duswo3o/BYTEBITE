from rest_framework import viewsets
from .models import Reviews, Comments
from .serializers import ReviewsSerializer, CommentSerializer
from rest_framework.permissions import AllowAny


class ReviewsViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Reviews.objects.all()
    serializer_class = ReviewsSerializer

    def perform_create(self, serializer):
        # serializer.save(author=self.request.user)
        if self.request.user.is_anonymous:
            serializer.save(author=None)
        else:
            serializer.save(author=self.request.user)


class CommentsViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Comments.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        review_id = self.kwargs.get("review_pk")
        serializer.save(review_id=review_id, author=None)

    def get_queryset(self):
        review_id = self.kwargs.get("review_pk")
        return self.queryset.filter(review_id=review_id)
