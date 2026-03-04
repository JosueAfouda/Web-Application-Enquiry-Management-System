# Enquiry Management System (EMS)

A full-stack web application for managing pharmaceutical product enquiries from first customer request to delivery closure.

## 1. Project Overview
EMS helps export/trading teams run a complex enquiry-to-order process in one system. Instead of tracking enquiries across spreadsheets, email threads, and chat, EMS centralizes the workflow with role-based access, controlled status transitions, pricing revisions, approvals, commercial documents, reporting, and audit history.

### What problem it solves
- Enquiries were hard to track across teams (BD, Admin, Super Admin, Supply Chain).
- Quotation negotiation history was fragmented.
- Commercial steps (PO, invoice, payment, delivery) lacked traceability.
- Managers lacked consistent KPI reporting.

### Who it is for
- Pharmaceutical export/trading operations teams
- Sales/BD teams
- Commercial and supply-chain teams
- Technical teams maintaining internal business systems

## 2. Business Context
In pharmaceutical export, each customer enquiry may go through multiple rounds of manufacturer pricing, internal approval, and commercial execution before closure. Delays or missing information can impact revenue and customer trust.

EMS standardizes this lifecycle:
- Capture enquiry
- Build and revise quotations
- Approve pricing
- Execute PO/invoice/payment/delivery
- Measure outcomes with reports

## 3. Core Business Concepts
- **Customer**: Buyer requesting products.
- **Manufacturer**: Supplier providing product rates and fulfilment.
- **Product**: Tradeable pharmaceutical item in master data.
- **Enquiry**: Customer request with one or more line items.
- **Quotation**: Commercial response linked to an enquiry.
- **Quotation Revision**: Versioned pricing iteration for negotiation.
- **Approval**: Formal decision on a submitted revision.
- **Customer PO**: Purchase order received from the customer.
- **RTM PO**: Internal/manufacturer-facing PO for procurement execution.
- **Invoice**: Billing document tied to enquiry/PO context.
- **Payment**: Money received against invoice, tracked with due/outstanding logic.
- **Delivery Tracking**: Shipment lifecycle and event timeline.

## 4. End-to-End Workflow
```text
Customer Request
   -> Enquiry Creation (BD/Admin)
   -> Enquiry Review & Status Tracking
   -> Quotation Creation
   -> Revision(s): freight + markup + line pricing
   -> Submit for Approval
   -> Approve/Reject (Admin/SuperAdmin)
   -> Customer PO / RTM PO
   -> Invoice Creation
   -> Payment Collection (partial/full)
   -> Delivery + Delivery Events
   -> KPI & Excel Reporting
```

## 5. Feature Design Methodology
### Authentication & Role-Based Access
- **Goal**: Restrict actions by role.
- **Problem solved**: Unauthorized edits and unclear ownership.
- **Design logic**: JWT auth + RBAC guards at API level and role-aware UI navigation.

### Master Data Management
- **Goal**: Keep customer/manufacturer/product data consistent.
- **Problem solved**: Duplicate or inconsistent records.
- **Design logic**: CRUD masters with validation and Excel imports for scale.

### Enquiry Lifecycle
- **Goal**: Track enquiry progression with accountability.
- **Problem solved**: Lost context and status ambiguity.
- **Design logic**: Controlled status transitions + history table (who/when/comment).

### Quotation Revision System
- **Goal**: Support negotiation without losing prior prices.
- **Problem solved**: Overwriting pricing history.
- **Design logic**: Immutable revision records with computed totals and lineage.

### Approval Workflow
- **Goal**: Formal governance before commercial commitment.
- **Problem solved**: Unapproved prices going downstream.
- **Design logic**: Submit/approve/reject states, approval timeline, required remarks for approve/reject.

### Purchase Orders
- **Goal**: Convert approved pricing into executable orders.
- **Problem solved**: Manual handoff gaps between teams.
- **Design logic**: Separate customer PO and RTM PO entities tied to approved revision.

### Invoice & Payment Tracking
- **Goal**: Track receivables and collection status.
- **Problem solved**: Poor visibility into outstanding amounts.
- **Design logic**: Invoice states (`UNPAID/PARTIAL/PAID`) derived from payment events with overpayment protection.

### Reporting & Excel Export
- **Goal**: Enable operational and management visibility.
- **Problem solved**: Manual KPI compilation.
- **Design logic**: KPI API + export endpoints (`enquiries/quotations/invoices/payments.xlsx`).

### Audit Trail
- **Goal**: Provide accountability and traceability.
- **Problem solved**: Difficult post-incident analysis.
- **Design logic**: Structured audit events around create/update/approve/reject/business actions.

