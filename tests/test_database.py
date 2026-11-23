
from unittest.mock import MagicMock

from sqlalchemy import create_engine, event

from src.core import database


class FakeSession:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


def test_get_db_closes_session(monkeypatch):
    fake_db = FakeSession()
    monkeypatch.setattr(database, "SessionLocal", lambda: fake_db)

    generator = database.get_db()
    db = next(generator)

    assert db is fake_db
    assert fake_db.closed is False

    generator.close()
    assert fake_db.closed is True


def test_get_db_closes_session_after_exception(monkeypatch):
    fake_db = FakeSession()
    monkeypatch.setattr(database, "SessionLocal", lambda: fake_db)

    generator = database.get_db()
    next(generator)

    try:
        generator.throw(RuntimeError("Test exception"))
    except RuntimeError:
        pass

    assert fake_db.closed is True


def test_transaction_rollback():
    from sqlalchemy import text

    test_engine = create_engine("sqlite://")

    with test_engine.connect() as connection:
        connection.execute(
            text("CREATE TABLE rollback_test (id INTEGER, name TEXT)")
        )
        connection.commit()

        transaction = connection.begin()

        connection.execute(
            text("INSERT INTO rollback_test VALUES (1, 'test')")
        )

        transaction.rollback()

        result = connection.execute(
            text("SELECT COUNT(*) FROM rollback_test")
        ).scalar()

        assert result == 0

    test_engine.dispose()


def test_connection_returns_false_on_failure(monkeypatch):
    def failing_connect():
        raise Exception("Database unavailable")

    monkeypatch.setattr(database.engine, "connect", failing_connect)

    assert database.test_connection() is False


def test_connection_returns_true(monkeypatch):
    mock_engine = MagicMock()
    monkeypatch.setattr(database, "engine", mock_engine)

    assert database.test_connection() is True


def test_sqlite_foreign_key_listener():
    sqlite_engine = create_engine("sqlite://")

    @event.listens_for(sqlite_engine, "connect")
    def enable_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    with sqlite_engine.connect() as connection:
        result = connection.exec_driver_sql("PRAGMA foreign_keys")
        assert result.scalar() == 1

    sqlite_engine.dispose()
def test_database_main_success(monkeypatch, capsys):
    import runpy
    import sqlalchemy

    sqlite_engine = create_engine("sqlite://")

    monkeypatch.setattr(
        sqlalchemy,
        "create_engine",
        lambda *args, **kwargs: sqlite_engine,
    )

    runpy.run_path(database.__file__, run_name="__main__")

    output = capsys.readouterr().out
    assert "Database connection successful" in output

    with sqlite_engine.connect() as connection:
        result = connection.exec_driver_sql("PRAGMA foreign_keys")
        assert result.scalar() == 1

    sqlite_engine.dispose()


def test_database_main_failure(monkeypatch, capsys):
    import runpy
    import sqlalchemy

    sqlite_engine = create_engine("sqlite://")

    def failing_connect():
        raise Exception("Database unavailable")

    monkeypatch.setattr(sqlite_engine, "connect", failing_connect)

    monkeypatch.setattr(
        sqlalchemy,
        "create_engine",
        lambda *args, **kwargs: sqlite_engine,
    )

    runpy.run_path(database.__file__, run_name="__main__")

    output = capsys.readouterr().out

    assert "Database connection failed" in output
    assert "Database unavailable" in output

    sqlite_engine.dispose()
