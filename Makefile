.PHONY: help install backend frontend test demo up down clean

help:
	@echo "EntraFlow – verfügbare Ziele:"
	@echo "  make install    Backend-Abhängigkeiten in ein venv installieren"
	@echo "  make backend    FastAPI-Backend starten (http://localhost:8000)"
	@echo "  make frontend   Next.js-Frontend starten (http://localhost:3000)"
	@echo "  make test       Backend-Testsuite ausführen"
	@echo "  make demo       Plan bauen + anwenden + Berichte auf der Konsole zeigen"
	@echo "  make up/down    Gesamtstack via docker compose starten/stoppen"

install:
	cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

backend:
	cd backend && . .venv/bin/activate && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

test:
	cd backend && . .venv/bin/activate && python -m pytest

demo:
	cd backend && . .venv/bin/activate && python -m app.demo

up:
	docker compose up --build

down:
	docker compose down

clean:
	rm -rf backend/.venv backend/.pytest_cache frontend/node_modules frontend/.next
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
