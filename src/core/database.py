from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from src.core.config import settings

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


if __name__ == "__main__":
    print(f"Testing database connection to: {settings.DATABASE_URL}")
    if test_connection():
        print("✓ Database connection successful!")
    else:
        print(
            "✗ Database connection failed. Please verify PostgreSQL service and credentials in .env"
        )
