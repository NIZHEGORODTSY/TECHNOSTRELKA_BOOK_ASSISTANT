from flask import Flask, render_template, jsonify, request
import os
import time
from pathlib import Path
from model_controller import ModelController
from scripts import format_answer, get_context

BASE_DIR = Path(__file__).resolve().parent

TEMPLATES_DIR = BASE_DIR / 'templates'
STATIC_DIR = BASE_DIR / 'static'

app = Flask(
    'Book assistant',
    template_folder=str(TEMPLATES_DIR),
    static_folder=str(STATIC_DIR),
)

mc = ModelController(temperature=1.3, max_completion_tokens=150)


@app.route('/')
def main():
    return render_template('main_page.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        user_text = request.form['user_text']
        start_time = time.time()
        answer = mc.generate(
            context=get_context(),
            question=user_text,
        )
        end_time = time.time()
        delta = round(float(end_time - start_time), 1)
        return render_template('search.html', answer=format_answer(answer), time=f'{str(delta)} сек.')
    return render_template('search.html', answer='1')


@app.route('/library')
def show_lib():
    return render_template('library.html')


@app.route('/question')
def question():
    return render_template('question.html', answer='1')


app.run('0.0.0.0', port=5000, debug=True)
