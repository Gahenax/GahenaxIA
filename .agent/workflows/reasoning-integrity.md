---
name: reasoning-integrity
description: Workflow de activación secuencial de las 17 skills epistémicas para garantizar integridad estructural en razonamiento complejo.
---

# 🧠 Reasoning Integrity Workflow

Protocolo de ejecución secuencial para tareas de alta complejidad o alto riesgo epistémico. Integra las 17 skills derivadas de `Gahenax/OEDA_HodgeRigidity`, `Gahenax/P-ATLAS-NP`, `Gahenax/OEDA_Kernel`, y `Gahenax/Gahenax-Yang-Mills`.

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
  ▼  (si argumento multi-paso o terminología reutilizada)
[7]  gauge-invariance-checker       ← ¿Conclusión invariante bajo reencuadres locales?
  │  Si gauge-dependiente → identificar artefacto y contenido puro
  │
  ▼  (si múltiples interpretaciones compiten)
[8]  yang-mills-energy-minimizer    ← Encontrar configuración de creencias de mínima energía
  │  YM > 0.5 → tensión alta; buscar configuración alternativa
  │
  ▼
[9]  ghost-loci-reasoning           ← ¿Conclusiones vecinas más correctas?
  │  Si ghost vivo → marcar como PROVISIONAL
  │
  ▼
[10] monodromy-circuit-breaker      ← ¿Argumento circular explícito?
  │  Si M ≥ 1 directo → HALT
  │
  ▼  (si argumento > 5 pasos con conceptos reutilizados)
[11] wilson-loop-drift-detector     ← ¿Deriva semántica acumulada en la cadena?
  │  W ≫ 1 → drift moderado/severo; det(W)<0 → inversión → no_verdict
  │
  ▼
[12] spectral-anomaly-alert         ← ¿Evidencia sospechosamente consistente?
  │  Si CR ≥ 0.4 → nombrar compresión
  │
  ▼
[13] hodge-rigidity-detector        ← H/M/S → Semáforo VERDE/NARANJA/ROJO
  │
  ▼
[14] adversarial-gate-validator     ← 5 gates antes de emitir
  │  < 3/5 → REJECT | 3-4/5 → PROVISIONAL | 5/5 → ACCEPTED
  │
  ▼
[15] mass-gap-estimator             ← Margen entre conclusión válida e inválida
  │  Δ < 0.05 → near-zero gap → bajar a conditional / no_verdict
  │  Δ < 0.2  → no usar como premisa downstream
  │
  ▼  (si acción o decisión → activar)
[16] fail-closed-execution          ← 6 gates para conclusiones accionables
  │  BLOCK si falta evidencia / autorización
  │
  ▼
[17] gahenax-contract-emitter       ← Emitir en formato contrato (6 bloques)
  │  Imperative Filter + UA audit
  │
  ▼
OUTPUT (con audit trail completo)
```

## Activación por Zona

| Zona | Skills activas |
|------|---------------|
| EASY | [1] + [4] + [9] + [13] + [15] + [17] |
| FRONTIER | [1] → [17] completo |
| HARD | [1] → [17] + satisficing explícito |
| OVER-CONSTRAINED | [1] + [2] + [3] → declarar infeasible vía [17] |
| Argumento largo (>5 pasos) | añadir [7] + [11] explícitamente |
| Acción irreversible (cualquier zona) | añadir [16] antes de [17] |
| Conclusión usada como premisa downstream | [15] obligatorio — verificar Δ ≥ 0.2 |

## Formato de Audit Trail Completo

```
=== REASONING INTEGRITY AUDIT ===
BL scan:         [CLEAR | HIT BL-XX]
Phase:           [EASY | FRONTIER | HARD | OVER-CONSTRAINED]
UA budget:       [Nx baseline]
Assumptions:     [N open / N validated / N reduced / N invalidated]
V-vector:        [stable | unstable]
SV:              [shortest vector assumptions]
Gauge:           [INVARIANT | DEPENDENT — artifact at step k]
YM energy:       [LOW | MEDIUM | HIGH | TOPOLOGICAL OBSTRUCTION]
Ghosts:          [N scanned, N ruled out, N live]
Monodromy:       M=[value] → [GREEN | ORANGE | RED]
Wilson loop:     [TRIVIAL | W=[value] — drift type]
Spectral:        CR=[value] → [NORMAL | WATCH | ALERT]
H/M/S:           H=[x] M=[x] S=[x] → [VERDE | NARANJA | ROJO]
Gates (5-gate):  [N/5 passed]
Mass gap Δ:      [value] → [LARGE | MODERATE | SMALL | NEAR-ZERO | MASSLESS]
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
| Gahenax-Yang-Mills | gauge-invariance-checker, yang-mills-energy-minimizer, wilson-loop-drift-detector, mass-gap-estimator |
