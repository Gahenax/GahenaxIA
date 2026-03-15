# Workflow Conjunto: Claude Code + Google Antigravity
## Empleados Digitales para Proyectos de Software Gahenax

---

## Visión General

Este documento define cómo **Claude Code** y **Google Antigravity** operan
como empleados digitales complementarios dentro de los proyectos Gahenax.
Cada uno tiene un rol especializado, responsabilidades claras, y protocolos
de comunicación para colaborar sin fricción.

```
┌─────────────────────────────────────────────────────────────────┐
│                    PIPELINE GAHENAX                             │
│                                                                 │
│  FASE 1 — DESARROLLO        FASE 2 — ENTREGA                   │
│  ┌──────────────────┐       ┌──────────────────────────┐       │
│  │   CLAUDE CODE    │──────▶│   GOOGLE ANTIGRAVITY     │       │
│  │  (Dev Senior)    │ push  │  (DevOps / Deploy Mgr)   │       │
│  └──────────────────┘       └──────────────────────────┘       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Roles y Responsabilidades

### Claude Code — Desarrollador Senior

**Fortalezas:**
- Comprensión profunda del código y arquitectura
- Razonamiento sobre lógica de negocio y patrones de diseño
- Revisión de código y detección de bugs sutiles
- Refactoring complejo con contexto amplio
- Escritura de tests con cobertura inteligente
- Documentación técnica precisa

**Responsabilidades:**

| Tarea | Descripción |
|-------|-------------|
| Nuevas features | Diseño e implementación desde el problema al código |
| Bug fixes | Análisis de causa raíz y corrección |
| Code review | Revisión de PRs con feedback concreto |
| Refactoring | Mejora de deuda técnica sin romper funcionalidad |
| Tests unitarios | Cobertura de casos edge, mocks, fixtures |
| Documentación | READMEs, docstrings, changelogs, ADRs |
| Arquitectura | Diseño de módulos, interfaces, contratos de datos |
| Seguridad | Detección de vulnerabilidades, validación de inputs |

**NO hace:**
- Build / compilación de artefactos
- Deploy a entornos reales
- Gestión de infraestructura
- Monitoreo de servicios en producción
- Gestión de secrets y credenciales de prod

---

### Google Antigravity — DevOps / Deploy Manager

**Fortalezas:**
- Ejecución autónoma de comandos en terminal y browser
- Orquestación de múltiples agentes en paralelo
- Integración con GitHub Actions, CI/CD pipelines
- Monitoreo en tiempo real de deployments
- Gestión de entornos (staging, production)

**Responsabilidades:**

| Tarea | Descripción |
|-------|-------------|
| Build | Compilar, empaquetar y generar artefactos |
| Tests de integración | Ejecutar suites completas en entorno real |
| Deploy staging | Push automático tras merge a main |
| Deploy producción | Deploy controlado con gates de aprobación |
| Monitoreo | Verificar health checks post-deploy |
| Rollback | Revertir deployments fallidos |
| Logs | Capturar y analizar build logs |
| Infraestructura | Actualizar configs de servidores, DNS, SSL |

**NO hace:**
- Escribir lógica de negocio
- Tomar decisiones de arquitectura
- Revisar código a nivel semántico
- Modificar tests o documentación técnica

---

## Pipeline de Trabajo

### Flujo Estándar (Feature / Fix)

```
1. INICIO
   └── Tarea asignada (issue, ticket, conversación con usuario)

2. CLAUDE CODE — Fase de Desarrollo
   ├── Leer contexto del repo y código relevante
   ├── Diseñar solución
   ├── Implementar cambios
   ├── Escribir / actualizar tests
   ├── Actualizar CHANGELOG.md
   ├── Commit en rama claude/<feature-name>-<id>
   └── Push + crear handoff file (.antigravity-handoff.json)

