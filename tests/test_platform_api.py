from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from src.main import app
from src.models.platform import Platform

client = TestClient(app)


@patch("src.api.platforms.platform_service.get_platforms")
def test_read_platforms(mock_get):
    mock_get.return_value = []
    response = client.get("/platforms/")
    assert response.status_code == 200
    assert response.json() == []


@patch("src.api.platforms.platform_service.get_platform")
def test_read_platform_not_found(mock_get):
    mock_get.return_value = None
    response = client.get("/platforms/999")
    assert response.status_code == 404


@patch("src.api.platforms.platform_service.get_platform")
def test_read_platform_success(mock_get):
    mock_get.return_value = Platform(
        id=1,
        name="Netflix",
        website_url="https://netflix.com",
        description="Streaming platform"
    )
    response = client.get("/platforms/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Netflix"


@patch("src.api.platforms.platform_service.create_platform")
def test_create_platform_success(mock_create):
    mock_create.return_value = Platform(
        id=1,
        name="Netflix",
        website_url="https://netflix.com",
        description="Streaming platform"
    )
    response = client.post(
        "/platforms/",
        json={
            "name": "Netflix",
            "website_url": "https://netflix.com",
            "description": "Streaming platform"
        }
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Netflix"


@patch("src.api.platforms.platform_service.create_platform")
def test_create_platform_duplicate(mock_create):
    mock_create.side_effect = ValueError("Platform already exists")
    response = client.post(
        "/platforms/",
        json={
            "name": "Netflix",
            "website_url": "https://netflix.com",
            "description": "Streaming platform"
        }
    )
    assert response.status_code == 409


@patch("src.api.platforms.platform_service.update_platform")
def test_update_platform_success(mock_update):
    mock_update.return_value = Platform(
        id=1,
        name="Netflix",
        website_url="https://netflix.com",
        description="Updated description"
    )
    response = client.patch(
        "/platforms/1",
        json={"description": "Updated description"}
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Updated description"


@patch("src.api.platforms.platform_service.update_platform")
def test_update_platform_not_found(mock_update):
    mock_update.return_value = None
    response = client.patch("/platforms/999", json={"description": "Updated"})
    assert response.status_code == 404


@patch("src.api.platforms.platform_service.update_platform")
def test_update_platform_duplicate(mock_update):
    mock_update.side_effect = ValueError("Platform already exists")
    response = client.patch("/platforms/1", json={"name": "Duplicate"})
    assert response.status_code == 409


@patch("src.api.platforms.platform_service.delete_platform")
def test_delete_platform_success(mock_delete):
    mock_delete.return_value = True
    response = client.delete("/platforms/1")
    assert response.status_code == 200
    assert response.json()["message"] == "Platform deleted successfully"


@patch("src.api.platforms.platform_service.delete_platform")
def test_delete_platform_not_found(mock_delete):
    mock_delete.return_value = False
    response = client.delete("/platforms/999")
    assert response.status_code == 404