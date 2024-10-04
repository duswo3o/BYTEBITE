# 표준 라이브러리
from datetime import datetime, timedelta

# 서드파티 라이브러리
import requests

# Django 기능 및 프로젝트 관련
from django.conf import settings
from django.core.management.base import BaseCommand
from movies.models import Movie, Ranking


class Command(BaseCommand):
    help = "박스오피스의 데이터 베이스를 업데이트합니다. 일주일이 지난 데이터는 삭제합니다."

    API_URL = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"

    yesterday = datetime.now() - timedelta(days=1)
    date_to_delete = datetime.now() - timedelta(days=7)

    def handle(self, *args, **options):
        Ranking.objects.filter(crawling_date__lt=self.date_to_delete.date()).delete()
        Ranking.objects.filter(crawling_date__lt=datetime.now().date()).delete()

        params = {
            "key": settings.KOFIC_API_KEY,
            "targetDt": self.yesterday.strftime("%Y%m%d"),
        }

        response = requests.get(self.API_URL, params=params)

        if response.status_code == 200:
            data = response.json()["boxOfficeResult"]["dailyBoxOfficeList"]

        else:
            self.stdout.write(self.style.ERROR("API에 연결하는 데 실패했습니다."))
            return

        self.save_to_database(data)

    def save_to_database(self, data):
        for item in data:
            title = item["movieNm"].strip()
            rank = item["rank"]
            crawling_date = self.yesterday.strftime("%Y-%m-%d")

            movie = Movie.objects.filter(title=title).order_by("-prodyear").first()
            movie_pk = movie.pk if movie else None

            Ranking.objects.create(
                title=title,
                rank=rank,
                crawling_date=crawling_date,
                movie_pk=movie_pk,
            )
