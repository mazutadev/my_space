from flask import Flask
from .config.config import Config
from .extentions.base import db, migrate, redis_client,api


def create_app():
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    api.init_app(app)

    from .main import main
    app.register_blueprint(main, url_prefix='/')

    with app.app_context():
        from .main import models

    return app
