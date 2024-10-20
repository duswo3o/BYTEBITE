import environ
from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import ObjectDoesNotExist


env = environ.Env(
    # 기본값을 설정하거나 강제할 수 있습니다.
    DEBUG=(bool, False)
)

User = get_user_model()


@shared_task
def send_activation_email(user_data):
    # 유저 데이터에서 사용자 ID 가져오기
    user_id = user_data["id"]
    user_email = user_data["email"]

    try:
        # User 객체를 가져옵니다.
        user = User.objects.get(pk=user_id)

        # 이메일 전송을 위한 토큰 생성
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        subject = "Activate Your Account"
        message = render_to_string(
            "accounts/account_active_email.html",  # 이메일 템플릿 경로
            {
                "user": user,
                "domain": env("domain"),  # 도메인 설정
                "uid": uid,
                "token": token,
            },
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,  # 발신자 이메일
            [user_email],  # 수신자 이메일
            fail_silently=False,
        )

    except ObjectDoesNotExist:
        print(f"User with id {user_id} does not exist.")
    except Exception as e:
        print(f"An error occurred while sending the email: {e}")
