from datetime import datetime, timedelta

from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, get_user_model
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.decorators import api_view

from .serializers import (
    UserCreateSerializer,
    ChangePasswordSerializer,
    UpdateProfileSerializer,
    UserProfileSerializer,
)
from .models import User


# Create your views here
class UserAPIView(APIView):
    def post(self, request):
        if request.user.is_authenticated:
            return Response(
                {"message": "현재 로그인된 상태입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = request.data.get("email")
        user = User.objects.filter(email=email)
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

        user = User.objects.filter(email=email)
        message = False
        if user and user[0].is_active == False:
            user[0].is_active = True
            user[0].deactivate_time = None
            user[0].save()
            message = "계정이 활성화되었습니다."

        user = authenticate(email=email, password=password)

        if not user:
            return Response(
                {"error": "이메일 혹은 패스워드가 일치하지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        refresh = RefreshToken.for_user(user)
        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        user = get_user_model().objects.get(email=email)
        data["id"] = user.id
        data["email"] = user.email
        data["nickname"] = user.nickname
        data["gender"] = user.gender
        data["age"] = user.age
        data["bio"] = user.bio

        if message:
            data["message"] = message

        return Response(
            data=data,
            status=status.HTTP_200_OK,
        )


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
