# Module Descriptions

See the [Week 2 verification](WEEK2_GENRES_PLATFORMS.md) for Genre and Platform evidence.

| Module | Current implementation |
| --- | --- |
| `src/main.py` | Creates the FastAPI app, registers title, movie, web-series, authentication, genre, and platform routers, and exposes home and health routes |
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
| `src/api/genres.py`, `src/api/platforms.py` | Provide list, create, retrieve, update, and delete endpoints for genres and platforms |
| `src/schemas/genre.py`, `src/schemas/platform.py` | Validate request fields and define response models |
| `src/services/genre_service.py`, `src/services/platform_service.py` | Implement CRUD, duplicate-name handling, and association cleanup |
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
| `1fdd48ea065c` | Updates SQLite timestamp defaults |

See the [M3 integration report](M3_INTEGRATION_REPORT.md) for the current migration head, database checks, and outstanding revision clarification.

## Testing

The [Week 1 verification](WEEK1_FINAL_VERIFICATION.md) records the title and authentication baseline. The [Week 2 verification](WEEK2_GENRES_PLATFORMS.md) records Genre and Platform API, validation, and relationship tests alongside separate live PostgreSQL checks.
