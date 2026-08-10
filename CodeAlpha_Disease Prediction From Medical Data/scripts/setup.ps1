$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

Write-Host "[1/6] Creating Python 3.14 virtual environment..." -ForegroundColor Cyan
Set-Location $Root
if (Test-Path "$Root\.venv") { Remove-Item -Recurse -Force "$Root\.venv" }
py -3.14 -m venv .venv

Write-Host "[2/6] Installing backend dependencies..." -ForegroundColor Cyan
& "$Root\.venv\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel
& "$Root\.venv\Scripts\python.exe" -m pip install --only-binary=:all: -r "$Root\backend\requirements.txt"
& "$Root\.venv\Scripts\python.exe" -m pip check

Write-Host "[3/6] Preparing environment files..." -ForegroundColor Cyan
if (-not (Test-Path "$Root\backend\.env")) { Copy-Item "$Root\backend\.env.example" "$Root\backend\.env" }
if (-not (Test-Path "$Root\frontend\.env")) { Copy-Item "$Root\frontend\.env.example" "$Root\frontend\.env" }

Write-Host "[4/6] Rebuilding dataset and training HeartTrack models..." -ForegroundColor Cyan
Set-Location "$Root\backend"
& "$Root\.venv\Scripts\python.exe" -m ml.data
& "$Root\.venv\Scripts\python.exe" -m ml.train --mode full

Write-Host "[5/6] Installing frontend dependencies..." -ForegroundColor Cyan
Set-Location "$Root\frontend"
npm install

Write-Host "[6/6] Running backend tests and frontend build..." -ForegroundColor Cyan
Set-Location "$Root\backend"
& "$Root\.venv\Scripts\python.exe" -m pytest -q
Set-Location "$Root\frontend"
npm run build

Write-Host "HeartTrack setup complete." -ForegroundColor Green
Write-Host "Run .\scripts\run-all.ps1 to start both services." -ForegroundColor Green
