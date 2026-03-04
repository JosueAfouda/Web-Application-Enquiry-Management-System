# EMS Implementation Roadmap (Pre-Coding Technical Plan)

## 1. Scope, Objectives, and Non-Negotiable Constraints

This roadmap delivers an MVP for a web-based Enquiry Management System (EMS) for a pharmaceutical export/trading workflow:

1. Enquiry receipt
2. Quotation preparation and revisioning
3. Approval workflow with pricing elements
4. Purchase Order generation (Customer PO and RTM PO)
5. Invoice and payment tracking
6. Delivery tracking
7. Reporting and Excel export

Mandatory constraints:

- Python `3.12.3`
- Ubuntu `24.04`
- Docker and Docker Compose for local development
- FastAPI backend (selected from allowed options)
- PostgreSQL database
- Open-source tooling only
- Zero-cost deployment target: Render free tier
- Curl-based smoke tests

## 2. Architecture Decisions and Required Amendments

Base architecture from `MVP_ARCHITECTURE.md` is accepted with these required amendments for requirement completeness:

1. Add explicit **delivery tracking** persistence model (`deliveries`, `delivery_events`), because customer need includes delivery tracking as a core lifecycle step.
2. Implement **workflow state machine enforcement** at service layer (not only status strings).
3. Add explicit **idempotency/uniqueness rules** for imported master data to prevent duplicate records from repeated Excel imports.
4. Add **refresh-token session table** for controlled logout and token revocation (recommended for security and auditability).
5. Add explicit **financial and quantity numeric constraints** (non-negative checks, precision definitions) to avoid data corruption.

## 3. Delivery Strategy (Incremental Phases)

Implementation is split into 10 executable phases. Each phase ends with acceptance checks before moving forward.

### Phase 0: Foundation and Repository Bootstrap

Deliverables:

1. Repository scaffold according to target layout (`backend/app/...`, `tests`, `Dockerfile`, `docker-compose.yml`, `.env.example`, `Makefile`).
2. Dependency management baseline (`requirements.txt` or `pyproject.toml` lock strategy).
3. Code quality tooling configured: `ruff`, `mypy`, `pytest`, `pre-commit`.
4. App bootstrap: `GET /health`, startup logging, config loading via environment.

Acceptance checks:

1. `docker compose up --build` starts API and DB.
2. `curl http://localhost:8000/health` returns `{"status":"ok"}`.
3. Lint and tests run in containerized environment.

### Phase 1: Database Baseline and Migration Framework

Deliverables:

1. SQLAlchemy base, session management, Alembic initialization.
2. Migration `001` enabling required extensions (`pgcrypto` for UUID generation if used server-side).
3. Migration strategy document defining naming standards and rollback approach.

Acceptance checks:

1. `alembic upgrade head` succeeds on empty DB.
2. `alembic downgrade base` and re-upgrade succeed in development DB.

### Phase 2: Identity, Authentication, RBAC, and Seed Data

Models and constraints:

1. `roles(id, name unique)` with seed values: `BD`, `Admin`, `SuperAdmin`, `SupplyChain`.
2. `users(id UUID PK, email unique, username unique, password_hash, is_active, created_at, updated_at)`.
3. `user_roles(user_id FK, role_id FK, unique(user_id, role_id))`.
4. `sessions(id UUID, user_id FK, refresh_token_hash, expires_at, revoked_at nullable, created_at)`.

API:

1. `POST /auth/login`
2. `POST /auth/refresh`
3. `POST /auth/logout`
4. `GET /auth/me`

Security behavior:

1. Password hashing with bcrypt.
2. JWT access token short TTL.
3. Refresh token rotation and revocation persistence.

Acceptance checks:

1. SuperAdmin seeded by migration or startup command.
2. Protected route access denied without token.
3. Role-protected route validated with positive and negative tests.

### Phase 3: Master Data Modules and Excel Imports

Models and constraints:

