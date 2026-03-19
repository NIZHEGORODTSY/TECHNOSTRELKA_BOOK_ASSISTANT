FROM python:3.14

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY src/ src/
COPY addition_data.txt addition_data.txt

CMD ["python", "src/app.py"]