# Gahenax Spy v16.1 - Transcendent Orchestrator (Patched)
# Author: Antigravity AI
# Purpose: Master PowerShell Script for Global Environment Management.

Write-Host "Gahenax Spy System v16.1 - THE UNIFIED SHELL" -ForegroundColor Cyan
Write-Host "================================================="

# 1. Verificación de Entorno
Write-Host "Verificando dependencias..."
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python no encontrado en el PATH."
    exit
}

if (!(Test-Path "c:\Users\jotam\OneDrive\Desktop\GahenaxAI\gahenax_spy_system\config.py")) {
    Write-Error "Archivo config.py no encontrado."
    exit
}

# 2. Rutas del Sistema
$basePath = "c:\Users\jotam\OneDrive\Desktop\GahenaxAI\gahenax_spy_system"

# 3. Lanzamiento de la Triada de Inteligencia
Write-Host "Lanzando Capa de Telemetria (Receiver)..."
Start-Process python -ArgumentList "$basePath\utils\ghost_receiver.py" -WindowStyle Hidden

Write-Host "Lanzando Tactica Dashboard v16.1..."
Start-Process python -ArgumentList "$basePath\dashboard\app.py"

Write-Host "Lanzando Agente de Infiltracion Selenium..."
$isChromeDebug = Test-NetConnection -ComputerName 127.0.0.1 -Port 9222 -WarningAction SilentlyContinue
if ($isChromeDebug.TcpTestSucceeded) {
    Write-Host "🛰️ Sesion existente detectada. Acoplando en modo PASIVO (No-Login)..." -ForegroundColor Cyan
    Start-Process python -ArgumentList "$basePath\agents\selenium_spy.py --remote"
} else {
    Write-Host "🚀 No se detecta sesion. Lanzando nueva infiltracion (Modo Dinamico)..." -ForegroundColor Yellow
    Start-Process python -ArgumentList "$basePath\agents\selenium_spy.py --dynamic"
}

Write-Host "Activando RASTREADOR TEMPORAL v18.0..."
Start-Process python -ArgumentList "$basePath\analysis\temporal_spectral_tracker.py"

Write-Host "Activando ANALIZADOR GLM AVANZADO v20.0..."
Start-Process python -ArgumentList "$basePath\analysis\glm_advanced_analyzer.py"

Write-Host "Activando ASESOR TACTICO Riemann v17.0..." # No interactivo
Start-Process python -ArgumentList "$basePath\agents\advisor_agent.py"

Write-Host "SISTEMA TOTALMENTE OPERATIVO." -ForegroundColor Green
Write-Host "Accede al tablero: http://localhost:5000"
Write-Host "Presiona Ctrl+C para finalizar la orquestacion manual."

# 4. Monitor de Salud
while($true) {
    Start-Sleep -Seconds 10
}
