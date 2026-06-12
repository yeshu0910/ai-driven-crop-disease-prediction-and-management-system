# User Authentication — Feature Specification

## Feature Overview
User Authentication enables registered farmers, agronomists, and administrators to securely access the Crop Disease Prediction and Management System. It provides email/password sign-up, JWT-based session management, OAuth2 social login (Google, Apple), phone number verification for regions without reliable email, and role-based access control (RBAC) for different user tiers.

## Problem Statement
Currently, the system lacks a secure identity layer. Without authentication:
- Users cannot save personalized disease history or field data.
- Agronomists cannot access premium consultation features.
- Administrators cannot manage users or ML model configurations.
- Multi-user access on shared farm devices is insecure.
45% of pilot test users requested offline-capable authentication given intermittent connectivity in rural areas.

## User Stories
- As a **Farmer**, I want to sign up with my phone number so that I can access the app without email.
- As a **Farmer**, I want to log in with Google so that I don't manage another password.
- As an **Agronomist**, I want role-specific dashboards so that I see only relevant tools.
- As an **Admin**, I want to manage user roles so that access controls are enforced.
- As a **User**, I want to reset my password so that I can recover my account.
- As a **User**, I want 72-hour offline sessions so that I can use the app in areas with no connectivity.

## Functional Requirements
- FR-1: Email and password registration with email verification link (expires in 24h).
- FR-2: Phone number registration with SMS OTP (6-digit, 10-minute expiry, resend cooldown: 60s).
- FR-3: OAuth2 login via Google and Apple providers.
- FR-4: JWT access token (15 min) and refresh token (7 days, rotating).
- FR-5: Password reset flow via email with time-limited token (1 hour).
- FR-6: Role-based access: `farmer`, `agronomist`, `admin`.
- FR-7: Account deactivation (soft delete) preserving historical data.
- FR-8: Session management — list and revoke active sessions.
- FR-9: Rate limiting: 5 login attempts per 15 minutes per IP.

## Non-Functional Requirements
- NFR-1: P95 login latency < 300ms under 10,000 concurrent users.
- NFR-2: All passwords hashed with Argon2id (memory: 64MB, iterations: 3).
- NFR-3: TLS 1.3 required for all auth endpoints.
- NFR-4: PII encryption at rest using AES-256-GCM.
- NFR-5: 99.9% auth service availability (≈ 8.7h downtime/year).
- NFR-6: Offline session cache valid for 72 hours using encrypted local storage.
- NFR-7: GDPR and India DPDP Act compliance for farmer data.

## Acceptance Criteria
1. New user can register with email and receives verification link within 2 minutes.
2. Unverified user cannot access protected endpoints.
3. Verified user receives access + refresh token pair on login.
4. Refresh token rotation invalidates old tokens on each use.
5. Revoked session is blocked on next request (P95 < 100ms check).
6. Admin can assign `agronomist` role and the user immediately sees agronomist dashboard.
7. OAuth2 flow redirects back to mobile app with valid JWT on success.
8. 6th failed login attempt returns 429 with Retry-After header.
9. Password reset token cannot be reused after successful password change.
10. Deactivated user receives 401 with generic `"Invalid credentials"` (no enumeration).

## Dependencies
- PostgreSQL database provisioned with `users` and `sessions` tables.
- Redis cluster for rate limiting and token blacklist.
- SendGrid or equivalent for transactional email.
- Twilio or equivalent for SMS OTP delivery.
- Apple Developer account for Sign in with Apple.

## Out of Scope
- Magic link authentication (deferred to v1.1).
- WebAuthn / passkeys (deferred to v1.2).
- Multi-factor authentication (deferred to v1.1).
- SSO with enterprise identity providers (deferred to v2.0).
