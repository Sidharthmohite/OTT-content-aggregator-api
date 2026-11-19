# Week 1 Testing Report

## Latest verification

Verified locally on 19 November 2026 on branch `fix/week1-test-cleanup`.

| Check | Result |
| --- | --- |
| Full automated test suite | 176 passed, 0 failed |
| Expected failures | 0 |
| Unexpected passes | 0 |
| Warning occurrences | 1 Starlette TestClient deprecation warning |
| Title API test suite | 34 passed |
| PostgreSQL migration | `9e811ea57f63 (head)` |
| Alembic schema comparison | No new upgrade operations detected |

Authentication and catalog endpoint tests use an in-memory SQLite database. PostgreSQL migration checks were performed separately against the local `ott_catalog` database.

The latest full test run used a generated `SECRET_KEY` supplied through the PowerShell environment. Persistent local secret configuration remains pending.

## Verification commands

Run from the repository root with the virtual environment active:

```powershell
python -m pytest tests --import-mode=importlib -q
python -m pytest tests/test_titles_api.py --import-mode=importlib -q
python -m alembic current
python -m alembic check
```

## Test coverage

| Test file | Verified coverage |
| --- | --- |
| `tests/test_health.py` | Welcome message and application liveness |
| `tests/test_auth_api.py` | Registration, login, duplicate accounts, invalid credentials, malformed requests, and inactive-user rejection |
| `tests/test_auth_validation.py` | Email, username, and password validation, password hashing, token creation, token decoding, and invalid or expired tokens |
| `tests/test_auth_complete.py` | Additional authentication and protected-profile scenarios |
| `tests/test_titles_api.py` | Title CRUD, field validation, combined-record PATCH validation, duplicate handling, and recovery after rejected updates |

## Resolved expected failures

All nine cases marked as expected failures in the original baseline now pass. Their outdated `xfail` decorators have been removed.

| Test case | Current result |
| --- | --- |
| `test_gap_inactive_user_cannot_login` | Passed. Inactive accounts are rejected |
| `test_gap_loose_email_regex[a@b..]` | Passed. Malformed email is rejected |
| `test_gap_loose_email_regex[a@b.-]` | Passed. Malformed email is rejected |
| `test_gap_loose_email_regex[a@-b.com]` | Passed. Malformed email is rejected |
| `test_gap_empty_language_rejected` | Passed. Empty language is rejected |
| `test_gap_movie_with_seasons_rejected` | Passed. Movies cannot have a season count |
| `test_gap_series_with_duration_rejected` | Passed. Web series cannot have a movie duration |
| `test_gap_patch_title_too_long_rejected` | Passed. PATCH rejects titles longer than 255 characters |
| `test_gap_duplicate_title_rejected` | Passed. Duplicate title identities return HTTP 409 |

## PATCH regression tests

| Test | Verified behavior |
| --- | --- |
| `test_patch_changes_only_given_fields` | Updates the supplied field and preserves other response fields |
| `test_patch_rejects_invalid_combination_without_saving` | Rejects conflicting movie or series fields and preserves the stored record |
| `test_patch_can_change_type_and_clear_conflicting_field` | Accepts a content-type change when the conflicting field is cleared in the same request |
| `test_duplicate_patch_returns_409_and_preserves_record` | Returns HTTP 409 for a duplicate identity, preserves the record, and accepts a subsequent valid update |

The invalid-combination test covers four parameterized cases. Parameterized tests contribute multiple cases to the reported totals.

## Duplicate-title rule

A duplicate has the same combination of:

- Title
- Content type
- Release year
- Language

Text matching is case-sensitive. Different release years are allowed, supporting remakes with the same name.

The database enforces the rule through the `uq_titles_identity` unique constraint. POST and PATCH return HTTP 409 when this constraint is violated.

The service rolls back the failed transaction. SQLite regression tests verify that a rejected duplicate PATCH preserves the existing record and that a subsequent valid update succeeds.

## PostgreSQL migration verification

| Item | Verified value |
| --- | --- |
| Development database | `ott_catalog` |
| Previous revision | `bdfe0e261206` |
| New revision | `9e811ea57f63` |
| Migration file | `alembic/versions/9e811ea57f63_add_unique_title_identity_constraint.py` |
| Constraint | `uq_titles_identity` |
| Duplicate precheck | No duplicate groups found |
| Upgrade result | Applied successfully |
| Current revision | `9e811ea57f63 (head)` |
| Schema comparison | No new upgrade operations detected |

Live PostgreSQL API verification of duplicate POST/PATCH handling remains pending. The automated duplicate tests use SQLite.

## Live API evidence

The earlier Swagger checks returned the expected status codes.

| Request | Observed HTTP status |
| --- | --- |
| GET `/health` | 200 |
| POST `/auth/register` | 201 |
| POST `/auth/login` with valid credentials | 200 |
| POST `/auth/login` with an incorrect password | 401 |
| GET `/titles/` | 200 |
| POST `/titles/` | 201 |
| GET `/titles/{title_id}` | 200 |
| PATCH `/titles/{title_id}` with valid changes | 200 |
| PATCH `/titles/{title_id}` with zero duration | 422 |
| DELETE `/titles/{title_id}` | 200 |
| GET `/titles/{title_id}` after deletion | 404 |

All 11 screenshots are included in `docs/week1-screenshots/`. Login screenshots were cropped to remove passwords and access tokens.

These screenshots predate the latest cleanup changes. New live evidence for duplicate handling and combined-record PATCH validation remains pending.

See [WEEK1_API_EVIDENCE.md](WEEK1_API_EVIDENCE.md) for the screenshot inventory.

## Historical results

| Stage | Recorded result |
| --- | --- |
| Original baseline at `007e41d` | 67 passed, 9 expected failures, 0 unexpected failures |
| Authentication integration update | 161 passed, 5 expected failures, 4 unexpected passes |
| Current cleanup branch | 176 passed, 0 expected failures, 0 unexpected passes |

Historical results describe earlier code and configuration. The latest verified result is 176 passed with one warning.

## Remaining warning

The latest run emitted one Starlette TestClient deprecation warning about HTTPX usage.

The default-secret and JWT key-length warnings were absent after setting a generated secret in the current PowerShell session. The session setting expires when that terminal closes.

## Completion status

The automated regression suite passes, and the PostgreSQL uniqueness migration is applied with no detected schema differences.

Remaining work:

- Configure a persistent unique local `SECRET_KEY` outside Git.
- Verify the new duplicate and PATCH behavior against the live PostgreSQL API.
- Review the Starlette TestClient deprecation warning.
- Check current OpenAPI declarations for HTTP 404, 409, and 422 responses.
- Update API and module documentation for the cleanup changes.
- Commit and push the cleanup branch.
- Create a separate pull request targeting `main` for review.

The latest cleanup has not yet been confirmed as committed, pushed, or merged.

See [WEEK1_BUG_REPORT.md](WEEK1_BUG_REPORT.md) for the issue status.