---
name: reasoning-integrity
description: Workflow de activación secuencial de las 9 skills epistémicas para garantizar integridad estructural en razonamiento complejo.
---

# 🧠 Reasoning Integrity Workflow

Protocolo de ejecución secuencial para tareas de alta complejidad o alto riesgo epistémico. Integra las 9 skills derivadas de `Gahenax/OEDA_HodgeRigidity` y `Gahenax/P-ATLAS-NP`.

## Orden de Ejecución

```
INPUT
  │
  ▼
[1] epistemic-blacklist           ← Pre-scan: ¿patrón conocido-malo?
  │  Si BL hit → HALT y reportar
  │
  ▼
[2] phase-transition-detector     ← ¿El problema está en zona EASY / FRONTIER / HARD?
  │  Determina la profundidad de análisis necesaria
  │
  ▼
[3] np-hardness-budget            ← Asignar UA budget antes de empezar
  │  EASY=1x | FRONTIER=2-3x | HARD=4-5x | OVER-CONSTRAINED=abort
  │
  ▼  (si FRONTIER o HARD)
[4] structural-signature-extractor ← Extraer V-vector del problema
  │  Si inestable → re-clasificar fase
  │
  ▼
[5] ghost-loci-reasoning          ← ¿Hay conclusiones vecinas más correctas?
  │  Si ghost vivo → marcar como PROVISIONAL
  │
  ▼
[6] monodromy-circuit-breaker     ← ¿El argumento depende de su propia conclusión?
  │  Si M ≥ 1 directo → HALT y reclasificar premisa
  │
  ▼
[7] spectral-anomaly-alert        ← ¿Evidencia sospechosamente consistente?
  │  Si CR ≥ 0.4 → nombrar compresión
  │
  ▼
[8] hodge-rigidity-detector       ← Métricas H/M/S → Semaforo VERDE/NARANJA/ROJO
  │
  ▼
[9] adversarial-gate-validator    ← 5 gates antes de emitir
  │  < 3/5 → REJECT | 3-4/5 → PROVISIONAL | 5/5 → ACCEPTED
  │
  ▼
OUTPUT (con audit trail completo)
```

## Cuándo Usar el Workflow Completo

- Preguntas causales complejas ("¿por qué X?", "¿qué causó Y?")
- Síntesis de múltiples fuentes en un solo veredicto
- Dominios de alto riesgo (ciencia, medicina, finanzas, derecho)
- Problemas de optimización o satisfacción de múltiples restricciones
- Cuando la respuesta llegó demasiado rápido o se siente obvia

## Activación por Zona

| Zona | Skills activas |
|------|---------------|
| EASY | [1] + [5] + [8] — mínimo viable |
| FRONTIER | [1] → [9] completo |
| HARD | [1] → [9] + satisficing explícito en output |
| OVER-CONSTRAINED | [1] + [2] + [3] → declarar infeasible |

## Formato de Audit Trail Completo

```
=== REASONING INTEGRITY AUDIT ===
BL scan:      [CLEAR | HIT BL-XX]
Phase:        [EASY | FRONTIER | HARD | OVER-CONSTRAINED]
UA budget:    [Nx baseline]
V-vector:     [stable | unstable]
Ghosts:       [N scanned, N ruled out, N live]
Monodromy:    M=[value] → [GREEN | ORANGE | RED]
Spectral:     CR=[value] → [NORMAL | WATCH | ALERT]
H/M/S:        H=[x] M=[x] S=[x] → [VERDE | NARANJA | ROJO]
Gates:        [N/5 passed]
Verdict:      [COMMITTED | PROVISIONAL | HALTED | INFEASIBLE]
==================================
```

## Activación Rápida (Solo Skills 1 + 8)

Para tareas de baja complejidad: `epistemic-blacklist` + `hodge-rigidity-detector` como verificación mínima.
