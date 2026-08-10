$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
& ".\backend\.venv\Scripts\Activate.ps1"
python ml\scripts\download_datasets.py --datasets mnist emnist-balanced emnist-byclass
python ml\scripts\train_all.py --batch-size 256
Write-Host "Training complete. Start WriteLens and open Model Lab." -ForegroundColor Green
