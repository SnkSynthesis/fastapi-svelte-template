from fastapi.testclient import TestClient


def test_root(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200, response.text
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
