from unittest.mock import MagicMock


def test_liveness_endpoint(client):
    response = client.get("/api/v1/health/live")
    response_json = response.json

    assert response.status_code == 200
    assert response_json["status"] == "success"
    assert response_json["data"]["status"] == "alive"


def test_readiness_success(client, monkeypatch):
    mock_session = MagicMock()
    mock_session.execute.return_value.scalar_one.return_value = 1

    monkeypatch.setattr("demo.extensions.get_session", lambda: mock_session)

    response = client.get("/api/v1/health/ready")
    response_json = response.json

    assert response.status_code == 200
    assert response_json["status"] == "success"
    assert response_json["data"]["status"] == "ready"


def test_readiness_failure(client, monkeypatch):
    def raise_error():
        raise Exception("DB down")

    # patch where it is used, not defined
    monkeypatch.setattr("demo.blueprints.api.routes.get_session", raise_error)

    response = client.get("/api/v1/health/ready")
    response_json = response.json

    assert response.status_code == 503
    assert response_json["status"] == "error"
