# User Authentication — Implementation Plan

## Architecture Overview

```
┌─────────────┐     ┌──────────────┐     ┌───────────────────┐
│   Mobile    │────▶│  FastAPI     │────▶│   PostgreSQL      │
│   App       │     │  Auth Service │     │   (users, sessions)│
│  (Flutter)  │     │              │     │                   │
└─────────────┘     └──────┬───────┘     └───────────────────┘
       │                    │
       │                    ▼
       │           ┌──────────────────┐
       │           │     Redis         │
       │           │ (rate limit,      │
       │           │  token blacklist) │
       │           └──────────────────┘
       │                    │
       │                    ▼
       │           ┌──────────────────┐     ┌──────────────┐
       │           │ External Providers│────▶│ SendGrid /   │
       │           │ (Google, Apple,   │     │ Twilio       │
       │           │  Email, SMS)      │     └──────────────┘
       │           └──────────────────┘
       ▼
┌──────────────┐
│  Flutter     │
│  Offline     │
│  Hive Cache  │
└──────────────┘
```

The Auth Service runs as a stateless FastAPI microservice scaled behind the API Gateway. All state is externalized to PostgreSQL (durability) and Redis (low-latency lookups).

## Technology Stack

| Layer               | Technology                              | Rationale                                      |
|---------------------|-----------------------------------------|-------------------------------------------------|
| API Framework       | FastAPI 0.100+, Python 3.10             | Async performance, automatic OpenAPI docs       |
| ORM                 | SQLAlchemy 2.0 + Alembic                | Type-safe queries, mature migration tooling     |
| Auth Library        | `python-jose` + `passlib[argon2]`       | JWT handling, Argon2id password hashing         |
| OAuth2              | `authlib`                               | Google, Apple provider abstractions             |
| Validation          | `pydantic` v2                           | Request/response schemas, strict typing         |
| Rate Limiting       | `slowapi` + Redis                       | IP and user-based rate limits                   |
| Caching / Sessions  | Redis 7.0+ (via `redis-py`)             | Token blacklist, session store, rate limit state|
| Email               | SendGrid REST API                       | Delivery tracking, templates                    |
| SMS                 | Twilio Verify API                       | OTP delivery, fraud detection                   |
| Testing              | `pytest`, `pytest-asyncio`, `httpx`     | Async API testing, fixture management           |
| CI/CD               | GitLab CI + Docker                      | Containerized deploy, automated testing         |

## Database Design

### `users` Table

```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE,
    phone           VARCHAR(20) UNIQUE,
    email_verified  BOOLEAN DEFAULT FALSE,
    phone_verified  BOOLEAN DEFAULT FALSE,
    full_name       VARCHAR(255) NOT NULL,
    password_hash   VARCHAR(255),
    role            VARCHAR(50) DEFAULT 'farmer' CHECK (role IN ('farmer','agronomist','admin')),
    is_active       BOOLEAN DEFAULT TRUE,
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_phone ON users(phone) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_role ON users(role) WHERE is_active = TRUE;
```

### `sessions` Table

```sql
CREATE TABLE sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    refresh_token   VARCHAR(500) NOT NULL,
    device_name     VARCHAR(255),
    device_type     VARCHAR(50),  -- 'ios', 'android', 'web'
    ip_address      INET,
    user_agent      TEXT,
    expires_at      TIMESTAMPTZ NOT NULL,
    revoked_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id) WHERE revoked_at IS NULL;
CREATE INDEX idx_sessions_refresh_token ON sessions(refresh_token) WHERE revoked_at IS NULL;
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);
```

### `password_reset_tokens` Table

```sql
CREATE TABLE password_reset_tokens (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash      VARCHAR(255) NOT NULL,
    expires_at      TIMESTAMPTZ NOT NULL,
    used_at         TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_prt_user_id ON password_reset_tokens(user_id);
CREATE INDEX idx_prt_token_hash ON password_reset_tokens(token_hash) WHERE used_at IS NULL AND expires_at > NOW();
```

### Migration Strategy
- Use Alembic for versioned schema changes.
- Deploy migrations via CI/CD with `alembic upgrade head` in pre-deploy hook.
- Zero-downtime: add columns as nullable, backfill, then set `NOT NULL`.

## API Design

### Base URL
```
/api/v1/auth
```

### Endpoints

