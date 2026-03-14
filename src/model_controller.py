from openai import OpenAI
import os
from dotenv import load_dotenv

# NOTE:
# В ходе продолжительных экспериментов было принято решение отказаться от локального использования моделей hugging face из-за ОЧЕНЬ низкой скорости работы
# Решено использовать api deepseek

# P.S. в ходе работы столкнулся с тем, что модель в своих ответах испоьзует символы '#' и '*' для выделения слов. пока что не придумал, как реализовать выделение таких слов при отображении на сайте

load_dotenv('_.env')


class ModelController:
    def __init__(self, temperature: float, max_completion_tokens: int = 150):
        self._client = OpenAI(
            api_key=os.environ.get("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
        )
        self._model = "deepseek-chat"
        self._temperature = temperature
        self._max_completion_tokens = max_completion_tokens

    def generate(self, context: str, question: str):
        messages = [
            {
                "role": "system",
                "content": "Ты помощник по вопросам содержания книг"
            },
            {
                "role": "system",
                "content": f"""Прочитай текст и ответь на предложенный вопрос. Текст: {context}. В своём ответе не используй символы '*' и '#'!!!"""
            },
            {
                "role": "user",
                "content": question
            }
        ]

        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=self._temperature,
            max_completion_tokens=self._max_completion_tokens,
            stream=False
        )

        return response.choices[0].message.content
