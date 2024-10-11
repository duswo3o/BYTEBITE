import requests

from django.conf import settings
from django.core.mail import send_mail

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


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
            "from@example.com",
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
        """
        이후에 실제 상품의 가격을 반환하도록 수정 예정
        """
        return 10
