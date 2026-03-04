# Repository Guidelines

## Project Structure & Module Organization
- `backend/`: FastAPI app, domain services, SQLAlchemy models, Alembic migrations, and API routers.
- `backend/app/api/`: route modules (`auth`, `masters`, `enquiries`, `quotations`, `commercial`, `reports`).
- `backend/app/services/`: business logic; keep route handlers thin and orchestration here.
- `backend/app/db/migrations/`: Alembic migration scripts (`versions/*.py`).
- `backend/tests/`: backend tests (`test_*.py`).
- `frontend/`: React + TypeScript + Vite UI.
- `frontend/src/pages/`: screen-level pages (use `*Page.tsx` naming).
- `frontend/src/components/`: reusable UI/layout components.
- `scripts/`: smoke checks for local API/frontend validation.

## Build, Test, and Development Commands
- `make up`: build and run `db`, `api`, and `web` via Docker Compose.
- `make down`: stop/remove local containers.
- `make test`: run backend pytest suite (`PYTHONPATH=backend pytest -q`).
- `make lint`: run Ruff linting on backend.
- `make format`: apply Ruff formatting on backend.
- `make typecheck`: run mypy on backend app.
- `make smoke`: run end-to-end curl smoke checks (`scripts/smoke_local.sh`).
- Frontend local loop:
```bash
cd frontend
npm run dev
npm run lint
npm run build
```

## Coding Style & Naming Conventions
- Python: 4-space indentation, type hints required, keep service methods cohesive and explicit.
- Use Ruff + mypy as the enforcement baseline; avoid bypassing failures in normal workflow.
- TypeScript: `strict` mode is enabled; no implicit `any`; prefer typed API contracts in `frontend/src/types/api.ts`.
- Python files/modules use `snake_case`.
- React components/pages use `PascalCase` (`DashboardPage.tsx`, `AppShell.tsx`).
- Commit messages follow Conventional Commit style seen in history (`feat:`, `fix:`, `chore:`, optionally scoped like `feat(frontend): ...`).

## Testing Guidelines
- Backend tests use `pytest`; place tests under `backend/tests/test_<feature>.py`.
- Add/adjust tests when changing workflow rules, status transitions, calculations, or error handling.
- Run before PR: `make lint && make typecheck && make test && make smoke`.
- Frontend currently relies on lint/build + manual workflow checks from `FRONTEND_USER_GUIDE.md`.

## Commit & Pull Request Guidelines
- Keep commits focused by feature or fix; avoid mixing refactors with behavior changes.
- PRs should include a concise summary of changed behavior.
- PRs should list impacted modules/files.
- PRs should call out migration/config impacts (`render.yaml`, env vars, Alembic).
- PRs should include validation evidence (command outputs or screenshots for UI changes).
- PRs should reference the linked issue/task when available.

## Security & Configuration Tips
- Never commit secrets; use `.env` locally and Render env vars in production.
- Default demo credentials (`admin/admin`) are for non-production only; rotate immediately outside local/dev.
