# Limpieza Final tras la Crisis de Requestly
$basePath = "C:\Users\jotam\OneDrive\Desktop\GahenaxAI"
$archivePath = "$basePath\research\archived_requestly"

Write-Host "--- GAHENAX HOUSEKEEPING ---" -ForegroundColor Cyan

# 1. Crear carpeta de archivo si no existe
if (!(Test-Path $archivePath)) { 
    Write-Host "[1/2] Creating archive directory: $archivePath" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $archivePath -Force
}

# 2. Mover archivos de Requestly y experimentos fallidos del casino al archivo
Write-Host "[2/2] Archiving Requestly rules and failed experiments..." -ForegroundColor Yellow
Get-ChildItem -Path $basePath -Filter "gahenax_stealth_*.json" | Move-Item -Destination $archivePath -ErrorAction SilentlyContinue
Get-ChildItem -Path "$basePath\gahenax_spy_system\analysis" -Filter "gahenax_yang_mills_v*.js" | Move-Item -Destination $archivePath -ErrorAction SilentlyContinue

Write-Host "[OK] Housekeeping completado. Sistema en Zero-Debt." -ForegroundColor Green
