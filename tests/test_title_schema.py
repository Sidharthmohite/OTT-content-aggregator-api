"""Tests for TitleCreate and TitleUpdate schemas."""

import pytest

from src.schemas.title import TitleCreate, TitleUpdate


def test_title_update_language_strips_whitespace():
    """Language should be stripped of surrounding whitespace."""
    title = TitleUpdate(language="  English  ")
    assert title.language == "English"


def test_title_create_language_strips_whitespace():
    """Language should be stripped when creating a title."""
    title = TitleCreate(
        title="Test Movie",
        content_type="movie",
        release_year=2020,
        language="  English  ",
    )
    assert title.language == "English"


def test_title_update_rejects_blank_language():
    """Language must not be blank when explicitly supplied."""
    with pytest.raises(ValueError):
        TitleUpdate(language="   ")
