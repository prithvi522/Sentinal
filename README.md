# SentinelAI OS

SentinelAI OS is a production-grade AI Cybersecurity Operating System with a modern full-stack architecture.

## Stack

- Frontend: React + Vite + TailwindCSS + Framer Motion
- Backend: FastAPI (Python)
- Database: PostgreSQL
- Real-time: WebSockets
- AI Layer: OpenAI/Gemini compatible abstraction with optional LangChain orchestration
- Packaging: Docker + Docker Compose

## Core Modules

- AI Vulnerability Intelligence Engine: SQL injection, XSS, hardcoded secrets, unsafe APIs, weak auth, dependency vulnerability detection, and secure fix suggestions.
- Prompt Firewall Assistant: prompt injection, jailbreak, sensitive data leakage detection, and prompt trust scoring.
- Threat Hunter Assistant: suspicious login analysis, brute-force detection, proxy/VPN/Tor heuristics, ASN-aware reputation enrichment, and unusual traffic detection.
- Threat Intelligence Integration: VirusTotal, ThreatFox, AbuseIPDB, and Shodan-enriched IP/domain lookups.
- Incident Response Assistant: AI attack summaries, containment/recovery guidance, and downloadable incident reports.
- AI Security Copilot: conversational cybersecurity operations guidance with provider selection.
- Real-time Dashboard: live threat alerts, attack graphs, risk heatmaps, severity charts, active scan status, and AI recommendations.
- PDF Security Reports: downloadable vulnerability and incident response reports.
- Demo Simulations: synthetic attacks generated continuously and by manual assistant actions.

## Project Structure

```text
backend/
  app/
    api/v1/endpoints/
    core/
    db/
    models/
    schemas/
    services/
    utils/
    main.py
  seed/seed_data.py
  requirements.txt
  Dockerfile
frontend/
  src/
    components/
    context/
    lib/
    pages/
    styles/
  package.json
  Dockerfile
docker-compose.yml
```

## GitHub-Ready Repository Layout

- Root keeps shared orchestration and docs: `docker-compose.yml`, `README.md`, `README_RUN.md`, `.env.example`, and CI/helper scripts.
- `backend/` contains only API/runtime code plus backend-specific tooling.
- `frontend/` contains only web app code plus frontend-specific tooling.
- Secrets and local runtime artifacts are excluded through `.gitignore`.
- Docker build contexts are optimized with `backend/.dockerignore` and `frontend/.dockerignore`.

## Environment Layout

- Backend runtime config lives in [backend/.env.example](backend/.env.example) and is loaded from `backend/.env` by [backend/app/core/config.py](backend/app/core/config.py).
- Frontend runtime config lives in [frontend/.env.example](frontend/.env.example) and is loaded from `frontend/.env` by Vite.
- The root [.env.example](.env.example) is a convenience map that shows which variables belong to each side.
- Keep real secrets out of Git; commit only the example files.

### First Push Checklist

```bash
git add .
git status
git commit -m "Initial project structure"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

## Local Run (Without Docker)

### 1. Backend

```bash
cd backend
cp .env.example .env
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

The frontend dev launcher also starts the backend automatically on port 8000, so this is the quickest way to run the app locally during development.

### 3. Seed demo data

```bash
cd backend
python -m seed.seed_data
```

### 4. One-command local run on Windows

From `frontend/`, run:

```powershell
npm run dev
```

The frontend launcher starts the backend, defaults to local SQLite for development, and uses the Vite proxy so you do not need PostgreSQL or Docker to get started.

## Docker Run

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

The frontend uses same-origin `/api/v1` requests and Vite proxies them to the backend during local development.

## Auth

- Register: `POST /api/v1/auth/register`
- Login: `POST /api/v1/auth/login`
- JWT Bearer required for secured endpoints.

Seeded default admin user after running seed script:

- Email: admin@sentinel.example.com
- Password: controlled via `SEED_ADMIN_PASSWORD` (defaults to `Admin@12345`)

## Real-time Alerts

WebSocket endpoint:

- `/api/v1/ws/alerts` during local development, proxied to the backend by Vite

## Production Notes

- Replace all secrets in `.env` before deployment.
- Configure TLS, secure reverse proxy, and WAF in production.
- Integrate SIEM/log pipeline for persistent telemetry.
- Use managed secrets vault and rotate credentials regularly.

## AI Keys

- Use `CHATGPT_API_KEY` for the ChatGPT/OpenAI provider.
- `OPENAI_API_KEY` is still accepted for backward compatibility.
- Use `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT`, and `AZURE_OPENAI_API_VERSION` for Azure OpenAI deployments. Azure AI Foundry `/openai/v1` endpoints are also supported; set `AZURE_OPENAI_ENDPOINT` to the full `/openai/v1` base URL and `AZURE_OPENAI_DEPLOYMENT` to the model/deployment name shown in Foundry.
- `GEMINI_API_KEY` continues to power the Gemini provider.
- Optional threat-intelligence providers: `VIRUSTOTAL_API_KEY`, `THREATFOX_API_KEY`, `ABUSEIPDB_API_KEY`, and `SHODAN_API_KEY`.
- Rate limiting can be tuned with `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_WINDOW_SECONDS`.
- Max upload size for scans: set `MAX_UPLOAD_SIZE_BYTES` in `backend/.env`. Set to `0` to disable the limit (be careful — disabling size limits may use large amounts of memory and CPU when scanning big files).
- Optional AI orchestration packages can be added later if you want LangChain-backed flows.

## Offline AI Mode

SentinelAI OS now supports optional local-only AI summaries through Ollama. If you have Ollama installed locally, run:

```bash
ollama run llama3
```

Then set the backend environment variables:

```bash
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3
```

If Ollama is unavailable, the phishing, log, and malware analyzers automatically fall back to rule-based summaries.

## New Demo Modules

- `GET /api/v1/simulate-attack` - synthetic attack simulator with websocket broadcast.
- `POST /api/v1/phishing-detector/analyze` - local phishing detector.
- `POST /api/v1/log-analyzer/analyze` - log analyzer for brute force and repeated failures.
- `POST /api/v1/malware-analyzer/analyze` - static malware behavior analyzer.
- `Threat Heatmap`, `AI Phishing Detector`, `AI Log Analyzer`, and `Malware Behavior Analyzer` are available in the frontend navigation.

The dashboard also now includes additional security-health widgets for firewall status, AI threat level, system integrity, active threats, critical alerts, and vulnerabilities detected.
