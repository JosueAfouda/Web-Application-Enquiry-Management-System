# EMS MVP — End-to-End Architecture (Local Dev → Production on Render)
**Audience:** AI coding agents (e.g., Codex)  
**Goal:** Define a complete, dockerized, zero-cost (open-source only) architecture for the EMS MVP: from local environment setup to production deployment on Render (free plan).  
**Context:** Python 3.12.3, Ubuntu 24.04.4 LTS, local dev. A Python venv already exists and is activated:
- `python3 -m venv .venv`
- `source .venv/bin/activate`

---

## 0) Architecture Choice (MVP)
### Backend
- **FastAPI** (preferred over Django for a clean API-first MVP with built-in OpenAPI docs)

### Database
- **PostgreSQL** (preferred unless functional constraints require otherwise)

### Local orchestration
- **Docker + Docker Compose**

### Production hosting
- **Render** (free plan)
  - Render free Postgres exists but has constraints (notably expiration and size limits). :contentReference[oaicite:0]{index=0}
  - Docker-based services are supported (Dockerfile build). :contentReference[oaicite:1]{index=1}

---

## 1) High-Level System View

### Services (local via Docker Compose)
1. `api` — FastAPI application (REST API + optional minimal server-rendered admin UI if needed later)
2. `db` — PostgreSQL
3. *(optional)* `pgadmin` — local DB admin UI (developer convenience only)

### External (production on Render)
1. Render Web Service: `api` (Docker build)
2. Render Postgres: `db` (free tier constraints apply) :contentReference[oaicite:2]{index=2}

---

## 2) Domain Modules (Functional Coverage)

### 2.1 Core Modules
- **Auth & RBAC**
  - Roles: `BD`, `Admin`, `SuperAdmin`, `SupplyChain`
- **Masters**
  - Customer Master
  - Product Master
  - Manufacturer Master
  - Excel import support
- **Enquiry lifecycle**
  - Enquiry creation and tracking
  - Status workflow + transitions
- **Quotations**
  - Multi-revision quotations linked to an enquiry
- **Approval workflow**
  - Approval steps
  - Price calculation elements: freight, markup
- **PO generation**
  - Customer PO
  - RTM PO
- **Invoicing & Payment tracking**
- **Reporting**
  - Dashboard endpoints
  - Excel export

### 2.2 Cross-Cutting Requirements
- Secure authentication
- Audit trail (who did what, when, and what changed)
- Cloud deployment readiness
- Scalable architecture (clear separation of concerns, stateless API container)

---

## 3) Data Model (MVP Entities)

### 3.1 Identity & Access
- `users`
- `roles`
- `user_roles`
- `sessions` *(optional; for refresh-token tracking if implemented)*

### 3.2 Masters
- `customers`
- `manufacturers`
- `products` (links to manufacturer)

### 3.3 Enquiry lifecycle
- `enquiries`
- `enquiry_items` (products + requested qty + notes)
- `enquiry_status_history` (status transitions over time)

### 3.4 Quotations & Approvals
- `quotations` (one enquiry → many quotations)
- `quotation_revisions` (one quotation → many revisions)
- `quotation_items` (per revision)
- `approvals` (approval records, per revision or per quotation step)

### 3.5 Purchase Orders & Invoices
- `customer_pos`
- `rtm_pos`
- `invoices`
- `payments`

### 3.6 Audit Trail
- `audit_events`
  - actor (user id)
  - entity type + entity id
  - action (CREATE/UPDATE/DELETE/STATUS_CHANGE/APPROVE/etc.)
  - before/after snapshots (JSONB)
  - timestamp

> Notes:
> - Use `UUID` primary keys for API safety and merging environments.
> - Use `JSONB` for audit snapshots and flexible calculation payloads.

---

## 4) API Design (REST Endpoints)

### 4.1 Authentication
- `POST /auth/login` → JWT access token (+ optional refresh token)
- `POST /auth/logout` *(optional)*
- `GET  /auth/me`

### 4.2 Masters
- `GET/POST /customers`
- `GET/PUT/DELETE /customers/{id}`
- same pattern for `/products`, `/manufacturers`

### 4.3 Excel Imports
- `POST /imports/customers` (multipart file)
- `POST /imports/products`
- `POST /imports/manufacturers`

### 4.4 Enquiries
- `POST /enquiries`
- `GET  /enquiries`
- `GET  /enquiries/{id}`
- `POST /enquiries/{id}/status` (transition)
- `GET  /enquiries/{id}/history`

