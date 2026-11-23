
from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from src.core.config import settings


# SQLAlchemy Engine configuration
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)


# Enable foreign keys for SQLite connections
if engine.dialect.name == "sqlite":

    @event.listens_for(engine, "connect")
    def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# SessionLocal factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# Declarative Base
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for managing database session lifecycle."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection() -> bool:
    """Test the database connection."""
    try:
        with engine.connect() as conn:
            return True
    except Exception as e:
        print(f"Database connection check error: {e}")
        return False


if __name__ == "__main__":
    print(f"Testing database connection to: {settings.DATABASE_URL}")

    if test_connection():
        print("✓ Database connection successful!")
    else:
        print(
            "✗ Database connection failed. "
            "Please verify PostgreSQL service and credentials in .env"
        )
