SHELL := /bin/bash

.PHONY: up down build logs test lint format typecheck precommit smoke

up:
	docker compose up -d --build

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f api

test:
	PYTHONPATH=backend pytest -q

lint:
	ruff check backend

format:
	ruff format backend

typecheck:
	mypy backend/app

precommit:
	pre-commit run --all-files

smoke:
	bash scripts/smoke_local.sh
