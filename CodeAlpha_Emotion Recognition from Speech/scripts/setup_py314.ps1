$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
}

py -3.14 -m venv backend\.venv
& backend\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
& backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt

Push-Location backend
try {
    & .\.venv\Scripts\python.exe -m alembic upgrade head
}
finally {
    Pop-Location
}

Push-Location frontend
try {
    npm install
}
finally {
    Pop-Location
}

Write-Host "INFLECT setup complete. Start it with:" -ForegroundColor Green
Write-Host "powershell -ExecutionPolicy Bypass -File scripts\dev.ps1"
