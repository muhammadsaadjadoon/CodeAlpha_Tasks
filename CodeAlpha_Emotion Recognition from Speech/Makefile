setup:
	python -m venv backend/.venv
	backend/.venv/bin/pip install -r backend/requirements.txt
	cd frontend && npm install

db:
	docker compose up -d db

migrate:
	cd backend && .venv/bin/alembic upgrade head

backend:
	cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

test:
	cd backend && .venv/bin/pytest -q
