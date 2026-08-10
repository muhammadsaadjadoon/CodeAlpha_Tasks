$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$problems = New-Object System.Collections.Generic.List[string]
$skipParts = @(".git", "node_modules", ".venv", "__pycache__", ".pytest_cache", "dist")

function Should-Skip([string]$Path) {
  foreach ($part in $skipParts) {
    if ($Path -match [regex]::Escape([IO.Path]::DirectorySeparatorChar + $part + [IO.Path]::DirectorySeparatorChar)) {
      return $true
    }
  }
  return $false
}

$forbiddenNames = @(".env", "inflect.db", "app.db")

Get-ChildItem -Path $Root -File -Recurse -Force | ForEach-Object {
  $relative = $_.FullName.Substring($Root.Length).TrimStart('\')

  if (Should-Skip $_.FullName) {
    return
  }

  if ($forbiddenNames -contains $_.Name) {
    $problems.Add("Forbidden runtime file: $relative")
  }

  if ($_.Extension -in @(".db", ".sqlite", ".sqlite3", ".pyc", ".pyo")) {
    $problems.Add("Forbidden generated file: $relative")
  }

  if ($_.Length -gt 95MB) {
    $problems.Add("File exceeds 95 MB preflight limit: $relative")
  }

  if ($relative -like "data\raw\*" -and $_.Name -ne ".gitkeep") {
    $problems.Add("Raw dataset file must not be committed: $relative")
  }

  if ($relative -match "(^|\\)(node_modules|\.venv|__pycache__|\.pytest_cache)(\\|$)") {
    $problems.Add("Dependency/cache folder content found: $relative")
  }
}

$frontendSource = Join-Path $Root "frontend\src"
if (Test-Path $frontendSource) {
  $storagePatterns = @(
    "(window\.|globalThis\.)?localStorage\s*\.\s*(setItem|getItem|removeItem|clear|key)\s*\(",
    "(window\.|globalThis\.)?sessionStorage\s*\.\s*(setItem|getItem|removeItem|clear|key)\s*\(",
    "(window\.|globalThis\.)?indexedDB\s*\.\s*(open|deleteDatabase|cmp|databases)\s*\("
  )

  foreach ($pattern in $storagePatterns) {
    $storageHits = Get-ChildItem $frontendSource -File -Recurse |
      Select-String -Pattern $pattern -CaseSensitive:$false

    foreach ($hit in $storageHits) {
      $relative = $hit.Path.Substring($Root.Length).TrimStart('\')
      $problems.Add("Browser persistence API use: $relative:$($hit.LineNumber)")
    }
  }
}

if ($problems.Count -gt 0) {
  Write-Host "Repository preflight failed:" -ForegroundColor Red
  $problems | Sort-Object -Unique | ForEach-Object { Write-Host " - $_" }
  exit 1
}

Write-Host "Repository preflight passed." -ForegroundColor Green
