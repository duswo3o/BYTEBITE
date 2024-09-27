from rest_framework import viewsets
from .models import Review, Comment
from .serializers import ReviewSerializer, CommentSerializer
from rest_framework.permissions import AllowAny


class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        # serializer.save(author=self.request.user)
        if self.request.user.is_anonymous:
            serializer.save(author=None)
        else:
            serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        review_id = self.kwargs.get("review_pk")
        serializer.save(review_id=review_id, author=None)

    def get_queryset(self):
        review_id = self.kwargs.get("review_pk")
        return self.queryset.filter(review_id=review_id)
