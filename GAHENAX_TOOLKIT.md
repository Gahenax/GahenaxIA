#  GAHENAX AI: ENTERPRISE TOOLKIT (v3.0)

Guía de herramientas soberanas instaladas para inteligencia, infraestructura y operaciones automatizadas.

---

##  Capa 1: Infraestructura y Seguridad (Wave 1)
- **Gitea**: Git forge local para control total del código fuente (reemplaza GitHub).
- **Vaultwarden**: Gestor de contraseñas y secretos (reemplaza 1Password).
- **Caddy**: Reverse proxy con HTTPS automático y soporte HTTP/3.

##  Capa 2: Inteligencia Artificial Soberana (Wave 3)
- **Ollama (v3.2)**: Runner local de modelos (Llama 3.2, DeepSeek-R1).
- **Open-WebUI**: Interfaz premium para interacción con LLMs locales.
- **AnythingLLM**: Motor de RAG para bases de conocimiento privadas.
- **Token-Savior**: Servidor MCP de indexación simbólica para ahorro de tokens (99% eficiencia).

##  Capa 3: Operaciones y Productividad (Wave 2 & 4)
- **Activepieces**: Motor de automatización no-code para flujos de negocio.
- **Twenty CRM**: Gestión de relaciones y leads B2B (reemplaza HubSpot).
- **Plausible**: Analítica web privada y ética (reemplaza Google Analytics).

##  Capa 4: Observabilidad y Sensorización (Wave 4)
- **Grafana & Prometheus**: Dashboards en tiempo real de salud del sistema.
- **Gahenax Spy System**: Telemetría avanzada y detección de patrones en vivo.

---

##  Comandos de Despacho (Quick Deployment)

### Desplegar el Stack por Olas (Waves):
```powershell
# Ola 1: Seguridad y Código
docker compose --profile wave1 up -d

# Ola 3: Inteligencia Artificial
docker compose --profile wave3 up -d

# Ver estado global
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

**Gahenax AI — Soberanía Digital por Diseño.**
