$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "$PSScriptRoot\run-backend.ps1"
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "$PSScriptRoot\run-frontend.ps1"
Write-Host "HeartTrack backend and frontend launchers started." -ForegroundColor Green
Write-Host "Frontend: http://localhost:5173"
Write-Host "API docs:  http://localhost:8000/docs"
