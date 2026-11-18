# Module Descriptions

Updated on 19 November 2026 for branch `fix/week1-test-cleanup`.

| Module | Current implementation |
| --- | --- |
| `src/main.py` | Creates the FastAPI app, registers title and authentication routers, and exposes home and health routes |
| `src/core/config.py` | Loads database and JWT settings. Warns when the default JWT secret is used |
| `src/core/database.py` | Provides the SQLAlchemy engine, declarative base, and per-request database sessions |
| `src/core/security.py` | Handles password hashing, password verification, JWT creation, and JWT decoding |
| `src/api/auth.py` | Provides registration, JSON login, OAuth2 form login, and authenticated profile endpoints |
| `src/models/user.py` | Defines the user database model |
| `src/schemas/user.py` | Defines user input validation and public response schemas |
| `src/services/user_service.py` | Handles account creation, authentication, and profile updates |
| `src/api/titles.py` | Provides title CRUD and translates missing records, duplicate identities, and validation errors into HTTP responses |
| `src/models/title.py` | Defines title fields, genre/platform relationships, and the `uq_titles_identity` constraint |
| `src/schemas/title.py` | Validates title length, language, release year, positive numeric values, and movie/web-series field combinations |
| `src/services/catalog_service.py` | Implements title CRUD, validates combined PATCH data before saving, and rolls back duplicate-write transactions |
| `src/models/genre.py`, `src/models/platform.py`, `src/models/associations.py` | Define genre/platform models and many-to-many relationships with titles |
| `src/api/genres.py`, `src/api/platforms.py` | Placeholders for dedicated genre and platform endpoints |
| `alembic/` | Contains migration configuration and PostgreSQL schema revisions |
| `tests/` | Contains health, authentication, validation, protected-profile, and title API tests |
| `M2_extracted_files/` | Historical standalone M2 project with its own test suite |

## Title validation

Title creation and PATCH enforce the following rules:

- Titles contain 1 to 255 characters.
- Language is trimmed and must contain non-whitespace characters.
- Movies cannot have a season count.
- Web series cannot have a movie duration.
- Supplied duration and season counts must be greater than zero.

PATCH combines incoming changes with the stored record and validates the resulting data before saving. A content-type change must clear conflicting fields in the same request.

Older records that violate these rules require their conflicting fields to be corrected in the same PATCH request.

## Duplicate handling

Duplicate identity uses the case-sensitive combination of title, content type, release year, and language.

The database enforces this through `uq_titles_identity`. Duplicate POST and PATCH requests return HTTP 409.

Rejected duplicate updates preserve the existing record. The service rolls back the failed transaction, allowing subsequent valid operations.

## Database migrations

| Revision | Purpose |
| --- | --- |
| `bdfe0e261206` | Creates the initial catalog, authentication, and association tables |
| `9e811ea57f63` | Adds the four-column title identity constraint |

Local PostgreSQL is at `9e811ea57f63 (head)`. Alembic reported no new upgrade operations.

## Testing

The latest full automated run reported 176 passed tests, zero expected failures, zero unexpected passes, and one Starlette TestClient deprecation warning.

The title API suite contains 34 passing cases, including combined-record PATCH validation, duplicate rejection, record preservation, and recovery after a rejected duplicate update.

Endpoint tests use in-memory SQLite. PostgreSQL migration verification was performed separately. Live PostgreSQL API checks for the new cleanup behavior remain pending.

## Remaining work

- Persist a unique local JWT secret outside Git.
- Verify duplicate handling and combined-record PATCH behavior against PostgreSQL through the running API.
- Review the Starlette TestClient deprecation warning.
- Verify generated OpenAPI error-response declarations.
- Commit, push, and submit the cleanup branch for review.

Genre/platform endpoints, search/filtering, caching, and background synchronization remain roadmap work.

See the [API reference](API_ENDPOINTS.md), [testing report](WEEK1_TEST_REPORT.md), and [bug report](WEEK1_BUG_REPORT.md).