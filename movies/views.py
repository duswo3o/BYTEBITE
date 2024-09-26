import requests
from rest_framework.views import APIView
from django.conf import settings

class MovieAPIView(APIView):
    def get(self, request):
        API_URL = "http://api.koreafilm.or.kr/openapi-data2/wisenut/search_api/search_json2.jsp"
        params = {
            "collection": "kmdb_new2",
            "detail": "N",
            "ServiceKey": settings.env('KMDB_API_KEY')
        }
        print('test')