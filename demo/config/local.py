import os
from pathlib import Path

from .config import BASEDIR, BaseConfig
from .settings import ApplicationSettings


class LocalConfig(BaseConfig):
    ENV = "local"
    DEBUG = True

    DB_TYPE = "sqlite"

    DB_PATH = os.path.join(BASEDIR, "instance", "site.db")
    DB_NAME = ApplicationSettings.defaults["db_name"]

    @classmethod
    def init_app(cls, app):
        # Ensure instance folder exists
        instance_path = Path(app.instance_path)
        instance_path.mkdir(parents=True, exist_ok=True)

        super(LocalConfig, LocalConfig).init_app(app)
