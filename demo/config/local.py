import os
from pathlib import Path

from .config import BASEDIR, BaseConfig
from .settings import ApplicationSettings


class LocalConfig(BaseConfig):
    ENV = "local"
    DEBUG = True

    DB_PATH = os.path.join(BASEDIR, "instance", "site.db")
    DB_NAME = ApplicationSettings.defaults["db_name"]

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"

    @staticmethod
    def init_app(app):
        # Ensure instance folder exists
        instance_path = Path(app.instance_path)
        instance_path.mkdir(parents=True, exist_ok=True)
