from flask import Flask

from .config import Config


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Blueprints
    from .routes.main import bp as main_bp
    from .routes.game import bp as game_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(game_bp)

    # Глобальные переменные для шаблонов
    @app.context_processor
    def inject_globals():
        from datetime import datetime
        return {"current_year": datetime.now().year}

    return app