# Используем базовый образ Python 3.10
FROM python:3.10-slim

# Определяем переменные окружения как аргументы
ARG DATABASE_URL
ARG FLASK_ENV

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь исходный код в контейнер
COPY . .

# Задаем переменные окружения
ENV DATABASE_URL=${DATABASE_URL}
ENV FLASK_ENV=${FLASK_ENV}
ENV FLASK_APP=run.py

# Открываем порт, на котором будет работать приложение
EXPOSE 8000

# Запускаем приложение с Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "run:app"]
