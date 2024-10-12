# 서드파티 라이브러리
from openai import OpenAI

# Django 기능 및 프로젝트 관련
from django.conf import settings
from django.core.management.base import BaseCommand
from movies.models import Movie, Tag


api_key = settings.OPENAI_API_KEY
client = OpenAI(api_key=api_key)


class Command(BaseCommand):
    help = "원하는 영화의 줄거리를 기준으로 ai를 통해 태그를 생성합니다."

    def add_arguments(self, parser):
        parser.add_argument("movie_cd", type=int, help="영화의 고유 코드")

    def handle(self, *args, **kwargs):
        movie_cd = kwargs["movie_cd"]
        try:
            movie = Movie.objects.get(id=movie_cd)
            movie_info = self.print_movie_info(movie)
            tags = self.print_tags()

        except Movie.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("해당 movie_cd에 대한 영화가 존재하지 않습니다.")
            )

        ai_tags = self.auto_tagging(movie_info, tags)
        ai_tags = [tag.strip() for tag in ai_tags.split(",")]
        print(ai_tags)

        self.update_tags(movie, ai_tags)

    # 특정 영화
    def print_movie_info(self, movie):
        movie_info = {
            "title": movie.title,
            "plot": movie.plot,
            "genre": [genre.name for genre in movie.genre.all()],
        }
        return movie_info

    # 모든 태그 정보
    def print_tags(self):
        tags = Tag.objects.all()
        tags = [tag.name for tag in tags]
        return tags

    def auto_tagging(self, movie_info, tags):

        content = (
            f"제목: {movie_info['title']}\n"
            f"줄거리: {movie_info['plot']}\n"
            f"장르: {', '.join(movie_info['genre'])}\n"
        )

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "1. You are a film critic. You provide you with information about the plot, title, and genre of the three movies"
                        f"2. A word must be selected from one to three of {tags}"
                        "3. Output format is as follows: Example 1, Example 2"
                        "4. When choosing words, feel free to express your subjective feelings by referring to the plot and genre."
                        "5. Do not give long answers. You have to answer with only a few words."
                    ),
                },
                {
                    "role": "user",
                    "content": content,
                },
            ],
        )

        return completion.choices[0].message.content

    def update_tags(self, movie, ai_tags):
        for tag_name in ai_tags:
            try:
                tag = Tag.objects.get(name=tag_name)
                movie.tags.add(tag)

            except Tag.DoesNotExist:
                continue
