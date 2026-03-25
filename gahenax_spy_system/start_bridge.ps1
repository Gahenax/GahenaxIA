# start_bridge.ps1 — Lanza el bridge en segundo plano (sin ventana CMD)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BridgeScript = Join-Path $ScriptDir "backend\main.py"
$PidFile = Join-Path $ScriptDir "bridge.pid"

# Verificar si ya está corriendo
if (Test-Path $PidFile) {
    $OldPid = Get-Content $PidFile
    $proc = Get-Process -Id $OldPid -ErrorAction SilentlyContinue
    if ($proc) {
        Write-Host "[BRIDGE] Ya está corriendo (PID $OldPid)" -ForegroundColor Green
        exit
    }
}

# Lanzar en segundo plano sin ventana
$proc = Start-Process python `
    -ArgumentList $BridgeScript `
    -WindowStyle Hidden `
    -PassThru

$proc.Id | Out-File $PidFile -Encoding ascii
Write-Host "[BRIDGE] Iniciado en segundo plano (PID $($proc.Id))" -ForegroundColor Green
Write-Host "[BRIDGE] Endpoint: http://localhost:8080/heartbeat" -ForegroundColor Cyan
