# ═══════════════════════════════════════════════════════════════
# Gahenax Infrastructure — Deploy Script (PowerShell para Windows)
# Traducción exacta de deploy.sh → deploy.ps1
#
# Uso:
#   .\deploy.ps1 -Wave 1
#   .\deploy.ps1 -Wave all
#   .\deploy.ps1 -Check
#   .\deploy.ps1 -Down
#   .\deploy.ps1 -Jules
# ═══════════════════════════════════════════════════════════════

param(
    [string]$Wave   = "",
    [switch]$Check  = $false,
    [switch]$Down   = $false,
    [switch]$Jules  = $false,
    [switch]$Help   = $false
)

$ErrorActionPreference = "Stop"

# ── Paths ─────────────────────────────────────────────────────
$ScriptDir    = Split-Path -Parent $MyInvocation.MyCommand.Path
$ComposeFile  = Join-Path $ScriptDir "docker-compose.yml"
$EnvFile      = Join-Path $ScriptDir ".env"

# Modelos Ollama a descargar en Wave 3
$OllamaModels = @("llama3.2:3b", "nomic-embed-text")

# ── Colores (equivalente a echo -e con colores ANSI) ──────────
function log  { param($msg) Write-Host "[GAHENAX] $msg" -ForegroundColor Cyan }
function ok   { param($msg) Write-Host "[OK] $msg"      -ForegroundColor Green }
function warn { param($msg) Write-Host "[WARN] $msg"    -ForegroundColor Yellow }
function err  {
    param($msg)
    Write-Host "[ERROR] $msg" -ForegroundColor Red
    exit 1
}

# ── Preflight checks ─────────────────────────────────────────
function Check-Requirements {
    log "Verificando requisitos..."

    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        err "Docker no encontrado. Instala Docker Desktop para Windows."
    }

    docker compose version | Out-Null
    if ($LASTEXITCODE -ne 0) {
        err "Docker Compose v2 no encontrado. Actualiza Docker Desktop."
    }

    if (-not (Test-Path $EnvFile)) {
        err ".env no encontrado. Ejecuta: Copy-Item .env.example .env"
    }

    # Verificar que no queden valores sin reemplazar
    $envContent = Get-Content $EnvFile -Raw
    if ($envContent -match "CAMBIA_ESTO") {
        err "Hay valores 'CAMBIA_ESTO' sin reemplazar en .env. Configura todos los secrets."
    }

    ok "Todos los requisitos cumplidos."
}

# ── Leer valor del .env ───────────────────────────────────────
function Get-EnvValue {
    param([string]$Key)
    $line = Get-Content $EnvFile | Where-Object { $_ -match "^$Key=" } | Select-Object -First 1
    if ($line) { return ($line -split "=", 2)[1].Trim() }
    return ""
}

# ── DNS check ────────────────────────────────────────────────
function Check-DNS {
    $domain = Get-EnvValue "DOMAIN"
    log "Verificando DNS para $domain..."

    try {
        $serverIp   = (Invoke-WebRequest -Uri "https://ifconfig.me" -UseBasicParsing).Content.Trim()
        $dnsResult  = Resolve-DnsName $domain -Type A -ErrorAction SilentlyContinue
        $domainIp   = if ($dnsResult) { $dnsResult.IPAddress } else { "" }

        if ($serverIp -eq $domainIp) {
            ok "DNS OK: $domain → $serverIp"
        } else {
            warn "DNS no apunta a este servidor. Servidor: $serverIp | DNS: $domainIp"
            warn "HTTPS automático (Caddy) fallará si el DNS no está configurado."
            $respuesta = Read-Host "¿Continuar de todas formas? [s/N]"
            if ($respuesta -notmatch "^[Ss]$") { exit 1 }
        }
    } catch {
        warn "No se pudo verificar DNS (sin acceso a red o error DNS). Continuando..."
    }
}

# ── Deploy por wave ──────────────────────────────────────────
function Deploy-Wave {
    param([string]$W)
    log "Iniciando Wave $W..."

    $envArgs = @("--env-file", $EnvFile, "-f", $ComposeFile)

    switch ($W) {
        "1" {
            log "Wave 1: Seguridad + Git Forge"
            log "  → Caddy (HTTPS automático)"
            log "  → Gitea (GitHub replacement)"
            log "  → Vaultwarden (1Password replacement)"
            docker compose @envArgs --profile wave1 --profile core up -d
            if ($LASTEXITCODE -ne 0) { err "Wave 1 falló." }

            $domain = Get-EnvValue "DOMAIN"
            warn "Gitea necesita inicialización. Visita: https://git.$domain"
            warn "Vaultwarden admin: https://vault.$domain/admin"
        }
        "2" {
            log "Wave 2: Productividad"
            log "  → Plausible (Google Analytics replacement)"
            log "  → Activepieces (Zapier replacement)"
            docker compose @envArgs --profile wave2 up -d
            if ($LASTEXITCODE -ne 0) { err "Wave 2 falló." }

            log "Esperando inicialización de Plausible (30s)..."
            Start-Sleep -Seconds 30

            $domain = Get-EnvValue "DOMAIN"
            ok "Plausible disponible: https://analytics.$domain"
            ok "Activepieces disponible: https://flows.$domain"
        }
        "3" {
            log "Wave 3: AI Stack"
            log "  → Ollama (OpenAI API replacement)"
            log "  → Open-WebUI (ChatGPT replacement)"
            log "  → AnythingLLM (RAG / Notion AI replacement)"
            docker compose @envArgs --profile wave3 up -d
            if ($LASTEXITCODE -ne 0) { err "Wave 3 falló." }

            log "Descargando modelos de lenguaje (puede tardar según conexión)..."
            foreach ($model in $OllamaModels) {
                log "  → Pulling $model..."
                docker exec gahenax-ollama ollama pull $model
                if ($LASTEXITCODE -eq 0) { ok "$model descargado" }
                else { warn "No se pudo descargar $model. Reintenta: docker exec gahenax-ollama ollama pull $model" }
            }

            $domain = Get-EnvValue "DOMAIN"
            ok "Chat AI disponible: https://chat.$domain"
            ok "RAG disponible: https://rag.$domain"
        }
        "4" {
            log "Wave 4: Observabilidad + CRM"
            log "  → Prometheus + Grafana (DataDog replacement)"
            log "  → Twenty CRM (HubSpot replacement)"
            docker compose @envArgs --profile wave4 up -d
            if ($LASTEXITCODE -ne 0) { err "Wave 4 falló." }

            $domain = Get-EnvValue "DOMAIN"
            ok "Grafana disponible: https://metrics.$domain"
            ok "CRM disponible: https://crm.$domain"
        }
        "all" {
            foreach ($wn in @("1","2","3","4")) { Deploy-Wave $wn }
        }
        default {
            err "Wave inválida: $W. Opciones: 1, 2, 3, 4, all"
        }
    }
}

