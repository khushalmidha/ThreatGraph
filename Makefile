.PHONY: up down logs test lint migrate

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

test:
	pytest backend/tests/

lint:
	flake8 backend/
	black --check backend/

migrate:
	cd backend && alembic upgrade head
