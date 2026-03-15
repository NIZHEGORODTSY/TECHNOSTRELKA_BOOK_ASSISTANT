from openai import OpenAI
import os
import markdown


class ModelController:
    def __init__(self, temperature: float, max_completion_tokens: int = 150):
        self._client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
        )
        self._model = "deepseek-chat"
        self._temperature = temperature
        self._max_completion_tokens = max_completion_tokens

    # TODO: изменить промпт под формат чанков: Автор, Название книги, Текст фрагмента
    def generate(self, context: str, question: str):
        messages = [
            {
                "role": "system",
                "content": "Ты помощник по вопросам содержания книг"
            },
            {
                "role": "system",
                "content": f"""Прочитай текст и ответь на предложенный вопрос. Текст: {context}. Отвечай на вопрос сразу, не пиши 'конечно!'."""
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

    def format_answer(self, answer: str) -> str:
        html = markdown.markdown(answer)
        return html
