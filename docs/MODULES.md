# Module Descriptions

> File names below come from the repo's initial commit (`tree src`); descriptions are still planned and the files may be empty placeholders. Replace/confirm each section with what M2–M5 actually implemented so documentation matches the code.

| Module | Owner | Planned description | Actual code status |
|---|---|---|---|
| User model & authentication | M2 | `src/models/user.py`, `src/schemas/user.py` exist; `auth_service.py`, `security.py` and the auth route are planned: registration, login, password hashing, JWT | _TBC from M2_ |
| Database configuration | M3 | `src/core/database.py`, `src/core/config.py` exist; Alembic setup is planned: PostgreSQL connection, sessions, migrations | _TBC from M3_ |
| Title model & schemas | M4 | `src/models/title.py`, `src/schemas/title.py`, `src/api/titles.py`, `src/services/catalog_service.py` | _TBC from M4_ |
| Genre & Platform | M5 | `src/models/genre.py`, `src/models/platform.py`, matching schemas, `src/api/genres.py`, `src/api/platforms.py` | _TBC from M5_ |

## Information to collect from each member

- Files created and their purpose
- Model fields / schema fields and relationships
- Endpoints added (method, path, auth)
- Any deviation from the suggested structure
