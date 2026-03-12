---
name: phase-transition-detector
description: Detects whether a reasoning problem is near its "phase transition" — the boundary between tractable and intractable — to allocate effort correctly before starting analysis. Derived from P-ATLAS-NP's kNN variance-based hardness frontier.
---

# 🌡️ Phase Transition Detector

In 3-SAT, problems near the clause-to-variable ratio α ≈ 4.267 are maximally hard — solvers that handle α=3.5 and α=5.5 easily can take exponential time at α=4.267. The phase transition is a structural property of the problem, detectable before solving.

This skill applies the same principle to reasoning: before investing effort, detect whether the problem is in the easy zone, hard zone, or at the boundary. That determines strategy.

**Source calibration**: `Gahenax/P-ATLAS-NP` — `src/atlas.py`, kNN variance thresholds, frontier analysis (~20% of studied graph population in chaos boundary).

## 🎯 When to Activate

Activate at the START of any non-trivial task to determine effort allocation strategy. Especially useful when:
- The question involves optimization ("what's the best X?")
- The problem requires satisfying multiple simultaneous constraints
- The scope is large and time/effort budget matters
- Prior attempts at similar problems have been unexpectedly hard or easy

## 📐 Phase Classification

Three zones, derived from P-ATLAS-NP's frontier analysis:

### Zone 1 — EASY (α < critical)
**Indicators:**
- Few constraints relative to degrees of freedom
- Constraints are non-conflicting or loosely coupled
- A greedy or linear approach likely works
- The solution space is large (many valid answers exist)

**Strategy**: Direct analysis, single pass, low UA budget.

### Zone 2 — FRONTIER (α ≈ critical) ⚠️
**Indicators:**
- Constraints are dense and interacting
- Small changes to inputs cause large changes in answer
- Multiple competing valid framings exist (high local hardness variability)
- Prior attempts at "nearby" problems were inconsistently hard

**Strategy**: Decompose into sub-problems. Apply structural signature extraction first (see `structural-signature-extractor`). Budget for backtracking.

### Zone 3 — HARD (α > critical)
**Indicators:**
- Constraints are over-determined (more constraints than degrees of freedom)
- The problem is asking for a global optimum with no relaxation
- Any solution requires satisfying all constraints simultaneously
- NP-complete problem structure detected (scheduling, packing, allocation)

**Strategy**: Do not attempt exact solution. Find the best satisficing answer. State explicitly that the problem is in the hard zone and exact optimality is not achievable in bounded effort.

## 🔍 Detection Protocol

**Step 1 — Count constraints vs. degrees of freedom**
```
α_estimate = (number of constraints) / (number of free variables)

α < 1.0    → Zone 1 EASY
α ∈ [1.0, 3.0] → Zone 1 EASY (likely)
α ∈ [3.0, 6.0] → Zone 2 FRONTIER — apply full structural analysis
α > 6.0    → Zone 3 HARD
```

**Step 2 — Check coupling**
Are the constraints independent or interacting?
- Independent → move one zone easier
- Densely coupled → move one zone harder

**Step 3 — Check solution space size**
- Many valid answers exist → EASY
- Few or one valid answer → HARD
- Unknown → FRONTIER

**Step 4 — Emit Phase Report**
```
=== PHASE TRANSITION REPORT ===
α_estimate:    [value]
Coupling:      [independent | moderate | dense]
Solution space: [large | bounded | unknown]
Zone:          [EASY | FRONTIER | HARD]
Strategy:      [direct | decompose | satisfice]
UA budget:     [low | medium | high]
================================
```

## 🏛️ Governing Laws

- **Law 1 — Detect before solve**: Phase classification runs before any analytical effort. Never discover hardness by running out of budget.
- **Law 2 — Frontier demands structure**: Any problem classified as FRONTIER must go through `structural-signature-extractor` before proceeding.
- **Law 3 — Hard problems get satisficing**: In Zone 3, exact optimality is not the target. The target is the best defensible answer within budget.
- **Law 4 — 20% rule**: P-ATLAS-NP found ~20% of studied problems in the chaos boundary. Expect approximately 1 in 5 problems to be harder than they look — budget accordingly.

---
*Derived from Gahenax/P-ATLAS-NP — atlas.py, kNN variance frontier, phase transition analysis*
