@echo off
echo Iniciando servidores de desarrollo para Cripta...

:: Set Cargo SSL Bypass Environment Variables
set CARGO_HTTP_CHECK_REVOKE=false
set CARGO_HTTP_SSL_VERIFY=false

:: Start FastAPI backend in a new command window
start "Cripta - Backend Sidecar" cmd /k "cd app\sidecar\python && python main.py"

:: Start Tauri app in the current window
echo Iniciando Tauri Frontend...
cd app\frontend
npx tauri dev
