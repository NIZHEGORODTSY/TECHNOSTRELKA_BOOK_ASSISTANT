from flask import Flask, render_template, request, flash, redirect, url_for
import os
import time
from pathlib import Path
from model_controller import ModelController
from pinecone_controller import PineconeController
from scripts import format_library, get_books_amount
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

mc = ModelController(temperature=1.4, max_completion_tokens=150)
pc = PineconeController()


@app.route('/')
def main():
    library = pc.list_all_books()
    amount = get_books_amount(library)
    return render_template('main_page.html', amount=amount)


@app.route('/search', methods=['GET'])
def search_show():
    library = pc.list_all_books()
    books_and_authors = format_library(library)
    return render_template('search.html', chunks='1', books_and_authors=books_and_authors)


@app.route('/search', methods=['POST'])
def search_post():
    user_question = request.form.get('user_question')
    amount = int(request.form.get('amount'))
    book_choice = request.form.get('books').split(' - ')
    author, book = book_choice[0], book_choice[-1]
    library = pc.list_all_books()
    books_and_authors = format_library(library)

    if user_question and user_question[0] != ' ':
        start_time = time.time()
        result = pc.search_similar_chunks(
            question=user_question,
            book_name=book,
            author_name=author,
            top_k=amount
        )
        end_time = time.time()
        delta = round(float(end_time - start_time), 1)
        return render_template('search.html', chunks=result, time=f'{str(delta)} сек.',
                               books_and_authors=books_and_authors)
    return render_template('search.html', chunks='1', books_and_authors=books_and_authors)


@app.route('/library', methods=['GET'])
def show_lib():
    _dict = pc.list_all_books()

    return render_template('library.html', data=_dict)


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

            pc.add_book(
                book_text=data,
                book_name=book_title,
                author_name=book_author
            )

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
    library = pc.list_all_books()
    books_and_authors = format_library(library)
    return render_template('question.html', answer='1', books_and_authors=books_and_authors)


@app.route('/question', methods=['POST'])
def question_post():
    user_text = request.form['user_text']
    book_choice = request.form.get('books').split(' - ')
    author, book = book_choice[0], book_choice[-1]
    library = pc.list_all_books()
    books_and_authors = format_library(library)
    start_time = time.time()
    chunks = pc.search_similar_chunks(question=user_text, author_name=author, book_name=book, top_k=10)
    prompt = mc.form_prompt_from_chunks_and_question(chunks=chunks, question=user_text)
    answer = mc.generate(prompt)
    end_time = time.time()
    delta = round(float(end_time - start_time), 1)
    return render_template('question.html', answer=mc.format_answer(answer), time=f'{str(delta)} сек.',
                           books_and_authors=books_and_authors)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