# ── Health check ─────────────────────────────────────────────
function Run-HealthCheck {
    $domain = Get-EnvValue "DOMAIN"
    log "Ejecutando health checks para $domain..."

    $services = @{
        "git.$domain"       = "Gitea"
        "vault.$domain"     = "Vaultwarden"
        "analytics.$domain" = "Plausible"
        "flows.$domain"     = "Activepieces"
        "chat.$domain"      = "Open-WebUI"
        "rag.$domain"       = "AnythingLLM"
        "metrics.$domain"   = "Grafana"
        "crm.$domain"       = "Twenty CRM"
    }

    $pass = 0; $fail = 0

    foreach ($url in $services.Keys) {
        $name = $services[$url]
        try {
            $response = Invoke-WebRequest -Uri "https://$url" -UseBasicParsing `
                -TimeoutSec 5 -MaximumRedirection 5 -ErrorAction SilentlyContinue
            $code = $response.StatusCode
            ok "$name → https://$url [$code]"
            $pass++
        } catch {
            $code = if ($_.Exception.Response) { [int]$_.Exception.Response.StatusCode } else { 0 }
            warn "$name → https://$url [$code]"
            $fail++
        }
    }

    Write-Host ""
    log "Resultado: $pass OK | $fail FALLOS"
}

# ── Jules integration ────────────────────────────────────────
function Setup-JulesIntegration {
    $domain = Get-EnvValue "DOMAIN"
    log "Generando script de integración Jules → ntfy..."

    $notifyPath = "$env:TEMP\jules_notify.sh"

    @"
#!/bin/bash
# Jules → ntfy push notifications
# Pegar en Katsina drones de Jules-LANCIS
# Uso: bash jules_notify.sh "PTR R30" "completado" "3721 curvas"

TOPIC="`$1"
STATUS="`$2"
DETAIL="`$3"
NTFY_SERVER="https://ntfy.$domain"

curl -s \
  -H "Title: Jules — `${TOPIC}" \
  -H "Tags: microscope,`$([ `"`$STATUS`" = "completado" ] && echo "white_check_mark" || echo "x")" \
  -H "Priority: `$([ `"`$STATUS`" = "completado" ] && echo "default" || echo "high")" \
  -d "`${STATUS}: `${DETAIL}" \
  "`${NTFY_SERVER}/jules-alerts"
"@ | Set-Content -Path $notifyPath -Encoding UTF8

    ok "Script Jules→ntfy generado en: $notifyPath"
    ok "Copiar a Katsina con:"
    Write-Host "  scp `"$notifyPath`" gahenax@patung:/srv/home/gahenax/scripts/jules_notify.sh" -ForegroundColor White
}

# ── Mostrar ayuda ────────────────────────────────────────────
function Show-Usage {
    Write-Host ""
    Write-Host "Gahenax Infrastructure Deploy — PowerShell Edition" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Uso:" -ForegroundColor White
    Write-Host "  .\deploy.ps1 -Wave 1|2|3|4|all   Deploy de la wave especificada"
    Write-Host "  .\deploy.ps1 -Check               Health check de todos los servicios"
    Write-Host "  .\deploy.ps1 -Down                Detener todos los servicios"
    Write-Host "  .\deploy.ps1 -Jules               Generar script de integración Jules→ntfy"
    Write-Host "  .\deploy.ps1 -Help                Mostrar esta ayuda"
    Write-Host ""
    Write-Host "Ejemplos:" -ForegroundColor White
    Write-Host "  .\deploy.ps1 -Wave 1       # Git forge + Password vault"
    Write-Host "  .\deploy.ps1 -Wave all     # Stack completo"
    Write-Host "  .\deploy.ps1 -Check        # Verificar estado"
    Write-Host ""
}

# ── Main ─────────────────────────────────────────────────────
if ($Help) {
    Show-Usage
    exit 0
}

if ($Check) {
    Check-Requirements
    Run-HealthCheck
    exit 0
}

if ($Down) {
    log "Deteniendo todos los servicios Gahenax..."
    docker compose --env-file $EnvFile -f $ComposeFile down
    ok "Stack detenido."
    exit 0
}

if ($Jules) {
    Check-Requirements
    Setup-JulesIntegration
    exit 0
}

if ($Wave -eq "") {
    Show-Usage
    err "Especifica -Wave 1|2|3|4|all"
}

Check-Requirements
Check-DNS
Deploy-Wave $Wave

Write-Host ""
Write-Host "═══════════════════════════════════════════" -ForegroundColor Green
Write-Host "  Gahenax Wave $Wave desplegada con éxito" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════" -ForegroundColor Green