### 4.5 Quotations & Revisions
- `POST /enquiries/{id}/quotations`
- `POST /quotations/{id}/revisions`
- `GET  /quotations/{id}`
- `GET  /quotations/{id}/revisions/{rev_id}`

### 4.6 Approvals
- `POST /quotations/{id}/revisions/{rev_id}/submit`
- `POST /quotations/{id}/revisions/{rev_id}/approve`
- `POST /quotations/{id}/revisions/{rev_id}/reject`

### 4.7 PO / Invoice / Payments
- `POST /quotations/{id}/revisions/{rev_id}/customer-po`
- `POST /quotations/{id}/revisions/{rev_id}/rtm-po`
- `POST /invoices`
- `POST /payments`

### 4.8 Reporting
- `GET /reports/kpis`
- `GET /reports/enquiries.xlsx`
- `GET /reports/quotations.xlsx`
- `GET /reports/invoices.xlsx`

---

## 5) Backend Implementation Stack (Open-Source Only)

### 5.1 Python libraries (install into the existing venv)
Core:
- `fastapi`
- `uvicorn[standard]`
- `pydantic`
- `python-multipart` (file uploads)
- `python-jose[cryptography]` (JWT)
- `passlib[bcrypt]` (password hashing)

Database:
- `sqlalchemy`
- `psycopg[binary]`
- `alembic`

Excel import/export:
- `pandas`
- `openpyxl` (read)
- `xlsxwriter` (write)

Observability / Ops:
- `structlog` *(or standard logging; keep minimal if preferred)*
- `prometheus-client` *(optional; only if you expose metrics)*

Testing / quality:
- `pytest`
- `pytest-asyncio`
- `httpx`
- `ruff`
- `mypy`
- `pre-commit`

### 5.2 Recommended install command (venv)
```bash
pip install --upgrade pip

pip install \
  fastapi uvicorn[standard] pydantic python-multipart \
  "python-jose[cryptography]" "passlib[bcrypt]" \
  sqlalchemy alembic "psycopg[binary]" \
  pandas openpyxl xlsxwriter \
  pytest pytest-asyncio httpx \
  ruff mypy pre-commit
````

---

## 6) Repository Layout (Monorepo)

```text
ems/
  backend/
    app/
      main.py
      core/
        config.py
        security.py
        rbac.py
        logging.py
      db/
        session.py
        base.py
        migrations/          # Alembic
      models/
        user.py
        customer.py
        product.py
        manufacturer.py
        enquiry.py
        quotation.py
        approval.py
        po.py
        invoice.py
        audit.py
      schemas/              # Pydantic DTOs
      services/             # business logic
      api/                  # routers
        auth.py
        masters.py
        enquiries.py
        quotations.py
        approvals.py
        orders.py
        invoices.py
        reports.py
      utils/
        excel.py
        audit.py
    tests/
    Dockerfile
  docker-compose.yml
  .env.example
  render.yaml              # optional blueprint file
  Makefile                 # convenience commands
  README.md
```

---

## 7) Environment Configuration

### 7.1 Local `.env` (example)

```dotenv
APP_ENV=local
APP_NAME=ems
SECRET_KEY=change-me
ACCESS_TOKEN_EXPIRE_MINUTES=60

DB_HOST=db
DB_PORT=5432
DB_NAME=ems
DB_USER=ems
DB_PASSWORD=ems

CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### 7.2 Production env vars on Render

* `APP_ENV=prod`
* `SECRET_KEY=<generated>`
* `DATABASE_URL=<Render Postgres connection string>` (Render provides this)

---

## 8) Dockerization

### 8.1 Backend Dockerfile (`backend/Dockerfile`)

**Principles**

* multi-stage optional (kept simple for MVP)
* use non-root user if desired
* run via Gunicorn + Uvicorn workers for production-grade process model

Example:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
  && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend /app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host=0.0.0.0", "--port=8000"]
```

> If you prefer a production runner:
>
> * Add `gunicorn` to requirements
> * Use: `gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000 --workers 2`

### 8.2 Docker Compose (`docker-compose.yml`)

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: ems
      POSTGRES_USER: ems
      POSTGRES_PASSWORD: ems
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ems -d ems"]
      interval: 5s
      timeout: 3s
      retries: 20

  api:
    build:
      context: .
      dockerfile: backend/Dockerfile
    env_file:
      - .env
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy

volumes:
  pgdata:
```

---

## 9) Database Migrations (Alembic)

### 9.1 Initialize

```bash
cd backend
alembic init app/db/migrations
```

### 9.2 Configure Alembic

