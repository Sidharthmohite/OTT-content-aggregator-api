
from unittest.mock import MagicMock
import pytest

from src.services import platform_service
from src.models.platform import Platform


def test_get_platforms():
    db = MagicMock()
    db.query.return_value.order_by.return_value.all.return_value = []

    result = platform_service.get_platforms(db)

    assert result == []


def test_get_platform():
    db = MagicMock()
    db.get.return_value = None

    result = platform_service.get_platform(db, 1)

    assert result is None


def test_create_platform():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None

    platform_data = MagicMock()
    platform_data.name = "Netflix"
    platform_data.model_dump.return_value = {
        "name": "Netflix",
        "website_url": "https://netflix.com",
        "description": "Streaming platform"
    }

    result = platform_service.create_platform(db, platform_data)

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()
    assert result is not None


def test_create_platform_duplicate():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None

    platform_data = MagicMock()
    platform_data.name = "Netflix"
    platform_data.model_dump.return_value = {
        "name": "Netflix",
        "website_url": "https://netflix.com",
        "description": "Streaming platform"
    }

    from sqlalchemy.exc import IntegrityError

    error = IntegrityError("duplicate", None, Exception("UNIQUE constraint failed: platforms.name"))
    db.commit.side_effect = error

    with pytest.raises(platform_service.DuplicatePlatformError):
        platform_service.create_platform(db, platform_data)

    db.rollback.assert_called_once()
def test_update_platform_not_found():
    db = MagicMock()
    db.get.return_value = None
    db.query.return_value.filter.return_value.first.return_value = None

    platform_data = MagicMock()
    platform_data.model_dump.return_value = {"name": "Amazon Prime"}

    result = platform_service.update_platform(db, 1, platform_data)

    assert result is None


def test_update_platform():
    db = MagicMock()
    platform = Platform(
        id=1,
        name="Netflix",
        website_url="https://netflix.com",
        description="Old description"
    )
    db.get.return_value = platform

    platform_data = MagicMock()
    platform_data.model_dump.return_value = {
        "description": "Updated description"
    }

    result = platform_service.update_platform(db, 1, platform_data)

    assert result.description == "Updated description"
    db.commit.assert_called_once()
    db.refresh.assert_called_once()


def test_update_platform_duplicate():
    db = MagicMock()

    platform = Platform(
        id=1,
        name="Netflix",
        website_url="https://netflix.com",
        description="Old description"
    )

    db.get.return_value = platform
    db.query.return_value.filter.return_value.filter.return_value.first.return_value = None

    platform_data = MagicMock()
    platform_data.model_dump.return_value = {"name": "Duplicate"}

    from sqlalchemy.exc import IntegrityError

    error = IntegrityError("duplicate", None, Exception("UNIQUE constraint failed: platforms.name"))
    db.commit.side_effect = error

    with pytest.raises(platform_service.DuplicatePlatformError):
        platform_service.update_platform(db, 1, platform_data)

    db.rollback.assert_called_once()
def test_delete_platform_not_found():
    db = MagicMock()
    db.get.return_value = None

    result = platform_service.delete_platform(db, 1)

    assert result is False


def test_delete_platform():
    db = MagicMock()
    platform = Platform(
        id=1,
        name="Netflix",
        website_url="https://netflix.com",
        description="Streaming platform"
    )
    db.get.return_value = platform

    result = platform_service.delete_platform(db, 1)

    assert result is True
    db.delete.assert_called_once_with(platform)
    db.commit.assert_called_once()


def test_update_platform_website_url():
    db = MagicMock()
    platform = Platform(
        id=1,
        name="Netflix",
        website_url="https://old-netflix.com",
        description="Streaming platform",
    )
    db.get.return_value = platform
    db.query.return_value.filter.return_value.filter.return_value.first.return_value = None

    platform_data = MagicMock()
    platform_data.model_dump.return_value = {
        "website_url": "https://netflix.com"
    }

    result = platform_service.update_platform(db, 1, platform_data)

    assert result.website_url == "https://netflix.com"
    db.commit.assert_called_once()
    db.refresh.assert_called_once()
