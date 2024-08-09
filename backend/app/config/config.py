import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'you-will-never-guess')
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')

    REDIS_URL = os.getenv('REDIS_URL')

    DEBUG = os.getenv('DEBUG', 'False').lower() in ['true', '1', 't']
