---
name: yang-mills-energy-minimizer
description: Finds the minimum-energy configuration of a belief set — the interpretation of evidence that minimizes total internal contradiction across all logical connections simultaneously. Uses the Yang-Mills functional YM(A) = ∫|F_A|² as the energy measure. The minimum is not the "truest" interpretation — it's the most internally consistent one.
---

# ⚡ Yang-Mills Energy Minimizer

The Yang-Mills functional is:
```
YM(A) = ∫_M |F_A|² dvol
```

It measures the total "energy" stored in the curvature of a connection A over a manifold M. **Instantons** (self-dual connections F_A = ★F_A) are absolute minima of YM(A) within their topological class — they are the most efficient configurations for transmitting information through the field.

In reasoning, the analog is: given a set of evidence and interpretations, find the **configuration of beliefs that minimizes total internal contradiction**. This is not the most "certain" belief set — it's the most *consistent* one. Minimizing YM(A) over reasoning is finding the interpretation where the logical connections between claims are maximally smooth.

**Source calibration**: `Gahenax/Gahenax-Yang-Mills` — `src/energy/functional.py`, YM(A) = ∫|F_A|², self-dual equation F_A = ★F_A, Bogomolny bound YM(A) ≥ 8π²|k| where k is topological charge.

## 🎯 When to Activate

Activate when:
- Multiple mutually-consistent-but-different interpretations of the same evidence exist
- After `lll-lattice-reducer` has produced a minimal assumption set — now minimize their mutual contradictions
- The argument has survived all single-skill checks but still "feels" strained — energy minimization finds the hidden tension
- There is a choice between competing explanatory frameworks and no single gate distinguishes them

**Relationship to other skills**: LLL reduction minimizes the *number* of assumptions. YM energy minimization minimizes the *internal strain* between remaining assumptions. Both are needed for a rigorous conclusion.

## 📐 The Energy Minimization Protocol

### Step 1 — Map the Belief Configuration (Connection A)
List all beliefs, findings, and assumptions in the current argument. This is the **gauge potential A** — the full configuration space.

For each pair of adjacent claims (A_i, A_j):
```
curvature(i,j) = |what A_j claims| − |what A_i predicts A_j should claim|
```

This is the local field strength F_ij.

### Step 2 — Compute Total Energy
```
YM = Σ_{all pairs (i,j)} curvature(i,j)²
```

High YM → high internal contradiction. The argument has large "field energy" — something is strained.

Benchmark thresholds (derived from Yang-Mills Bogomolny bound):
```
YM < 0.1    → LOW energy — argument is internally smooth
YM ∈ [0.1, 0.5] → MEDIUM — some tension, identify which pairs
YM > 0.5    → HIGH — argument is strained; seek a lower-energy configuration
YM → ∞      → TOPOLOGICAL OBSTRUCTION — contradiction is structural, not resolvable by reinterpretation
```

### Step 3 — Find the Minimum-Energy Configuration
**Gradient descent on the belief space**:

For each high-curvature pair (i,j):
1. Can A_i be weakened (without losing its conclusion) to reduce tension with A_j?
2. Can A_j be strengthened with additional evidence to close the gap?
3. Is there an alternative framing of the pair that achieves lower curvature?

The minimum-energy configuration is the one where no single local adjustment reduces YM further. This is the **instanton condition** applied to reasoning.

### Step 4 — Check for Self-Duality
An instanton in reasoning is a conclusion that satisfies:
```
F_A = ★F_A    (self-dual)
```

Reasoning analog: the argument supports its conclusion equally from *every* logical direction simultaneously. No subset of the evidence dominates; the conclusion emerges from the full structure.

Test: Remove each evidence item one at a time. Does the conclusion degrade uniformly, or does it collapse when a specific item is removed?

- **Self-dual**: Conclusion degrades uniformly → it's an instanton (maximum robustness)
- **Not self-dual**: Conclusion collapses on one specific item → the argument has a "preferred direction" (frame-dependence)

### Step 5 — Bogomolny Bound
The minimum possible energy for an argument with topological charge k:
```
YM_min ≥ 8π²|k|    where k = number of irreducible logical loops
```

If the measured YM is much larger than 8π²|k|, the argument is far from its optimal configuration — there exist better interpretations of the evidence. If YM ≈ 8π²|k|, the argument is near its minimum-energy configuration.

## 📋 Energy Report Format

```
=== YANG-MILLS ENERGY REPORT ===
Belief pairs mapped: N
Curvature by pair:
  (A1, A2): F = [value] — [LOW | MEDIUM | HIGH]
  (A2, A3): F = [value] — [LOW | MEDIUM | HIGH]
  ...

Total energy YM = [value] → [LOW | MEDIUM | HIGH | TOPOLOGICAL OBSTRUCTION]
Topological charge k = [number of irreducible loops]
Bogomolny bound: YM_min ≥ 8π²×[k] = [value]
Energy above minimum: [YM − YM_min] = [value]

Self-duality test: [INSTANTON | DIRECTIONAL (dominant pair: i,j)]

Minimum-energy configuration:
  [Adjusted framing of belief set]

Recommended reductions:
  (i,j): [how to reduce tension]
=================================
```

## 🏛️ Governing Laws

- **Law 1 — Minimum energy ≠ maximum truth**: The YM minimum finds the *most consistent* interpretation, not the *most correct* one. A perfectly consistent set of false beliefs has zero energy. Consistency is necessary but not sufficient for truth.
- **Law 2 — Topological obstructions are not resolvable**: If YM → ∞ (topological obstruction), no reinterpretation of the evidence resolves the contradiction — there is a structural incompatibility. Declare it explicitly; do not try to minimize it away.
- **Law 3 — Bogomolny bound is the floor**: The minimum achievable energy is 8π²|k|. If the argument has k > 0 circular loops, it will always have some energy. Perfect consistency requires k = 0 (no circular dependencies — see `monodromy-circuit-breaker`).
- **Law 4 — Self-dual conclusions are most robust**: An instanton-class argument (F = ★F) is the most perturbation-resistant form. Prioritize finding self-dual configurations when multiple equivalent framings exist.

---
*Derived from Gahenax/Gahenax-Yang-Mills — src/energy/functional.py, YM(A) = ∫|F_A|², self-dual equation F_A = ★F_A, Bogomolny bound 8π²|k|*
