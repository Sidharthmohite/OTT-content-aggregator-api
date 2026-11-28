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

## Acceptance checklist

| Requirement | Expected result | Evidence |
| --- | --- | --- |
| Create, list, read, update, and delete | Both resources accept valid requests and return the status codes above | [CRUD workflow tests](../tests/test_genres_platforms_crud.py#L49) and the live PostgreSQL checks below |
| Reject invalid changes | Blank or null names return 422, duplicate names return 409, and stored data is preserved | [Validation and duplicate tests](../tests/test_genres_platforms_crud.py#L102) |
| Preserve omitted fields and clear optional values | PATCH keeps omitted values and accepts null for descriptions and platform URLs | [CRUD workflow](../tests/test_genres_platforms_crud.py#L49) and [platform URL tests](../tests/test_genres_platforms_crud.py#L152) |
| Maintain title associations | Invalid foreign keys are rejected. Deleting a linked genre or platform removes the link and preserves the title | [Relationship tests](../tests/test_genres_platforms_crud.py#L182) |
| Publish errors in OpenAPI | Item operations declare the applicable 404 and 409 responses | [OpenAPI tests](../tests/test_genres_platforms_crud.py#L260) and the [API reference](API_ENDPOINTS.md#genres-and-ott-platforms-owner-m5) |

## Reproduce the automated checks

From the repository root in a PowerShell session with the project virtual environment active:

```powershell
python -m pip install -r requirements.txt
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
$env:DATABASE_URL = 'sqlite://'
$env:SECRET_KEY = python -c 'import secrets; print(secrets.token_hex(32))'
git rev-parse --short HEAD
python -m pytest tests/test_genres_platforms_api.py tests/test_genres_platforms_crud.py tests/test_m3_relationships.py --import-mode=importlib -q
python -m pytest tests --import-mode=importlib -q -rx
```

The environment variables are for the test shell. Use a separate PowerShell session for live PostgreSQL checks.

## Final automated verification

Verified against `eacb21f` on 28 November 2026 using Python 3.14 on Windows, SQLite, and the commands above with third-party pytest plugin autoload disabled.

| Check | Result |
| --- | --- |
| Focused Genre, Platform, and relationship suites | 68 passed |
| Full repository suite under `tests/` | 416 passed in a fresh virtual environment, with one Starlette TestClient deprecation warning |
| Repository migration head from `python -m alembic heads` | `1fdd48ea065c` |

The focused tests are included in the full suite. The 416-test result is from a later revision than the 390-test M3 run. The [M1 verification](../tests/M1_TEST_RESULTS.md) records 26 tests for the movie and web-series API modules present in the verified revision. The historical M3 count and migration questions are tracked in the [M3 report](M3_INTEGRATION_REPORT.md).

### Earlier Week 2 evidence

- Original Week 2 full-suite baseline: 258 passed, with one Starlette TestClient deprecation warning.
- Initial genre/platform API suite: 27 passed.
- Additional CRUD and relationship suite: 35 passed.
- Tests use isolated SQLite databases.
- Relationship tests enable SQLite foreign-key enforcement.
- Tests verify persisted relationships, invalid foreign keys, association
  cleanup, and title preservation after deleting a genre/platform.

## Recorded PostgreSQL verification

- Revision at the time of the Week 2 run: `9e811ea57f63`. See the [M3 report](M3_INTEGRATION_REPORT.md) for the later migration revision.
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

The fresh virtual environment reported one Starlette TestClient deprecation warning. All 416 tests passed.
