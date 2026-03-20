from openai import OpenAI
import os
import markdown
from objects import *


class ModelController:
    def __init__(self, temperature: float, max_completion_tokens: int = 150):
        self._client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
        )
        self._model = "deepseek-chat"
        self._temperature = temperature
        self._max_completion_tokens = max_completion_tokens

    def generate(self, prompt):
        response = self._client.chat.completions.create(
            model=self._model,
            messages=prompt,
            temperature=self._temperature,
            max_completion_tokens=self._max_completion_tokens,
            stream=False
        )

        return response.choices[0].message.content

    def format_answer(self, answer: str) -> str:
        html = markdown.markdown(answer)
        return html

    def form_prompt_from_chunks_and_question(self, chunks: list[Chunk], question: str) -> list[dict[str, str]]:
        fragments = ""
        for i in range(len(chunks)):
            fragment = f"Автор: {chunks[i].author} Название: \"{chunks[i].book}\" {chunks[i].text}    "
            fragments += fragment

        prompt = [
            {
                "role": "system",
                "content": "Ты помощник по вопросам содержания книг"
            },
            {
                "role": "system",
                "content": f"""Тебе предложено несколько фрагментов разных книг: {fragments}"""
            },
            {
                "role": "system",
                "content": "Ответь на предложенный вопрос; отвечай на него сразу, не пиши 'конечно!' Постарайся цитировать предложенные фрагменты как можно чаще"
            },
            {
                "role": "user",
                "content": question
            }
        ]

        return prompt
