$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Test-Path "backend\.venv\Scripts\python.exe")) { throw "Run scripts\setup.ps1 first." }
if (-not (Test-Path "frontend\node_modules")) { throw "Run npm install in frontend or scripts\setup.ps1 first." }

$backend = Start-Process powershell -PassThru -ArgumentList @(
  "-NoExit", "-ExecutionPolicy", "Bypass", "-Command",
  "Set-Location '$Root'; & '.\backend\.venv\Scripts\Activate.ps1'; python -m uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000"
)
$frontend = Start-Process powershell -PassThru -ArgumentList @(
  "-NoExit", "-ExecutionPolicy", "Bypass", "-Command",
  "Set-Location '$Root\frontend'; npm run dev"
)
Write-Host "Backend window PID: $($backend.Id)" -ForegroundColor Cyan
Write-Host "Frontend window PID: $($frontend.Id)" -ForegroundColor Cyan
Write-Host "Open http://localhost:5173" -ForegroundColor Green
