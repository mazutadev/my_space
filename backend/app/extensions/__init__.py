from .base import db, migrate, api, jwt, redis_client
from .logger import setup_logger

logger = setup_logger()