* Point Alembic to SQLAlchemy metadata
* Use env var `DATABASE_URL` or compose-based host settings

### 9.3 Run migrations in Docker

```bash
docker compose up -d --build
docker compose exec api alembic upgrade head
```

---

## 10) Smoke Tests (Local) — curl

### 10.1 Health endpoint

Implement:

* `GET /health` → `{"status":"ok"}`

Run:

```bash
curl -s http://localhost:8000/health | jq .
```

### 10.2 OpenAPI availability

```bash
curl -I http://localhost:8000/docs
curl -I http://localhost:8000/openapi.json
```

### 10.3 Auth flow smoke test (example sequence)

1. Login

```bash
curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

2. Use token to call a protected endpoint

```bash
TOKEN="...paste..."
curl -s http://localhost:8000/customers \
  -H "Authorization: Bearer $TOKEN"
```

> Seed an initial `SuperAdmin` user via a one-time CLI command or migration script executed inside `api` container (still fully open-source, no external services).

---

## 11) Security & RBAC (MVP Architecture)

### 11.1 Authentication

* JWT access token for stateless auth
* Password hashing with bcrypt
* Token validation middleware (FastAPI dependency)

### 11.2 Authorization

* RBAC policy layer:

  * route-level enforcement (`Depends(require_roles(...))`)
  * entity-level enforcement for actions (e.g., approval only for Admin/SuperAdmin)

### 11.3 Audit trail

* Central audit writer:

  * executed inside service layer methods
  * records:

    * actor user id
    * action
    * entity reference
    * before/after JSONB snapshots

---

## 12) Reporting & Excel Export

### 12.1 Dashboard KPIs

* Implement read-only endpoints returning aggregated metrics:

  * enquiry counts by status
  * quotation conversion counts
  * invoice/payment summaries

### 12.2 Excel export

* Generate `.xlsx` on-demand:

  * `GET /reports/enquiries.xlsx`
* Use:

  * `pandas` + `xlsxwriter` to stream a file response

---

## 13) Production Deployment on Render (Free)

### 13.1 Render constraints to account for

* **Free Postgres expiration**: newly created free PostgreSQL DBs expire after **30 days**. ([Render][1])
* **Free Postgres limits**: one free DB per workspace; fixed storage capacity of **1 GB**. ([Render][2])
* Docker builds are supported for Render services. ([Render][3])

### 13.2 Deploy strategy (Docker-based)

* Push repository to GitHub
* Create:

  1. Render Postgres database
  2. Render Web Service using the repo’s Dockerfile

Render will build using BuildKit from the Dockerfile. ([Render][3])

### 13.3 Render start command

* Keep container command as defined in `CMD` (uvicorn/gunicorn)
* Ensure app binds to `0.0.0.0:$PORT` if Render requires dynamic ports (Render typically provides `PORT` env var; configure accordingly in entrypoint).

### 13.4 Database connection

* Use `DATABASE_URL` in production
* Map SQLAlchemy engine creation to:

  * `DATABASE_URL` if present
  * else compose vars (`DB_HOST`, `DB_PORT`, etc.)

### 13.5 Migrations on deploy

* Add a pre-start command in Render (or a release step pattern) to run:

  * `alembic upgrade head`
* Keep idempotent.

---

## 14) Minimal CI (Open-Source)

### 14.1 What CI should do

* Lint: `ruff`
* Typecheck: `mypy`
* Tests: `pytest`
* Build: Docker build test

### 14.2 GitHub Actions (optional but recommended)

* Fully free (public repos), open-source tooling only

---

## 15) Operational Notes (MVP)

### 15.1 Stateless API container

* No local file persistence required
* Excel exports generated on the fly

### 15.2 Logging

* Structured logs to stdout (Render captures logs)
* Include request id and user id when available

### 15.3 Scaling posture

* MVP runs as a single web service instance
* DB is the single source of truth
* Architecture cleanly separates:

  * routers (API)
  * services (business rules)
  * repositories/models (DB)

---

## 16) Deliverables Checklist (MVP Architecture Output)

* FastAPI project with modular routers + service layer
* PostgreSQL schema + Alembic migrations
* RBAC enforcement for the defined roles
* Audit trail stored in Postgres
* Excel import endpoints for masters
* Enquiry → quotation revisions → approval → PO → invoice/payment → delivery tracking entities
* Reporting endpoints + Excel export
* Dockerfile + docker-compose.yml
* Smoke tests documented and executable with `curl`
* Render deployment configuration using Docker build + Render Postgres ([Render][3])
