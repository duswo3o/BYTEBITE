import requests

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Product
from .serializers import ProductSerializer, UserSerializer


class ProductAPIView(APIView):
    def get(self, request):
        products = Product.objects.all().order_by('-pk')
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LoginUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)


# 상품 상세페이지
class ProductDetailAPIView(APIView):
    def get(self, request, product_pk):
        product = get_object_or_404(Product, pk=product_pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 결제 관련 로직
class PaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print(request.data)

        imp_uid = request.data.get("imp_uid")
        merchant_uid = request.data.get("merchant_uid")
        name = request.data.get("name")

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
            f"결제가 완료되었습니다.\n이름: {name}\n주문번호: {merchant_uid}\n",
            [email],  # 수신자 이메일
            fail_silently=False,
        )

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
        product_id = merchant_uid[0]

        try:
            product = Product.objects.get(id=product_id)
            return product.price
        except Product.DoesNotExist:
            return None
