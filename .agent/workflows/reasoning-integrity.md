---
name: reasoning-integrity
description: Workflow de activación secuencial de las 13 skills epistémicas para garantizar integridad estructural en razonamiento complejo.
---

# 🧠 Reasoning Integrity Workflow

Protocolo de ejecución secuencial para tareas de alta complejidad o alto riesgo epistémico. Integra las 13 skills derivadas de `Gahenax/OEDA_HodgeRigidity`, `Gahenax/P-ATLAS-NP`, y `Gahenax/OEDA_Kernel`.

## Orden de Ejecución

```
INPUT
  │
  ▼
[1]  epistemic-blacklist            ← Pre-scan: ¿patrón conocido-malo?
  │  Si BL hit → HALT y reportar
  │
  ▼
[2]  phase-transition-detector      ← ¿EASY / FRONTIER / HARD?
  │
  ▼
[3]  np-hardness-budget             ← Asignar UA budget
  │  EASY=1x | FRONTIER=2-3x | HARD=4-5x | OVER-CONSTRAINED=abort
  │
  ▼
[4]  assumption-lifecycle-tracker   ← Inicializar registro de supuestos
  │  Todos los supuestos nacen OPEN
  │
  ▼  (si FRONTIER o HARD)
[5]  structural-signature-extractor ← Extraer V-vector del problema
  │  Si inestable → re-clasificar fase
  │
  ▼  (si FRONTIER o HARD)
[6]  lll-lattice-reducer            ← Reducir supuestos al mínimo necesario
  │  Identificar Shortest Vector; MAX_CRITICAL = 3
  │
  ▼
[7]  ghost-loci-reasoning           ← ¿Conclusiones vecinas más correctas?
  │  Si ghost vivo → marcar como PROVISIONAL
  │
  ▼
[8]  monodromy-circuit-breaker      ← ¿Argumento circular?
  │  Si M ≥ 1 directo → HALT
  │
  ▼
[9]  spectral-anomaly-alert         ← ¿Evidencia sospechosamente consistente?
  │  Si CR ≥ 0.4 → nombrar compresión
  │
  ▼
[10] hodge-rigidity-detector        ← H/M/S → Semáforo VERDE/NARANJA/ROJO
  │
  ▼
[11] adversarial-gate-validator     ← 5 gates antes de emitir
  │  < 3/5 → REJECT | 3-4/5 → PROVISIONAL | 5/5 → ACCEPTED
  │
  ▼  (si acción o decisión → activar)
[12] fail-closed-execution          ← 6 gates para conclusiones accionables
  │  BLOCK si falta evidencia / autorización
  │
  ▼
[13] gahenax-contract-emitter       ← Emitir en formato contrato (6 bloques)
  │  Imperative Filter + UA audit
  │
  ▼
OUTPUT (con audit trail completo)
```

## Activación por Zona

| Zona | Skills activas |
|------|---------------|
| EASY | [1] + [4] + [7] + [10] + [13] |
| FRONTIER | [1] → [13] completo |
| HARD | [1] → [13] + satisficing explícito |
| OVER-CONSTRAINED | [1] + [2] + [3] → declarar infeasible vía [13] |
| Acción irreversible (cualquier zona) | añadir [12] antes de [13] |

## Formato de Audit Trail Completo

```
=== REASONING INTEGRITY AUDIT ===
BL scan:         [CLEAR | HIT BL-XX]
Phase:           [EASY | FRONTIER | HARD | OVER-CONSTRAINED]
UA budget:       [Nx baseline]
Assumptions:     [N open / N validated / N reduced / N invalidated]
V-vector:        [stable | unstable]
SV:              [shortest vector assumptions]
Ghosts:          [N scanned, N ruled out, N live]
Monodromy:       M=[value] → [GREEN | ORANGE | RED]
Spectral:        CR=[value] → [NORMAL | WATCH | ALERT]
H/M/S:           H=[x] M=[x] S=[x] → [VERDE | NARANJA | ROJO]
Gates (5-gate):  [N/5 passed]
Gates (fail-cls):[N/6 passed | N/A]
Verdict ceiling: [no_verdict | conditional | rigorous]
Verdict:         [COMMITTED | PROVISIONAL | HALTED | INFEASIBLE]
==================================
```

## Skill Map por Repositorio de Origen

| Repositorio | Skills |
|-------------|--------|
| OEDA_HodgeRigidity | hodge-rigidity-detector, ghost-loci-reasoning, spectral-anomaly-alert, monodromy-circuit-breaker, epistemic-blacklist |
| P-ATLAS-NP | phase-transition-detector, np-hardness-budget, structural-signature-extractor, adversarial-gate-validator |
| OEDA_Kernel | lll-lattice-reducer, gahenax-contract-emitter, fail-closed-execution, assumption-lifecycle-tracker |
