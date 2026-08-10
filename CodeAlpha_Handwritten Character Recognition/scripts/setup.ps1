$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env" }
if (-not (Test-Path "backend\.venv")) { py -3.14 -m venv backend\.venv }
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& ".\backend\.venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r backend\requirements.txt
python -m pip install -r ml\requirements-train.txt
python -m alembic -c backend\alembic.ini upgrade head
Push-Location frontend
npm install
Pop-Location
Write-Host "WriteLens setup complete." -ForegroundColor Green
