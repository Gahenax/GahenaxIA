# Gahenax PC Optimization Script — KernelOS Pattern
# Hardware target: Intel i7-1065G7 / NVIDIA MX330 / 16GB / Kioxia NVMe SSD
# Run this script as Administrator (Right-click → Run with PowerShell as Admin)

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " GAHENAX PC OPTIMIZER - KernelOS" -ForegroundColor Cyan  
Write-Host "=====================================" -ForegroundColor Cyan

# ─── TWEAK 1: Win32PrioritySeparation ─────────────────────────────────────────
# Default Windows = 2 (broken) | Balanced compute = 38 | Gaming = 42
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\PriorityControl" `
    -Name "Win32PrioritySeparation" -Value 38
Write-Host "  [OK] Win32PrioritySeparation = 38 (balanced foreground boost)" -ForegroundColor Green

# ─── TWEAK 2: MMCSS — reduce CPU throttling durante compute ───────────────────
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" `
    -Name "SystemResponsiveness" -Value 10
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" `
    -Name "NetworkThrottlingIndex" -Value 4294967295
Write-Host "  [OK] MMCSS: SystemResponsiveness=10, NetworkThrottling=Disabled" -ForegroundColor Green

# ─── TWEAK 3: SysMain (Superfetch) — innecesario en NVMe ─────────────────────
Stop-Service -Name SysMain -Force -ErrorAction SilentlyContinue
Set-Service  -Name SysMain -StartupType Disabled
Write-Host "  [OK] SysMain (Superfetch) → Disabled [NVMe no lo necesita]" -ForegroundColor Green

# ─── TWEAK 4: DiagTrack — Telemetría Microsoft ────────────────────────────────
Stop-Service -Name DiagTrack -Force -ErrorAction SilentlyContinue  
Set-Service  -Name DiagTrack -StartupType Disabled
Write-Host "  [OK] DiagTrack (Telemetry) → Disabled" -ForegroundColor Green

# ─── TWEAK 5: WSearch — indexado innecesario en NVMe ─────────────────────────
Stop-Service -Name WSearch -Force -ErrorAction SilentlyContinue
Set-Service  -Name WSearch -StartupType Manual
Write-Host "  [OK] Windows Search → Manual (solo activo cuando buscas)" -ForegroundColor Green

# ─── TWEAK 6: BITS — background downloads interferencia ──────────────────────
Stop-Service -Name BITS -Force -ErrorAction SilentlyContinue
Set-Service  -Name BITS -StartupType Manual
Write-Host "  [OK] BITS → Manual" -ForegroundColor Green

# ─── TWEAK 7: GameDVR ─────────────────────────────────────────────────────────
$gdvr = "HKCU:\System\GameConfigStore"
if (-not (Test-Path $gdvr)) { New-Item -Path $gdvr -Force | Out-Null }
Set-ItemProperty -Path $gdvr -Name "GameDVR_Enabled" -Value 0
$gdvrPol = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\GameDVR"
if (-not (Test-Path $gdvrPol)) { New-Item -Path $gdvrPol -Force | Out-Null }
Set-ItemProperty -Path $gdvrPol -Name "AllowGameDVR" -Value 0
Write-Host "  [OK] GameDVR → Disabled" -ForegroundColor Green

# ─── TWEAK 8: MMCSS Games profile (específico para procesos de alta prioridad) ─
$gamesPath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games"
if (-not (Test-Path $gamesPath)) { New-Item -Path $gamesPath -Force | Out-Null }
Set-ItemProperty -Path $gamesPath -Name "GPU Priority"          -Value 8
Set-ItemProperty -Path $gamesPath -Name "Priority"              -Value 6
Set-ItemProperty -Path $gamesPath -Name "Scheduling Category"   -Value "High"
Set-ItemProperty -Path $gamesPath -Name "SFIO Priority"         -Value "High"
Write-Host "  [OK] MMCSS Games profile → GPU Priority=8, Priority=6, High" -ForegroundColor Green

# ─── TWEAK 9: NVIDIA MX330 — Power Management via registry ───────────────────
# Forzar modo de máxima performance (evita que el driver baje el clock en idle)
$nvReg = "HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0001"
if (Test-Path $nvReg) {
    Set-ItemProperty -Path $nvReg -Name "PerfLevelSrc" -Value 0x3322 -ErrorAction SilentlyContinue
    Write-Host "  [OK] NVIDIA MX330 PowerMizer → Prefer Maximum Performance" -ForegroundColor Green
} else {
    Write-Host "  [SKIP] NVIDIA registry path not at 0001, manual GPU config may be needed" -ForegroundColor Yellow
}

# ─── VERIFICACIÓN FINAL ───────────────────────────────────────────────────────
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " VERIFICACIÓN FINAL" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

$pri = (Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Control\PriorityControl").Win32PrioritySeparation
Write-Host "Win32PrioritySeparation: $pri" $(if($pri -eq 38){"✅"}else{"❌ (esperado 38)"})

$mm = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile"
Write-Host "MMCSS SystemResponsiveness: $($mm.SystemResponsiveness)" $(if($mm.SystemResponsiveness -eq 10){"✅"}else{"❌"})

@('SysMain','DiagTrack','WSearch','BITS') | ForEach-Object {
    $s = Get-Service $_ -ErrorAction SilentlyContinue
    if ($s) { Write-Host "$($s.Name): $($s.Status) [$($s.StartType)]" $(if($s.StartType -ne 'Automatic'){"✅"}else{"⚠️"}) }
}

Write-Host ""
Write-Host "Reinicia el PC para que todos los cambios de scheduler tengan efecto." -ForegroundColor Yellow
Write-Host "=====================================" -ForegroundColor Cyan
