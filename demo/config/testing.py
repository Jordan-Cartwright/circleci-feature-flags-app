from .config import BaseConfig


class TestingConfig(BaseConfig):
    ENV = "testing"
    TESTING = True

    DB_TYPE = "sqlite"
