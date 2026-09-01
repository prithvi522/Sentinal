# Quick start

From the repository root in PowerShell:

```powershell
python -m venv backend\.venv
.\backend\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backend\requirements.txt

cd frontend
npm install
npm run dev
```

Then open http://localhost:5173.

`npm run dev` starts FastAPI on port `8000` and Vite on port `5173`. Press `Ctrl+C` to stop the local stack.

If PowerShell blocks virtual-environment activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` once in that terminal and retry.

Optional AI and threat-intelligence keys belong in `backend/.env`. Start from `backend/.env.example`; never commit the resulting `.env` file.
