$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$problems = New-Object System.Collections.Generic.List[string]

if (-not (Test-Path ".env.example")) { $problems.Add("Missing .env.example") }
if (-not (Test-Path "models\registry.json")) { $problems.Add("Missing model registry") }
if (Test-Path ".env") { Write-Host "Local .env exists (correct for local development; it is gitignored)." -ForegroundColor Yellow }

$patterns = @(
  "localStorage\s*\.\s*(setItem|getItem|removeItem|clear)\s*\(",
  "sessionStorage\s*\.\s*(setItem|getItem|removeItem|clear)\s*\(",
  "indexedDB\s*\.\s*(open|deleteDatabase)\s*\("
)
foreach ($pattern in $patterns) {
  $hits = Get-ChildItem frontend\src -Recurse -File | Select-String -Pattern $pattern -CaseSensitive:$false
  foreach ($hit in $hits) { $problems.Add("Browser persistence API use: $($hit.Path):$($hit.LineNumber)") }
}

python -m compileall -q backend\app ml
if ($LASTEXITCODE -ne 0) { $problems.Add("Python source compilation failed") }

if ($problems.Count -gt 0) {
  Write-Host "Preflight failed:" -ForegroundColor Red
  $problems | ForEach-Object { Write-Host " - $_" }
  exit 1
}
Write-Host "WriteLens preflight passed." -ForegroundColor Green
