from fastapi.testclient import TestClient
from fastapi import status
from requests.models import Response
import pytest

ITEM_API_URL = "/api/v1/items"

item = {
    "name": "This is an item",
    "desc": "This is a very cool item",
    "owner_username": "user_a",
}

updated_item = {
    "name": "This is a renamed item",
    "desc": "This is a very cool item, however, it has been renamed",
    "owner_username": "user_a",
}


def test_error_responses(client: TestClient) -> None:
    def check_response(response: Response) -> None:
        assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
        assert response.json() == {"detail": "Not Found"}

    check_response(client.get(f"{ITEM_API_URL}/1"))
    check_response(client.put(f"{ITEM_API_URL}/1", json=updated_item))
    check_response(client.delete(f"{ITEM_API_URL}/1"))


@pytest.mark.dependency()
def test_create(client: TestClient) -> None:
    response = client.post(f"{ITEM_API_URL}/", json=item)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    data = response.json()
    assert "id" in data
    del data["id"]
    assert data == item


@pytest.mark.dependency(depends=["test_create"])
def test_read(client: TestClient) -> None:
    response = client.get(f"{ITEM_API_URL}/1")
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    data = response.json()
    assert "id" in data
    data_without_id = data.copy()
    del data_without_id["id"]
    assert data_without_id == item

    response = client.get(f"{ITEM_API_URL}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    assert isinstance(response.json(), list)
    assert data in response.json()


@pytest.mark.dependency(depends=["test_read"])
def test_update(client: TestClient) -> None:
    response = client.put(f"{ITEM_API_URL}/1", json=updated_item)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    data = response.json()
    assert "id" in data
    del data["id"]
    assert data == updated_item


@pytest.mark.dependency(depends=["test_update"])
def test_delete(client: TestClient) -> None:
    response = client.delete(f"{ITEM_API_URL}/1")
    assert response.status_code == status.HTTP_204_NOT_FOUND, response.text