1. `customers(id UUID, code unique, name, country, contact_fields, is_active, timestamps)`.
2. `manufacturers(id UUID, code unique, name, country, is_active, timestamps)`.
3. `products(id UUID, sku unique, name, manufacturer_id FK, unit, is_active, timestamps)`.
4. Optional uniqueness for business identity on customers and manufacturers: `unique(lower(name), country)`.
5. Optional uniqueness for products where needed: `unique(lower(name), manufacturer_id)`.

API:

1. CRUD endpoints for `/customers`, `/manufacturers`, `/products`.
2. Import endpoint `POST /imports/customers`.
3. Import endpoint `POST /imports/manufacturers`.
4. Import endpoint `POST /imports/products`.

Import rules:

1. Template-driven columns and strict schema validation.
2. Row-level error collection and downloadable error report.
3. Upsert behavior keyed on `code` or `sku`.
4. Import audit event written with row statistics.

Acceptance checks:

1. Re-importing same file is idempotent.
2. Invalid rows do not silently persist.

### Phase 4: Enquiry Lifecycle Core

Models and constraints:

1. `enquiries(id UUID, enquiry_no unique, customer_id FK, owner_user_id FK, status, received_date, currency, notes, timestamps)`.
2. `enquiry_items(id UUID, enquiry_id FK, product_id FK, requested_qty numeric(14,3) check >= 0, target_price numeric(14,2) nullable check >= 0, notes)`.
3. `enquiry_status_history(id UUID, enquiry_id FK, from_status, to_status, changed_by FK users, changed_at, comment)`.

Workflow states (MVP):

1. `RECEIVED`
2. `IN_REVIEW`
3. `QUOTED`
4. `PENDING_APPROVAL`
5. `APPROVED`
6. `REJECTED`
7. `PO_CREATED`
8. `INVOICED`
9. `IN_DELIVERY`
10. `DELIVERED`
11. `CLOSED`
12. `CANCELLED`

API:

1. `POST /enquiries`
2. `GET /enquiries`
3. `GET /enquiries/{id}`
4. `POST /enquiries/{id}/status`
5. `GET /enquiries/{id}/history`

Acceptance checks:

1. Invalid status transitions return `409`.
2. Every transition writes both status history and audit event.

### Phase 5: Quotation Revision and Approval Workflow

Models and constraints:

1. `quotations(id UUID, enquiry_id FK, quotation_no unique, current_revision_no, status, timestamps)`.
2. `quotation_revisions(id UUID, quotation_id FK, revision_no, freight numeric(14,2) >= 0, markup_percent numeric(6,3) >= 0, subtotal, total, currency, submitted_at nullable, approved_at nullable, rejected_at nullable, unique(quotation_id, revision_no))`.
3. `quotation_items(id UUID, revision_id FK, enquiry_item_id FK nullable, product_id FK, qty numeric(14,3) >= 0, unit_price numeric(14,4) >= 0, line_total numeric(14,2) >= 0)`.
4. `approvals(id UUID, revision_id FK, step_name, decision, decided_by FK users nullable, decided_at nullable, remarks)`.

API:

1. `POST /enquiries/{id}/quotations`
2. `POST /quotations/{id}/revisions`
3. `GET /quotations/{id}`
4. `GET /quotations/{id}/revisions/{rev_id}`
5. `POST /quotations/{id}/revisions/{rev_id}/submit`
6. `POST /quotations/{id}/revisions/{rev_id}/approve`
7. `POST /quotations/{id}/revisions/{rev_id}/reject`

Business rules:

1. Only one active pending revision at a time.
2. Only approved revision can move to PO generation.
3. Approval action restricted to `Admin` and `SuperAdmin`.

Acceptance checks:

1. Revision numbering increments without gaps.
2. Rejected revisions cannot generate PO.

### Phase 6: Purchase Orders, Invoices, Payments, and Delivery Tracking

Models and constraints:

