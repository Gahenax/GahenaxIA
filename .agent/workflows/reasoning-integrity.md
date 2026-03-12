---
name: reasoning-integrity
description: Workflow de activación secuencial de las 25 skills epistémicas para garantizar integridad estructural en razonamiento complejo.
---

# 🧠 Reasoning Integrity Workflow

Protocolo de ejecución secuencial para tareas de alta complejidad o alto riesgo epistémico. Integra las 25 skills derivadas de `Gahenax/OEDA_HodgeRigidity`, `Gahenax/P-ATLAS-NP`, `Gahenax/OEDA_Kernel`, `Gahenax/Gahenax-Yang-Mills`, `Gahenax/Gahenax-BSD`, y `Gahenax/OEDA_GahenaxIA`.

## Orden de Ejecución

```
INPUT
  │
  ▼
[1]  epistemic-blacklist            ← Pre-scan: ¿patrón conocido-malo?
  │  BL hit → HALT
  │
  ▼
[2]  cni-fingerprint-integrity      ← ¿Esta tarea tiene historial en CMR?
  │  fingerprint drift → flag; chain break → HALT
  │
  ▼
[3]  semaforo-chronos-hodge         ← Salud poblacional histórica (ventana N)
  │  RED detectado → HALT; ORANGE>30% → recalibrar antes de continuar
  │
  ▼
[4]  phase-transition-detector      ← ¿EASY / FRONTIER / HARD?
  │
  ▼
[5]  np-hardness-budget             ← Asignar UA budget
  │
  ▼
[6]  execution-gateway-protocol     ← 8 gates de autorización pre-ejecución
  │  BLOCKED → diagnosticar; REPLAY → retornar cached
  │
  ▼
[7]  assumption-lifecycle-tracker   ← Inicializar registro; todos OPEN
  │
  ▼  (si FRONTIER o HARD)
[8]  structural-signature-extractor ← V-vector; si inestable → re-clasificar
  │
  ▼  (si FRONTIER o HARD)
[9]  lll-lattice-reducer            ← Shortest Vector; MAX_CRITICAL = 3
  │
  ▼  (si FRONTIER o HARD)
[10] descent-search-protocol        ← Local-to-global; rank(Sel) = cota superior
  │
  ▼  (si argumento multi-paso)
[11] gauge-invariance-checker       ← ¿Invariante bajo reencuadres locales?
  │
  ▼  (si múltiples interpretaciones compiten)
[12] yang-mills-energy-minimizer    ← Configuración de mínima energía interna
  │
  ▼
[13] ghost-loci-reasoning           ← ¿Conclusiones vecinas más correctas?
  │
  ▼
[14] monodromy-circuit-breaker      ← ¿Circularidad explícita? M≥1 → HALT
  │
  ▼  (si argumento > 5 pasos con conceptos reutilizados)
[15] wilson-loop-drift-detector     ← Deriva semántica acumulada
  │  det(W)<0 → inversión de concepto → no_verdict
  │
  ▼
[16] spectral-anomaly-alert         ← CR≥0.4 → evidencia comprimida
  │
  ▼
[17] hodge-rigidity-detector        ← H/M/S → Semáforo punto-en-tiempo
  │
  ▼  (si algún step anterior falló K veces)
[18] circuit-breaker-quarantine     ← ¿Patrón en cuarentena? BLOCKED → diagnosticar
  │
  ▼  (si todos los componentes pasaron localmente)
[19] sha-obstruction-detector       ← ¿Globalmente consistente o Sha-bloqueado?
  │  Ш infinito → rechazar; Ш finito → restricción global faltante
  │
  ▼  (si conclusión de alto alcance o cadena larga)
[20] canonical-height-complexity    ← ĥ(C) = alcance vs. evidencia disponible
  │  overleveraged (ratio<0.5) → bajar a provisional
  │
  ▼
[21] adversarial-gate-validator     ← 5 gates; <3/5 → REJECT
  │
  ▼  (si conclusión usada como premisa downstream o Δ<0.3)
[22] bsd-dual-measurement-checker   ← Dos métodos independientes
  │  desacuerdo → el gap ES el hallazgo
  │
  ▼
[23] mass-gap-estimator             ← Δ=E₁−E₀; Δ<0.05 → conditional
  │
  ▼  (si acción irreversible)
[24] fail-closed-execution          ← 6 gates de autorización de acción
  │
  ▼
[25] gahenax-contract-emitter       ← 6 bloques + Imperative Filter + UA audit
  │
  ▼
OUTPUT → CMR.record_run (evidence_hash, prev_hash chain)
```

