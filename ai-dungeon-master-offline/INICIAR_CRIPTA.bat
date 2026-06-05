@echo off
chcp 65001 >nul
title CRIPTA - Dungeon Master AI

echo.
echo  ========================================
echo   CRIPTA - Dungeon Master Virtual Offline
echo  ========================================
echo.

REM Verify Ollama is running
echo [1/3] Verificando Ollama...
ollama list >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Ollama no esta corriendo. Abrelo primero.
    pause
    exit /b 1
)

REM Show active models
echo  Modelos disponibles:
ollama list
echo.

REM Start Python sidecar in background
echo [2/3] Iniciando servidor backend (FastAPI)...
start "CRIPTA Backend" /min cmd /c "cd /d %~dp0app\sidecar\python && python main.py"

REM Wait for backend to be ready
timeout /t 3 /nobreak >nul
echo  Backend listo en http://127.0.0.1:8000
echo.

REM Start Tauri frontend
echo [3/3] Iniciando interfaz Tauri...
cd /d %~dp0app\frontend
start "CRIPTA Frontend" cmd /c "npx tauri dev"

echo.
echo  ========================================
echo   Todo listo. La ventana del juego abrira
echo   en unos segundos.
echo  ========================================
echo.
echo  Para cerrar: cierra las ventanas de
echo  "CRIPTA Backend" y "CRIPTA Frontend"
echo.
pause
