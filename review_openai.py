import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": "너는 입력된 내용을 은유와 비유를 사용해서 평론가 처럼 바꿔줘.",
        },
        {"role": "user", "content": "이 영화 노잼임"},
    ],
)

print(completion.choices[0].message.content)
