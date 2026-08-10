Set-Location $PSScriptRoot
npm config delete proxy
npm config delete https-proxy
npm config set registry https://registry.npmjs.org/
if (Test-Path .\node_modules) { Remove-Item -Recurse -Force .\node_modules }
if (Test-Path .\package-lock.json) { Remove-Item -Force .\package-lock.json }
npm cache verify
npm install --no-audit --no-fund
npm run dev
