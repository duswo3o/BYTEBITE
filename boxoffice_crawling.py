import schedule
import time
import sys
from datetime import datetime, timedelta
import pprint
import requests

# from popcorngeek.config import KOFIC_API_KEY


######################################################################################
######################### 외부 파일에서 장고 내부에 접근하기 위한 설정 ##########################

# 1번 파일이 실행될 때 환경변수에 현재 자신의 프로젝트의 settings.py파일 경로를 등록.
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "popcorngeek.settings")

# 2번 실행파일에 Django 환경을 불러오는 작업.
import django

django.setup()
from movies.models import Ranking

######################################################################################
######################################################################################

import environ
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    # 기본값을 설정하거나 강제할 수 있습니다.
    DEBUG=(bool, False)
)

environ.Env.read_env(BASE_DIR / ".env")


def base_boxoffice():
    """
    일주일치 데이터베이스를 만들기 위한 반복문 작업
    이후에는 하루 단위로 진행 예정.
    """
    for i in range(8, 1, -1):
        # api key
        key = env("KOFIC_API_KEY")
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
        print(datetime.today())
        print("==========================")
        # pprint.pprint(boxoffice_list)

        for j in range(10):
            now_movie = boxoffice_list[j]
            title = now_movie.get("movieNm")
            rank = now_movie.get("rank")

            Ranking.objects.create(title=title, rank=rank, crawling_date=crawling_date)
        print("============= fin =============")


# base_boxoffice()
# 오래된 순위 10개의 데이터
# old_data = Ranking.objects.filter(crawling_date="2024-09-25")
# print(old_data)
# old_data.delete()


# api key
key = env("KOFIC_API_KEY")
# 어제 날짜
yesterday = datetime.today() - timedelta(days=1)


def boxoffice_rank():
    # 일주일치 데이터만 보관예정 : 일주일이 지난 데이터는 삭제
    delete_date = (yesterday - timedelta(days=7)).strftime("%Y-%m-%d")
    old_data = Ranking.objects.filter(crawling_date=delete_date)
    old_data.delete()

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
    boxoffice_list = data.get("boxOfficeResult").get("dailyBoxOfficeList")

    for j in range(10):
        now_movie = boxoffice_list[j]
        title = now_movie.get("movieNm")
        rank = now_movie.get("rank")

        Ranking.objects.create(title=title, rank=rank, crawling_date=crawling_date)


# boxoffice_rank()

# # step3.실행 주기 설정
# schedule.every().day.at("12:00:00").do(boxoffice_rank)  # 매일 오후 12시에 실행
# # schedule.every(1).minutes.do(headline_summary)
#
#
# # step4.스캐쥴 시작
# while True:
#     schedule.run_pending()
#     time.sleep(1)
