"""Real SQLite tests for user database uniqueness and transaction rollback."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from src.core.database import Base
from src.models.user import User


@pytest.fixture
def test_db(tmp_path):
    """Create an isolated temporary SQLite database for each test."""

    db_file = tmp_path / "test_users.db"

    test_engine = create_engine(
        f"sqlite:///{db_file.as_posix()}",
    )

    Base.metadata.create_all(bind=test_engine)

    TestSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )

    db = TestSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()


def make_user(email, username):
    """Create a user record for database testing."""

    return User(
        email=email,
        username=username,
        hashed_password="test_hashed_password",
        full_name="Database Test User",
        is_active=True,
        is_superuser=False,
    )


def test_database_rejects_duplicate_email(test_db):
    """The database must reject duplicate emails."""

    original_user = make_user(
        "email@example.com",
        "user_one",
    )

    test_db.add(original_user)
    test_db.commit()

    duplicate_user = make_user(
        "email@example.com",
        "user_two",
    )

    test_db.add(duplicate_user)

    with pytest.raises(IntegrityError):
        test_db.commit()

    test_db.rollback()

    users = test_db.query(User).all()

    assert len(users) == 1
    assert users[0].email == "email@example.com"


def test_database_rejects_duplicate_username(test_db):
    """The database must reject duplicate usernames."""

    original_user = make_user(
        "first@example.com",
        "same_username",
    )

    test_db.add(original_user)
    test_db.commit()

    duplicate_user = make_user(
        "second@example.com",
        "same_username",
    )

    test_db.add(duplicate_user)

    with pytest.raises(IntegrityError):
        test_db.commit()

    test_db.rollback()

    users = test_db.query(User).all()

    assert len(users) == 1
    assert users[0].username == "same_username"


def test_transaction_rollback_preserves_original_data(test_db):
    """Rollback must preserve original data after a failed insert."""

    original_user = make_user(
        "original@example.com",
        "original_user",
    )

    test_db.add(original_user)
    test_db.commit()

    duplicate_user = make_user(
        "original@example.com",
        "rollback_user",
    )

    test_db.add(duplicate_user)

    with pytest.raises(IntegrityError):
        test_db.commit()

    test_db.rollback()

    original_record = (
        test_db.query(User)
        .filter(User.email == "original@example.com")
        .first()
    )

    rolled_back_record = (
        test_db.query(User)
        .filter(User.username == "rollback_user")
        .first()
    )

    assert original_record is not None
    assert original_record.username == "original_user"
    assert rolled_back_record is None