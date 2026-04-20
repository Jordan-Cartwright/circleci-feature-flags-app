import os

from flask import Flask

from .config import Config
from .config.settings import ApplicationSettings
from .extensions import db, migrate


def create_app(config_name: str = "") -> Flask:
    # Respect the FLASK_ENV when running database migrations
    if config_name == "":
        config_name = os.getenv("FLASK_ENV", "default")

    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # Load config class and Instantiate the config object
    app_config = Config[config_name]()
    app.config.from_object(app_config)

    # Load any settings defined with environment variables
    ApplicationSettings.load_environment(app)

    # Run config-specific initialization
    app_config.init_app(app)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from .blueprints.api import api_blueprint
    from .blueprints.dashboard import ui_blueprint

    app.register_blueprint(ui_blueprint)
    app.register_blueprint(api_blueprint)

    return app
