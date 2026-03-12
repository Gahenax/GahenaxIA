---
name: structural-signature-extractor
description: Extracts a compressed structural signature (v-vector) from a problem or argument before attempting to solve it — enabling pattern recognition, hardness estimation, and strategy selection based on geometry rather than brute force. Derived from P-ATLAS-NP's feature extraction pipeline.
---

# 🧬 Structural Signature Extractor

P-ATLAS-NP doesn't measure SAT hardness by running a solver — it extracts a structural "v-vector" from the problem's topology, thermodynamics, and algebraic properties, then maps it into a 7-dimensional latent space with ~90% projection stability. The geometry of the problem predicts its behavior before any solving begins.

This skill extracts an analogous structural signature from any reasoning problem — a compact representation of its topology, constraint density, and algebraic simplifiability — to guide strategy selection.

**Source calibration**: `Gahenax/P-ATLAS-NP` — `src/signatures/extractors.py`, `src/signatures/compressor.py`, 7-dimensional latent space, 90% projection stability.

## 🎯 When to Activate

Activate when a problem is classified as FRONTIER or HARD by `phase-transition-detector`, or when:
- The problem structure is unfamiliar
- Previous similar problems were solved incorrectly
- Multiple conflicting approaches seem equally valid
- The problem can be decomposed but the right decomposition isn't obvious

## 📐 The Three Feature Families

Directly mirroring P-ATLAS-NP's extractor families:

### Family 1 — Topology (Discrete Poincaré)
*How is the problem connected?*

Extract:
- **Spectral gap**: How tightly coupled are the core concepts? (High gap = loosely coupled = easier)
- **Fiedler value proxy**: What's the minimum "bottleneck" between problem components?
- **Bipartite structure**: Can the problem be cleanly split into two independent sub-problems?

Signature vector T = [coupling_density, bottleneck_width, bipartite_score]

### Family 2 — Thermodynamics (Energy Landscape)
*How constrained is the solution space?*

Extract:
- **β proxy** (inverse temperature): How "frozen" is the problem? High β = few valid solutions = hard
- **Clause density equivalent**: Ratio of constraints to free variables
- **Spin-glass indicator**: Are there many local optima that could trap a search?

Signature vector E = [constraint_ratio, solution_freedom, local_optima_risk]

### Family 3 — Algebraic Simplifiability (Horn Normalization)
*Can the problem be reduced before solving?*

Extract:
- **Unit propagation potential**: How many constraints resolve immediately from a single assumption?
- **2-SAT collapse potential**: What fraction of the problem can be solved in polynomial time?
- **Reduction resistance**: How much of the problem remains hard after simplification?

Signature vector A = [propagation_potential, poly_solvable_fraction, irreducible_core_size]

## 🗜️ Compression to V-Vector

Combine the three families into a single compressed signature:

```
V = compress(T, E, A)
  = [topology_score, energy_score, algebra_score,
     coupling_index, hardness_estimate, simplification_gain,
     overall_complexity_class]
```

Report stability: if V changes significantly when problem is reframed → FRONTIER signal. If V is stable → reliable signature.

## 📋 Signature Report Format

```
=== STRUCTURAL SIGNATURE ===
Family 1 — Topology:
  Coupling density:   [low | medium | high]
  Bottleneck:         [wide | narrow | absent]
  Bipartite split:    [yes | partial | no]

Family 2 — Thermodynamics:
  Constraint ratio:   [α value]
  Solution freedom:   [high | bounded | near-zero]
  Local optima risk:  [low | medium | high]

Family 3 — Algebra:
  Propagation gain:   [% constraints resolvable immediately]
  Poly-solvable:      [% of problem]
  Irreducible core:   [small | medium | large]

V-vector:  [topology | energy | algebra | hardness_class]
Stability: [stable | unstable — reframe sensitivity detected]
============================
```

## 🏛️ Governing Laws

- **Law 1 — Extract before solve**: Signature extraction precedes any solving attempt in FRONTIER/HARD zones.
- **Law 2 — Simplify first**: If algebraic family shows high propagation potential, apply simplifications before full analysis. Never solve what can be reduced.
- **Law 3 — Instability is signal**: If the v-vector changes significantly under reframing, the problem is near the chaos boundary — do not commit to a strategy until the instability is understood.
- **Law 4 — 90% stability threshold**: P-ATLAS-NP requires ~90% projection stability for a v-vector to be trusted. A signature that shifts >10% under minor reframing is unreliable.

---
*Derived from Gahenax/P-ATLAS-NP — extractors.py, compressor.py, 7-dimensional latent space*
