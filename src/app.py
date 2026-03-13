from flask import Flask, render_template, jsonify
import os
import time
from pathlib import Path
from model_controller import ModelController

BASE_DIR = Path(__file__).resolve().parent

TEMPLATES_DIR = BASE_DIR / 'templates'
STATIC_DIR = BASE_DIR / 'static'

app = Flask(
    'Book assistant',
    template_folder=str(TEMPLATES_DIR),
    static_folder=str(STATIC_DIR),
)

# NOTE: варианты моделей:
# t-bank-ai/ruDialoGPT-small - ответы в странной форме диалога + матерится !!!!
# mistralai/Mistral-7B-v0.3 - ОЧЕНЬ медленно работает. на маленьких промптах выдаёт осмысленный текст (примерно 6 минут), на большом промпте ответ более-менее адекватный (26 минут)

mc = ModelController('mistralai/Mistral-7B-v0.3')

@app.route('/')
def main():
    return render_template('base.html')


@app.route('/health')
def dummy():
    return render_template('healthcheck.html')

# NOTE: тестовая функция для проверки работы модели
@app.route('/test_model')
def test_model():
    question = 'Каким описывается Илья Обломов? Что можно сказать об отношении автора к нему?'

    start_time = time.time()

    prompt = mc.form_prompt(question)

    answer = mc.generate(
        prompt=prompt,
        max_new_tokens=350,
    )

    end_time = time.time()

    return jsonify({
        'question': question,
        'prompt': prompt,
        'answer': answer,
        "time": end_time - start_time,
    })


app.run('0.0.0.0', port=5000, debug=True)
