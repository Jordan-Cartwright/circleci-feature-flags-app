import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


import pytest

from demo import create_app, db


@pytest.fixture(scope="session")
def app():
    app = create_app("testing")

    with app.app_context():
        # Apply migrations to the test database
        db.create_all()

        yield app

        # Clean up DB state after all tests are done
        db.drop_all()
        db.session.remove()
        db.engine.dispose()


@pytest.fixture
def session(app):
    return db.session


@pytest.fixture
def client(app):
    return app.test_client()
