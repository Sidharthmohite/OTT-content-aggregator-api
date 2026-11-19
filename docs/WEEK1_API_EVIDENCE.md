# Week 1 Live API Evidence

The latest verification is recorded in [WEEK1_FINAL_VERIFICATION.md](WEEK1_FINAL_VERIFICATION.md). Its current results supersede older counts and pending-status statements below.

The requests below were executed in local Swagger UI on port 8001 on 18 November 2026 (IST). Codes were verified under **Server response** in the screenshots shared during testing.

| Request | Observed HTTP status | Result | Suggested screenshot filename |
| --- | --- | --- | --- |
| GET /health | 200 | Returned healthy | health-200.png |
| POST /auth/register | 201 | Created the test account | register-201.png |
| POST /auth/login with valid credentials | 200 | Returned a bearer token | login-200.png |
| POST /auth/login with an incorrect password | 401 | Rejected invalid credentials | login-401.png |
| GET /titles/ | 200 | Returned an empty list before creating a title | titles-list-200.png |
| POST /titles/ | 201 | Created the test title | title-create-201.png |
| GET /titles/1 | 200 | Retrieved the created title | title-get-200.png |
| PATCH /titles/2 | 200 | Changed duration from 90 to 95 minutes and preserved omitted fields on a fresh record | title-update-200.png |
| PATCH /titles/2 with zero duration | 422 | Rejected the invalid duration | title-invalid-422.png |
| DELETE /titles/2 | 200 | Returned the deletion confirmation | title-delete-200.png |
| GET /titles/2 after deletion | 404 | Returned Title not found | title-missing-404.png |

Swagger marked the actual 401 login and 404 title responses as undocumented. Record these as OpenAPI documentation gaps. An earlier PATCH on title 1 returned placeholder values in other fields. The cause remains unconfirmed, and the behavior did not recur on the fresh record.

All 11 screenshots are included in `docs/week1-screenshots/`. The login screenshots were cropped to remove credentials and tokens.
