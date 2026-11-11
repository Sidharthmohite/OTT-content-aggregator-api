# Testing Checklist – OTT Content Aggregator API

Mark each case `[x]` once a test is written and passing.

## Database & Core Configuration (M3)
- [x] Configuration reads `DATABASE_URL` and app settings correctly from `.env`
- [x] Database connection succeeds with valid credentials (`src.core.database.test_connection`)
- [x] FastAPI database dependency `get_db` yields active session and closes it cleanly after request
- [x] Alembic initializes and detects model metadata correctly for migrations

## User Model, Schemas & Authentication (M2)
- [x] User SQLAlchemy model defines all required fields (`id`, `email`, `username`, `hashed_password`, `full_name`, `is_active`, `is_superuser`, timestamps)
- [x] User model sets unique constraints on `email` and `username`
- [x] Passwords are never stored in plain text; always hashed
- [x] UserCreate schema validates required fields and password strength
- [x] Email normalization strips whitespace and converts to lowercase
- [x] Invalid email format rejected with descriptive error message
- [x] Username validation enforces 3-50 length and valid characters
- [x] Password validation enforces minimum 8 chars, uppercase, lowercase, number, and special character
- [x] UserResponse schema excludes sensitive password fields
- [x] UserUpdate schema allows partial updates
- [x] Duplicate email registration rejected with `DuplicateEmailError`
- [x] Duplicate email with differing case rejected
- [x] Duplicate username registration rejected with `DuplicateUsernameError`
- [x] User update rejects duplicate email if already registered to another user
- [x] Password verification and authentication succeeds for valid credentials
- [x] Authentication rejects invalid passwords and non-existent users
- [x] JWT token generation and decoding succeeds

## Movie Data (M4)
- [ ] Valid movie data creation and retrieval
- [ ] Title search and filtering
- [ ] Year and genre validation

## Genre & Platform (M5)
- [ ] Platform creation and retrieval
- [ ] Genre creation and retrieval

## Integration & Caching (Week 3 & 4)
- [ ] Redis cache hit/miss behaviour
- [ ] Background sync task runs and adds simulated titles
- [ ] Pytest test coverage reaches at least 80% of endpoints
