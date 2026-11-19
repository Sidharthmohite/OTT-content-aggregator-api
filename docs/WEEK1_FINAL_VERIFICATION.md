# Week 1 Final Verification

Post-edit verification passed: 185 tests passed with one tracked Starlette warning, all expected OpenAPI error declarations were present, and git diff --check was clean.

Verified locally on 19 November 2026 after merging PRs #15 and #16.

| Check | Observed result |
| --- | --- |
| Latest full automated run before final OpenAPI edits | 185 passed, zero failures, one Starlette TestClient deprecation warning |
| Saved JWT secret | Configuration test passed after removing the temporary environment override |
| Secret file | `.env` is ignored and untracked |
| PostgreSQL | `9e811ea57f63 (head)`; Alembic found no schema differences |
| Duplicate POST | HTTP 409 |
| Invalid movie PATCH | HTTP 422 |
| Record after invalid PATCH | HTTP 200; duration 90 and seasons null |
| Same title with different release year | HTTP 201; ID 8 |
| Duplicate PATCH on ID 8 | HTTP 409 |
| Record after duplicate PATCH | HTTP 200; release year remained 2025 |
| Valid update after rejected duplicate | HTTP 200; duration changed to 95 |

Seven additional screenshots are included in `week1-screenshots/` alongside the original eleven. The original evidence remains historical.

The case-sensitive title identity comprises title, content type, release year, and language. Automated endpoint tests use SQLite. The additional live requests used the local PostgreSQL-backed API on port 8003.

## OpenAPI declarations

Title routes declare applicable 404 and 409 responses. Authentication routes declare applicable credential, inactive-account, missing-user, and duplicate-account responses. Final schema inspection and a regression run must be recorded after these declarations are saved.

## Remaining issue and review

One Starlette TestClient deprecation warning remains tracked. This verification does not claim later roadmap features are complete.

The final verification branch awaits its post-edit checks, commit, push, and review. No secret value is included in these reports.
