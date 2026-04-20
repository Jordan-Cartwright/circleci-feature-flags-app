import pytest

from demo import create_app
from demo.config.local import LocalConfig
from demo.config.settings import ApplicationSettings


@pytest.fixture
def app(tmp_path):
    app = create_app("local")

    # ensure isolation per test run
    app.instance_path = str(tmp_path / "instance")

    with app.app_context():
        yield app


def test_basic_attributes():
    assert LocalConfig.ENV == "local"
    assert LocalConfig.DEBUG is True
    assert LocalConfig.DB_NAME == ApplicationSettings.defaults["db_name"]


def test_sqlalchemy_database_uri_points_to_instance(app):
    LocalConfig.init_app(app)

    uri = app.config["SQLALCHEMY_DATABASE_URI"]

    assert uri.startswith("sqlite:///")
    assert "instance/site.db" in uri
