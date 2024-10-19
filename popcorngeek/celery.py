from __future__ import absolute_import
import os
from celery import Celery

# Django의 settings 모듈을 Celery의 기본 설정으로 사용
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "popcorngeek.settings")

# Celery 인스턴스 생성
app = Celery("popcorngeek", broker="redis://redis:6379/0")

# 여기서 Django의 설정 파일에서 CELERY 관련 설정을 가져옴
app.config_from_object("django.conf:settings", namespace="CELERY")

# Django에서 설정한 모든 앱에서 비동기 태스크를 찾음
app.autodiscover_tasks()

app.conf.broker_url = (
    "redis://redis:6379/0"  # Docker에서 'redis' 컨테이너를 호스트로 사용
)
app.conf.update(
    broker_url="redis://redis:6379/0",  # Docker 환경에서 Redis 컨테이너 이름 사용
    result_backend="redis://redis:6379/0",
)
