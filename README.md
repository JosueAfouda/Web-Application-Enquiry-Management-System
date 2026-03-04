# Web-Application-Enquiry-Management-System

Web-based Enquiry Management System (EMS) MVP for a pharmaceutical export/trading workflow.

## Current Status

EMS MVP backend + frontend are implemented:
- FastAPI backend with PostgreSQL and Alembic migrations
- React + TypeScript frontend (Vite build served by Nginx)
- Docker Compose stack (`db`, `api`, `web`)
- RBAC, masters/imports, enquiry workflow, quotations/revisions/approvals, PO/invoice/payment/delivery, KPI reporting/export
- Curl smoke scripts (`scripts/smoke_local.sh`, `scripts/smoke_frontend.sh`)

## Quick Start (Local)

1. Copy environment file:

```bash
cp .env.example .env
```

2. Start services:

```bash
docker compose up -d --build
```

3. Check health:

```bash
curl -i http://localhost:8000/health
```

4. Run smoke script:

```bash
bash scripts/smoke_local.sh
```

5. Stop services:

```bash
docker compose down
```

Note:
- The database is intentionally **not** exposed on host ports (`5432`/`5433` safe).
- The API is exposed on `http://localhost:8000`.
- The frontend is exposed on `http://localhost:3000`.

Frontend workflow and happy-path checklist:
- See `FRONTEND_USER_GUIDE.md`.

## Database Migrations (Alembic)

Apply latest migrations:

```bash
docker compose exec -T api alembic -c alembic.ini upgrade head
```

Rollback to base:

```bash
docker compose exec -T api alembic -c alembic.ini downgrade base
```

Re-apply to head:

```bash
docker compose exec -T api alembic -c alembic.ini upgrade head
```

## Authentication Seed Data (Phase 2)

After applying migrations, a default `SuperAdmin` account is available:
- `username`: `admin`
- `password`: `admin`

Rotate this credential immediately in non-local environments.

## Auth Smoke (Phase 2)

Login:

```bash
curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

Me endpoint (replace `TOKEN`):

```bash
curl -s http://localhost:8000/auth/me \
  -H "Authorization: Bearer TOKEN"
```

## Masters (Phase 3)

Create a customer:

```bash
curl -s -X POST http://localhost:8000/customers \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"code":"CUST001","name":"Acme Pharma","country":"India","contact_fields":{"contact_email":"ops@acme.example"},"is_active":true}'
```

Import manufacturers from Excel:

```bash
curl -s -X POST "http://localhost:8000/imports/manufacturers" \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@./manufacturers.xlsx"
```

## Enquiries (Phase 4)

Create an enquiry:

```bash
curl -s -X POST http://localhost:8000/enquiries \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"<CUSTOMER_UUID>","currency":"USD","items":[{"product_id":"<PRODUCT_UUID>","requested_qty":10.0,"target_price":15.50}]}'
```

Transition status:

```bash
curl -s -X POST http://localhost:8000/enquiries/<ENQUIRY_UUID>/status \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"to_status":"IN_REVIEW","comment":"triage started"}'
```

## Quotations (Phase 5)

Create quotation:

```bash
curl -s -X POST http://localhost:8000/enquiries/<ENQUIRY_UUID>/quotations \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

Create revision:

```bash
curl -s -X POST http://localhost:8000/quotations/<QUOTATION_UUID>/revisions \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"freight":15.5,"markup_percent":7.5,"currency":"USD","items":[{"product_id":"<PRODUCT_UUID>","qty":10,"unit_price":9.99}]}'
```

## Commercial Flow (Phase 6)

Create customer PO from approved revision:

```bash
curl -s -X POST http://localhost:8000/quotations/<QUOTATION_UUID>/revisions/<REVISION_UUID>/customer-po \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

Create invoice:

```bash
curl -s -X POST http://localhost:8000/invoices \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"enquiry_id":"<ENQUIRY_UUID>","total_amount":120.00,"currency":"USD"}'
```

Create payment:

```bash
curl -s -X POST http://localhost:8000/payments \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"invoice_id":"<INVOICE_UUID>","amount":40.00,"method":"BANK_TRANSFER","reference_no":"TXN-123"}'
```

Create delivery:

```bash
curl -s -X POST http://localhost:8000/deliveries \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"enquiry_id":"<ENQUIRY_UUID>","courier_name":"DHL","tracking_no":"TRK-001"}'
```

## Reporting (Phase 7)

KPI JSON report:

```bash
curl -s "http://localhost:8000/reports/kpis?date_from=2026-01-01&date_to=2026-12-31" \
  -H "Authorization: Bearer TOKEN"
```

Download enquiries Excel report:

```bash
curl -s "http://localhost:8000/reports/enquiries.xlsx?status=APPROVED" \
  -H "Authorization: Bearer TOKEN" \
  -o enquiries.xlsx
```

Download payments Excel report:

```bash
curl -s "http://localhost:8000/reports/payments.xlsx?date_from=2026-01-01&date_to=2026-12-31" \
  -H "Authorization: Bearer TOKEN" \
  -o payments.xlsx
```

## Error Schema and Request ID (Phase 8)

Every response includes `X-Request-ID`. API errors are normalized to:

```json
{
  "error": {
    "code": "http_401",
    "message": "Not authenticated",
    "request_id": "b0e6f8f2-2d31-4a92-b20b-cb4f2c9a08c7",
    "details": null
  }
}
```

## Quality Checks

```bash
.venv/bin/ruff check backend
.venv/bin/mypy backend/app
PYTHONPATH=backend .venv/bin/pytest -q
```
