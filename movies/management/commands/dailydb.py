# 표준 라이브러리
from datetime import datetime, timedelta

# 서드파티 라이브러리
import requests

# Django 기능 및 프로젝트 관련
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from movies.models import Genre, Movie, Ranking, Staff


class Command(BaseCommand):
    help = "개봉예정인 영화와 작일의 박스오피스 순위를 업데이트합니다."

    RANK_API_URL = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    API_URL = "http://api.koreafilm.or.kr/openapi-data2/wisenut/search_api/search_json2.jsp?collection=kmdb_new2"

    YESTERDAY = datetime.now() - timedelta(days=1)
    DEFAULT_UPDATE_DATE = datetime.now() + timedelta(days=8)
    DELETE_DATE = datetime.now() - timedelta(days=8)

    def add_arguments(self, parser):
        # 오직 UPDATE_DATE만 인자로 받도록 설정
        parser.add_argument(
            "--update-date", type=str, help="--update-date는 YYYY-MM-DD 형식 (선택)"
        )

    def handle(self, *args, **options):
        update_date_str = options.get("update_date")

        if update_date_str:
            try:
                self.UPDATE_DATE = datetime.strptime(update_date_str, "%Y-%m-%d")
            except ValueError:
                self.stdout.write(
                    self.style.ERROR("Invalid update date format. Use YYYY-MM-DD.")
                )
                return
        else:
            self.UPDATE_DATE = self.DEFAULT_UPDATE_DATE

        # 8일 이전의 박스오피스 순위 삭제
        Ranking.objects.filter(crawling_date__lt=self.DELETE_DATE.date()).delete()
        # 작일 박스오피스 순위 삭제(중복 실행 시 오류 방지)
        Ranking.objects.filter(crawling_date=self.YESTERDAY.date()).delete()

        # 8일 후 개봉 예정 영화의 정보 입력
        self.update_date()

        # 작일 기준 박스오피스 순위 업데이트
        self.update_ranking()

    def update_ranking(self):
        params = {
            "key": settings.KOFIC_API_KEY,
            "targetDt": self.YESTERDAY.strftime("%Y%m%d"),
        }

        response = requests.get(self.RANK_API_URL, params=params)

        if response.status_code == 200:
            data = response.json()["boxOfficeResult"]["dailyBoxOfficeList"]

        else:
            self.stdout.write(self.style.ERROR("API에 연결하는 데 실패했습니다."))
            return

        for item in data:
            title = item["movieNm"].strip().upper()
            rank = item["rank"]
            crawling_date = self.YESTERDAY.strftime("%Y-%m-%d")
            release_date = item["openDt"]

            movie = Movie.objects.filter(title=title, release_date=release_date).first()

            Ranking.objects.create(
                title=title,
                rank=rank,
                crawling_date=crawling_date,
                movie_pk=movie,
            )

    def update_date(self):
        params = {
            "ServiceKey": settings.KMDB_API_KEY,
            "listCount": 100,
            "detail": "Y",
            "releaseDts": self.UPDATE_DATE.strftime("%Y%m%d"),
            "releaseDte": self.UPDATE_DATE.strftime("%Y%m%d"),
        }

        response = requests.get(self.API_URL, params=params)

        if response.status_code == 200:
            data = response.json()["Data"][0]

        else:
            self.stdout.write(self.style.ERROR("API에 연결하는 데 실패했습니다."))
            return

        if data["Count"] != 0:
            self.save_to_database(data["Result"])

    def save_to_database(self, data):
        for item in data:
            movie_cd = item["movieSeq"]
            title = item["title"].strip().upper()
            runtime = item["runtime"] if item["runtime"] else None
            rating = item["rating"] if item["rating"] else None
            plot = item["plots"]["plot"][0]["plotText"]
            release_date = self.UPDATE_DATE.strftime("%Y-%m-%d")
            poster = item["posters"].split("|")[0] if item["posters"] else None

            genres = item["genre"].split(",")
            genre_objects = []

            for genre_name in genres:
                genre_name = genre_name.strip()
                genre, created = Genre.objects.get_or_create(name=genre_name)
                genre_objects.append(genre)

            movie, created = Movie.objects.update_or_create(
                movie_cd=movie_cd,
                defaults={
                    "title": title,
                    "runtime": runtime,
                    "grade": rating,
                    "plot": plot,
                    "release_date": release_date,
                    "poster": poster,
                },
            )

            movie.genre.set(genre_objects)

            directors = item["directors"]["director"]
            actors = item["actors"]["actor"]

            self.create_staff(movie, directors, actors)

            movie.save()

    def create_staff(self, movie, directors, actors):
        staffs = []

        for director in directors:
            staffs.append(
                {
                    "name_cd": director["directorId"],
                    "name": director["directorNm"],
                    "role": "director",
                }
            )

        for actor in actors:
            staffs.append(
                {"name_cd": actor["actorId"], "name": actor["actorNm"], "role": "actor"}
            )

        for staff in staffs:
            name_cd = staff.get("name_cd")
            name_cd = int(name_cd) if name_cd else None
            name = staff.get("name")
            role = staff.get("role")

        try:
            if name_cd is not None:
                staff, created = Staff.objects.get_or_create(
                    name_cd=name_cd, defaults={"name": name, "role": role}
                )

            else:
                staff, created = Staff.objects.get_or_create(name=name, role=role)
            movie.staffs.add(staff)
        except IntegrityError:
            pass
