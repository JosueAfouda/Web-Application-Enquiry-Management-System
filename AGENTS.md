# Repository Guidelines

## Project Structure & Module Organization
The backend lives under `backend/app` and is split by concern:
- `api/` FastAPI routers (`auth`, `masters`, `enquiries`, `quotations`, `commercial`, `reports`)
- `services/` business logic and workflow rules
- `models/` SQLAlchemy ORM entities
- `schemas/` Pydantic request/response contracts
- `db/migrations/versions/` Alembic migrations (ordered, immutable once merged)
- `core/` config, security, logging, error handling
- `utils/` shared helpers (Excel import/export)

Tests are in `backend/tests`. Operational scripts are in `scripts/`. Top-level runtime files include `docker-compose.yml`, `Makefile`, and `.env.example`.

## Build, Test, and Development Commands
Use the Make targets for consistency:
- `make up` / `make down`: start/stop API + PostgreSQL containers
- `make build`: rebuild images
- `make logs`: stream API logs
- `make smoke`: run local curl health smoke script
- `make lint`: run Ruff checks
- `make format`: run Ruff formatter
- `make typecheck`: run mypy on `backend/app`
- `make test`: run pytest (`PYTHONPATH=backend`)
- `make precommit`: run all configured hooks

Apply migrations after startup:
`docker compose exec -T api alembic -c alembic.ini upgrade head`

## Coding Style & Naming Conventions
Target Python 3.12, 4-space indentation, explicit type hints on new code.
Ruff rules and formatting are authoritative (`line-length = 100`).
Naming:
- modules/files: `snake_case.py`
- classes: `PascalCase`
- functions/variables: `snake_case`
- constants/enums: `UPPER_SNAKE_CASE`

## Testing Guidelines
Framework: `pytest` (+ `anyio/asyncio` plugins).  
Place tests in `backend/tests` and name files `test_*.py`.
Prefer focused unit tests for service rules plus API-level smoke tests for critical workflows.
Before opening a PR, run: `make lint && make typecheck && make test`.

## Commit & Pull Request Guidelines
History uses short imperative summaries (e.g., `Implement EMS phases 5-8...`, `Initial commit`).
Follow that pattern and keep commits scoped to one change set.

PRs should include:
- purpose and impacted modules
- migration notes (if any)
- validation evidence (`make` commands, curl smoke outputs, status codes)
- config/env changes and backward-compatibility notes

## Security & Configuration Tips
Never commit real secrets. Keep `.env` local and commit only `.env.example`.
Default local admin credentials are for development only; rotate outside local environments.
