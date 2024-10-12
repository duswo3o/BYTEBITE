from datetime import datetime, timedelta

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import get_object_or_404, render
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
import requests
import os
from dotenv import load_dotenv
from django.shortcuts import redirect
from django.http import JsonResponse


from .serializers import (
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
        if user and user[0].is_active == False:
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

        if not request.user.check_password(password):
            return Response(
                {"password": "패스워드가 일치하지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.user.is_active = False
        # 9시간을 더해줘야 한국 표준시가 됨
        request.user.deactivate_time = datetime.now() + timedelta(hours=9)  # 현재시간
        request.user.save()
        return Response(
            {"message": "회원정보가 비활성화 되었습니다."}, status=status.HTTP_200_OK
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


@api_view(["POST"])
def delete_user(request):
    deactivate_users = User.objects.filter(is_active=False)
    now = datetime.now()
    delete_cnt = 0
    for user in deactivate_users:
        # 테스트용 2분
        if (now - user.deactivate_time.replace(tzinfo=None)).seconds > 120:
            user.delete()
            delete_cnt += 1

    return Response(
        {"message": f"{delete_cnt}개의 계정이 삭제되었습니다."},
        status=status.HTTP_200_OK,
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

    def post(self, request, user_pk):
        user = get_object_or_404(User, pk=user_pk)
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


class PaymentAPIView(RetrieveAPIView):
    def post(self, request, *args, **kwargs):
        # 결제 정보를 터미널에 출력
        print(request.data)

        # 테스트 응답
        return Response(
            {"message": "결제 정보가 성공적으로 전달되었습니다."},
            status=status.HTTP_200_OK,
        )


# 소셜로그인
load_dotenv()
KAKAO_REST_API_KEY = os.getenv("KAKAO_API_KEY")
BASE_URL = "http://127.0.0.1:8000"
FRONTEND_BASE_URL = "http://127.0.0.1:5500"


class KakaoLoginView(APIView):
    def get(self, request):
        client_id = KAKAO_REST_API_KEY
        redirect_uri = f"{BASE_URL}/api/v1/accounts/kakao/callback/"
        return redirect(
            f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
        )


class KakaoCallbackView(APIView):
    def get(self, request):
        code = request.GET.get("code")
        access_token = self.get_kakao_token(code)
        user_info = self.get_kakao_user_info(access_token)
        user_data = self.get_or_create_user(user_info)
        tokens = self.create_jwt_token(user_data)
        nickname = user_info["properties"]["nickname"]
        email = user_info["kakao_account"]["email"]

        redirect_url = (
            f"{FRONTEND_BASE_URL}/front/accounts/profile.html"
            f"?access_token={tokens['access']}&refresh_token={tokens['refresh']}"
            f"&nickname={nickname}&email={email}"
        )
        return redirect(redirect_url)

    def get_kakao_token(self, code):
        client_id = KAKAO_REST_API_KEY
        redirect_uri = f"{BASE_URL}/api/v1/accounts/kakao/callback/"
        token_url = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "code": code,
        }
        response = requests.post(token_url, data=data)
        return response.json().get("access_token")

    def get_kakao_user_info(self, access_token):
        user_info_url = "https://kapi.kakao.com/v2/user/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(user_info_url, headers=headers)
        return response.json()

    def get_or_create_user(self, user_info):
        # 카카오 ID 확인
        kakao_id = user_info.get("id")
        if not kakao_id:
            raise ValueError("Kakao 사용자 정보에서 'id'를 찾을 수 없습니다.")

        # 이메일 확인
        email = user_info["kakao_account"].get("email")
        if not email:
            raise ValueError("Kakao에서 이메일이 제공되지 않았습니다.")

        # 닉네임 확인
        nickname = user_info["properties"].get("nickname")
        if not nickname:
            nickname = user_info["kakao_account"]["profile"].get("nickname")

        if not nickname:
            raise ValueError("Kakao에서 닉네임을 가져오지 못했습니다.")
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "email": email,
                "nickname": nickname,
            },
        )

        if created:
            user.set_unusable_password()
            user.save()

        return user

    def create_jwt_token(self, user_data):
        if isinstance(user_data, dict):
            email = user_data.get("email")
            user = User.objects.get(email=email)
        else:
            user = user_data

        # JWT 토큰 생성
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
