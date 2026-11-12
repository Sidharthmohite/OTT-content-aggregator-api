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
| `titles.py` | Movie and web-series endpoints | Implemented (M4) |

## 3. Core Module (`src/core/`)

Manages application configuration, database connectivity, and database sessions (assigned to M3).

| File | Intended Responsibility | Status | Implementation Details |
|---|---|---|---|
| `config.py` | Environment and application configuration | Implemented (M3) | Built with Pydantic v2 `BaseSettings` (`pydantic-settings`). Reads environment variables (`DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REDIS_URL`) from `.env` with fallback defaults, ensuring secrets and credentials are not hardcoded. |
| `database.py` | Database connection and session management | Implemented (M3) | Configures SQLAlchemy `create_engine` with `pool_pre_ping=True`, initializes thread-safe `SessionLocal` sessionmaker, declares the `Base` class for ORM models, provides the `get_db` generator dependency for FastAPI routes, and includes a `test_connection()` verification function. |

### Alembic Migrations (`alembic/`)

Alembic migration environment configured for PostgreSQL database versioning and schema migrations.

| File / Directory | Purpose | Status |
|---|---|---|
| `alembic.ini` | Main Alembic configuration pointing to migration scripts and logging setup | Implemented (M3) |
| `alembic/env.py` | Migration runner script dynamically bound to `settings.DATABASE_URL` and `Base.metadata` for automated migration detection | Implemented (M3) |
| `alembic/script.py.mako` | Migration template for generating versioned revision scripts | Implemented (M3) |
| `alembic/versions/` | Directory where schema migration files are stored | Implemented (M3) |

## 4. Models Module (`src/models/`)

Intended to define SQLAlchemy database models.

| File | Intended Responsibility | Status |
|---|---|---|
| `genre.py` | Genre model | Placeholder |
| `platform.py` | OTT platform model | Placeholder |
| `title.py` | Movie and web-series model | Implemented (M4) |
| `user.py` | User model | Placeholder |

## 5. Schemas Module (`src/schemas/`)

Intended to define Pydantic request and response schemas.

| File | Intended Responsibility | Status |
|---|---|---|
| `genre.py` | Genre schemas | Placeholder |
| `platform.py` | Platform schemas | Placeholder |
| `title.py` | Title schemas | Implemented (M4) |
| `user.py` | User schemas | Placeholder |

## 6. Services Module (`src/services/`)

Intended to contain business logic.

| File | Intended Responsibility | Status |
|---|---|---|
| `catalog_service.py` | Catalog-related business operations | Implemented (M4) |

## 7. Team Ownership Overview

| Module | Owner | Status |
|---|---|---|
| User model & authentication | M2 | `src/models/user.py`, `src/schemas/user.py` exist; `auth_service.py`, `security.py` and the auth route are planned |
| Database configuration & Alembic | M3 | Fully implemented: `src/core/database.py`, `src/core/config.py`, `alembic.ini`, and `alembic/` |
| Title model & catalog service | M4 | Implemented: `src/models/title.py`, `src/schemas/title.py`, `src/api/titles.py`, `src/services/catalog_service.py` |
| Genre & Platform | M5 | `src/models/genre.py`, `src/models/platform.py`, matching schemas, `src/api/genres.py`, `src/api/platforms.py` |
| Documentation & Testing | M6 | `README.md`, `docs/`, and `tests/testing_checklist.md` |

## 8. Implementation Notes

- **Application Entry & Scaffolding:** FastAPI application entry point and basic home/health-check endpoints are functional.
- **Core Database & Configuration (M3):** Database engine, connection pooling, SessionLocal, declarative Base, FastAPI session dependency (`get_db`), environment configuration via Pydantic Settings, and Alembic migration infrastructure are fully implemented.
- **Catalog Service & Title Models (M4):** Title model, schema validation, and catalog CRUD service added.
- **Remaining Modules:** User models & authentication (M2) and Genre/Platform models & endpoints (M5) will be implemented by their respective team members according to the 4-week roadmap.

