import pytest
from unittest.mock import MagicMock
from sqlalchemy.exc import IntegrityError

from src.services.catalog_service import commit_title


def test_commit_title_reraises_non_duplicate_integrity_error():
    db = MagicMock()

    original_error = IntegrityError(
        "INSERT statement",
        {},
        Exception("Foreign key constraint failed"),
    )

    db.commit.side_effect = original_error

    with pytest.raises(IntegrityError) as exc_info:
        commit_title(db)

    assert exc_info.value is original_error
    db.rollback.assert_called_once()