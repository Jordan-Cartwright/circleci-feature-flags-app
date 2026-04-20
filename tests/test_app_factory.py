from demo import db


def test_app_creates(app):
    assert app is not None
    assert app.name is not None


def test_config_loaded(app):
    assert app.config["TESTING"] is True

    assert "DB_TYPE" in app.config
    assert app.config["DB_TYPE"] == "sqlite"

    assert "SQLALCHEMY_DATABASE_URI" in app.config
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"


def test_db_initialized(app):
    assert db.engine is not None
