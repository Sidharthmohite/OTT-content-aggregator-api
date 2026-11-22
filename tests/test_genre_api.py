from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from src.main import app
from src.models.genre import Genre

client = TestClient(app)


@patch("src.api.genres.genre_service.get_genres")
def test_read_genres(mock_get):
    mock_get.return_value = []
    response = client.get("/genres/")
    assert response.status_code == 200
    assert response.json() == []


@patch("src.api.genres.genre_service.get_genre")
def test_read_genre_not_found(mock_get):
    mock_get.return_value = None
    response = client.get("/genres/999")
    assert response.status_code == 404


@patch("src.api.genres.genre_service.get_genre")
def test_read_genre_success(mock_get):
    mock_get.return_value = Genre(id=1, name="Action", description="Action movies")
    response = client.get("/genres/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Action"


@patch("src.api.genres.genre_service.create_genre")
def test_create_genre_success(mock_create):
    mock_create.return_value = Genre(id=1, name="Comedy", description="Funny movies")
    response = client.post("/genres/", json={"name": "Comedy", "description": "Funny movies"})
    assert response.status_code == 201
    assert response.json()["name"] == "Comedy"


@patch("src.api.genres.genre_service.create_genre")
def test_create_genre_duplicate(mock_create):
    mock_create.side_effect = ValueError("Genre already exists")
    response = client.post("/genres/", json={"name": "Action", "description": "Action movies"})
    assert response.status_code == 409


@patch("src.api.genres.genre_service.update_genre")
def test_update_genre_success(mock_update):
    mock_update.return_value = Genre(id=1, name="Action", description="Updated")
    response = client.patch("/genres/1", json={"description": "Updated"})
    assert response.status_code == 200
    assert response.json()["description"] == "Updated"


@patch("src.api.genres.genre_service.update_genre")
def test_update_genre_not_found(mock_update):
    mock_update.return_value = None
    response = client.patch("/genres/999", json={"description": "Updated"})
    assert response.status_code == 404


@patch("src.api.genres.genre_service.update_genre")
def test_update_genre_duplicate(mock_update):
    mock_update.side_effect = ValueError("Genre already exists")
    response = client.patch("/genres/1", json={"name": "Duplicate"})
    assert response.status_code == 409


@patch("src.api.genres.genre_service.delete_genre")
def test_delete_genre_success(mock_delete):
    mock_delete.return_value = True
    response = client.delete("/genres/1")
    assert response.status_code == 200
    assert response.json()["message"] == "Genre deleted successfully"


@patch("src.api.genres.genre_service.delete_genre")
def test_delete_genre_not_found(mock_delete):
    mock_delete.return_value = False
    response = client.delete("/genres/999")
    assert response.status_code == 404