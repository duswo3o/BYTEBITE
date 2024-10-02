# 표준 라이브러리
import time

# 서드파티 라이브러리
import requests

# Django 기능 및 프로젝트 관련
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from movies.models import Genre, Movie, Staff


class Command(BaseCommand):
    help = "API에서 최신 데이터를 가져와 영화 데이터베이스를 업데이트합니다."

    API_URL = "http://api.koreafilm.or.kr/openapi-data2/wisenut/search_api/search_json2.jsp?collection=kmdb_new2"

    def handle(self, *args, **options):
        start_count = 0
        total_data = []

        while True:
            params = {
                "ServiceKey": settings.KMDB_API_KEY,
                "listCount": 100,
                "startCount": start_count,
                "detail": "N",
            }

            response = requests.get(self.API_URL, params=params)

            if response.status_code == 200:
                data = response.json()["Data"][0]["Result"]
                total_data.extend(data)

                if len(data) < 1000:
                    break
                # 아래의 break문을 주석처리 하면 KMDb의 모든 데이터를 가져오게 됩니다.
                break

                start_count += 1000

                time.sleep(3)

            else:
                self.stdout.write(self.style.ERROR("API에 연결하는 데 실패했습니다."))
                return

        self.save_to_database(total_data)

    def save_to_database(self, total_data):
        for item in total_data:
            movie_cd = item["movieSeq"]
            title = item["title"]
            runtime = item["runtime"] if item["runtime"] else None
            rating = item["rating"] if item["rating"] else None
            plot = item["plots"]["plot"][0]["plotText"]

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
