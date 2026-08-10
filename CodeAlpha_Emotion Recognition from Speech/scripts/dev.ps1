$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot "backend\.venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    throw "Python environment not found. Run: py -3.14 -m venv backend\.venv"
}

$backend = Start-Process -PassThru -NoNewWindow -FilePath $python -ArgumentList "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000" -WorkingDirectory (Join-Path $projectRoot "backend")
$frontend = Start-Process -PassThru -NoNewWindow -FilePath "npm.cmd" -ArgumentList "run", "dev" -WorkingDirectory (Join-Path $projectRoot "frontend")

try {
    Wait-Process -Id $backend.Id, $frontend.Id
}
finally {
    Stop-Process -Id $backend.Id, $frontend.Id -ErrorAction SilentlyContinue
}
