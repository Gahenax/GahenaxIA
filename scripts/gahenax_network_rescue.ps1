Write-Host "--- GAHENAX NETWORK RESCUE ---" -ForegroundColor Cyan

# 1. Matar procesos de Requestly y Curl
Write-Host "[1/3] Terminating Requestly and Curl processes..." -ForegroundColor Yellow
Get-Process -Name "Requestly", "curl" -ErrorAction SilentlyContinue | Stop-Process -Force

# 2. Desactivar Proxy en el Registro de Windows (Internet Settings)
Write-Host "[2/3] Disabling System Proxy via Registry..." -ForegroundColor Yellow
$regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings"
Set-ItemProperty -Path $regPath -Name "ProxyEnable" -Value 0
Set-ItemProperty -Path $regPath -Name "ProxyServer" -Value ""
Set-ItemProperty -Path $regPath -Name "ProxyOverride" -Value ""

# 3. Notificar al sistema del cambio
$proxyKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings'
$proxyStatus = (Get-ItemProperty -Path $proxyKey).ProxyEnable
if ($proxyStatus -eq 0) {
    Write-Host "[3/3] [OK] Proxy Disabled successfully." -ForegroundColor Green
} else {
    Write-Host "[FAIL] Could not disable proxy." -ForegroundColor Red
}

Write-Host "`n[ACTION] Please try opening a website now." -ForegroundColor Cyan
