# Migration Strategy

## Goal

Keep the PostgreSQL schema deterministic, reviewable, and reversible through Alembic migrations.

## Conventions

1. One migration per intentional schema change.
2. Revisions are ordered by roadmap sequence (`001_`, `002_`, ...).
3. Every migration must define both `upgrade()` and `downgrade()`.
4. Avoid implicit autogenerate-only migrations; review and edit generated SQL before commit.
5. Use explicit constraints and names for indexes, unique constraints, and foreign keys.

## Current Baseline

- `001_extensions_and_base_enums`
  - enables `pgcrypto`
  - creates base ENUM types for workflow/status fields
- `002_roles_users_sessions`
  - creates identity tables (`roles`, `users`, `user_roles`, `sessions`)
  - seeds roles: `BD`, `Admin`, `SuperAdmin`, `SupplyChain`
  - seeds default `SuperAdmin` user (`admin` / `admin`) for first login
- `003_masters_catalog`
  - creates master tables: `customers`, `manufacturers`, `products`
  - adds uniqueness constraints for business keys (`code`, `sku`)
  - adds functional uniqueness indexes for name/country and product name/manufacturer
- `004_enquiries_workflow`
  - creates `enquiries`, `enquiry_items`, and `enquiry_status_history`
  - adds workflow-level constraints and indexes for status/date lookup
  - adds `audit_events` table used by enquiry lifecycle status transitions
- `005_quote_approval_workflow`
  - creates quotation tables: `quotations`, `quotation_revisions`, `quotation_items`, `approvals`
  - enforces revision uniqueness (`quotation_id`, `revision_no`)
  - enables approval decision tracking (`PENDING`, `APPROVED`, `REJECTED`)
- `006_po_invoice_payment_delivery`
  - creates commercial tables: `customer_pos`, `rtm_pos`, `invoices`, `payments`, `deliveries`, `delivery_events`
  - enforces amount/date constraints (non-negative totals, positive payment amount, `due_date >= issue_date`)
  - enforces delivery integrity (`delivered_at >= shipped_at`) and unique business IDs (`po_no`, `invoice_no`, `shipment_no`)
- `007_phase8_indexes_hardening`
  - adds missing FK/date indexes to reduce query cost on operational flows and reporting windows
  - adds observability indexes on `audit_events.request_id` and `audit_events.created_at`

## Local Workflow

Run from repository root:

```bash
docker compose up -d --build
docker compose exec -T api alembic -c alembic.ini upgrade head
```

Rollback test:

```bash
docker compose exec -T api alembic -c alembic.ini downgrade base
docker compose exec -T api alembic -c alembic.ini upgrade head
```

## Creating a New Migration

```bash
docker compose exec -T api alembic -c alembic.ini revision -m "short_change_summary"
```

If using autogenerate:

```bash
docker compose exec -T api alembic -c alembic.ini revision --autogenerate -m "short_change_summary"
```

Then manually review and fix the file before applying.

## Render Deployment Strategy

At deploy/release time, run:

```bash
alembic -c alembic.ini upgrade head
```

This keeps production schema aligned with application code and remains idempotent.
