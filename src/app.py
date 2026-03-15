from flask import Flask, render_template, jsonify, request
import os
import time
from pathlib import Path
from model_controller import ModelController
from pinecone_controller import PineconeController
from scripts import format_answer, get_context
from dotenv import load_dotenv



BASE_DIR = Path(__file__).resolve().parent

TEMPLATES_DIR = BASE_DIR / 'templates'
STATIC_DIR = BASE_DIR / 'static'

app = Flask(
    'Book assistant',
    template_folder=str(TEMPLATES_DIR),
    static_folder=str(STATIC_DIR),
)

mc = ModelController(temperature=1.3, max_completion_tokens=150)
pc = PineconeController()


@app.route('/')
def main():
    return render_template('main_page.html')


@app.route('/search', methods=['GET'])
def search_show():
    return render_template('search.html')
    # if request.method == 'POST':
    #     user_text = request.form['user_text']
    #     start_time = time.time()
    #     answer = mc.generate(
    #         context=get_context(),
    #         question=user_text,
    #     )
    #     end_time = time.time()
    #     delta = round(float(end_time - start_time), 1)
    #     return render_template('search.html', answer=format_answer(answer), time=f'{str(delta)} сек.')
    # return render_template('search.html', answer='1')

@app.route('/search', methods=['POST'])
def search_post():
    user_text = request.form['user_text']
    result = pc.get_fragments('вопросик может не зайти)') # list[str] - найденные фрагменты
    return render_template('search.html', answer=result)

@app.route('/library')
def show_lib():
    return render_template('library.html')


@app.route('/question', methods=['GET'])
def question_show():
    return render_template('question.html')

@app.route('/question', methods=['POST'])
def question_post():
    user_text = request.form['user_text']
    start_time = time.time()
    answer = mc.generate(
        context=get_context(),
        question=user_text,
    )
    end_time = time.time()
    delta = round(float(end_time - start_time), 1)
    return render_template('question.html', answer=format_answer(answer), time=f'{str(delta)} сек.')


app.run('0.0.0.0', port=5000, debug=True)
