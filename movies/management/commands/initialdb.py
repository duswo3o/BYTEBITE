# 표준 라이브러리
from datetime import datetime, timedelta
import json
import time

# 서드파티 라이브러리
import requests

# Django 기능 및 프로젝트 관련
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from django.core.management.base import BaseCommand
from django.db import IntegrityError, OperationalError, transaction
from movies.models import Genre, Movie, Ranking, Staff


class Command(BaseCommand):
    help = "프로젝트의 초기 세팅에 사용되는 명령입니다. 서버에 업로드 후 한번만 사용하시면 됩니다."

    API_URL = "http://api.koreafilm.or.kr/openapi-data2/wisenut/search_api/search_json2.jsp?collection=kmdb_new2"
    RANK_API_URL = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"

    TODAY = datetime.today()

    def handle(self, *args, **options):

        # 전체 데이터 베이스를 입력하는 함수(배포시 주석해제)
        # total_data = self.database_initial_setup()

        # 테스트 데이터를 입력하는 함수(배포시 주석처리)
        total_data = self.test_setup()

        BATCH_SIZE = 1000
        for batch_start in range(0, len(total_data), BATCH_SIZE):
            batch = total_data[batch_start : batch_start + BATCH_SIZE]
            self.save_to_database(batch)

        # 앞으로 7일간 개봉할 영화의 개봉일 입력
        release_data = self.initial_release_date()

        self.save_to_database(release_data)

        # 이전 7일간의 박스오피스 순위 입력
        self.save_to_rank_database()

    def fetch_data_from_api(self, url, params):
        try:
            response = requests.get(url, params=params)

            if response.status_code == 200:
                try:
                    data = response.json()
                    return data["Data"][0]["Result"]
                except json.JSONDecodeError as e:
                    print(f"JSON 파싱 오류: {e}")
                    return None
            else:
                print("API 요청에 실패했습니다.")
                return None

        except requests.RequestException as e:
            print(f"요청 예외 발생: {e}")
            return None

    def database_initial_setup(self):
        total_data = []

        # 0 ~ 40000까지 입력
        first_count = 0
        while True:
            params = {
                # 다른 api키 필요
                "ServiceKey": settings.KMDB_API_KEY_EX1,
                "listCount": 1000,
                "startCount": first_count,
                "detail": "Y",
            }

            data = self.fetch_data_from_api(self.API_URL, params)

            if data:
                total_data.extend(data)
            else:
                print(
                    f"{first_count}번째 요청에서 데이터 누락, 다음 요청으로 넘어갑니다."
                )

            if first_count == 40000:
                break

            first_count += 1000

            time.sleep(3)

        # 40000 ~ 80000까지 입력
        second_count = 40000
        while True:
            params = {
                # 다른 api키 필요
                "ServiceKey": settings.KMDB_API_KEY_EX2,
                "listCount": 1000,
                "startCount": second_count,
                "detail": "Y",
            }

            data = self.fetch_data_from_api(self.API_URL, params)

            if data:
                total_data.extend(data)
            else:
                print(
                    f"{second_count}번째 요청에서 데이터 누락, 다음 요청으로 넘어갑니다."
                )

            if second_count == 80000:
                break

            second_count += 1000

            time.sleep(3)

        # 80000 ~ 입력
        last_count = 80000
        while True:
            params = {
                # 다른 api키 필요
                "ServiceKey": settings.KMDB_API_KEY,
                "listCount": 1000,
                "startCount": last_count,
                "detail": "Y",
            }

            data = self.fetch_data_from_api(self.API_URL, params)

            if data:
                total_data.extend(data)
            else:
                print(
                    f"{last_count}번째 요청에서 데이터 누락, 다음 요청으로 넘어갑니다."
                )

            if len(data) < 1000:
                break

            last_count += 1000

            time.sleep(3)

        return total_data

    def test_setup(self):
        start_count = 107000

        params = {
            "ServiceKey": settings.KMDB_API_KEY,
            # 입력할 테스트 케이스의 갯수 조절(1 ~ 1000)
            "listCount": 100,
            "startCount": start_count,
            "detail": "Y",
        }

        response = requests.get(self.API_URL, params=params)

        if response.status_code == 200:
            return response.json()["Data"][0]["Result"]

        else:
            self.stdout.write(self.style.ERROR("API에 연결하는 데 실패했습니다."))
            return

    def initial_release_date(self):
        release_data = []

        for date in range(1, 8):
            update_date = self.TODAY + timedelta(days=date)

            params = {
                "ServiceKey": settings.KMDB_API_KEY,
                "listCount": 100,
                "detail": "Y",
                "releaseDts": update_date.strftime("%Y%m%d"),
                "releaseDte": update_date.strftime("%Y%m%d"),
            }

            response = requests.get(self.API_URL, params=params)

            if response.status_code == 200:
                if response.json()["Data"][0]["Count"] != 0:
                    data = response.json()["Data"][0]["Result"]

                    for d in data:
                        d["release_date"] = update_date.strftime("%Y-%m-%d")
                    release_data.extend(data)

            else:
                self.stdout.write(self.style.ERROR("API에 연결하는 데 실패했습니다."))
                return

        return release_data

    def validate_date(self, date_str):
        try:
            return datetime.strptime(date_str, "%Y%m%d").date()
        except ValueError:
            return datetime(1900, 1, 1).date()

    def save_to_database(self, total_data):
        for item in total_data:
            movie_cd = item["movieSeq"]
            title = item["title"].strip().upper()
            runtime = item["runtime"] if item["runtime"] else None
            rating = item["rating"] if item["rating"] else None
            plot = item["plots"]["plot"][0]["plotText"]
            poster = item["posters"].split("|")[0] if item["posters"] else None

            release_date = item["repRlsDate"]
            release_date = self.validate_date(release_date)
            release_date = release_date.strftime("%Y-%m-%d")

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

            if not name_cd or not name or not role:
                continue

            try:
                if name_cd is not None:
                    staff, created = Staff.objects.get_or_create(
                        name_cd=name_cd, defaults={"name": name, "role": role}
                    )
                else:
                    staff_obj, created = Staff.objects.get_or_create(
                        name=name, role=role
                    )

                movie.staffs.add(staff)

            except MultipleObjectsReturned:
                continue

            except IntegrityError:
                pass

    def save_to_rank_database(self):
        for date in range(1, 8):
            update_date = self.TODAY - timedelta(days=date)

            params = {
                "key": settings.KOFIC_API_KEY,
                "targetDt": update_date.strftime("%Y%m%d"),
            }

            response = requests.get(self.RANK_API_URL, params=params)

            if response.status_code == 200:
                data = response.json()["boxOfficeResult"]["dailyBoxOfficeList"]

                for item in data:
                    title = item["movieNm"].strip().upper()
                    rank = item["rank"]
                    crawling_date = update_date.strftime("%Y-%m-%d")
                    release_date = item["openDt"]

                    movie = Movie.objects.filter(
                        title=title, release_date=release_date
                    ).first()

                    Ranking.objects.create(
                        title=title,
                        rank=rank,
                        crawling_date=crawling_date,
                        movie_pk=movie,
                    )

            else:
                self.stdout.write(self.style.ERROR("API에 연결하는 데 실패했습니다."))
                return
