# EMS Frontend (React + TypeScript)

UI for the Enquiry Management System (EMS) MVP.

## Stack
- React 19 + TypeScript + Vite
- Tailwind CSS
- React Router
- TanStack Query
- React Hook Form + Zod
- Axios API client with backend error normalization

## Run in Dev Mode

```bash
npm install
npm run dev
```

Default API target is `http://localhost:8000`.
Override with:

```bash
VITE_API_URL=http://localhost:8000 npm run dev
```

## Build + Lint

```bash
npm run lint
npm run build
```

## Docker (Production-like)

This folder includes a multi-stage Dockerfile:
- Build stage: Node 20
- Runtime stage: Nginx (serves static Vite build)

Nginx config supports SPA routing using `try_files ... /index.html`.

In root project directory:

```bash
docker compose up -d --build
```

Frontend will be available at `http://localhost:3000`.
