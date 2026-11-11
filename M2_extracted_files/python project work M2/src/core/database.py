"""Database configuration and session management (M3 Core Integration).

Configures the SQLAlchemy engine, session maker, declarative base, and the
get_db dependency for FastAPI routes.
"""

from collections.abc import Generator
from typing import Any

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import declarative_base, sessionmaker, Session
    HAS_SQLALCHEMY = True
except ImportError:  # pragma: no cover
    HAS_SQLALCHEMY = False

from src.core.config import settings

if HAS_SQLALCHEMY:
    # SQLAlchemy Engine configuration
    # pool_pre_ping checks the connection validity before executing queries
    engine = create_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )

    # SessionLocal factory for generating new database sessions per request
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    # Declarative Base class for all SQLAlchemy models across the project
    Base = declarative_base()

    def get_db() -> Generator[Session, None, None]:
        """FastAPI dependency for managing database session lifecycle.

        Yields an active database session and ensures it is safely closed
        when the request completes.
        """
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def test_connection() -> bool:
        """Test the database connection.

        Returns True if connection succeeds, False otherwise.
        """
        try:
            with engine.connect() as conn:
                return True
        except Exception as e:
            print(f"Database connection check error: {e}")
            return False

else:  # pragma: no cover
    # Standalone mock base for environments without SQLAlchemy installed
    class MockBase:
        metadata = None

    Base = MockBase
    engine = None
    SessionLocal = None
    get_db = None
    test_connection = lambda: False


if __name__ == "__main__":
    print(f"Testing database connection to: {settings.DATABASE_URL}")
    if test_connection():
        print("✓ Database connection successful!")
    else:
        print("✗ Database connection failed. Please verify PostgreSQL service and credentials in .env")
