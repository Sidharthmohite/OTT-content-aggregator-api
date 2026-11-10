# Module Descriptions

## 1. Application Entry Point (`src/main.py`)

The main module initializes the FastAPI application and defines the basic API endpoints.

**Application Details:**
- Application Title: OTT Content Aggregator API
- Description: API to explore movies, web series and OTT platforms
- Version: 1.0.0

**Implemented Endpoints:**

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Returns a welcome message |
| GET | `/health` | Returns the application health status |

## 2. API Module (`src/api/`)

This directory is intended to contain API route handlers.

| File | Intended Responsibility | Status |
|---|---|---|
| `genres.py` | Genre-related endpoints | Placeholder |
| `platforms.py` | OTT platform endpoints | Placeholder |
| `titles.py` | Movie and web-series endpoints | Placeholder |

## 3. Core Module (`src/core/`)

Manages application configuration, database connectivity, and database sessions (assigned to M3).

| File | Intended Responsibility | Status | Implementation Details |
|---|---|---|---|
| `config.py` | Environment and application configuration | Implemented | Built with Pydantic v2 `BaseSettings` (`pydantic-settings`). Reads environment variables (`DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REDIS_URL`) from `.env` with fallback defaults, ensuring secrets and credentials are not hardcoded. |
| `database.py` | Database connection and session management | Implemented | Configures SQLAlchemy `create_engine` with `pool_pre_ping=True`, initializes thread-safe `SessionLocal` sessionmaker, declares the `Base` class for ORM models, provides the `get_db` generator dependency for FastAPI routes, and includes a `test_connection()` verification function. |

### Alembic Migrations (`alembic/`)

Alembic migration environment configured for PostgreSQL database versioning and schema migrations.

| File / Directory | Purpose | Status |
|---|---|---|
| `alembic.ini` | Main Alembic configuration pointing to migration scripts and logging setup | Implemented |
| `alembic/env.py` | Migration runner script dynamically bound to `settings.DATABASE_URL` and `Base.metadata` for automated migration detection | Implemented |
| `alembic/script.py.mako` | Migration template for generating versioned revision scripts | Implemented |
| `alembic/versions/` | Directory where schema migration files are stored | Implemented |

## 4. Models Module (`src/models/`)

Intended to define SQLAlchemy database models.

| File | Intended Responsibility | Status |
|---|---|---|
| `genre.py` | Genre model | Placeholder |
| `platform.py` | OTT platform model | Placeholder |
| `title.py` | Movie and web-series model | Placeholder |
| `user.py` | User model | Placeholder |

## 5. Schemas Module (`src/schemas/`)

Intended to define Pydantic request and response schemas.

| File | Intended Responsibility | Status |
|---|---|---|
| `genre.py` | Genre schemas | Placeholder |
| `platform.py` | Platform schemas | Placeholder |
| `title.py` | Title schemas | Placeholder |
| `user.py` | User schemas | Placeholder |

## 6. Services Module (`src/services/`)

Intended to contain business logic.

| File | Intended Responsibility | Status |
|---|---|---|
| `catalog_service.py` | Catalog-related business operations | Placeholder |

## 7. Implementation Notes

- **Application Entry & Scaffolding:** FastAPI application entry point and basic home/health-check endpoints are functional.
- **Core Database & Configuration (M3):** Database engine, connection pooling, SessionLocal, declarative Base, FastAPI session dependency (`get_db`), environment configuration via Pydantic Settings, and Alembic migration infrastructure are fully implemented.
- **Remaining Modules:** User models & authentication (M2), Title models & catalog service (M4), and Genre/Platform models & endpoints (M5) are structured placeholders and will be implemented by their respective team members according to the 4-week roadmap.
