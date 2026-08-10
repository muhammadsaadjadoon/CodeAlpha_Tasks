# HeartTrack Quick Start

## First-time setup

From the repository root in PowerShell:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install --only-binary=:all: -r backend\requirements.txt
Copy-Item backend\.env.example backend\.env
Copy-Item frontend\.env.example frontend\.env
cd frontend
npm install
cd ..
```

## Start the backend

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Start the frontend

Open another terminal:

```powershell
cd frontend
npm run dev
```

Open `http://localhost:5173`.

Included account:

```text
Email: demo@hearttrack.ai
Password: HeartTrack@2026
```

## Optional: retrain the models

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -m ml.data
python -m ml.train --mode full
python -m ml.evaluate
```
