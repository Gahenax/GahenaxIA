#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# Gahenax Infrastructure — Deploy Script
# Autor: Gahenax AI Research
# Uso:   bash deploy.sh [--wave 1|2|3|4|all] [--check] [--down]
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

COMPOSE_FILE="$(dirname "$0")/docker-compose.yml"
ENV_FILE="$(dirname "$0")/.env"
OLLAMA_MODELS=("llama3.2:3b" "nomic-embed-text")

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log()  { echo -e "${CYAN}[GAHENAX]${NC} $*"; }
ok()   { echo -e "${GREEN}[OK]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
err()  { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

# ── Preflight checks ─────────────────────────────────────────
check_requirements() {
    log "Verificando requisitos..."
    command -v docker >/dev/null 2>&1 || err "Docker no encontrado. Instala Docker Engine."
    docker compose version >/dev/null 2>&1 || err "Docker Compose v2 no encontrado."
    [[ -f "$ENV_FILE" ]] || err ".env no encontrado. Ejecuta: cp .env.example .env && nano .env"
    
    source "$ENV_FILE"
    [[ "${DOMAIN:-}" == "gahenax.ai" || "${DOMAIN:-}" =~ \. ]] || err "DOMAIN no configurado en .env"
    
    # Verificar que los secrets no sean los defaults
    if grep -q "CAMBIA_ESTO" "$ENV_FILE"; then
        err "Hay valores 'CAMBIA_ESTO' sin reemplazar en .env. Configurar todos los secrets primero."
    fi
    
    ok "Todos los requisitos cumplidos."
}

# ── DNS check ────────────────────────────────────────────────
check_dns() {
    source "$ENV_FILE"
    log "Verificando DNS para ${DOMAIN}..."
    SERVER_IP=$(curl -s https://ifconfig.me)
    DOMAIN_IP=$(dig +short "$DOMAIN" | tail -1)
    
    if [[ "$SERVER_IP" == "$DOMAIN_IP" ]]; then
        ok "DNS OK: ${DOMAIN} → ${SERVER_IP}"
    else
        warn "DNS no apunta a este servidor. Servidor: ${SERVER_IP} | DNS: ${DOMAIN_IP}"
        warn "HTTPS automático (Caddy/Let's Encrypt) fallará si el DNS no está configurado."
        read -p "¿Continuar de todas formas? [s/N] " -r
        [[ "$REPLY" =~ ^[Ss]$ ]] || exit 1
    fi
}

# ── Deploy por wave ──────────────────────────────────────────
deploy_wave() {
    local WAVE="$1"
    log "Iniciando Wave ${WAVE}..."
    
    case "$WAVE" in
        1)
            log "Wave 1: Seguridad + Git Forge"
            log "  → Caddy (HTTPS automático)"
            log "  → Gitea (GitHub replacement)"
            log "  → Vaultwarden (1Password replacement)"
            docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" \
                --profile wave1 --profile core up -d
            
            warn "Gitea necesita inicialización. Visita: https://git.${DOMAIN:-localhost}"
            warn "Vaultwarden admin: https://vault.${DOMAIN:-localhost}/admin"
            ;;
        2)
            log "Wave 2: Productividad"
            log "  → Plausible (Google Analytics replacement)"
            log "  → Activepieces (Zapier replacement)"
            docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" \
                --profile wave2 up -d
            
            # Esperar a que Plausible arranque
            log "Esperando inicialización de Plausible (30s)..."
            sleep 30
            ok "Plausible disponible: https://analytics.${DOMAIN:-localhost}"
            ok "Activepieces disponible: https://flows.${DOMAIN:-localhost}"
            ;;
        3)
            log "Wave 3: AI Stack"
            log "  → Ollama (OpenAI API replacement)"
            log "  → Open-WebUI (ChatGPT replacement)"
            log "  → AnythingLLM (RAG / Notion AI replacement)"
            docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" \
                --profile wave3 up -d
            
            # Pull modelos Ollama
            log "Descargando modelos de lenguaje..."
            for MODEL in "${OLLAMA_MODELS[@]}"; do
                log "  → Pulling ${MODEL}..."
                docker exec gahenax-ollama ollama pull "$MODEL" && ok "${MODEL} descargado"
            done
            
            ok "Chat AI disponible: https://chat.${DOMAIN:-localhost}"
            ok "RAG disponible: https://rag.${DOMAIN:-localhost}"
            ;;
        4)
            log "Wave 4: Observabilidad + CRM"
            log "  → Prometheus + Grafana (DataDog replacement)"
            log "  → Twenty CRM (HubSpot replacement)"
            docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" \
                --profile wave4 up -d
            
            ok "Grafana disponible: https://metrics.${DOMAIN:-localhost}"
            ok "CRM disponible: https://crm.${DOMAIN:-localhost}"
            ;;
        all)
            for W in 1 2 3 4; do deploy_wave "$W"; done
            ;;
        *)
            err "Wave inválida: $WAVE. Opciones: 1, 2, 3, 4, all"
            ;;
    esac
}

