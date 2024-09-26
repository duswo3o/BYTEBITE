import requests
import time
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Movie


class MovieAPIView(APIView):
    API_URL = "http://api.koreafilm.or.kr/openapi-data2/wisenut/search_api/search_json2.jsp?collection=kmdb_new2"

    def get(self, request):
        start_count = 0
        total_data = []

        while True:
            params = {
                "ServiceKey": settings.KMDB_API_KEY,
                "listCount": 1000,
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
                return Response(
                    {"error": "API에 접속에 실패했습니다."},
                    status=status.HTTP_400_BAD_REQUEST
                                )

        save_to_database(total_data)
        return Response(
            {"message": f"{len(total_data)}개의 영화 데이터가 저장되었습니다."},
            status=status.HTTP_200_OK
            )


def save_to_database(total_data):
    for item in total_data:
        movie_cd = item['movieSeq']
        title = item['title']
        # genre = item['genre']
        runtime = item['runtime'] if item['runtime'] else None
        plot = item['plots']['plot'][0]['plotText']

        movie, created = Movie.objects.update_or_create(
            movie_cd=movie_cd,
            defaults={
                'title': title,
                # 'genre': genre,
                'runtime': runtime,
                'plot': plot
                }
            )
