from datetime import datetime, timedelta

import django
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


# Create your models here.
# Helper Class : 모델을 관리하는 클래스로 user 생성과 superuer를 생성할 때의 행위를 지정
class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError({"email": "이메일은 필수 입력항목입니다."})
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


# Custom User Model
class User(AbstractUser):
    GENDER_CHOICES = [("M", "남자"), ("F", "여자")]

    # 비활성화 필드
    username = None
    first_name = None
    last_name = None

    # 필수 필드
    email = models.EmailField(unique=True, blank=False)
    USERNAME_FIELD = "email"  # uesrname 대신 email을 ID로 사용
    REQUIRED_FIELDS = []
    objects = UserManager()  # custon UserManager 사용을 명시함
    nickname = models.CharField(max_length=20, unique=True)

    # 선택 필드
    gender = models.CharField(
        choices=GENDER_CHOICES, max_length=1, blank=True, null=True
    )
    age = models.PositiveIntegerField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    followings = models.ManyToManyField(
        to="self", related_name="followers", symmetrical=False
    )

    # 비활성화된 시점을 저장하여 일정 기간동안만 해당 유저의 정보를 보관하기위해 필드 추가
    deactivate_time = models.DateTimeField(
        default=django.utils.timezone.now, blank=True, null=True)

    # 유저가 작성한 라뷰 또는 댓글이 누적신고 n회 이상으로 삭제조치 되었을 때 증가
    admonition = models.PositiveIntegerField(default=0)
    is_suspended = models.BooleanField(default=False)
    suspended_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.nickname
