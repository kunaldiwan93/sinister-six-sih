.PHONY: install seed dev-backend dev-frontend dev docker-up test lint

install:
	cd backend && python -m venv .venv && .venv/Scripts/pip install -r requirements.txt
	cd frontend && npm install

seed:
	cd backend && .venv/Scripts/python ../scripts/seed_demo.py

dev-backend:
	cd backend && .venv/Scripts/uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

dev:
	@echo "Run 'make dev-backend' in terminal 1 and 'make dev-frontend' in terminal 2"

docker-up:
	docker compose up --build

test:
	cd backend && .venv/Scripts/pytest
