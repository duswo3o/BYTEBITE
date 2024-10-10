from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = "일정 기간동안 비활성화된 유저들의 계정을 삭제합니다"

    def add_arguments(self, parser):
        parser.add_argument(
            "duration", type=int, help="n일 이상 계정이 비활성화된 계정을 삭제합니다"
        )

    def handle(self, *args, **kwargs):
        duration_days = kwargs["duration"]
        threshold_date = timezone.now() - timedelta(days=duration_days)

        # 비활성화된 계정을 찾고 삭제
        deactivate_users = User.objects.filter(
            is_active=False, deactivate_time__lt=threshold_date
        )

        for user in deactivate_users:
            user.delete()
            self.stdout.write(
                self.style.SUCCESS(f"{user.nickname} 계정이 삭제되었습니다.")
            )

        if not deactivate_users.exists():
            self.stdout.write(self.style.WARNING("삭제할 계정이 없습니다."))
