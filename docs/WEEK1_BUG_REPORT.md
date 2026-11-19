# Week 1 Bug Report and Pending Issues

The latest verification is recorded in [WEEK1_FINAL_VERIFICATION.md](WEEK1_FINAL_VERIFICATION.md). Its current results supersede older counts and pending-status statements below.

Updated on 19 November 2026 for branch `docs/week1-final-verification`.

## Latest verification

| Check | Result |
| --- | --- |
| Latest full automated run | 185 passed, 0 failed |
| Expected failures and unexpected passes | 0 |
| Remaining warnings | 1 Starlette TestClient deprecation |
| Saved-secret configuration | Passed after removing the temporary environment override |
| `.env` Git status | Ignored and untracked |
| PostgreSQL revision | `9e811ea57f63 (head)` |
| Alembic schema comparison | No new upgrade operations detected |
| Live PostgreSQL duplicate and PATCH checks | Passed |
| OpenAPI POST `/titles/` responses | 201, 409, 422 |
| OpenAPI PATCH `/titles/{title_id}` responses | 200, 404, 409, 422 |

The 185-test run preceded the latest OpenAPI declaration changes. Those declarations were verified by inspecting the generated schema.

## Issue status

| ID | Issue | Current status |
| --- | --- | --- |
| AUTH-01 | Inactive users could log in | Resolved. Regression test passes |
| AUTH-02 | Malformed email domains were accepted | Resolved. Regression tests pass |
| AUTH-03 | Default or short JWT signing key | Resolved locally. Saved configuration passed without the temporary environment override |
| CAT-01 | Blank language was accepted | Resolved through language validation |
| CAT-02 | Movie and web-series fields could conflict | Resolved. Creation and combined-record PATCH tests pass |
| CAT-03 | PATCH accepted titles longer than 255 characters | Resolved through schema validation |
| CAT-04 | Duplicate title identities were accepted | Resolved. Automated tests and live PostgreSQL POST/PATCH checks confirm HTTP 409 |
| QA-01 | Starlette TestClient deprecation warning | Open. One warning remains |
| QA-02 | Live API screenshots | Original 11 screenshots are included. Additional verification screenshots await inclusion |
| QA-03 | Missing OpenAPI error declarations | Title POST and PATCH declarations verified. GET/DELETE 404 and authentication declarations require final verification |

## Live PostgreSQL verification

| Check | Result |
| --- | --- |
| Duplicate title creation | HTTP 409 |
| PATCH movie ID 6 with a season count | HTTP 422 |
| GET ID 6 after the rejected PATCH | HTTP 200. Duration remained 90 and season count remained null |
| Create the same title with release year 2025 | HTTP 201. Created ID 8 |
| PATCH ID 8 to the existing 2026 identity | HTTP 409 |
| GET ID 8 after the rejected duplicate PATCH | HTTP 200. Release year remained 2025 |
| PATCH ID 8 with duration 95 | HTTP 200. Valid update succeeded |

Duplicate identity uses the case-sensitive combination of title, content type, release year, and language.

The live checks confirm that rejected validation and duplicate requests preserve the existing record. A subsequent valid update succeeds.

## Secret configuration

A generated secret was saved in the local `.env` file.

Verification confirmed that:

- The saved configuration loads without the temporary environment override.
- The configuration test passes.
- `.env` is ignored by Git.
- `.env` is untracked.

The secret value is excluded from this report.

## Publication status

Catalog cleanup PR #15 and secret-warning PR #16 were merged into `main`.

The latest title OpenAPI declarations and final verification report updates are on `docs/week1-final-verification`. Publication and review of this branch remain pending.

## Remaining work

- Include the additional live verification screenshots.
- Verify GET/DELETE 404 and authentication OpenAPI declarations.
- Run the relevant checks after the latest declaration changes.
- Update the testing report and module documentation with the final results.
- Commit and push the final verification branch.
- Create a separate PR targeting `main` for review.
- Track the remaining Starlette TestClient deprecation warning.