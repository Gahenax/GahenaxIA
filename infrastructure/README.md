# Gahenax Infrastructure

Stack self-hosted unificado. **12 servicios, 4 waves, 1 comando.**

## Prerequisitos

| Requisito | Mínimo | Recomendado |
|---|---|---|
| OS | Ubuntu 22.04 LTS | Ubuntu 24.04 LTS |
| RAM | 4 GB | 8 GB |
| Disco | 80 GB SSD | 160 GB SSD |
| Docker | 24+ | latest |
| Dominio | *.gahenax.ai DNS apuntando al servidor | mismo |

```bash
# Instalar Docker en Ubuntu (si no lo tienes)
curl -fsSL https://get.docker.com | bash
```

## Setup inicial (1 vez)

```bash
# 1. Clonar / copiar este directorio al servidor
scp -r infrastructure/ root@TU_VPS_IP:/opt/gahenax/

# 2. Entrar al servidor
ssh root@TU_VPS_IP
cd /opt/gahenax/infrastructure

# 3. Configurar secrets
cp .env.example .env
nano .env   # Rellenar TODOS los valores (leer comentarios)

# 4. Dar permisos al deploy script
chmod +x deploy.sh
```

## Deploy por waves

```bash
# Wave 1 — Git Forge + Password Vault (URGENTE → 15 min)
bash deploy.sh --wave 1

# Wave 2 — Analytics + Automation (→ 20 min)
bash deploy.sh --wave 2

# Wave 3 — AI Stack completo (→ 10 min + descarga de modelos)
bash deploy.sh --wave 3

# Wave 4 — Observabilidad + CRM (→ 15 min)
bash deploy.sh --wave 4

# Todo de una vez
bash deploy.sh --wave all
```

## Servicios disponibles post-deploy

| Subdominio | Servicio | Reemplaza |
|---|---|---|
| `git.gahenax.ai` | Gitea | GitHub |
| `vault.gahenax.ai` | Vaultwarden | 1Password |
| `analytics.gahenax.ai` | Plausible | Google Analytics |
| `flows.gahenax.ai` | Activepieces | Zapier |
| `chat.gahenax.ai` | Open-WebUI + Ollama | ChatGPT |
| `rag.gahenax.ai` | AnythingLLM | Notion AI |
| `metrics.gahenax.ai` | Grafana | DataDog |
| `crm.gahenax.ai` | Twenty CRM | HubSpot |

## Health check

```bash
bash deploy.sh --check
```

## Integración con Jules (LANCIS)

```bash
# Configura el bridge Jules → ntfy (alertas push de jobs)
bash deploy.sh --jules

# Copia el script generado a los drones Katsina
scp /tmp/jules_notify.sh gahenax@patung:/srv/home/gahenax/scripts/
```

Luego añadir al final de `run_ptr_r30.sh` en Jules:
```bash
bash /srv/home/gahenax/scripts/jules_notify.sh "PTR R30" "completado" "${TOTAL} curvas procesadas"
```

## Comandos útiles

```bash
# Ver logs en tiempo real
docker compose logs -f gahenax-ollama

# Detener todo
bash deploy.sh --down

# Pull modelos adicionales de Ollama
docker exec -it gahenax-ollama ollama pull deepseek-r1:7b

# Backup de Vaultwarden
docker cp gahenax-vaultwarden:/data ./backups/vault-$(date +%F)
```

## Estructura de archivos

```
infrastructure/
├── docker-compose.yml      ← Stack completo (12 servicios, 4 waves)
├── Caddyfile               ← Reverse proxy + HTTPS automático
├── .env.example            ← Template de secrets (copiar a .env)
├── deploy.sh               ← Script de deploy en 1 comando
├── .gitignore              ← Excluye .env y datos de Docker
├── monitoring/
│   ├── prometheus.yml      ← Métricas: VPS + Jules Katsina drones
│   └── grafana/            ← Dashboards provisionados
└── README.md               ← Este archivo
```
