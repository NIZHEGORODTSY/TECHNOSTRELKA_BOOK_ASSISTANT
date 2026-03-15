from flask import Flask, render_template, request, flash, redirect, url_for
import os
import time
from pathlib import Path
from model_controller import ModelController
from pinecone_controller import PineconeController
from scripts import format_answer, get_context
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv('_.env')

BASE_DIR = Path(__file__).resolve().parent

TEMPLATES_DIR = BASE_DIR / 'templates'
STATIC_DIR = BASE_DIR / 'static'

app = Flask(
    'Book assistant',
    template_folder=str(TEMPLATES_DIR),
    static_folder=str(STATIC_DIR),
)

# Настройки загрузки файлов
app.config['UPLOAD_FOLDER'] = 'uploads'  # папка для сохранения файлов
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # максимальный размер файла 16MB
app.config['SECRET_KEY'] = 'your-secret-key-here'  # для flash сообщений

# Создаем папку для загрузок если её нет
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

mc = ModelController(temperature=1.3, max_completion_tokens=150)
pc = PineconeController()


@app.route('/')
def main():
    return render_template('main_page.html')


@app.route('/search', methods=['GET'])
def search_show():
    return render_template('search.html', chunks='1')


@app.route('/search', methods=['POST'])
def search_post():
    user_question = request.form.get('user_question')
    amount = int(request.form.get('amount'))

    print(amount)

    start_time = time.time()
    # TODO: временно None, потом доставать из формы
    user_book = None
    user_author = None
    result = pc.search_similar_chunks(
        question=user_question,
        book_name=user_book,
        author_name=user_author,
        top_k=amount
    )  # list[str] - найденные фрагменты
    end_time = time.time()
    delta = round(float(end_time - start_time), 1)
    return render_template('search.html', chunks=result, time=f'{str(delta)} сек.')


@app.route('/library', methods=['GET'])
def show_lib():
    _dict = pc.list_all_books()
    _dict = {
        "Л.Н.Толстой": ["Война и мир Том 1", "Война и мир Том 2", "Война и мир Том 3"],
        "О.Генри": ["Дары волхвов"],
        "К. Паустовский": ["Акварельные краски"]
    }

    return render_template('library.html', data = _dict)


@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        book_title = request.form.get('bookTitle')
        book_author = request.form.get('bookAuthor')

        print(f"Название книги: {book_title}")
        print(f"Автор: {book_author}")

        if 'file' not in request.files:
            flash('Ошибка: нет файла в запросе', 'error')
            return redirect(url_for('show_lib'))

        file = request.files['file']

        if file.filename == '':
            flash('Ошибка: файл не выбран', 'error')
            return redirect(url_for('show_lib'))

        if not file.filename.endswith('.txt'):
            flash('Ошибка: поддерживаются только .txt файлы', 'error')
            print('ошибка формата')
            return redirect(url_for('show_lib'))

        if not book_title or not book_author:
            flash('Ошибка: необходимо указать название книги и автора', 'error')
            return redirect(url_for('show_lib'))

        if file and file.filename:
            filename = secure_filename(file.filename)

            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            name_part = os.path.splitext(filename)[0]
            ext = os.path.splitext(filename)[1]
            new_filename = f"{timestamp}_{name_part}{ext}"

            file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)

            file.save(file_path)

            with open(file_path, 'r') as f:
                data = f.read()
            book = data

            flash(f'Файл "{filename}" успешно загружен!', 'success')
            flash(f'Название: {book_title}, Автор: {book_author}', 'info')

            return redirect(url_for('show_lib'))

        flash('Неизвестная ошибка при загрузке файла', 'error')
        return redirect(url_for('show_lib'))

    except Exception as e:
        print(f"Ошибка при загрузке файла: {e}")
        flash(f'Произошла ошибка при загрузке файла: {str(e)}', 'error')
        return redirect(url_for('show_lib'))


@app.route('/question', methods=['GET'])
def question_show():
    return render_template('question.html', answer='1')


@app.route('/question', methods=['POST'])
def question_post():
    user_text = request.form['user_text']
    start_time = time.time()
    answer = mc.generate(
        context=get_context(),  # get_context временно, потом будет mc.search_similar_chunks
        question=user_text,
    )
    end_time = time.time()
    delta = round(float(end_time - start_time), 1)
    return render_template('question.html', answer=mc.format_answer(answer), time=f'{str(delta)} сек.')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
