from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from pathlib import Path

from config import Config, ProductionConfig, BASE_DIR


db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=ProductionConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp)

    error_handlers(app)

    # with app.app_context():
    #     db.create_all()

    # Create uploads folder if it doesn't exist
    Path(BASE_DIR + "/app/static/uploads").mkdir(parents=True, exist_ok=True)

    return app


def error_handlers(app):
    """
    Present error messages in JSON.
    """
    from app.api.errors import error_response

    @app.errorhandler(404)
    def not_found_error(error):
        return error_response(404, 'Запрашиваемый ресурс не обнаружен.')

    @app.errorhandler(500)
    def internal_error(error):
        return error_response(500, 'Ошибка сервера.')

    @app.errorhandler(405)
    def not_found_error(error): # noqa
        return error_response(405, 'Недопустимый метод.')


from app import models # noqa
