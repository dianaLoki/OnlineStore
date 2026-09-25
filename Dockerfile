FROM python:3.11-slim

WORKDIR /app

# Запрещаем Python писать .pyc файлы и буферизовать вывод
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .