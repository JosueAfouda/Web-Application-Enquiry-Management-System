# EMS Frontend User Guide

## 1. Run Locally (Docker Compose)

```bash
cp .env.example .env

docker compose up -d --build
```

Access:
- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs

Run smoke checks:

```bash
bash scripts/smoke_local.sh
bash scripts/smoke_frontend.sh
```

Stop services:

```bash
docker compose down
```

## 2. Frontend Dev Workflow (Hot Reload)

```bash
cd frontend
npm run dev
```

Then open http://localhost:5173 (Vite dev server). Ensure API is running at `http://localhost:8000`.

## 3. Demo Login Credentials

Seed user from migrations:
- Username: `admin`
- Password: `admin`
- Role: `SuperAdmin`

## 4. Happy-Path Validation (UI)

1. Login at `/login`.
2. Optional fast-start for demo:
   - On `Dashboard`, click `DEMO DATA` (Admin/SuperAdmin only).
   - This seeds a full sample flow (masters, enquiry, quotation/revision/approval, PO, invoice, payment, delivery).
3. If the API is unavailable, a warning banner appears in the top shell with a `Retry` action.
4. Manual flow (if not using demo seed):
   - Create masters:
     - Customers
     - Manufacturers
     - Products
   - (Optional) Use `Masters > Imports` and upload sample Excel/CSV.
   - Create enquiry at `Enquiries > Create Enquiry` with at least one item.
   - Open enquiry detail and create quotation.
   - On quotation page:
     - Create revision
     - Submit revision
     - Approve revision
     - Create Customer PO and/or RTM PO
   - Open `Commercial`:
     - Create invoice
     - Add payment
     - Attempt overpayment (should show backend 400 message)
     - Create delivery and add delivery events
   - Open `Reports`:
     - Verify KPI cards load from `/reports/kpis`
     - Download `enquiries.xlsx`, `quotations.xlsx`, `invoices.xlsx`, `payments.xlsx`

## 5. Production-Like Container Build

Frontend image build (same image used by Compose):

```bash
docker compose build web
```

The `web` container serves Vite build output via Nginx with SPA fallback (`try_files ... /index.html`).

## 6. Render Deployment Notes

- API service: deploy backend Dockerfile on Render Web Service (free tier).
- Database: attach Render PostgreSQL (free tier if available in your account).
- Run migrations on deploy/release:

```bash
alembic -c alembic.ini upgrade head
```

- Frontend can be deployed as a second Render Web Service using `frontend/Dockerfile`.
- Set `VITE_API_URL` in frontend service to your Render API URL.
