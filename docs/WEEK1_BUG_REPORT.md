# Week 1 Bug Report and Pending Issues

| ID | Open issue | Expected outcome or decision |
| --- | --- | --- |
| AUTH-01 | Inactive users can log in. | Reject login for inactive accounts. |
| AUTH-02 | Email rules accept malformed domains. | Reject `a@b..`, `a@b.-`, and `a@-b.com`. |
| AUTH-03 | The test run warned about a 20-byte JWT signing key. | Review local/test secret setup and verify the warnings are resolved. |
| CAT-01 | Blank language is accepted. | Reject empty input. |
| CAT-02 | Movie season counts and web-series runtime values are accepted. | Decide and enforce the field rules by content type. |
| CAT-03 | PATCH permits a title longer than the database column. | Return a validation error for input over 255 characters. |
| CAT-04 | Duplicate titles can be stored. | Agree on title identity before enforcing uniqueness. |
| QA-01 | Starlette emitted an HTTPX TestClient deprecation warning. | Review the test dependency setup. |
| QA-02 | Live Swagger screenshots | Resolved. All 11 screenshots are included. |
| QA-03 | Swagger marks the actual login 401 and missing-title 404 as undocumented. | Declare error responses in OpenAPI. |

Earlier collection errors, the SQLAlchemy relationship error, and the missing health route were resolved in PR #12. PostgreSQL successfully applied the initial migration after the local database was configured. Dedicated genre/platform APIs, protected routes, search/filtering, Redis, and background sync remain roadmap items. Confirm Week 1 scope with the team before treating later milestones as acceptance criteria.
