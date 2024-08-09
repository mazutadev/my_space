FROM python:3.12-slim

WORKDIR /app

COPY ./backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["celery", "-A", "tasks", "worker", "--loglevel=info"]