| Method | Endpoint                          | Auth     | Description                         |
|--------|-----------------------------------|----------|-------------------------------------|
| POST   | `/register/email`                 | None     | Register with email and password    |
| POST   | `/register/phone`                 | None     | Request SMS OTP for phone signup    |
| POST   | `/register/phone/verify`          | None     | Verify OTP and create account       |
| POST   | `/login/email`                    | None     | Email/password login                |
| POST   | `/login/phone`                    | None     | Phone + OTP login                   |
| POST   | `/login/oauth/{provider}`         | None     | OAuth2 callback (Google/Apple)      |
| POST   | `/refresh`                        | None     | Rotate access token via refresh     |
| POST   | `/logout`                         | Bearer   | Revoke current session              |
| POST   | `/logout/all`                     | Bearer   | Revoke all user sessions            |
| GET    | `/sessions`                       | Bearer   | List active sessions                |
| POST   | `/password/forgot`                | None     | Request password reset email        |
| POST   | `/password/reset`                 | None     | Reset password with token           |
| GET    | `/me`                             | Bearer   | Get current user profile            |
| PATCH  | `/me`                             | Bearer   | Update full name                    |
| DELETE | `/me`                             | Bearer   | Deactivate own account              |

### Request / Response Schemas

```jsonc
// POST /register/email
// Request
{
  "email": "farmer@example.com",
  "password": "SecureP@ss123",
  "full_name": "Ravi Kumar"
}

// Response 201
{
  "id": "uuid",
  "email": "farmer@example.com",
  "email_verified": false,
  "message": "Verification email sent. Expires in 24 hours."
}

// POST /login/email
// Request
{
  "email": "farmer@example.com",
  "password": "SecureP@ss123"
}

// Response 200
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### Validation Rules
- Password: min 12 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special char.
- Email: RFC 5322 compliant, max 255 chars.
- Phone: E.164 format, country code required.
- Full name: 2–100 chars, letters and spaces only.
- Rate limit: 5 requests per 15 minutes per IP on login endpoints.
- OTP: 6 digits numeric, 10-minute expiry, max 3 resends per hour.

## Implementation Strategy

### Phase 1 (Week 1–2): Core Auth Infrastructure
- Set up FastAPI project structure with layered architecture.
- Implement `users`, `sessions`, `password_reset_tokens` tables via Alembic.
- Build `AuthService` class with dependency injection for rate limiting.
- Implement Argon2id password hashing utility.

### Phase 2 (Week 3–4): Registration & Login
- Implement email registration with verification token.
- Implement phone OTP registration via Twilio Verify.
- Implement email/password login with JWT issuance.
- Implement refresh token rotation with Redis blacklist for revoked tokens.

### Phase 3 (Week 5): OAuth2 & Account Management
- Integrate Google OAuth2 and Apple Sign In via Authlib.
- Build password reset flow with expiring tokens.
- Implement session listing and revocation.
- Implement soft-delete account deactivation.

### Phase 4 (Week 6): RBAC & Integration
- Add role enforcement middleware on API Gateway.
- Update mobile app auth screens with new flows.
- End-to-end integration testing with staging environment.

### Rollout
- Feature flag `AUTH_V2_ENABLED` for gradual rollout.
- Canary: 5% of users for 48 hours, then 25%, then 100%.
- Monitor: login success rate, P95 latency, error rate per endpoint.

## Risks and Mitigation

| Risk                          | Likelihood | Impact | Mitigation                                                |
|-------------------------------|------------|--------|-----------------------------------------------------------|
| Phone OTP delivery delays     | Medium     | High   | Fall back to email; Twilio fallback carrier routing        |
| JWT secret rotation issues     | Low        | High   | Dual-key rollout; keep old key valid during grace period   |
| Rate limit false positives     | Medium     | Medium | Whitelist known farm device IP ranges; dynamic adjustment  |
| Argon2id CPU cost at scale    | Medium     | Medium | Offload to dedicated auth workers; tune memory params      |
| OAuth2 provider downtime      | Low        | Medium | Health checks; fallback to email/password registration     |
| GDPR/DPDP compliance gaps     | Medium     | High   | Legal review before launch; data export/deletion endpoints |

## Testing Strategy
- **Unit**: All service methods, password hashing, JWT encode/decode.
- **Integration**: Full auth flows via `httpx` test client against test DB.
- **Security**: `bandit` SAST, OWASP ZAP scan on staging.
- **ML-relevant**: None (auth layer is independent).

## Rollout Plan
- Deploy to staging with production-like data volume (100k users).
- Run penetration test before production cutover.
- Coordinate with mobile team for app update release.
- Post-launch: error budget = 0.1% failed logins; alert if exceeded.
