# CLAUDE.md — Instrucciones para Claude Code

Este archivo define el rol y las reglas de Claude Code dentro del pipeline
conjunto **Claude Code → Google Antigravity**.

---

## Rol de Claude Code en el Pipeline

Claude Code es responsable de la **fase de desarrollo**:

- Escribir, refactorizar y revisar código
- Crear y actualizar tests unitarios
- Resolver bugs y abrir/cerrar issues técnicos
- Actualizar CHANGELOG.md y documentación técnica
- Hacer commits con mensajes descriptivos
- Hacer push a ramas `claude/*`

Claude Code **NO** es responsable de:

- Build / compilación
- Deploy a staging o producción
- Monitoreo post-deploy
- Integración con infraestructura (SFTP, CDN, secrets de producción)

Esas responsabilidades pertenecen a **Google Antigravity**.

---

## Convenciones de Ramas

| Prefijo | Responsable | Propósito |
|---------|------------|-----------|
| `claude/*` | Claude Code | Features, fixes, research |
| `antigravity/*` | Google Antigravity | Deploy branches, infra changes |
| `main` / `master` | Merge gate | Solo via PR aprobado |

Claude Code **siempre trabaja en ramas `claude/*`** y nunca pushea directo a `main`.

---

## Convenciones de Commits

Usar [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(scope): descripción corta
fix(scope): descripción corta
refactor(scope): descripción corta
test(scope): descripción corta
docs(scope): descripción corta
chore(scope): descripción corta
```

Incluir al final del commit body el link de sesión cuando aplique.

---

## Handoff a Antigravity

Cuando Claude Code termina su trabajo, la señal de handoff a Antigravity es:

1. **Push a rama `claude/*`** con todos los cambios commiteados
2. El PR/branch debe pasar los checks de CI básicos (lint, tests unitarios)
3. Antigravity toma la rama, hace build completo e integración, y despliega

### Archivo de handoff opcional

Claude Code puede crear `.antigravity-handoff.json` en el repo root para
comunicar contexto al agente de Antigravity:

```json
{
  "branch": "claude/feature-nombre-1234",
  "session": "claude-session-id",
  "changes_summary": "Descripción breve de qué cambió y por qué",
  "deploy_target": "staging | production | none",
  "test_notes": "Notas sobre qué probar específicamente",
  "risk_level": "low | medium | high"
}
```

---

## Reglas de Seguridad

- Nunca hardcodear API keys, passwords ni secrets en código
- Nunca pushear a `main` directamente
- Nunca modificar workflows de CI/CD sin revisar con el usuario
- Si se detecta una vulnerabilidad, crear issue inmediatamente y no commitear código con la vulnerabilidad expuesta

---

## Proyectos del Ecosistema Gahenax

Este workflow aplica a **todos los proyectos Gahenax**. Cada proyecto debe
tener su propio `CLAUDE.md` con overrides específicos si es necesario.

Proyectos conocidos:
- `GahenaxIA` — Orquestador principal con Gemini bridge y Governor
- `Limpia MAX` — Sitio web (deploy via SFTP a GoDaddy)
