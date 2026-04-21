# Vocab Backend

FastAPI backend for the personal vocabulary app.

## Setup

Create `backend/.env` from `backend/.env.example` and replace the database password:

```env
APP_ENV=development
DATABASE_URL=postgresql://DB_USER:DB_PASSWORD@DB_HOST:5432/DB_NAME
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Install dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
```

Run the API:

```powershell
.\.venv\Scripts\python -m uvicorn app.main:app --reload
```

Health checks:

- `GET /health`
- `GET /health/db`
