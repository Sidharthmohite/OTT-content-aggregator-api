# Week 2: Genre and OTT Platform Management

## Implemented endpoints

Both /genres/ and /platforms/ support:

| Method | Path | Success | Errors |
| --- | --- | --- | --- |
| GET | Collection | 200 | |
| POST | Collection | 201 | 409, 422 |
| GET | /{id} | 200 | 404, 422 |
| PATCH | /{id} | 200 | 404, 409, 422 |
| DELETE | /{id} | 200 | 404, 422 |

## Behavior

- Names are trimmed and must not be blank.
- Explicit null names are rejected on PATCH.
- Genre names allow up to 100 characters.
- Platform names allow up to 150 characters.
- Names use case-sensitive database uniqueness.
- Optional platform URLs use HTTP/HTTPS and allow up to 500 characters.
- PATCH preserves omitted fields.
- Description and platform website URL can be cleared with null.
- Duplicate updates return 409 and preserve the stored record.
- Deleting a genre/platform removes its title links and preserves titles.
- OpenAPI declares not-found and duplicate responses.
- These endpoints currently require no authentication.

## Automated verification

- Full suite: 258 passed, one tracked Starlette deprecation warning.
- Initial genre/platform API suite: 27 passed.
- Additional CRUD and relationship suite: 35 passed.
- Tests use isolated SQLite databases.
- Relationship tests enable SQLite foreign-key enforcement.
- Tests verify persisted relationships, invalid foreign keys, association
  cleanup, and title preservation after deleting a genre/platform.

## PostgreSQL verification

- Migration revision: 9e811ea57f63 (head).
- Alembic check: No new upgrade operations detected.
- No new migration was required.

Live HTTP verification completed on 23 November 2026 using a temporary
Uvicorn server on port 8011 against the configured local PostgreSQL database.

For both genres and platforms, verification covered:
- Creation and retrieval.
- Duplicate PATCH rejection with 409.
- Null and blank name rejection with 422.
- Record preservation after rejected updates.
- Successful PATCH and persisted retrieval.
- Deletion and subsequent GET/PATCH/DELETE returning 404.

Platform checks also verified website URL updates and clearing with null.
All live CRUD checks passed, and all records created by this CRUD run were
deleted successfully. The temporary server stopped automatically.

The earlier six create/duplicate/list checks also passed on port 8010.
Live evidence is recorded from terminal output; screenshots are not included.
Relationship and foreign-key verification above was performed in SQLite,
not independently repeated against live PostgreSQL.

## Remaining maintenance

One Starlette TestClient deprecation warning remains tracked.
