# Gahenax Stealth Spy Launcher v1.0
# Lanzador silencioso en segundo plano

$basePath = "c:\Users\jotam\OneDrive\Desktop\GahenaxAI\gahenax_spy_system"
Write-Host "🚀 Iniciando Gahenax Spy en modo STEALTH..." -ForegroundColor Cyan

# 1. Dashboard en Segundo Plano (Puerto 5000)
Write-Host "Iniciando Dashboard..."
Start-Process python -ArgumentList "$basePath\dashboard\app.py" -WindowStyle Hidden

# 2. Esperar a que el puerto esté listo
Start-Sleep -Seconds 2

# 3. Agente de Telemetría en Segundo Plano
# Usamos aviator_spy.py --cdp si Chrome está abierto, si no selenium_spy.py
$isChromeDebug = Test-NetConnection -ComputerName 127.0.0.1 -Port 9222 -WarningAction SilentlyContinue 
if ($isChromeDebug.TcpTestSucceeded) {
    Write-Host "✅ Chrome detectado. Iniciando captura de WebSocket..."
    Start-Process python -ArgumentList "$basePath\utils\aviator_spy.py --cdp" -WindowStyle Hidden
} else {
    Write-Host "⚠️ Chrome no detectado en 9222. Iniciando Sniffer DOM..."
    Start-Process python -ArgumentList "$basePath\agents\selenium_spy.py" -WindowStyle Hidden
}

Write-Host "✅ Gahenax Spy activo en segundo plano." -ForegroundColor Green
Write-Host "Los logs se están guardando en: gahenax_spy_system/utils/aviator_telemetry.jsonl"
Write-Host "Usa 'Stop-Process -Name python' para detener todo."
