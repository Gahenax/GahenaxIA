# stop_bridge.ps1 — Detiene el bridge
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PidFile = Join-Path $ScriptDir "bridge.pid"

if (-not (Test-Path $PidFile)) {
    Write-Host "[BRIDGE] No hay bridge corriendo." -ForegroundColor Yellow
    exit
}

$OldPid = Get-Content $PidFile
try {
    Stop-Process -Id $OldPid -Force
    Remove-Item $PidFile
    Write-Host "[BRIDGE] Detenido (PID $OldPid)" -ForegroundColor Red
} catch {
    Write-Host "[BRIDGE] No se pudo detener (PID $OldPid): $_" -ForegroundColor Red
}
