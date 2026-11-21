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
    from sqlalchemy import create_engine, text

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
    from src.core import database

    def failing_connect():
        raise Exception("Database unavailable")

    monkeypatch.setattr(database.engine, "connect", failing_connect)

    assert database.test_connection() is False