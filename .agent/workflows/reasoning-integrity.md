---
name: reasoning-integrity
description: Workflow de activación secuencial de las 21 skills epistémicas para garantizar integridad estructural en razonamiento complejo.
---

# 🧠 Reasoning Integrity Workflow

Protocolo de ejecución secuencial para tareas de alta complejidad o alto riesgo epistémico. Integra las 21 skills derivadas de `Gahenax/OEDA_HodgeRigidity`, `Gahenax/P-ATLAS-NP`, `Gahenax/OEDA_Kernel`, `Gahenax/Gahenax-Yang-Mills`, y `Gahenax/Gahenax-BSD`.

## Orden de Ejecución

```
INPUT
  │
  ▼
[1]  epistemic-blacklist            ← Pre-scan: ¿patrón conocido-malo?
  │  BL hit → HALT
  │
  ▼
[2]  phase-transition-detector      ← ¿EASY / FRONTIER / HARD?
  │
  ▼
[3]  np-hardness-budget             ← Asignar UA budget
  │
  ▼
[4]  assumption-lifecycle-tracker   ← Inicializar registro; todos OPEN
  │
  ▼  (si FRONTIER o HARD)
[5]  structural-signature-extractor ← V-vector; si inestable → re-clasificar
  │
  ▼  (si FRONTIER o HARD)
[6]  lll-lattice-reducer            ← Shortest Vector; MAX_CRITICAL = 3
  │
  ▼  (si FRONTIER o HARD)
[7]  descent-search-protocol        ← Local-to-global: condiciones locales
  │  primero, luego levantar; rank(Sel) = cota superior de conclusiones válidas
  │
  ▼  (si argumento multi-paso)
[8]  gauge-invariance-checker       ← ¿Invariante bajo reencuadres locales?
  │
  ▼  (si múltiples interpretaciones compiten)
[9]  yang-mills-energy-minimizer    ← Configuración de mínima energía interna
  │
  ▼
[10] ghost-loci-reasoning           ← ¿Conclusiones vecinas más correctas?
  │
  ▼
[11] monodromy-circuit-breaker      ← ¿Circularidad explícita? M≥1 → HALT
  │
  ▼  (si argumento > 5 pasos con conceptos reutilizados)
[12] wilson-loop-drift-detector     ← Deriva semántica acumulada
  │  det(W)<0 → inversión de concepto → no_verdict
  │
  ▼
[13] spectral-anomaly-alert         ← CR≥0.4 → evidencia comprimida
  │
  ▼
[14] hodge-rigidity-detector        ← H/M/S → Semáforo
  │
  ▼  (si todos los componentes pasaron localmente)
[15] sha-obstruction-detector       ← ¿Globalmente consistente o Sha-bloqueado?
  │  Ш infinito → rechazar; Ш finito → identificar restricción global faltante
  │
  ▼  (si conclusión de alto alcance o cadena larga)
[16] canonical-height-complexity    ← ĥ(C) = alcance vs. evidencia disponible
  │  overleveraged (ratio<0.5) → bajar a provisional
  │
  ▼
[17] adversarial-gate-validator     ← 5 gates; <3/5 → REJECT
  │
  ▼  (si conclusión usada como premisa downstream o Δ<0.3)
[18] bsd-dual-measurement-checker   ← Dos métodos independientes; acuerdo=corroboración
  │  desacuerdo → el gap ES el hallazgo
  │
  ▼
[19] mass-gap-estimator             ← Δ=E₁−E₀; Δ<0.05 → conditional; Δ<0.2 → no downstream
  │
  ▼  (si acción irreversible)
[20] fail-closed-execution          ← 6 gates de autorización
  │
  ▼
[21] gahenax-contract-emitter       ← 6 bloques + Imperative Filter + UA audit
  │
  ▼
OUTPUT
```

## Activación por Zona

| Zona | Skills activas |
|------|---------------|
| EASY | [1]+[4]+[10]+[14]+[19]+[21] |
| FRONTIER | [1]→[21] completo |
| HARD | [1]→[21] + satisficing explícito |
| OVER-CONSTRAINED | [1]+[2]+[3] → infeasible vía [21] |
| Argumento largo (>5 pasos) | + [8]+[12] explícitos |
| Síntesis multi-dominio | + [15] obligatorio |
| Conclusión usada como premisa | + [18]+[19] obligatorios, Δ≥0.2 |
| Acción irreversible | + [20] antes de [21] |

## Formato de Audit Trail Completo

```
=== REASONING INTEGRITY AUDIT ===
BL scan:          [CLEAR | HIT BL-XX]
Phase:            [EASY | FRONTIER | HARD | OVER-CONSTRAINED]
UA budget:        [Nx baseline]
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
Sha:              [Ш=0 | finite | ∞ — obstruction type]
Height ĥ(C):      [value] → [COMPLIANT | UNDERFUNDED | OVERLEVERAGED]
Gates (5-gate):   [N/5 passed]
Dual measurement: [AGREEMENT | DISAGREEMENT gap=[value]]
Mass gap Δ:       [value] → [LARGE | MODERATE | SMALL | NEAR-ZERO]
Gates (fail-cls): [N/6 passed | N/A]
Verdict ceiling:  [no_verdict | conditional | rigorous]
Verdict:          [COMMITTED | PROVISIONAL | HALTED | INFEASIBLE]
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
