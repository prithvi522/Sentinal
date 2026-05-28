Quick Run (local dev)

1) Create and activate Python venv, install backend deps:

```powershell
cd backend
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2) Install frontend deps and run dev server:

```powershell
cd frontend
npm install
# from repo root run both frontend and backend with helper script
cd ..
.\scripts\run_dev.ps1
```

Notes:
- The helper script defaults to a local SQLite DB so you don't need Postgres/Docker for development.
- The frontend talks to the backend through the Vite dev proxy at `/api/v1`, so the browser does not need to hit `http://localhost:8000` directly.
- Put real API keys in `backend/.env` or environment variables before running production features.
- To run only the backend:

```powershell
cd backend
. .\.venv\Scripts\Activate.ps1
$env:DATABASE_URL='sqlite:///./dev.db'
python -m uvicorn app.main:app --reload --port 8000
```
