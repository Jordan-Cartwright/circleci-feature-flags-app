def test_create_flag_api(client):
    response = client.post("/api/v1/flags", json={"name": "api_flag"})
    response_json = response.json

    assert response.status_code == 201
    assert response_json["status"] == "success"

    assert "data" in response_json
    assert response_json["data"]["name"] == "api_flag"
