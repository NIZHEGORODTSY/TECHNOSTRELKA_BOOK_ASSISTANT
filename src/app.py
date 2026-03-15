from flask import Flask, render_template, jsonify, request
import os
import time
from pathlib import Path
from model_controller import ModelController
from pinecone_controller import PineconeController
from scripts import format_answer, get_context
from dotenv import load_dotenv

load_dotenv('_.env')


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

@app.route('/search', methods=['POST'])
def search_post():
    user_question = request.form.get('user_question')
    # TODO: временно None, потом доставать из формы
    user_book = None
    user_author = None
    result = pc.search_similar_chunks(
        question=user_question,
        book_name=user_book,
        author_name=user_author
    ) # list[str] - найденные фрагменты
    return render_template('search.html', chunks=result)

@app.route('/library', methods=['GET'])
def show_lib():
    return render_template('library.html')

@app.route('/question', methods=['GET'])
def question_show():
    return render_template('question.html', answer='1')

@app.route('/question', methods=['POST'])
def question_post():
    user_text = request.form['user_text']
    start_time = time.time()
    answer = mc.generate(
        context=get_context(), # get_context временно, потом будет mc.search_similar_chunks 
        question=user_text,
    )
    end_time = time.time()
    delta = round(float(end_time - start_time), 1)
    return render_template('question.html', answer=mc.format_answer(answer), time=f'{str(delta)} сек.')


app.run('0.0.0.0', port=5000, debug=True)
