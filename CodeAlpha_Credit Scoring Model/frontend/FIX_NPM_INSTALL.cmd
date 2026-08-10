@echo off
cd /d "%~dp0"
npm config delete proxy
npm config delete https-proxy
npm config set registry https://registry.npmjs.org/
if exist node_modules rmdir /s /q node_modules
if exist package-lock.json del /f package-lock.json
npm cache verify
npm install --no-audit --no-fund
npm run dev
