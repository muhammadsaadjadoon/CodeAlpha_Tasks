param(
  [Parameter(Mandatory = $true)]
  [string]$RepositoryUrl
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  throw "Git is not installed or is not available in PATH."
}

& (Join-Path $PSScriptRoot "preflight_repo.ps1")

if (-not (Test-Path ".git")) {
  git init
}

git branch -M main
git add .

$hasHead = $true
git rev-parse --verify HEAD *> $null
if ($LASTEXITCODE -ne 0) {
  $hasHead = $false
}

if ($hasHead) {
  git diff --cached --quiet
  if ($LASTEXITCODE -ne 0) {
    git commit -m "Prepare INFLECT repository"
  }
}
else {
  git commit -m "Initial commit: INFLECT"
}

git remote get-url origin *> $null
if ($LASTEXITCODE -eq 0) {
  git remote set-url origin $RepositoryUrl
}
else {
  git remote add origin $RepositoryUrl
}

git push -u origin main
