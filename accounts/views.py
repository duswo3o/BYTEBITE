import os

import requests

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    BasketSerializer,
    ChangePasswordSerializer,
    UpdateProfileSerializer,
    UserCreateSerializer,
    UserProfileSerializer,
    UserSigninSerializer,
)


User = get_user_model()


# Create your views here
class UserAPIView(APIView):
    def post(self, request):
        if request.user.is_authenticated:
            return Response(
                {"message": "현재 로그인된 상태입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = request.data.get("email")
        user = User.objects.filter(email=email).first()

        # 이미 존재하는 사용자가 있고, 그 사용자가 비활성화된 상태인 경우
        if user and user.is_active == False:
            return Response(
                {
                    "message": "계정이 비활성화 상태입니다. 로그인해서 계정을 활성화 할 수 있습니다."
                }
            )

        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @permission_classes([IsAuthenticated])
    def delete(self, request):
        password = request.data.get("password")

        if (not request.user.has_usable_password()) or (
            request.user.check_password(password)
        ):
            request.user.is_active = False
            request.user.deactivate_time = timezone.now()  # 현재시간
            request.user.save()
            return Response(
                {"message": "회원정보가 비활성화 되었습니다."},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"password": "패스워드가 일치하지 않습니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @permission_classes([IsAuthenticated])
    def put(self, request):
        user = request.user
        serializer = UpdateProfileSerializer(
            instance=user, data=request.data, partial=True, context=user
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserActivate(APIView):
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = urlsafe_base64_decode(uidb64)  # .decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        token_generator = PasswordResetTokenGenerator()
        if user is not None and token_generator.check_token(user, token):
            user.is_active = True
            user.deactivate_time = None
            user.save()
            return Response(
                {"message": "계정이 활성화되었습니다. 다시 로그인을 시도해주세요."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": "링크가 유효하지 않거나 이미 사용되었습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserSigninAPIView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        serializer = UserSigninSerializer(data=request.data)
        if serializer.is_valid():
            # 로그인 성공 후의 추가 작업 (예: JWT 토큰 생성 등)
            user = authenticate(email=email, password=password)
            refresh = RefreshToken.for_user(user)
            data = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
            signin_user = User.objects.get(email=email)
            data["id"] = signin_user.id
            data["email"] = signin_user.email
            data["nickname"] = signin_user.nickname
            data["gender"] = signin_user.gender
            data["age"] = signin_user.age
            data["bio"] = signin_user.bio

            return Response(data=data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSignoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"token": "refresh token이 필요합니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

        except:
            return Response(
                {"token": "유효하지 않은 token 입니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"message": "로그아웃 되었습니다"}, status=status.HTTP_200_OK)


class UserChangePasswordAPIView(APIView):
    def put(self, request):
        user = User.objects.get(pk=request.user.pk)
        serializer = ChangePasswordSerializer(
            instance=user, data=request.data, context=user
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"password": "패스워드가 변경되었습니다."}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserFollowAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, nickname):
        user = get_object_or_404(User, nickname=nickname)
        me = request.user

        if me == user:
            return Response(
                {"message": "나를 팔로우 할 수 없습니다"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if me in user.followers.all():
            user.followers.remove(me)
            return Response(
                {"message": f"{user.nickname}을/를 언팔로우 하였습니다"},
                status=status.HTTP_200_OK,
            )
        else:
            user.followers.add(me)
            return Response(
                {"message": f"{user.nickname}을/를 팔로우 하였습니다"},
                status=status.HTTP_200_OK,
            )


class UserProfileAPIView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = "nickname"


class UserBasketAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        serializer = BasketSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 소셜로그인
NAVER_CLIENT_SECRET = settings.NAVER_CLIENT_SECRET
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
BASE_URL = "http://127.0.0.1:8000"
FRONTEND_BASE_URL = "http://127.0.0.1:5500"


class SocialLoginView(APIView):
    def get(self, request, provider):
        if provider == "kakao":
            client_id = settings.KAKAO_API_KEY
            redirect_uri = f"{BASE_URL}/api/v1/accounts/social/callback/{provider}/"
            auth_url = (
                f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}"
                f"&redirect_uri={redirect_uri}&response_type=code"
            )
        elif provider == "naver":
            client_id = settings.NAVER_API_KEY
            redirect_uri = f"{BASE_URL}/api/v1/accounts/social/callback/{provider}/"
            auth_url = (
                f"https://nid.naver.com/oauth2.0/authorize?client_id={client_id}"
                f"&redirect_uri={redirect_uri}&response_type=code"
            )
        elif provider == "google":
            client_id = settings.GOOGLE_CLIENT_ID
            redirect_uri = f"{BASE_URL}/api/v1/accounts/social/callback/{provider}/"
            scope = "email profile"
            auth_url = (
                f"https://accounts.google.com/o/oauth2/auth?client_id={client_id}"
                f"&redirect_uri={redirect_uri}&response_type=code&scope={scope}"
            )
        else:
            return Response(
                {"error": "지원되지 않는 소셜 로그인 제공자입니다."}, status=400
            )

        return redirect(auth_url)


class SocialCallbackView(APIView):
    def get(self, request, provider):
        code = request.GET.get("code")

        access_token = self.get_token(provider, code)
        user_info = self.get_user_info(provider, access_token)

        if provider == "kakao":
            email = user_info["kakao_account"]["email"]
            nickname = user_info["properties"]["nickname"]
        elif provider == "naver":
            email = user_info["response"]["email"]
            nickname = user_info["response"]["nickname"]
        elif provider == "google":
            email = user_info["email"]
            nickname = user_info["name"]

        user_data = self.get_or_create_user(provider, email, nickname)
        tokens = self.create_jwt_token(user_data)

        redirect_url = (
            f"{FRONTEND_BASE_URL}/front/accounts/profile.html"
            f"?access_token={tokens['access']}&refresh_token={tokens['refresh']}"
            f"&nickname={nickname}&email={email}"
        )
        return redirect(redirect_url)

    def get_token(self, provider, code):
        if provider == "kakao":
            token_url = "https://kauth.kakao.com/oauth/token"
            client_id = settings.KAKAO_API_KEY
        elif provider == "naver":
            token_url = "https://nid.naver.com/oauth2.0/token"
            client_id = settings.NAVER_API_KEY
        elif provider == "google":
            token_url = "https://oauth2.googleapis.com/token"
            client_id = settings.GOOGLE_CLIENT_ID
        else:
            raise ValueError("지원되지 않는 소셜 로그인 제공자입니다.")

        redirect_uri = f"{BASE_URL}/api/v1/accounts/social/callback/{provider}/"
        data = {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "code": code,
        }

        if provider in ["naver", "google"]:
            data["client_secret"] = os.getenv(f"{provider.upper()}_CLIENT_SECRET")

        response = requests.post(token_url, data=data)
        return response.json().get("access_token")

    def get_user_info(self, provider, access_token):
        if provider == "kakao":
            user_info_url = "https://kapi.kakao.com/v2/user/me"
        elif provider == "naver":
            user_info_url = "https://openapi.naver.com/v1/nid/me"
        elif provider == "google":
            user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        else:
            raise ValueError("지원되지 않는 소셜 로그인 제공자입니다.")

        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(user_info_url, headers=headers)
        return response.json()

    def get_or_create_user(self, provider, email, nickname):
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "nickname": nickname,
            },
        )
        if created:
            user.set_unusable_password()
            user.save()

        if user:
            user.is_active = True
            user.save()

        return user

    def create_jwt_token(self, user_data):
        if isinstance(user_data, dict):
            email = user_data.get("email")
            user = User.objects.get(email=email)
        else:
            user = user_data

        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
