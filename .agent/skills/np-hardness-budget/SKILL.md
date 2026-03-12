---
name: np-hardness-budget
description: Allocates reasoning depth and UA budget based on estimated structural hardness — using the thermodynamic analogy from P-ATLAS-NP to avoid both under-investment in hard problems and over-investment in easy ones.
---

# 💰 NP Hardness Budget

P-ATLAS-NP models SAT hardness as a thermodynamic system: β ~ 1/T (inverse temperature) measures how "frozen" the solution space is. High β = low temperature = few valid solutions = hard. Low β = high temperature = many valid solutions = easy.

This skill translates that thermodynamic model into a UA budget allocation framework. The goal is the same as Gahenax Core's P over NP paradigm: **maximize ΔS (entropy reduction) per UA spent**, not solve everything exhaustively.

**Source calibration**: `Gahenax/P-ATLAS-NP` — thermodynamic energy landscape, β pseudo-temperature, spin-glass freezing barriers. Directly aligned with `GahenaxIA` UA Governor.

## 🎯 When to Activate

Activate after `phase-transition-detector` has classified the problem zone. This skill decides *how much* to invest in each zone.

Also activate when:
- Context window or time budget is limited
- A task has multiple sub-problems of varying difficulty
- A previous attempt ran out of budget before completing

## 🌡️ Thermodynamic Budget Table

| Zone | β (hardness) | UA Multiplier | Strategy |
|------|-------------|---------------|----------|
| EASY | β < 1.0 | 1x (baseline) | Direct solve, single pass |
| FRONTIER | β ∈ [1.0, 3.0] | 2-3x | Decompose, structural signature, backtrack budget |
| HARD | β > 3.0 | 4-5x (cap) | Satisficing only — no exhaustive search |
| OVER-CONSTRAINED | β → ∞ | 1x (abort) | Declare infeasible, return best partial |

**Note**: High UA multiplier does NOT mean "try harder indefinitely." It means the budget ceiling is higher before declaring failure. The spin-glass law applies: past a β threshold, more search yields diminishing returns — abort and satisfice.

## 📊 Budget Allocation Protocol

**Step 1 — Receive phase classification**
Input: Zone from `phase-transition-detector` + V-vector from `structural-signature-extractor`

**Step 2 — Compute β estimate**
```
β_estimate = constraint_ratio / solution_freedom_score

Where:
  constraint_ratio    = from structural-signature-extractor Family 2
  solution_freedom    = inverse of local_optima_risk score
```

**Step 3 — Set budget parameters**
```
base_ua     = complexity-adjusted baseline
ua_ceiling  = base_ua × multiplier(zone)
abort_at    = ua_ceiling × 0.8  ← trigger satisficing before hard abort
checkpoint  = ua_ceiling × 0.4  ← mid-point review: is progress linear?
```

**Step 4 — Mid-point checkpoint**
At 40% of UA budget consumed:
- Is the remaining problem size decreasing proportionally? → continue
- Is the problem resisting reduction? → switch to satisficing early
- Has a new sub-problem appeared that wasn't in the original signature? → re-run phase detector

**Step 5 — Emit Budget Report**
```
=== NP HARDNESS BUDGET ===
Zone:           [EASY | FRONTIER | HARD | OVER-CONSTRAINED]
β estimate:     [value]
UA multiplier:  [Nx]
Checkpoint at:  [40% budget]
Abort/satisfice at: [80% budget]
Strategy:       [direct | decompose | satisfice | declare-infeasible]
==========================
```

## 🏛️ Governing Laws

- **Law 1 — Budget before analysis**: UA allocation is set before starting. Never discover the problem is NP-hard by exhausting the context window.
- **Law 2 — Spin-glass abort**: When ΔS/UA drops below 0.1 for two consecutive steps, the problem has entered spin-glass territory. Stop searching. Emit best current partial answer.
- **Law 3 — Satisficing is not failure**: In HARD and OVER-CONSTRAINED zones, the best achievable answer within budget is the correct answer. Claiming to find the global optimum in bounded time is the real failure.
- **Law 4 — Re-classify on surprise**: If a problem classified as EASY turns out to require 2x the expected effort, re-run `phase-transition-detector`. The initial classification was wrong — do not just push harder.
- **Law 5 — UA alignment**: This skill's budget estimates map directly onto GahenaxIA's `ua_budget` field in `ExecutionRequest`. EASY = 1-2 UA, FRONTIER = 3-4 UA, HARD = 5-6 UA, OVER-CONSTRAINED = 0.5 UA (fast fail).

---
*Derived from Gahenax/P-ATLAS-NP — thermodynamic energy landscape, β pseudo-temperature, spin-glass barriers. Aligned with GahenaxIA UA Governor.*
