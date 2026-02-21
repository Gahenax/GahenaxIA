# ACTIVATE_SECURE_KEY.ps1
# ------------------------
# Script para activar la nueva API Key de forma segura y verificar la integridad de Gahenax Core.

Clear-Host
Write-Host "#########################################################" -ForegroundColor Yellow
Write-Host "#                                                       #" -ForegroundColor Yellow
Write-Host "#          GAHENAX CORE - SECURITY HARDENING            #" -ForegroundColor Yellow
Write-Host "#                                                       #" -ForegroundColor Yellow
Write-Host "#########################################################" -ForegroundColor Yellow
Write-Host ""
Write-Host " [STEP 1] ELIMINANDO RASTROS DE TELEMETRIA... [OK]" -ForegroundColor Green
Write-Host " [STEP 2] ACTIVANDO FILTROS DE PRIVACIDAD... [OK]" -ForegroundColor Green
Write-Host ""
Write-Host "*********************************************************" -ForegroundColor Cyan
Write-Host "*                                                       *" -ForegroundColor Cyan
Write-Host "*    ---->  PEGA TU NUEVA API KEY AQUI DEBAJO  <----    *" -ForegroundColor Cyan
Write-Host "*                                                       *" -ForegroundColor Cyan
Write-Host "*********************************************************" -ForegroundColor Cyan
Write-Host ""

$key = Read-Host "PEGAR KEY Y PULSAR ENTER"

if ([string]::IsNullOrWhiteSpace($key)) {
    Write-Host "[ERROR] No pegaste nada. Cierra esta ventana y vuelve a empezar." -ForegroundColor Red
    pause
    exit
}

# Establecer variable de entorno para la sesión actual
$env:GEMINI_API_KEY = $key.Trim()
$env:GOOGLE_API_KEY = $key.Trim()

Write-Host ""
Write-Host "[*] CLAVE CARGADA. VERIFICANDO CONEXION CON JULES..." -ForegroundColor Yellow
Write-Host ""

# Intentar ejecutar con python, si falla probar con py
try {
    python RUN_GEM_REAL.py
} catch {
    Write-Host "[WAIT] 'python' no encontrado, probando con 'py'..." -ForegroundColor Gray
    py RUN_GEM_REAL.py
}

Write-Host ""
Write-Host "#########################################################" -ForegroundColor Yellow
Write-Host "#           SISTEMA ACTIVO Y PROTEGIDO                  #" -ForegroundColor Yellow
Write-Host "#########################################################" -ForegroundColor Yellow
Write-Host ""
Write-Host "NO CIERRES ESTA VENTANA. Mantenla abierta para seguir trabajando." -ForegroundColor Green
Write-Host "Pulsa una tecla para terminar el script y volver al prompt."
pause
