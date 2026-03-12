---
name: reasoning-integrity
description: Workflow de activación secuencial de las 5 skills epistémicas para garantizar integridad estructural en razonamiento complejo.
---

# 🧠 Reasoning Integrity Workflow

Protocolo de ejecución secuencial para tareas de alta complejidad o alto riesgo epistémico. Integra las 5 skills derivadas de `Gahenax/OEDA_HodgeRigidity`.

## Orden de Ejecución

```
INPUT
  │
  ▼
[1] epistemic-blacklist        ← Pre-scan: ¿el argumento usa un patrón conocido-malo?
  │  Si BL hit → HALT y reportar
  │
  ▼
[2] ghost-loci-reasoning       ← ¿Hay conclusiones vecinas más correctas que no exploré?
  │  Si ghost vivo → marcar como PROVISIONAL
  │
  ▼
[3] monodromy-circuit-breaker  ← ¿El argumento depende de su propia conclusión?
  │  Si M ≥ 1 directo → HALT y reclasificar premisa
  │
  ▼
[4] spectral-anomaly-alert     ← ¿La evidencia es sospechosamente consistente?
  │  Si CR ≥ 0.4 → nombrar compresión y fuente probable
  │
  ▼
[5] hodge-rigidity-detector    ← Métrica final H/M/S → Semaforo VERDE/NARANJA/ROJO
  │
  ▼
OUTPUT (con audit trail)
```

## Cuándo Usar el Workflow Completo

- Preguntas causales complejas ("¿por qué X?", "¿qué causó Y?")
- Síntesis de múltiples fuentes en un solo veredicto
- Dominios de alto riesgo (ciencia, medicina, finanzas, derecho)
- Cuando la respuesta llegó demasiado rápido o se siente obvia

## Formato de Audit Trail

```
=== REASONING INTEGRITY AUDIT ===
BL scan:    [CLEAR | HIT BL-XX]
Ghosts:     [N scanned, N ruled out, N live]
Monodromy:  M = [value] → [GREEN | ORANGE | RED]
Spectral:   CR = [value] → [NORMAL | WATCH | ALERT]
H/M/S:      H=[x] M=[x] S=[x] → [VERDE | NARANJA | ROJO]
Verdict:    [COMMITTED | PROVISIONAL | HALTED]
==================================
```

## Activación Rápida (Solo Skill 5)

Para tareas de baja complejidad, activar solo `hodge-rigidity-detector` como verificación mínima antes de emitir.