1. `customer_pos(id UUID, po_no unique, enquiry_id FK, quotation_revision_id FK, customer_id FK, po_date, total_amount numeric(14,2) >= 0, status, timestamps)`.
2. `rtm_pos(id UUID, po_no unique, enquiry_id FK, quotation_revision_id FK, manufacturer_id FK nullable, po_date, total_amount numeric(14,2) >= 0, status, timestamps)`.
3. `invoices(id UUID, invoice_no unique, enquiry_id FK, customer_po_id FK nullable, issue_date, due_date, currency, total_amount numeric(14,2) >= 0, status, timestamps)`.
4. `payments(id UUID, invoice_id FK, payment_date, amount numeric(14,2) > 0, method, reference_no, notes, timestamps)`.
5. `deliveries(id UUID, enquiry_id FK, invoice_id FK nullable, shipment_no unique nullable, courier_name, tracking_no, shipped_at nullable, expected_delivery_at nullable, delivered_at nullable, status, timestamps)`.
6. `delivery_events(id UUID, delivery_id FK, event_type, event_time, location, details_jsonb, created_by FK users nullable)`.

API:

1. `POST /quotations/{id}/revisions/{rev_id}/customer-po`
2. `POST /quotations/{id}/revisions/{rev_id}/rtm-po`
3. `POST /invoices`
4. `POST /payments`
5. `POST /deliveries`
6. `POST /deliveries/{id}/events`
7. `GET /deliveries/{id}`

Business rules:

1. Invoice status derived from payments (`UNPAID`, `PARTIAL`, `PAID`).
2. Sum of payments must not exceed invoice amount.
3. Delivery can start only after required commercial step (`PO_CREATED` or `INVOICED`, as configured).

Acceptance checks:

1. Overpayment returns validation error.
2. Delivery event timeline is append-only.

### Phase 7: Audit Trail and Reporting

Models:

1. `audit_events(id UUID, actor_user_id FK nullable, entity_type, entity_id, action, before_jsonb, after_jsonb, request_id, created_at)`.

Reporting endpoints:

1. `GET /reports/kpis`
2. `GET /reports/enquiries.xlsx`
3. `GET /reports/quotations.xlsx`
4. `GET /reports/invoices.xlsx`
5. `GET /reports/payments.xlsx`

KPI baseline:

1. Enquiry counts by status and date range.
2. Quotation approval rate.
3. PO conversion rate.
4. Invoice outstanding vs collected.
5. Delivery completion rate.

Acceptance checks:

1. Exported Excel files open cleanly and match filter criteria.
2. Audit events exist for create/update/delete/status-change/approve/reject/import actions.

### Phase 8: Hardening, Observability, and Performance

Implementation:

1. Structured logging with request ID and user ID context.
2. Global exception handlers for consistent API errors.
3. DB index review for status/date access on `enquiries`.
4. DB index review for FK columns across all relationship tables.
5. DB unique/index review for business identifiers: `enquiry_no`, `quotation_no`, `po_no`, `invoice_no`.
6. Pagination and filtering defaults on list endpoints.
7. CORS locked to configured origins.

Acceptance checks:

1. No N+1 query hotspots on main list/detail endpoints.
2. Consistent error schema across API.

### Phase 9: Dockerization, Smoke Tests, and Deployment to Render

Local containerization:

1. `backend/Dockerfile` for API image.
2. `docker-compose.yml` with `api` and `db`.
3. Healthchecks for API and PostgreSQL.
4. One-command startup and migration execution.

Smoke test suite (`scripts/smoke.sh` with curl):

1. Health endpoint check.
2. Auth login check.
3. Protected endpoint check.
4. Minimal end-to-end happy path step: create customer/product/manufacturer.
5. Minimal end-to-end happy path step: create enquiry and item.
6. Minimal end-to-end happy path step: create quotation revision.
7. Minimal end-to-end happy path step: approve revision.
8. Minimal end-to-end happy path step: create customer PO.
9. Minimal end-to-end happy path step: create invoice.
10. Minimal end-to-end happy path step: post payment.
11. Minimal end-to-end happy path step: create delivery event.

Render deployment:

1. Provision free Render Postgres.
2. Provision Web Service from Dockerfile.
3. Set env vars (`APP_ENV`, `SECRET_KEY`, `DATABASE_URL`, token settings, CORS).
4. Run `alembic upgrade head` in release/pre-start command.
5. Verify public health endpoint and smoke tests against deployed URL.

Free-tier operations note:

