from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from redis import Redis
from celery import Celery
from flask_restful import Api

from ..config.config import Config

db = SQLAlchemy()
migrate = Migrate()
api = Api()
redis_client = Redis.from_url(Config.REDIS_URL)