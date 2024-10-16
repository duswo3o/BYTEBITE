import random
from faker import Faker
from tqdm import tqdm

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand


fake = Faker(locale="ko_KR")
User = get_user_model()


class Command(BaseCommand):

    def handle(self, *args, **options):
        user_list = []

        for __ in tqdm(range(10), desc="유저 생성"):
            email = fake.email()
            nickname = f"bot{__}"
            password = nickname
            user = User.objects.create_user(
                email=email, password=password, nickname=nickname
            )
            user_list.append(user)
