from django.db import models
from django.conf import settings
from movies.models import Movie


class Review(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, related_name="reviews")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    is_spoiler = models.BooleanField(default=False)
    private = models.BooleanField(default=False)
    is_positive = models.BooleanField(null=True)

    def __str__(self):
        return self.content[:20]

    def like_count(self):
        return self.review_likes.count()

    def comment_count(self):
        return self.comments.all().count()


class Comment(models.Model):
    review = models.ForeignKey(
        "Review", on_delete=models.CASCADE, related_name="comments"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
        null=True,
        blank=True,
    )
    is_spoiler = models.BooleanField(default=False)

    def __str__(self):
        return self.content[:20]

    def like_count(self):
        return self.comment_likes.count()


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="likes_given",
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="review_likes",
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="comment_likes",
    )

    class Meta:
        unique_together = ("user", "review", "comment")


class Report(models.Model):
    reporter = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="reported_user",
    )
    review = models.ForeignKey(
        to=Review,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reported_review",
    )
    comment = models.ForeignKey(
        to=Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reported_comment",
    )

    report_type = models.CharField(max_length=13, default="inappropriate")

    class Meta:
        # 중복 신고가 불가능하도록 여러 필드에 대해 unique 옵션 설정
        unique_together = ["reporter", "review", "comment"]

    def __str__(self):
        if self.review:
            return (
                f"{self.reporter.nickname}님이 {self.review.id} 리뷰를 신고하였습니다."
            )
        elif self.comment:
            return (
                f"{self.reporter.nickname}님이 {self.comment.id} 댓글을 신고하였습니다."
            )
