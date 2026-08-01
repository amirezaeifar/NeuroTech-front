# NeuroTech Backend — Phase 1

Phase 1 adds a Flask authentication backend and the complete database foundation alongside the existing Vue application. It does not move or integrate the frontend.

## Architecture

The dependency direction is:

```text
HTTP controllers
  -> AuthService / OtpService
  -> repository and external-service ports
  -> SQLAlchemy / Redis / PyJWT adapters
  -> MariaDB / Redis
```

`app/main.py` is the composition root. Controllers validate and translate HTTP only. Services contain workflows and control transactions through `UnitOfWork`. Repositories never commit. Redis, JWT, password hashing, clocks, OTP delivery, and secret encryption are behind interfaces. See [ADR-001](docs/ADR-001-clean-architecture.md).

## Layout

```text
app/core                    configuration, normalization, errors, response envelope
app/domain/entities         87 SQLAlchemy tables and stable lowercase enums
app/domain/repositories     authentication ports and Phase 2 repository foundations
app/domain/ports            token, password, OTP, clock, and encryption contracts
app/domain/services         authentication and OTP use cases
app/infrastructure/db       engine, scoped sessions, SQLAlchemy Unit of Work
app/infrastructure/redis    Redis client and atomic OTP adapter
app/infrastructure/security Werkzeug, PyJWT, and Fernet adapters
app/interfaces/http         schemas, decorators, controllers, and error handlers
migrations                  Alembic environment and complete initial revision
tests                       unit, functional, architecture, and gated integration tests
```

## Technology

Python 3.11, Flask, SQLAlchemy 2.x, `mysql+mysqlconnector`, MariaDB, Redis, PyJWT, Marshmallow, Werkzeug, Alembic, Flask-CORS, `email-validator`, `cryptography`, pytest, Docker, and Docker Compose.

## Local setup

Copy `.env.example` to `.env` and replace development secrets as appropriate.

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
flask --app app.main create-roles
flask --app app.main create-admin
flask --app app.main run --debug
```

The database account must be able to access a MariaDB/MySQL database configured with `utf8mb4` and `utf8mb4_unicode_ci`. SQLAlchemy builds a `mysql+mysqlconnector` URL from `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASS`, and `DB_NAME`. Pool size, overflow, recycle time, SQL echo, and pre-ping behavior are configurable.

Redis is configured with `REDIS_URL`. It stores OTP records only; MariaDB stores refresh-session metadata.

## Configuration

`.env.example` documents application, MariaDB, Redis, JWT, cookie, OTP, password, encryption, and development-administrator values. Boolean and integer parsing is strict. Production rejects placeholder secrets, development database credentials, insecure refresh cookies, and development OTP mode.

`load_dotenv()` is called only by `app/core/config.py`. Neither routes nor adapters load environment files.

## Database and migrations

The initial revision is `migrations/versions/054a2fcab5bd_initial_phase_1_schema.py`.

```powershell
alembic current
alembic upgrade head
alembic downgrade -1
alembic check
```

Normal application startup never calls `Base.metadata.create_all()`. Isolated functional tests use it only for their in-memory test schema. Major records use internal BIGINT keys plus public UUIDs; public APIs expose only UUIDs. Translation rows enforce one locale per parent. Monetary data uses `NUMERIC(18, 2)`.

## Authentication

Endpoints:

```text
POST /auth/register
POST /auth/login
POST /auth/request-otp
POST /auth/verify-otp
POST /auth/refresh
POST /auth/logout
POST /auth/logout-all
GET  /auth/me
POST /auth/change-password
GET  /health
```

Responses use:

```json
{"success": true, "data": {}, "message": null, "meta": {}}
```

Errors use the matching `success: false` envelope and never include secrets or stack traces.

Access tokens are short-lived PyJWT tokens returned in JSON. They contain the user public UUID, roles, token type, JTI, version, issuer, audience, and time claims. The server pins the configured HMAC algorithm and validates type, issuer, audience, time claims, user status, current roles, and token version.

Refresh tokens are sent only in the configured HttpOnly cookie. MariaDB stores an HMAC hash, JTI, family, issue/expiry time, client metadata, revocation time, and replacement JTI—never the raw token. Refresh rotates both tokens and revokes the old record. Reuse of a revoked refresh token revokes its whole family and increments the user's token version. Logout revokes one session; logout-all and password change revoke every session and increment the version.

`@auth_required` and `@roles_required(...)` reload the user and roles from MariaDB for authorization.

## OTP

OTP codes are numeric and generated with `secrets`. Redis stores only an HMAC hash in namespaced keys with TTL. Lua scripts atomically enforce resend cooldown, hourly request limits, failed-attempt limits, and single use.

The Phase 1 sender intentionally performs no SMS or email delivery. With `OTP_DEVELOPMENT_MODE=true`, the request response contains `development_otp` for local testing. Production configuration forbids that mode and never returns or logs a code.

## CLI

`create-roles` idempotently creates `admin`, `specialist`, `content_manager`, and `user`.

`create-admin` reads defaults from the environment or explicit options, updates only intended profile fields, assigns the admin role idempotently, and requires an explicit password in Production.

## Tests

```powershell
pytest
pytest --cov=app --cov-report=term-missing
```

Unit tests use fake repositories and fake ports and require neither Flask, MariaDB, nor Redis services. Functional tests use the real Flask routes and SQLAlchemy adapters with an explicitly isolated in-memory test database. Architecture tests inspect imports and transaction calls.

Integration tests never replace MariaDB with SQLite. They run only when both are set:

```powershell
$env:INTEGRATION_DATABASE_URL = "mysql+mysqlconnector://user:pass@localhost/neurotech_test"
$env:INTEGRATION_REDIS_URL = "redis://localhost:6379/15"
pytest -m integration
```

Use a disposable database: the integration fixture creates and drops the Phase 1 schema.

## Docker

From the repository root:

```powershell
docker compose config
docker compose up --build
```

Compose provides `web`, `db`, and `redis`. MariaDB and Redis use persistent volumes and health checks. The web service waits for healthy dependencies and runs `alembic upgrade head` before Flask; it does not use a fixed sleep.

## Phase boundary

Phase 1 includes model foundations for products, academy, courses, events, partners, international trade, orders, payments, contact/content, media, moderation, settings, and audit logs.

Complete product, course, event, partner, trade, order, payment, content-management, contact-management, file-upload, and administration workflows are intentionally deferred to later phases. No fake payment, enrollment, course access, or event registration success API is implemented.
