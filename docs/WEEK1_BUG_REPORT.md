# Week 1 Bug Report and Pending Issues

Updated on 19 November 2026 for branch `fix/week1-test-cleanup`.

## Latest verification

- Full automated suite: 176 passed, 0 failed.
- Expected failures and unexpected passes: 0.
- Remaining warnings: 1 Starlette TestClient deprecation.
- PostgreSQL revision: `9e811ea57f63 (head)`.
- Alembic check: No new upgrade operations detected.

## Issue status

| ID | Issue | Status |
| --- | --- | --- |
| AUTH-01 | Inactive users could log in | Resolved. Regression test passes |
| AUTH-02 | Malformed email domains were accepted | Resolved. Regression tests pass |
| AUTH-03 | Default or short JWT signing key | Resolved for the verified terminal session. Persistent local configuration is pending |
| CAT-01 | Blank language was accepted | Resolved through language validation |
| CAT-02 | Movie and web-series fields could conflict | Resolved for creation and combined-record PATCH validation |
| CAT-03 | PATCH accepted titles longer than 255 characters | Resolved through schema validation |
| CAT-04 | Duplicate title identities were accepted | Resolved in SQLite tests. PostgreSQL constraint applied. Live API verification is pending |
| QA-01 | Starlette TestClient deprecation warning | Open. One warning remains |
| QA-02 | Live API screenshots | Eleven earlier checks and screenshots are included. Cleanup behavior needs new live evidence |
| QA-03 | Missing OpenAPI error-response declarations | Open. Recheck current declarations for HTTP 404, 409, and 422 |

## Duplicate-title behavior

Duplicate identity uses the case-sensitive combination of title, content type, release year, and language.

The `uq_titles_identity` constraint is included in migration `9e811ea57f63`, which was applied to local PostgreSQL. No duplicate groups were found before the migration.

POST and PATCH duplicate requests return HTTP 409 in the automated SQLite tests. A rejected duplicate PATCH preserves the record, and a subsequent valid update succeeds.

## Remaining work

- Persist a unique local JWT secret outside Git.
- Verify duplicate handling and PATCH validation against the live PostgreSQL API.
- Review the test-client deprecation warning.
- Update API and module documentation.
- Commit, push, and submit the cleanup branch through a separate PR targeting `main`.

The current fixes are verified locally. Publication and review of the cleanup branch remain pending.