### Observability
- **Goal**: Make runtime behavior diagnosable.
- **Problem solved**: Slow debugging and opaque failures.
- **Design logic**: `/health`, structured logs, per-request ID propagation, normalized error schema.

## 6. System Architecture
### High-Level
```text
[React + Nginx (web)]  --->  [FastAPI (api)]  --->  [PostgreSQL (db)]
         |                        |
         |                        +--> Alembic migrations
         |
         +--> Role-aware UI, forms, workflow actions
```

### Components
- **Frontend**: React + TypeScript SPA (Vite build) served by Nginx.
- **Backend**: FastAPI service exposing REST APIs and business workflow rules.
- **Database**: PostgreSQL with Alembic migration history.
- **API Contract**: OpenAPI available at `/docs` and `/openapi.json`.
- **Container Platform**: Docker Compose for local orchestration.
- **Production**: Render Blueprint (`render.yaml`) for API + static frontend + managed Postgres.

## 7. Technology Stack
- **Backend**: Python 3.12, FastAPI, SQLAlchemy, Alembic, Pydantic.
- **Database**: PostgreSQL 16.
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS, React Query, React Hook Form + Zod.
- **Auth/Security**: JWT access/refresh model, password hashing, RBAC.
- **Reporting**: Pandas/OpenPyXL/XlsxWriter for Excel exports.
- **Infra**: Docker, Docker Compose, Render.

Why this stack:
- Open-source and zero-cost compatible
- Fast API iteration with strong typing and validation
- Reliable deployment path from local to cloud

## 8. Project Structure
```text
backend/
  app/
    api/            # HTTP endpoints
    services/       # business logic
    models/         # SQLAlchemy entities
    schemas/        # request/response contracts
    db/migrations/  # Alembic revisions
  tests/            # backend tests

frontend/
  src/
    pages/          # route-level screens
    components/     # UI and layout building blocks
    context/        # auth/workflow state
    lib/            # API client, helpers, formatting

scripts/
  smoke_local.sh
  smoke_frontend.sh

render.yaml         # production blueprint
docker-compose.yml  # local orchestration
```

## 9. Running the System Locally
### Prerequisites
- Docker + Docker Compose

### 1) Configure environment
```bash
cp .env.example .env
```

### 2) Start all services
```bash
docker compose up -d --build
```

### 3) Apply database migrations
```bash
docker compose exec -T api alembic -c alembic.ini upgrade head
```

### 4) Access the system
- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### 5) Default login (local/dev)
- Username: `admin`
- Password: `admin`

### Important environment variables
- `APP_ENV`, `APP_NAME`, `APP_VERSION`
- `SECRET_KEY`, `JWT_ALGORITHM`, token expirations
- `DB_*` or `DATABASE_URL`
- `CORS_ORIGINS`
- `DELIVERY_START_REQUIRED_STEP`
- `VITE_API_URL` (frontend build-time API target)

## 10. Smoke Testing
Run automated sanity checks:
```bash
bash scripts/smoke_local.sh
bash scripts/smoke_frontend.sh
```

What these verify:
- API health endpoint
- Authentication flow (`/auth/login`, `/auth/me`)
- Frontend reachability and SPA routing

## 11. Deployment (Render)
Production is defined in `render.yaml`:
- `ems-api` (Python web service)
- `ems-web` (static web service)
- `ems-postgres` (managed Postgres)

Deployment flow:
1. Render builds API with `build.sh`.
2. API start command waits for DB (`wait-for-postgres.py`).
3. Alembic migrations run at startup.
4. Uvicorn serves FastAPI.
5. Frontend builds in Render and publishes static assets.
6. `VITE_API_URL` is wired from API service URL.

## 12. Security Model
- JWT-based authentication (access + refresh tokens).
- RBAC enforced in backend endpoints and reflected in UI navigation.
- Standardized error payload with request identifiers.
- Audit events recorded for key business actions.
- CORS allow-list controlled by environment.

## 13. Observability
- **Health checks**:
  - API: `/health`
  - Container healthchecks in Docker Compose
- **Request tracking**:
  - `X-Request-ID` generated/preserved per request
  - Returned in responses and error payloads
- **Logging**:
  - Structured request logs with method, path, status, duration
- **Operational behavior**:
  - Frontend monitors API availability and surfaces retry UX

## 14. Future Improvements
- Advanced BRD extensions (broader workflow stages and extra business fields)
- Password reset and user approval administration UX
- Attachment management for quotations/invoices
- Email reminders and digest notifications
- Additional reports (ageing, performance, revenue detail, PDF export)
- Optional customer/manufacturer self-service portals

---
If you want a guided validation path through the UI, see `FRONTEND_USER_GUIDE.md`.
