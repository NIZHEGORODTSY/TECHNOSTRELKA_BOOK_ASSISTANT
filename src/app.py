from flask import Flask, render_template, jsonify, request

import os
import time
from pathlib import Path
from model_controller import ModelController
from scripts import format_answer

BASE_DIR = Path(__file__).resolve().parent

TEMPLATES_DIR = BASE_DIR / 'templates'
STATIC_DIR = BASE_DIR / 'static'

context = """В Гороховой улице, в одном из больших домов, народонаселения которого стало бы на целый уездный город, лежал утром в постели, на своей квартире, Илья Ильич Обломов.

Это был человек лет тридцати двух-трех от роду, среднего роста, приятной наружности, с темно-серыми глазами, но с отсутствием всякой определенной идеи, всякой сосредоточенности в чертах лица. Мысль гуляла вольной птицей по лицу, порхала в глазах, садилась на полуотворенные губы, пряталась в складках лба, потом совсем пропадала, и тогда во всем лице теплился ровный свет беспечности. С лица беспечность переходила в позы всего тела, даже в складки шлафрока. <...>

И поверхностно наблюдательный, холодный человек, взглянув мимоходом на Обломова, сказал бы: «Добряк должен быть, простота!» Человек поглубже и посимпатичнее, долго вглядываясь в лицо его, отошел бы в приятном раздумье, с улыбкой."""

app = Flask(
    'Book assistant',
    template_folder=str(TEMPLATES_DIR),
    static_folder=str(STATIC_DIR),
)

# NOTE: варианты моделей:
# t-bank-ai/ruDialoGPT-small - ответы в странной форме диалога + матерится !!!!
# mistralai/Mistral-7B-v0.3 - ОЧЕНЬ медленно работает. на маленьких промптах выдаёт осмысленный текст (примерно 6 минут), на большом промпте ответ более-менее адекватный (26 минут)

mc = ModelController(temperature=1.3, max_completion_tokens=150)


@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        # Получаем текст из формы
        user_text = request.form['user_text']
        answer = mc.generate(
            context=context,
            question=user_text,
        )
        print(answer)
        return render_template('base.html', answer=format_answer(answer))

    return render_template('base.html')


# @app.route('/health')
# def dummy():
#     return render_template('healthcheck.html')


# NOTE: тестовая функция для проверки работы модели
@app.route('/test_model')
def test_model():
    context = """В Гороховой улице, в одном из больших домов, народонаселения которого стало бы на целый уездный город, лежал утром в постели, на своей квартире, Илья Ильич Обломов.

Это был человек лет тридцати двух-трех от роду, среднего роста, приятной наружности, с темно-серыми глазами, но с отсутствием всякой определенной идеи, всякой сосредоточенности в чертах лица. Мысль гуляла вольной птицей по лицу, порхала в глазах, садилась на полуотворенные губы, пряталась в складках лба, потом совсем пропадала, и тогда во всем лице теплился ровный свет беспечности. С лица беспечность переходила в позы всего тела, даже в складки шлафрока. <...>

И поверхностно наблюдательный, холодный человек, взглянув мимоходом на Обломова, сказал бы: «Добряк должен быть, простота!» Человек поглубже и посимпатичнее, долго вглядываясь в лицо его, отошел бы в приятном раздумье, с улыбкой."""

    question = 'расскажи про Обломова'

    start_time = time.time()

    answer = mc.generate(
        context=context,
        question=question,
    )

    end_time = time.time()

    return jsonify({
        'question': question,
        'context': context,
        'answer': answer,
        "time": end_time - start_time,
    })


app.run('0.0.0.0', port=5000, debug=True)