## Activación por Zona

| Zona | Skills activas |
|------|---------------|
| EASY | [1]+[2]+[7]+[13]+[17]+[23]+[25] |
| FRONTIER | [1]→[25] completo |
| HARD | [1]→[25] + satisficing explícito |
| OVER-CONSTRAINED | [1]+[4]+[5] → infeasible vía [25] |
| Argumento largo (>5 pasos) | + [11]+[14] explícitos |
| Síntesis multi-dominio | + [19] obligatorio |
| Conclusión usada como premisa | + [22]+[23] obligatorios, Δ≥0.2 |
| Acción irreversible | + [24] antes de [25] |
| Tarea con historial CMR | + [2]+[3] al inicio |
| Patrón fallando repetidamente | + [18] antes del siguiente intento |

## Formato de Audit Trail Completo

```
=== REASONING INTEGRITY AUDIT ===
BL scan:          [CLEAR | HIT BL-XX]
CNI fingerprint:  [sha256[:12]] → [FIRST-RUN | STABLE | DRIFT | TAMPERED]
Semáforo histórico: [OPTIMAL | RECALIBRATION | CRITICAL] (N=[N] sessions)
Phase:            [EASY | FRONTIER | HARD | OVER-CONSTRAINED]
UA budget:        [Nx baseline]
Gateway:          [OK | BLOCKED ErrorClass | REPLAY request_id]
Assumptions:      [N open / N validated / N reduced / N invalidated]
V-vector:         [stable | unstable]
SV:               [shortest vector assumptions]
Descent:          [rank(Sel)=N, lifted=M, Sha candidates=K]
Gauge:            [INVARIANT | DEPENDENT — artifact at step k]
YM energy:        [LOW | MEDIUM | HIGH | TOPOLOGICAL OBSTRUCTION]
Ghosts:           [N scanned, N live]
Monodromy:        M=[value] → [GREEN | ORANGE | RED]
Wilson loop:      [TRIVIAL | W=[value] — drift type]
Spectral:         CR=[value] → [NORMAL | WATCH | ALERT]
H/M/S:            H=[x] M=[x] S=[x] → [VERDE | NARANJA | ROJO]
Circuit breakers: [ALL CLOSED | P_k QUARANTINED (Xs)]
Sha:              [Ш=0 | finite | ∞ — obstruction type]
Height ĥ(C):      [value] → [COMPLIANT | UNDERFUNDED | OVERLEVERAGED]
Gates (5-gate):   [N/5 passed]
Dual measurement: [AGREEMENT | DISAGREEMENT gap=[value]]
Mass gap Δ:       [value] → [LARGE | MODERATE | SMALL | NEAR-ZERO]
Gates (fail-cls): [N/6 passed | N/A]
Verdict ceiling:  [no_verdict | conditional | rigorous]
Verdict:          [COMMITTED | PROVISIONAL | HALTED | INFEASIBLE]
CMR record:       [evidence_hash[:12]] chain=[prev_hash[:12] | GENESIS]
==================================
```

## Skill Map por Repositorio de Origen

| Repositorio | Skills |
|-------------|--------|
| OEDA_HodgeRigidity | hodge-rigidity-detector, ghost-loci-reasoning, spectral-anomaly-alert, monodromy-circuit-breaker, epistemic-blacklist |
| P-ATLAS-NP | phase-transition-detector, np-hardness-budget, structural-signature-extractor, adversarial-gate-validator |
| OEDA_Kernel | lll-lattice-reducer, gahenax-contract-emitter, fail-closed-execution, assumption-lifecycle-tracker |
| Gahenax-Yang-Mills | gauge-invariance-checker, yang-mills-energy-minimizer, wilson-loop-drift-detector, mass-gap-estimator |
| Gahenax-BSD | bsd-dual-measurement-checker, sha-obstruction-detector, canonical-height-complexity, descent-search-protocol |
| OEDA_GahenaxIA | execution-gateway-protocol, circuit-breaker-quarantine, cni-fingerprint-integrity, semaforo-chronos-hodge |
