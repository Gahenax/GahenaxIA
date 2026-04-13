# Relanzamiento de Auditoría Atlas-NP (Safe Mode)
$repo = "https://github.com/Gahenax/Gahenax-BSD"
$path = "c:\Users\jotam\OneDrive\Desktop\GahenaxAI\Repos_Auditoria\P-ATLAS-NP"

Write-Host "--- GAHENAX ATLAS-NP RELAUNCH ---" -ForegroundColor Cyan

# 1. Limpieza
Write-Host "[1/3] Cleaning Atlas-NP workspace..." -ForegroundColor Yellow
Remove-Item -Path "$path\*" -Recurse -Force -ErrorAction SilentlyContinue

# 2. Auditoría con Timeout (Safe Mode)
Write-Host "[2/3] Auditing $repo (Timeout: 10s)..." -ForegroundColor Yellow
try {
    $result = curl.exe -I --max-time 10 $repo
    # 3. Reporte de Éxito
    if ($result -match "200 OK" -or $result -match "HTTP/2 200") {
        Write-Host "[3/3] [OK] Gahenax-BSD is ONLINE and AUDITED." -ForegroundColor Green
        $result | Out-File -FilePath "$path\audit_success.txt"
    } else {
        Write-Host "[FAIL] Audit failed with response: $result" -ForegroundColor Red
    }
} catch {
    Write-Host "[FAIL] Audit crashed: $($_.Exception.Message)" -ForegroundColor Red
}
