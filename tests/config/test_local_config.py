from demo.config.local import LocalConfig
from demo.config.settings import ApplicationSettings


def test_basic_attributes():
    assert LocalConfig.ENV == "local"
    assert LocalConfig.DEBUG is True
    assert LocalConfig.DB_NAME == ApplicationSettings.defaults["db_name"]


def test_sqlalchemy_database_uri_points_to_instance():
    uri = LocalConfig.SQLALCHEMY_DATABASE_URI

    assert uri.startswith("sqlite:///")
    assert "instance/site.db" in uri
