import logging
from logging.handlers import RotatingFileHandler
import os
from ..config.config import Config

def setup_logger():

    if not os.path.exists('logs'):
        os.makedirs('logs')

    logger = logging.getLogger('backend')
    logger.setLevel(Config.LOGGING_LEVEL)

    handler = RotatingFileHandler(Config.LOGGING_LOCATION, maxBytes=1000000, backupCount=3)
    handler.setLevel(Config.LOGGING_LEVEL)

    formatter = logging.Formatter(Config.LOGGING_FORMAT)
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger