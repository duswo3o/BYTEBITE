# 표준 라이브러리
from datetime import datetime, timedelta

# 서드파티 라이브러리
import requests

# Django 기능 및 프로젝트 관련
from django.conf import settings
from django.core.management.base import BaseCommand
from movies.models import Movie, Ranking


class Command(BaseCommand):
    help = "개봉예정인 영화와 작일의 박스오피스 순위를 업데이트합니다."

    API_URL = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"

    YESTERDAY = datetime.now() - timedelta(days=1)
    DELETE_DATE = datetime.now() - timedelta(days=8)

    def handle(self, *args, **options):
        # 8일 이전의 박스오피스 순위 삭제
        Ranking.objects.filter(crawling_date__lt=self.DELETE_DATE.date()).delete()
        # 작일 박스오피스 순위 삭제(중복 실행 시 오류 방지)
        Ranking.objects.filter(crawling_date=self.YESTERDAY.date()).delete()

        # 작일 기준 박스오피스 순위 업데이트
        self.save_to_database()

    def save_to_database(self):
        params = {
            "key": settings.KOFIC_API_KEY,
            "targetDt": self.YESTERDAY.strftime("%Y%m%d"),
        }

        response = requests.get(self.API_URL, params=params)

        if response.status_code == 200:
            data = response.json()["boxOfficeResult"]["dailyBoxOfficeList"]

        else:
            self.stdout.write(self.style.ERROR("API에 연결하는 데 실패했습니다."))
            return

        for item in data:
            title = item["movieNm"].strip().upper()
            rank = item["rank"]
            crawling_date = self.YESTERDAY.strftime("%Y-%m-%d")

            movie = Movie.objects.filter(title=title).order_by("-prodyear").first()
            movie_pk = movie.pk if movie else None

            Ranking.objects.create(
                title=title,
                rank=rank,
                crawling_date=crawling_date,
                movie_pk=movie_pk,
            )
