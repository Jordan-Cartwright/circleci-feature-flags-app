from .config import BaseConfig


class TestingConfig(BaseConfig):
    ENV = "testing"
    TESTING = True

    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    @staticmethod
    def init_app(app):
        pass
