import requests

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Product, PurchasedProduct
from .serializers import ProductSerializer, UserSerializer


# 상품페이지
class ProductAPIView(APIView):
    def get(self, request):
        products = Product.objects.all().order_by("-pk")
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 로그인 중인 유저 정보 반환
class LoginUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)


# 상품 상세페이지
class ProductDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Product, pk=pk)

    def get(self, request, product_pk):
        product = self.get_object(product_pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 장바구니
    @permission_classes([IsAuthenticated])
    def post(self, request, product_pk):
        product = self.get_object(product_pk)

        if product.consumer.filter(pk=request.user.pk).exists():
            product.consumer.remove(request.user)
            return Response({"detail": "장바구니에서 삭제"}, status=status.HTTP_200_OK)
        else:
            product.consumer.add(request.user)
            product.save()
            return Response({"detail": "장바구니에 추가"}, status=status.HTTP_200_OK)


# 결제 로직
class PaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 요청 데이터 가져오기
        data = request.data
        imp_uid = data.get("imp_uid")
        merchant_uid = data.get("merchant_uid")
        name = data.get("name")
        address = data.get("address")
        address2 = data.get("address2")
        products = data.get("products", [])
        total_amount = data.get("total_amount")

        # 필수 파라미터 검증
        if not imp_uid or not merchant_uid:
            return self.error_response(
                "imp_uid와 merchant_uid는 필수입니다.", status.HTTP_400_BAD_REQUEST
            )

        # 사전검증
        iamport_access_token = self.get_access_token()
        if not iamport_access_token:
            return self.error_response(
                "포트원 인증에 실패했습니다.", status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # 사후검증
        payment_data = self.get_payment_data(iamport_access_token, imp_uid)
        if not payment_data:
            return self.error_response(
                "결제 정보를 가져오지 못했습니다.", status.HTTP_400_BAD_REQUEST
            )

        # 결제 금액 확인
        if payment_data["amount"] != total_amount:
            return self.error_response(
                "결제 금액이 일치하지 않습니다.", status.HTTP_400_BAD_REQUEST
            )

        # 상품 처리 및 데이터 저장
        purchased_products = self.process_products(
            products, merchant_uid, address, address2
        )
        if isinstance(purchased_products, Response):  # 에러가 발생한 경우
            return purchased_products

        # 이메일 전송
        self.send_email(name, products, total_amount, merchant_uid, request.user.email)

        return Response(
            {"message": "결제 정보가 성공적으로 전달되었습니다."},
            status=status.HTTP_200_OK,
        )

    def error_response(self, message, status_code):
        return Response({"error": message}, status=status_code)

    def process_products(self, products, merchant_uid, address, address2):
        purchased_products = []

        for product_info in products:
            product_id = product_info.get("product_id")
            quantity = product_info.get("quantity")

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return self.error_response(
                    f"상품 ID {product_id}를 찾을 수 없습니다.",
                    status.HTTP_400_BAD_REQUEST,
                )

            # PurchasedProduct 테이블에 데이터 저장
            purchased_product = PurchasedProduct.objects.create(
                product=product,
                user=self.request.user,
                merchant_uid=merchant_uid,
                price=product.price * quantity,
                address=address,
                address2=address2,
                quantity=quantity,
            )
            purchased_products.append(purchased_product)

            # 장바구니에서 해당 상품 삭제
            product.consumer.remove(self.request.user)

        return purchased_products

    def send_email(self, name, products, total_amount, merchant_uid, recipient_email):
        product_list = ", ".join(
            [f"{p['product_name']} (수량: {p['quantity']})" for p in products]
        )
        send_mail(
            "[WEB 발신] 결제 완료 알림",
            f"결제가 완료되었습니다.\n구매자명: {name}\n주문상품: {product_list}\n결제금액: {total_amount} 원\n주문번호: {merchant_uid}\n",
            settings.EMAIL_HOST_USER,
            [recipient_email],
            fail_silently=False,
        )

    def get_access_token(self):
        url = "https://api.iamport.kr/users/getToken"
        data = {"imp_key": settings.IMP_KEY, "imp_secret": settings.IMP_SECRET}

        response = requests.post(url, data=data)
        return (
            response.json().get("response", {}).get("access_token")
            if response.status_code == 200
            else None
        )

    def get_payment_data(self, access_token, imp_uid):
        url = f"https://api.iamport.kr/payments/{imp_uid}"
        headers = {"Authorization": access_token}

        response = requests.get(url, headers=headers)
        return response.json().get("response") if response.status_code == 200 else None
