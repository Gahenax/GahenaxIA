---
name: reasoning-integrity
description: Workflow de activación secuencial de las 29 skills epistémicas para garantizar integridad estructural en razonamiento complejo.
---

# 🧠 Reasoning Integrity Workflow

Protocolo de ejecución secuencial para tareas de alta complejidad o alto riesgo epistémico. Integra las 29 skills derivadas de `Gahenax/OEDA_HodgeRigidity`, `Gahenax/P-ATLAS-NP`, `Gahenax/OEDA_Kernel`, `Gahenax/Gahenax-Yang-Mills`, `Gahenax/Gahenax-BSD`, `Gahenax/OEDA_GahenaxIA`, y `Gahenax/Mersenne-Gahen`.

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
  │  chain break → HALT; drift → flag
  │
  ▼
[3]  semaforo-chronos-hodge         ← Salud poblacional histórica (ventana N)
  │  RED → HALT; ORANGE>30% → recalibrar
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
  ▼  (si la conclusión necesita verificar irreducibilidad)
[11] lucas-lehmer-iterative-test    ← s₀=4, s_{i+1}=s_i²−2 mod M_p
  │  residue=0 → irreducible; residue≠0 → composite → [13]
  │
  ▼  (durante y después de LL)
[12] roundoff-error-budget          ← roundoff_max ≤ 0.40 por iteración
  │  roundoff_max>0.40 → INVALID → reemplazar step contaminante
  │
  ▼  (si LL retornó composite)
[13] mersenne-factor-structure      ← buscar q=2kp+1 que divida M_p
  │  factor encontrado → sub-claim a k-ésimo armónico
  │
  ▼  (si se requiere certificación distribuida)
[14] residue-hash-certification     ← two-session hash match; mismatch → error
  │
  ▼  (si argumento multi-paso)
[15] gauge-invariance-checker       ← ¿Invariante bajo reencuadres locales?
  │
  ▼  (si múltiples interpretaciones compiten)
[16] yang-mills-energy-minimizer    ← Configuración de mínima energía interna
  │
  ▼
[17] ghost-loci-reasoning           ← ¿Conclusiones vecinas más correctas?
  │
  ▼
[18] monodromy-circuit-breaker      ← ¿Circularidad? M≥1 → HALT
  │
  ▼  (si >5 pasos con conceptos reutilizados)
[19] wilson-loop-drift-detector     ← Deriva semántica acumulada
  │
  ▼
[20] spectral-anomaly-alert         ← CR≥0.4 → evidencia comprimida
  │
  ▼
[21] hodge-rigidity-detector        ← H/M/S → Semáforo punto-en-tiempo
  │
  ▼  (si algún step falló K veces)
[22] circuit-breaker-quarantine     ← ¿Patrón en cuarentena?
  │
  ▼  (si todos los componentes pasaron localmente)
[23] sha-obstruction-detector       ← ¿Globalmente consistente?
  │
  ▼  (si conclusión de alto alcance)
[24] canonical-height-complexity    ← ĥ(C) = alcance vs. evidencia
  │
  ▼
[25] adversarial-gate-validator     ← 5 gates; <3/5 → REJECT
  │
  ▼  (si conclusión usada como premisa o Δ<0.3)
[26] bsd-dual-measurement-checker   ← Dos métodos independientes
  │
  ▼
[27] mass-gap-estimator             ← Δ=E₁−E₀
  │
  ▼  (si acción irreversible)
[28] fail-closed-execution          ← 6 gates de autorización
  │
  ▼
[29] gahenax-contract-emitter       ← 6 bloques + Imperative Filter + UA audit
  │
  ▼
OUTPUT → CMR.record_run + residue_hash sealed
```

## Activación por Zona

| Zona | Skills activas |
|------|---------------|
| EASY | [1]+[2]+[7]+[17]+[27]+[29] |
| FRONTIER | [1]→[29] completo |
| HARD | [1]→[29] + satisficing + LL full pass |
| OVER-CONSTRAINED | [1]+[4]+[5] → infeasible vía [29] |
| Decriptado/Irreducibilidad | + [11]+[12]+[13]+[14] |
| Síntesis multi-dominio | + [23] obligatorio |
| Conclusión como premisa | + [14]+[26]+[27], Δ≥0.2 |
| Acción irreversible | + [28] antes de [29] |
| Tarea con historial CMR | + [2]+[3] al inicio |
| Patrón fallando K veces | + [22] antes del siguiente intento |

## Formato de Audit Trail Completo

```
=== REASONING INTEGRITY AUDIT ===
BL scan:          [CLEAR | HIT BL-XX]
CNI fingerprint:  [sha256[:12]] → [FIRST-RUN | STABLE | DRIFT | TAMPERED]
Semáforo histórico: [OPTIMAL | RECALIBRATION | CRITICAL]
Phase:            [EASY | FRONTIER | HARD | OVER-CONSTRAINED]
UA budget:        [Nx baseline]
Gateway:          [OK | BLOCKED ErrorClass | REPLAY]
Assumptions:      [N open / N validated / N reduced / N invalidated]
V-vector:         [stable | unstable]
SV:               [shortest vector assumptions]
Descent:          [rank(Sel)=N, lifted=M, Sha=K]
LL test:          [is_prime=T residue=0 | is_prime=F residue=[hash[:8]]]
Roundoff:         [roundoff_max=[val] → VALID | MARGINAL | INVALID at step i=[X]]
Factors:          [irreducible | q=2([k])[p]+1=[val] at k=[K]]
Residue cert:     [CERTIFIED (A=B) | MISMATCH | SINGLE-SESSION]
Gauge:            [INVARIANT | DEPENDENT step k]
YM energy:        [LOW | MEDIUM | HIGH | TOPOLOGICAL]
Ghosts:           [N scanned, N live]
Monodromy:        M=[val] → [GREEN | ORANGE | RED]
Wilson loop:      [TRIVIAL | W=[val] — drift type]
Spectral:         CR=[val] → [NORMAL | WATCH | ALERT]
H/M/S:            H=[x] M=[x] S=[x] → [VERDE | NARANJA | ROJO]
Circuit breakers: [ALL CLOSED | P_k QUARANTINED]
Sha:              [Ш=0 | finite | ∞]
Height ĥ(C):      [val] → [COMPLIANT | UNDERFUNDED | OVERLEVERAGED]
Gates (5-gate):   [N/5 passed]
Dual measurement: [AGREEMENT | DISAGREEMENT gap=[val]]
Mass gap Δ:       [val] → [LARGE | MODERATE | SMALL | NEAR-ZERO]
Gates (fail-cls): [N/6 | N/A]
Verdict ceiling:  [no_verdict | conditional | rigorous]
Verdict:          [COMMITTED | PROVISIONAL | HALTED | INFEASIBLE]
CMR + residue:    evidence_hash=[sha256[:12]] residue_hash=[sha256[:12]]
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
| Mersenne-Gahen | lucas-lehmer-iterative-test, residue-hash-certification, roundoff-error-budget, mersenne-factor-structure |
