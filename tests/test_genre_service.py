
from unittest.mock import MagicMock
import pytest

from src.services import genre_service
from src.models.genre import Genre


def test_get_genres():
    db = MagicMock()
    db.query.return_value.order_by.return_value.all.return_value = []

    result = genre_service.get_genres(db)

    assert result == []


def test_get_genre():
    db = MagicMock()
    db.get.return_value = None

    result = genre_service.get_genre(db, 1)

    assert result is None
    db.get.assert_called_once_with(Genre, 1)


def test_create_genre():
    db = MagicMock()

    genre_data = MagicMock()
    genre_data.name = "Action"
    genre_data.model_dump.return_value = {
        "name": "Action",
        "description": "Action movies",
    }

    db.query.return_value.filter.return_value.first.return_value = None

    result = genre_service.create_genre(db, genre_data)

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()
    assert result is not None


def test_create_genre_duplicate():
    db = MagicMock()

    genre_data = MagicMock()
    genre_data.name = "Action"
    genre_data.model_dump.return_value = {
        "name": "Action",
        "description": "Action movies",
    }

    existing_genre = Genre(
        id=1,
        name="Action",
        description="Action movies",
    )

    db.query.return_value.filter.return_value.first.return_value = existing_genre

    with pytest.raises(
        genre_service.DuplicateGenreError,
        match="A genre with this name already exists",
    ):
        genre_service.create_genre(db, genre_data)

    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_update_genre_not_found():
    db = MagicMock()
    db.get.return_value = None

    genre_data = MagicMock()
    genre_data.model_dump.return_value = {"name": "Comedy"}

    result = genre_service.update_genre(db, 1, genre_data)

    assert result is None
    db.get.assert_called_once_with(Genre, 1)


def test_update_genre():
    db = MagicMock()

    genre = Genre(id=1, name="Action", description="Old description")
    db.get.return_value = genre

    genre_data = MagicMock()
    genre_data.model_dump.return_value = {
        "description": "Updated description"
    }

    result = genre_service.update_genre(db, 1, genre_data)

    assert result.description == "Updated description"
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(genre)


def test_update_genre_duplicate():
    db = MagicMock()

    genre = Genre(id=1, name="Action", description="Old")
    existing_genre = Genre(id=2, name="Duplicate", description="Existing")

    db.get.return_value = genre
    db.query.return_value.filter.return_value.filter.return_value.first.return_value = existing_genre

    genre_data = MagicMock()
    genre_data.model_dump.return_value = {"name": "Duplicate"}

    with pytest.raises(
        genre_service.DuplicateGenreError,
        match="A genre with this name already exists",
    ):
        genre_service.update_genre(db, 1, genre_data)

    db.commit.assert_not_called()


def test_delete_genre_not_found():
    db = MagicMock()
    db.get.return_value = None

    result = genre_service.delete_genre(db, 1)

    assert result is False
    db.delete.assert_not_called()


def test_delete_genre():
    db = MagicMock()

    genre = Genre(id=1, name="Action", description="Action movies")
    db.get.return_value = genre

    result = genre_service.delete_genre(db, 1)

    assert result is True
    db.delete.assert_called_once_with(genre)
    db.commit.assert_called_once()
