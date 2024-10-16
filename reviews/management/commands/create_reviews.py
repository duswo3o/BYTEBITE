from faker import Faker
import random

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Avg, FloatField, Q, Value
from django.db.models.functions import Coalesce, Round

from reviews.models import Review
from movies.models import Movie

User = get_user_model()

positive_reviews = [
    "이 영화는 정말 감동적이었어요. 많은 생각을 하게 만들었습니다.",
    "출연진의 연기가 뛰어나서 몰입할 수 있었습니다.",
    "스토리가 탄탄하고 전개가 훌륭했습니다. 다시 보고 싶어요!",
    "영상미가 압도적이어서 화면을 보는 것만으로도 즐거웠습니다.",
    "감동적인 장면이 많아 눈물이 핑 돌았어요.",
    "재미있는 유머와 따뜻한 메시지가 마음에 남았습니다.",
    "이 영화 덕분에 하루가 밝아진 기분이에요.",
    "음악과 영상이 조화를 이루며 정말 훌륭한 작품이었습니다.",
    "감독의 섬세한 연출이 돋보이는 영화였어요.",
    "주제도 신선하고 전개도 흥미로워서 즐거웠습니다.",
    "캐릭터들이 매력적이어서 더욱 빠져들게 만들었어요.",
    "이 영화는 가족과 함께 보기 좋은 작품입니다.",
    "신선한 소재와 멋진 스토리라인이 인상적이었습니다.",
    "명장면이 많아서 기억에 오래 남을 것 같아요.",
    "편안한 마음으로 볼 수 있는 따뜻한 영화입니다.",
    "각 캐릭터의 성장 이야기가 아름다웠습니다.",
    "이 영화는 웃음과 감동을 동시에 줍니다.",
    "주제곡이 너무 좋아서 듣고 또 듣고 싶어요.",
    "시청 후 기분이 좋아져서 친구들에게 추천하고 싶습니다.",
    "재미있고 의미 있는 시간이었습니다. 꼭 보세요!",
    "다양한 감정을 느낄 수 있는 훌륭한 작품이었습니다.",
    "이 영화는 진정한 우정에 대해 생각하게 만들었어요.",
    "상상 이상으로 좋았던 영화, 강력 추천합니다!",
    "모든 연령층이 즐길 수 있는 영화라고 생각해요.",
    "여운이 남는 좋은 영화였습니다. 다시 보고 싶어요.",
    "배우들의 연기력이 영화의 매력을 더했습니다.",
    "가슴 따뜻한 이야기로 일상의 피로를 잊게 해줍니다.",
    "이 영화는 사랑에 대한 새로운 시각을 줍니다.",
    "정말 잘 만든 영화로, 여러 번 보고 싶어요.",
    "마음이 따뜻해지는 행복한 영화를 찾는다면 이 영화가 제격이에요.",
]

negative_reviews = [
    "이 영화는 정말 실망스러웠어요. 기대 이하였습니다.",
    "스토리가 너무 지루해서 중간에 잠이 들었어요.",
    "연기력이 부족해 몰입하기 힘들었습니다.",
    "결말이 너무 뻔하고 예측 가능했어요.",
    "영화의 전개가 느려서 답답했습니다.",
    "특별한 메시지나 주제가 없는 영화였어요.",
    "캐릭터들이 매력적이지 않아 감정이입이 안 되더군요.",
    "이 영화는 시간 낭비였다고 생각합니다.",
    "음악이 너무 어색하게 배치되어 있었어요.",
    "여러모로 아쉬운 점이 많았던 작품입니다.",
    "비현실적인 설정 때문에 현실감을 잃었어요.",
    "영화의 분위기가 너무 무겁고 우울했습니다.",
    "명장면이 없는 평범한 영화였습니다.",
    "이해하기 어려운 전개가 많아서 혼란스러웠어요.",
    "상투적인 이야기로 새로운 느낌이 없었습니다.",
    "코미디 요소가 너무 억지스러웠어요.",
    "배우들의 캐미가 전혀 느껴지지 않았습니다.",
    "후반부로 갈수록 더 지루해졌어요.",
    "프리퀄이나 속편이 필요 없던 영화입니다.",
    "이런 주제는 더 잘 다룰 수 있을 것 같아요.",
    "전반적으로 부족한 점이 많은 영화였습니다.",
    "이 영화는 제 취향에 전혀 맞지 않았어요.",
    "관객을 고려하지 않은 듯한 연출이 아쉬웠습니다.",
    "영화가 끝나고도 여운이 남지 않았습니다.",
    "이해하기 어려운 비유와 상징이 많았어요.",
    "캐릭터들이 너무 평면적이어서 감정이입이 힘들었어요.",
    "이 영화는 기대를 저버린 작품입니다.",
    "연출이 서툴러서 긴장감이 전혀 없었습니다.",
    "정말 실망스러운 경험이었어요.",
    "리뷰가 좋았던 이유를 모르겠어요.",
    "이 영화는 다시 보고 싶지 않네요.",
    "영화를 보고 나니 시간과 돈이 아까웠습니다.",
]

movies_list = []

graded_movies = Movie.objects.annotate(
    average_grade=Round(
        Coalesce(Avg("ratings__score"), Value(0), output_field=FloatField()),
        1,  # 소수점 첫 번째 자리까지 반올림
    )
).order_by("-average_grade")[:10]

liked_movies = (
    Movie.objects.annotate(
        like_count=models.Count("like_users"),
        dislike_count=models.Count("dislike_users"),
    )
    .annotate(like=models.F("like_count") - models.F("dislike_count"))
    .order_by("-like")[:10]
)

movies_list += graded_movies
movies_list += liked_movies

bots = User.objects.filter(nickname__icontains="bot")


class Command(BaseCommand):
    help = "리뷰 생성"

    def add_arguments(self, parser):
        parser.add_argument(
            "--positive", type=int, default=10, help="number of positive review"
        )
        parser.add_argument(
            "--negative", type=int, default=10, help="number of negative review"
        )

    def handle(self, *args, **kwargs):
        num_positive = kwargs["positive"]
        num_negative = kwargs["negative"]
        faker = Faker("ko_KR")  # 한국어 로케일 설정

        # 로케일 확인
        print(f"Faker locale: {faker.locales}")
        print(faker.sentence(nb_words=random.randint(5, 15)))

        self.stdout.write(
            self.style.NOTICE(
                f"Creating {num_positive} positive and {num_negative} negative reviews..."
            )
        )

        for _ in range(num_positive):
            Review.objects.create(
                content=random.choice(positive_reviews),
                movie=random.choice(movies_list),  # 영화
                author=random.choice(bots),
                is_spoiler=random.choice([True, False]),
                is_positive=True,
            )

        for _ in range(num_negative):
            Review.objects.create(
                content=random.choice(negative_reviews),
                movie=random.choice(movies_list),  # 영화
                author=random.choice(bots),
                is_spoiler=random.choice([True, False]),
                is_positive=False,  # 부정 리뷰일 경우 False로 설정
            )

        self.stdout.write(self.style.SUCCESS("Reviews created successfully."))
