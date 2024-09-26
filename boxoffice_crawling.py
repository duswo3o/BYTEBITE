import os
import sys
from datetime import datetime, timedelta
import pprint
import requests

from popcorngeek.config import KOFIC_API_KEY

# 1번 파일이 실행될 때 환경변수에 현재 자신의 프로젝트의 settings.py파일 경로를 등록.
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "popcorngeek.settings")

# 2번 실행파일에 Django 환경을 불러오는 작업.
import django

django.setup()
from movies.models import Ranking

# print((datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d"))


def base_boxoffice():
    """
    일주일치 데이터베이스를 만들기 위한 반복문 작업
    이후에는 하루 단위로 진행 예정.
    """
    for i in range(7, 0, -1):
        # api key
        key = KOFIC_API_KEY
        # 어제 날짜
        yesterday = datetime.today() - timedelta(days=i)
        # api 요청을 위한 날짜 포맷팅
        target_dt = yesterday.strftime("%Y%d%m")
        # 데이터베이스에 저장을 위한 날짜 포맷팅
        crawling_date = yesterday.strftime("%Y-%m-%d")

        # 크롤링 한 api url
        url = f"http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json?key={key}&targetDt={target_dt}"

        # 데이터 요청 후 변수에 json 형태로 저장
        response = requests.get(url)
        data = response.json()
        # pprint.pprint(data)

        # 해당 일의 1~10위 박스오피스 순위
        boxoffice_list = data.get("boxOfficeResult").get("dailyBoxOfficeList")  # [0]
        # pprint.pprint(boxoffice_list)

        # print(datetime.today().year)
        for j in range(10):
            now_movie = boxoffice_list[j]
            title = now_movie.get("movieNm")
            rank = now_movie.get("rank")

            Ranking.objects.create(title=title, rank=rank, crawling_date=crawling_date)


# 오래된 순위 10개의 데이터
# old_data = Ranking.objects.filter(crawling_date="2024-09-25")
# print(old_data)
# old_data.delete()

# api key
key = KOFIC_API_KEY
# 어제 날짜
yesterday = datetime.today() - timedelta(days=1)

# 일주일치 데이터만 보관예정 : 일주일이 지난 데이터는 삭제
delete_date = (yesterday - timedelta(days=8)).strftime("%Y-%m-%d")
old_data = Ranking.objects.filter(crawling_date=delete_date)
# old_data.delete()

# api 요청을 위한 날짜 포맷팅
target_dt = yesterday.strftime("%Y%d%m")
# 데이터베이스에 저장을 위한 날짜 포맷팅
crawling_date = yesterday.strftime("%Y-%m-%d")


# 크롤링 한 api url
url = f"http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json?key={key}&targetDt={target_dt}"

# 데이터 요청 후 변수에 json 형태로 저장
response = requests.get(url)
data = response.json()

# 해당 일의 1~10위 박스오피스 순위
boxoffice_list = data.get("boxOfficeResult").get("dailyBoxOfficeList")  # [0]

for j in range(10):
    now_movie = boxoffice_list[j]
    title = now_movie.get("movieNm")
    rank = now_movie.get("rank")

    Ranking.objects.create(title=title, rank=rank, crawling_date=crawling_date)
