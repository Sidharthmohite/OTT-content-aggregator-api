# Module Descriptions

| Module | Current implementation |
| --- | --- |
| `src/main.py` | Registers title and auth routers and exposes home and health routes. Health reports app liveness. |
| `src/core/config.py` | Loads database URL, JWT settings, and other application settings. |
| `src/core/database.py` | SQLAlchemy engine, declarative base and per-request database session. |
| `src/core/security.py` | Password hashing and verification, token creation and decoding. |
| `src/api/auth.py` | Registration and login endpoints. |
| `src/models/user.py`, `src/schemas/user.py`, `src/services/user_service.py` | User persistence, validation, public response schemas, and account authentication. |
| `src/api/titles.py`, `src/models/title.py`, `src/schemas/title.py`, `src/services/catalog_service.py` | Catalog CRUD, persistence and request/response validation. |
| `src/models/genre.py`, `src/models/platform.py`, `src/models/associations.py` | Genre and platform models and many-to-many relationships with titles. |
| `src/api/genres.py`, `src/api/platforms.py` | Placeholders for dedicated endpoints. |
| `alembic/` | Model metadata and initial PostgreSQL migration `bdfe0e261206`. |
| `tests/` | Main project tests for health, title CRUD, auth API, and auth validation. |
| `M2_extracted_files/` | Standalone historical M2 project with its own test suite. |

See the [API reference](API_ENDPOINTS.md) and [pending issues](WEEK1_BUG_REPORT.md).
