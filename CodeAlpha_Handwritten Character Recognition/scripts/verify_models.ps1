$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$required = @(
  "models\checkpoints\mnist_digit.pt",
  "models\checkpoints\mnist_digit.json",
  "models\checkpoints\emnist_byclass.pt",
  "models\checkpoints\emnist_byclass.json",
  "models\reports\mnist_digit.metrics.json",
  "models\reports\emnist_byclass.metrics.json"
)
$missing = $required | Where-Object { -not (Test-Path $_) }
if ($missing.Count -gt 0) {
  Write-Host "Model verification failed. Missing:" -ForegroundColor Red
  $missing | ForEach-Object { Write-Host " - $_" }
  exit 1
}
Write-Host "MNIST and EMNIST application models are present." -ForegroundColor Green
