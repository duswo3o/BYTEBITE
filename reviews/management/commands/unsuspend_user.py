from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = "일정 기간동안 정지된 유저들의 정지를 해제합니다."

    def add_arguments(self, parser):
        parser.add_argument(
            "duration", type=int, help="n일 이상 정지된 유저들의 정지를 해제합니다"
        )

    def handle(self, *args, **kwargs):
        duration_days = kwargs["duration"]
        threshold_date = timezone.now() - timedelta(days=duration_days)

        # 정지된 사용자를 찾고 정지 해제
        suspended_users = User.objects.filter(
            is_suspended=True, suspended_time__lt=threshold_date
        )

        for user in suspended_users:
            user.is_suspended = False
            user.suspended_time = None
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"정지해제가 성공적으로 이루어졌습니다: {user.nickname}"
                )
            )

        if not suspended_users.exists():
            self.stdout.write(self.style.WARNING("정지해제할 계정이 없습니다"))
