from .config import BaseConfig
from .settings import ApplicationSettings


class DevelopmentConfig(BaseConfig):
    ENV = "development"
    DEBUG = True

    DB_TYPE = ApplicationSettings.defaults["db_type"]

    DB_HOST = ApplicationSettings.defaults["db_host"]
    DB_PORT = ApplicationSettings.defaults["db_port"]
    DB_USER = ApplicationSettings.defaults["db_user"]
    DB_PASSWORD = ApplicationSettings.defaults["db_password"]
    DB_NAME = ApplicationSettings.defaults["db_name"]
