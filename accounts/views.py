from datetime import datetime, timedelta

import requests

from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

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


class PaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 결제 정보를 터미널에 출력
        print(request.data)

        imp_uid = request.data.get("imp_uid")
        merchant_uid = request.data.get("merchant_uid")
        name = request.data.get("name")
        address = request.data.get("address")
        tel = request.data.get("tel")

        if not imp_uid or not merchant_uid:
            return Response(
                {"error": "imp_uid와 merchant_uid는 필수입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 사전검증
        iamport_access_token = self.get_access_token()
        if not iamport_access_token:
            return Response(
                {"error": "포트원 인증에 실패했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 사후검증
        payment_data = self.get_payment_data(iamport_access_token, imp_uid)
        if not payment_data:
            return Response(
                {"error": "결제 정보를 가져오지 못했습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 포트원에서 확인한 결제 금액
        amount_paid = payment_data["amount"]
        # 서버에서 저장된 결제 금액
        amount_to_pay = self.get_order_amount(merchant_uid)

        if amount_paid != amount_to_pay:
            return Response(
                {"error": "결제 금액이 일치하지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # JWT 토큰에서 이메일 추출
        email = request.user.email

        # 이메일 전송
        send_mail(
            "[WEB 발신] 결제 완료 알림",
            f"결제가 완료되었습니다.\n이름: {name}\n주소: {address}\n전화번호: {tel}\n",
            "from@example.com",  # 발신자 이메일
            [email],  # 수신자 이메일
            fail_silently=False,
        )

        # 테스트 응답
        return Response(
            {"message": "결제 정보가 성공적으로 전달되었습니다."},
            status=status.HTTP_200_OK,
        )

    # 엑세스 키 발급 함수
    def get_access_token(self):
        url = "https://api.iamport.kr/users/getToken"
        data = {"imp_key": settings.IMP_KEY, "imp_secret": settings.IMP_SECRET}

        response = requests.post(url, data=data)
        if response.status_code != 200:
            return None
        result = response.json()
        return result["response"]["access_token"]

    # 결제정보 조회 함수
    def get_payment_data(self, access_token, imp_uid):
        url = f"https://api.iamport.kr/payments/{imp_uid}"
        headers = {"Authorization": access_token}

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return None
        result = response.json()
        return result["response"]

    # 결제금액 확인
    def get_order_amount(self, merchant_uid):
        """
        이후에 실제 상품의 가격을 반환하도록 수정 예정
        """
        return 10
