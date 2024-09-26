from django.db import models
from django.conf import settings


class Reviews(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        null=True,  # 로그인 기능이 아직 개발 중이라 임시 방편
        blank=True,
    )

    def __str__(self):
        return self.content[:20]
