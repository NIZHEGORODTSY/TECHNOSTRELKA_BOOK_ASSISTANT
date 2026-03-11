from flask import Flask, render_template
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

TEMPLATES_DIR = BASE_DIR / 'templates'

a = str(TEMPLATES_DIR)

app = Flask(
    'Book assistant',
    template_folder=str(TEMPLATES_DIR)
)

@app.route('/health')
def dummy():
    return render_template('healthcheck.html')

app.run('0.0.0.0', port=5000, debug=True)