1. Render free Postgres has expiration/size constraints; define a recurring backup-and-restore runbook for non-production data continuity.

### Phase 10: Documentation and Handover

Deliverables:

1. Updated `README.md` with local run instructions, migration commands, and smoke test execution.
2. API usage examples with curl commands.
3. RBAC permission matrix document.
4. Data dictionary for all tables and enums.
5. Deployment runbook for Render free tier.

Acceptance checks:

1. A new engineer can bootstrap and run locally using only documented steps.
2. All critical workflows are reproducible via curl.

## 4. Migration Plan (Ordered, Concrete)

Apply migrations in this exact sequence:

1. `001_extensions_and_base_enums`
2. `002_roles_users_user_roles_sessions`
3. `003_customers_manufacturers_products`
4. `004_enquiries_enquiry_items_status_history`
5. `005_quotations_revisions_items_approvals`
6. `006_customer_pos_rtm_pos`
7. `007_invoices_payments`
8. `008_deliveries_delivery_events`
9. `009_audit_events`
10. `010_indexes_constraints_backfill`
11. `011_seed_roles_superadmin`

Each migration must include:

1. Forward and downgrade logic.
2. Explicit constraints (FKs, uniques, checks).
3. Data backfill where new non-null columns are introduced.

## 5. API Module Implementation Order

Build routers/services in this order to reduce dependency risk:

1. `auth`
2. `masters`
3. `enquiries`
4. `quotations`
5. `approvals`
6. `orders` (PO)
7. `invoices`
8. `deliveries`
9. `reports`
10. `audit` read endpoints (optional admin-only)

Rule: every router must call service-layer methods; direct DB logic inside routers is prohibited.

## 6. RBAC Baseline Matrix (MVP)

Minimum enforcement:

1. `SuperAdmin`: full access including user/role administration.
2. `Admin`: approvals, masters, operational records, reports.
3. `BD`: enquiry creation/update, quotation drafting, customer-facing flow visibility.
4. `SupplyChain`: RTM PO operations, delivery updates, relevant reporting views.

Implementation rule: deny-by-default policy; route and action permissions explicitly granted.

## 7. Testing Strategy (Must Be Implemented Early)

Test layers:

1. Unit tests for service rules (status transitions, pricing, approval guards, payment limits).
2. API integration tests for each module with test DB.
3. Migration tests (upgrade + downgrade + upgrade).
4. Smoke tests with curl for local and deployed environment.

Quality gates before merge:

1. `ruff` passes.
2. `mypy` passes for `app/`.
3. `pytest` passes.
4. Docker image builds.
5. Smoke script passes against local compose stack.

## 8. CI/CD Blueprint (Zero-Cost)

GitHub Actions pipeline:

1. Lint and typecheck job.
2. Test job with PostgreSQL service container.
3. Docker build verification job.
4. Optional deploy trigger to Render (manual approval recommended for MVP).

All tools must remain open-source and free-to-use.

## 9. 8-12 Week Milestone Schedule

1. Week 1: Phase 0 and Phase 1 complete.
2. Week 2: Phase 2 complete (auth and RBAC).
3. Week 3: Phase 3 complete (masters and imports).
4. Week 4: Phase 4 complete (enquiry lifecycle).
5. Week 5: Phase 5 complete (quotations and approvals).
6. Week 6: Phase 6 complete (PO, invoice, payment, delivery).
7. Week 7: Phase 7 complete (audit and reporting).
8. Week 8: Phase 8 hardening and full smoke coverage.
9. Week 9: Phase 9 deployment readiness and Render validation.
10. Week 10-12: UAT feedback, bug-fix cycles, documentation finalization, handover.

## 10. Definition of Done (Project-Level)

Project is considered implementation-ready and complete when all conditions are true:

1. All required modules are live and connected in one end-to-end flow.
2. Role-based access is enforced and tested.
3. Audit trail captures critical actions.
4. Docker local stack works on Ubuntu 24.04 with Python 3.12.3.
5. Curl smoke suite passes locally and on Render deployment.
6. PostgreSQL schema is migration-managed and reproducible.
7. Documentation is sufficient for autonomous continuation by AI coding agents.