# ── Health check ─────────────────────────────────────────────
run_health_check() {
    source "$ENV_FILE"
    log "Ejecutando health checks..."
    
    SERVICES=(
        "git.${DOMAIN}:Gitea"
        "vault.${DOMAIN}:Vaultwarden"
        "analytics.${DOMAIN}:Plausible"
        "flows.${DOMAIN}:Activepieces"
        "chat.${DOMAIN}:Open-WebUI"
        "rag.${DOMAIN}:AnythingLLM"
        "metrics.${DOMAIN}:Grafana"
        "crm.${DOMAIN}:Twenty CRM"
    )
    
    PASS=0; FAIL=0
    for SERVICE in "${SERVICES[@]}"; do
        URL=$(echo "$SERVICE" | cut -d: -f1)
        NAME=$(echo "$SERVICE" | cut -d: -f2)
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "https://${URL}" || echo "000")
        if [[ "$HTTP_CODE" =~ ^(200|301|302|307|308)$ ]]; then
            ok "${NAME} → https://${URL} [${HTTP_CODE}]"
            ((PASS++))
        else
            warn "${NAME} → https://${URL} [${HTTP_CODE}]"
            ((FAIL++))
        fi
    done
    
    echo ""
    log "Resultado: ${PASS} OK | ${FAIL} FALLOS"
}

# ── Jules integration ─────────────────────────────────────────
setup_jules_integration() {
    source "$ENV_FILE"
    log "Configurando integración Jules → Gahenax stack..."
    
    # Crear script para que Jules notifique a ntfy cuando termine un job
    cat > /tmp/jules_notify.sh << 'EOF'
#!/bin/bash
# Pegar este script en los drones Katsina de Jules
# Usar al final de cada ptr_rNN_worker.py como: bash jules_notify.sh "PTR R30" "completado" "3721 curvas"

TOPIC="$1"
STATUS="$2"
DETAIL="$3"
NTFY_SERVER="${NTFY_SERVER:-https://ntfy.DOMAIN}"  # Reemplazar DOMAIN

curl -s \
  -H "Title: Jules — ${TOPIC}" \
  -H "Tags: microscope,$([ "$STATUS" = "completado" ] && echo "white_check_mark" || echo "x")" \
  -H "Priority: $([ "$STATUS" = "completado" ] && echo "default" || echo "high")" \
  -d "${STATUS}: ${DETAIL}" \
  "${NTFY_SERVER}/jules-alerts"
EOF
    
    sed -i "s/DOMAIN/${DOMAIN}/g" /tmp/jules_notify.sh
    ok "Script Jules→ntfy generado en /tmp/jules_notify.sh"
    ok "Copiar a Katsina con: scp /tmp/jules_notify.sh gahenax@patung:/srv/home/gahenax/scripts/"
}

# ── Main ─────────────────────────────────────────────────────
usage() {
    echo "Uso: $0 [opciones]"
    echo ""
    echo "Opciones:"
    echo "  --wave 1|2|3|4|all   Deploy de la wave especificada"
    echo "  --check               Health check de todos los servicios"
    echo "  --down                Detener todos los servicios"
    echo "  --jules               Configurar integración con Jules LANCIS"
    echo "  --help                Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  bash deploy.sh --wave 1          # Deploy security + git forge"
    echo "  bash deploy.sh --wave all        # Deploy completo"
    echo "  bash deploy.sh --check           # Verificar estado de todos"
}

WAVE=""
ACTION="deploy"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --wave)    WAVE="$2"; shift 2 ;;
        --check)   ACTION="check"; shift ;;
        --down)    ACTION="down"; shift ;;
        --jules)   ACTION="jules"; shift ;;
        --help)    usage; exit 0 ;;
        *)         err "Argumento desconocido: $1" ;;
    esac
done

case "$ACTION" in
    deploy)
        [[ -z "$WAVE" ]] && { usage; err "Especifica --wave 1|2|3|4|all"; }
        check_requirements
        check_dns
        deploy_wave "$WAVE"
        echo ""
        ok "═══════════════════════════════════════════"
        ok "  Gahenax Wave ${WAVE} desplegada con éxito"
        ok "═══════════════════════════════════════════"
        ;;
    check)
        run_health_check
        ;;
    down)
        log "Deteniendo todos los servicios Gahenax..."
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down
        ok "Stack detenido."
        ;;
    jules)
        check_requirements
        setup_jules_integration
        ;;
esac
