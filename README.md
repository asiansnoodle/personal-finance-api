# Personal Finance API

> A production-ready personal finance REST API built with **FastAPI**, **PostgreSQL**, and **Docker** — featuring JWT authentication, spend analytics, and budget variance tracking.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.137-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-migrations-6BA81E)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![JWT](https://img.shields.io/badge/Auth-JWT-000000?logo=jsonwebtokens&logoColor=white)

---

## Features

- **JWT authentication** with bcrypt password hashing — stateless tokens, hashed credentials, no plaintext passwords stored.
- **Account & transaction management** with ownership-enforced access control — every resource is scoped to the authenticated user, so no one can read or mutate another user's data.
- **Spend analytics** — monthly breakdown by category, including each category's percentage of total spend, plus income and net totals.
- **Budget variance tracking** — compare actual spend against per-category monthly targets and surface how much of each budget has been used.
- **Transaction filtering** — narrow results by category, date range, and account.
- **Consistent error responses** — every error returns the same JSON envelope (`{ "error", "detail", "status_code" }`) regardless of where it originates.
- **Fully containerized** — one `docker compose up` brings up the database, applies migrations, and serves the API.

---

## Architecture

The codebase follows a **layered architecture** that keeps responsibilities cleanly separated:

- **Routers** (`app/routers/`) handle HTTP concerns only — parsing requests, validating input via Pydantic, enforcing auth, and shaping responses.
- **Services** (`app/services/`) hold the business logic — password hashing, token creation, and the analytics/variance aggregation queries — so logic isn't tangled into route handlers.
- **Models** (`app/models/`) are SQLAlchemy ORM classes that own persistence and relationships.
- **Schemas** (`app/schemas/`) are Pydantic models defining the request/response contract, decoupled from the database layer.

This separation keeps the HTTP layer thin, makes the business logic unit-testable in isolation, and means the persistence layer can evolve without rewriting route handlers.

---

## Getting Started

### Running with Docker (recommended)

```bash
git clone https://github.com/asiansnoodle/personal-finance-api
cd personal-finance-api

# Create your .env (the app fails fast if SECRET_KEY is missing)
cp .env.example .env
# then edit .env and set SECRET_KEY, e.g.:
#   python -c "import secrets; print(secrets.token_urlsafe(48))"

docker compose up --build        # starts Postgres + API, runs migrations on boot
docker compose exec app python seed.py   # optional: load demo data
```

Then visit **http://localhost:8000/docs**.

> Migrations (`alembic upgrade head`) run automatically as part of the app container's startup command, so a fresh database volume is schema-ready before the API serves traffic.

A demo account is created by the seed script:

| Email | Password |
|-------|----------|
| `demo@financeapi.dev` | `demopass123` |

### Running locally (without Docker)

```bash
git clone https://github.com/asiansnoodle/personal-finance-api
cd personal-finance-api

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # set DATABASE_URL + SECRET_KEY

# Start a Postgres instance (or just the db service from compose):
docker compose up -d db

alembic upgrade head
python seed.py                  # optional demo data
uvicorn app.main:app --reload
```

---

## API Documentation

FastAPI generates interactive docs automatically:

- **Swagger UI** → http://localhost:8000/docs
- **ReDoc** → http://localhost:8000/redoc

Both are live against the running app — you can authenticate and exercise every endpoint directly from the browser.

---

## Endpoint Reference

| Method | Endpoint                        | Description                              | Auth |
|--------|---------------------------------|------------------------------------------|------|
| POST   | `/auth/register`                | Register a new user                      | No   |
| POST   | `/auth/login`                   | Log in and receive a JWT                 | No   |
| GET    | `/accounts`                     | List the user's accounts                 | Yes  |
| POST   | `/accounts`                     | Create an account                        | Yes  |
| GET    | `/accounts/{account_id}`        | Get a single account                     | Yes  |
| GET    | `/transactions`                 | List transactions (with filters)         | Yes  |
| POST   | `/transactions`                 | Create a transaction                     | Yes  |
| GET    | `/transactions/{transaction_id}`| Get a single transaction                 | Yes  |
| PATCH  | `/transactions/{transaction_id}`| Update a transaction                     | Yes  |
| GET    | `/budgets`                      | List budgets (with filters)              | Yes  |
| POST   | `/budgets`                      | Create a budget                          | Yes  |
| GET    | `/budgets/{budget_id}`          | Get a single budget                      | Yes  |
| PATCH  | `/budgets/{budget_id}`          | Update a budget                          | Yes  |
| GET    | `/analytics/summary`            | Monthly spend by category                | Yes  |
| GET    | `/analytics/variance`           | Budget vs. actual spend per category     | Yes  |

> Protected endpoints expect an `Authorization: Bearer <token>` header. Obtain the token from `/auth/login`.

---

## Design Decisions

- **FastAPI over Flask** — native async support, automatic OpenAPI/Swagger docs, and Pydantic-based request validation out of the box. Less boilerplate, stronger type safety, and self-documenting endpoints.
- **Router / service split** — keeping HTTP handling and business logic in separate layers enforces separation of concerns and makes the core logic (auth, analytics aggregation) testable without spinning up the web layer.
- **Alembic for migrations** — schema changes are version-controlled and reproducible across environments, the same pattern used in production systems, rather than ad-hoc `CREATE TABLE` scripts.
- **JWT for authentication** — stateless tokens mean no server-side session store, so the API scales horizontally without sticky sessions or shared session storage.
- **`Decimal` for money** — monetary fields use `Decimal` mapped to SQL `Numeric(12,2)` to avoid floating-point rounding errors in balances and totals.

---

## Future Improvements

- **Plaid API integration** for syncing real bank account and transaction data.
- **Transaction service layer** — extract the remaining transaction logic out of the router into a dedicated service for consistency with the rest of the codebase.
- **Redis caching** for analytics endpoints, which run aggregate queries that are read-heavy and change infrequently within a month.
- **Test suite** — unit tests for services and integration tests covering the auth and ownership flows.
- **CI/CD pipeline** with GitHub Actions — automated linting, tests, and image builds on every push.

---

## Tech Stack

**Language:** Python 3.12 · **Framework:** FastAPI · **Database:** PostgreSQL 16 · **ORM:** SQLAlchemy 2.0 · **Migrations:** Alembic · **Auth:** JWT (python-jose) + passlib/bcrypt · **Validation:** Pydantic v2 · **Containerization:** Docker Compose