3. HANDOFF → ANTIGRAVITY
   └── Antigravity detecta nueva rama claude/* con handoff file

4. ANTIGRAVITY — Fase de Entrega
   ├── Pull de la rama
   ├── npm install / pip install / build
   ├── Ejecutar tests de integración
   ├── Si tests pasan → deploy a staging
   ├── Verificar health checks en staging
   ├── Si OK → crear PR a main o deploy a producción
   └── Actualizar estado en handoff file o issue
```

### Flujo de Hotfix (Urgente)

```
1. Antigravity detecta fallo en producción
2. Antigravity crea issue con logs y contexto
3. Claude Code recibe el issue, analiza, implementa fix
4. Claude Code hace push a claude/hotfix-<issue>
5. Antigravity hace deploy directo a producción (skip staging)
6. Antigravity verifica y cierra el issue
```

---

## Protocolo de Comunicación

### Archivo de Handoff

Al terminar cada sesión de desarrollo, Claude Code crea/actualiza
`.antigravity-handoff.json` en el root del proyecto:

```json
{
  "timestamp_utc": "2026-03-15T10:30:00Z",
  "branch": "claude/feature-nombre-1234",
  "claude_session": "session-id",
  "changes_summary": "Descripción de qué cambió y por qué",
  "files_changed": ["src/foo.py", "tests/test_foo.py"],
  "deploy_target": "staging",
  "deploy_notes": "Requiere migración de DB antes del deploy",
  "test_focus": "Probar endpoint /api/foo con payload grande",
  "risk_level": "low",
  "blockers": []
}
```

`risk_level` guide:
- `low` — cambio aislado, tests cubren todo
- `medium` — cambio con dependencias externas o schema changes
- `high` — cambio crítico, requiere revisión manual antes de producción

### Branch Naming

```
claude/<tipo>-<descripcion-corta>-<id-corto>

Ejemplos:
  claude/feat-auth-jwt-a1b2
  claude/fix-ledger-seal-c3d4
  claude/refactor-governor-e5f6
  claude/research-google-antigravity-1zOdN  ← ejemplo actual
```

### Labels de Issues / PRs

| Label | Asignado a | Significado |
|-------|-----------|-------------|
| `dev:claude` | Claude Code | Requiere trabajo de desarrollo |
| `deploy:antigravity` | Antigravity | Listo para build/deploy |
| `blocked:needs-review` | Humano | Requiere decisión humana |
| `hotfix` | Ambos | Urgente, pipeline acelerado |
| `risk:high` | Antigravity | Deploy requiere aprobación manual |

---

## Reglas de Colaboración

### Claude Code debe:
1. Siempre leer el código antes de modificarlo
2. Nunca pushear a `main` directamente
3. Dejar el repo en estado verde (tests pasando) antes del handoff
4. Documentar decisiones no obvias en el código o en ADRs
5. Actualizar `.antigravity-handoff.json` antes de cada push final

### Antigravity debe:
1. Nunca modificar código fuente de negocio directamente
2. Si el build falla, crear issue con logs completos para Claude Code
3. Requerir aprobación humana para `risk_level: high`
4. Preservar logs de todos los deployments
5. Nunca deployar a producción sin pasar por staging primero

### Ambos deben:
1. Nunca hardcodear secrets o API keys
2. Comunicar blockers inmediatamente via issues o handoff file
3. Mantener CHANGELOG.md actualizado
4. Seguir las convenciones de commits de este proyecto

---

## Onboarding de Nuevo Proyecto

Para aplicar este workflow a cualquier proyecto nuevo:

```bash
# 1. Copiar archivos base de GahenaxIA
cp GahenaxIA/CLAUDE.md <nuevo-proyecto>/CLAUDE.md
cp GahenaxIA/WORKFLOW.md <nuevo-proyecto>/WORKFLOW.md
cp GahenaxIA/.github/workflows/claude-to-antigravity.yml \
   <nuevo-proyecto>/.github/workflows/

# 2. Crear .antigravity-handoff.json inicial
echo '{"status": "initialized"}' > <nuevo-proyecto>/.antigravity-handoff.json

# 3. Agregar al .gitignore si se quiere ignorar el handoff file
# (opcional — puede ser útil tenerlo trackeado)
```

Luego editar `CLAUDE.md` con overrides específicos del proyecto si es necesario.

---

## Proyectos Activos

| Proyecto | Repo | Stack | Deploy Target |
|----------|------|-------|---------------|
| GahenaxIA | `GahenaxIA/` | Python | — |
| Limpia MAX | `limpiamax-web/` | Next.js | GoDaddy SFTP |

---

## Historial de Versiones

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0 | 2026-03-15 | Versión inicial del workflow conjunto |
