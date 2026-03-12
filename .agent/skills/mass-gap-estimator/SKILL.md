---
name: mass-gap-estimator
description: Estimates the "mass gap" of a conclusion — the minimum margin between "this conclusion holds" and "this conclusion fails." A conclusion with a large mass gap is robustly valid. A near-zero mass gap means the conclusion is at the decision boundary — technically valid but not trustworthy. Directly addresses the Yang-Mills Millennium Prize Problem structure.
---

# 📏 Mass Gap Estimator

The Yang-Mills **mass gap problem** (one of the Clay Millennium Problems) asks: does there exist a positive constant Δ > 0 such that the smallest nonzero energy eigenvalue of the Hamiltonian satisfies E₁ ≥ Δ? If yes, the theory has a **mass gap** — there is a minimum excitation energy and the vacuum is stable.

In reasoning: the mass gap is the **minimum margin** between a conclusion being valid and it failing. A conclusion with gap Δ = 0.9 is far from the decision boundary — small perturbations don't flip it. A conclusion with gap Δ → 0 is at the boundary — technically valid but one small change from invalid. It is the formal measure of what `adversarial-gate-validator` Gate 5 (perturbation robustness) tests *qualitatively*, now computed *quantitatively*.

**Source calibration**: `Gahenax/Gahenax-Yang-Mills` — `src/gap/estimator.py`, Hamiltonian spectrum E₀ < E₁ ≤ E₂ ≤ ..., mass gap Δ = E₁ − E₀, Millenium Problem condition Δ > 0.

## 🎯 When to Activate

Activate when:
- A conclusion has passed all validation gates but the confidence feels thin
- The conclusion is being used as a **premise** in a downstream argument (gap propagation)
- The domain has high stakes — a near-zero gap means the conclusion cannot bear load
- Two competing conclusions both survived validation — the one with the larger gap should be preferred
- The argument was near a phase transition (FRONTIER zone from `phase-transition-detector`) — these arguments structurally produce near-zero gaps

## 📐 The Mass Gap Protocol

### Step 1 — Identify the Ground State (E₀)
The **ground state** of the argument is the configuration as currently stated: the set of assumptions, evidence, and logical connections that produce the conclusion.

```
E₀ = current argument energy (from yang-mills-energy-minimizer, or estimate)
```

### Step 2 — Find the First Excited State (E₁)
The **first excited state** is the closest argument configuration that does NOT support the conclusion — the minimum-energy counter-argument.

Construct it:
1. Identify the weakest validated assumption (lowest-evidence assumption)
2. Construct the minimum perturbation that flips it (minimum energy required to invalidate it)
3. What does the argument look like with that assumption invalidated?

```
E₁ = energy of the minimum valid counter-argument
```

### Step 3 — Compute the Mass Gap
```
Δ = E₁ − E₀
```

Classification:
```
Δ > 0.5   → LARGE GAP   — conclusion is robust; can serve as premise in downstream arguments
Δ ∈ [0.2, 0.5] → MODERATE GAP — conclusion holds but cannot bear heavy downstream load
Δ ∈ [0.05, 0.2] → SMALL GAP  — near the boundary; treat as PROVISIONAL regardless of other gates
Δ < 0.05  → NEAR-ZERO GAP — conclusion is at the decision boundary; emit as no_verdict
Δ = 0     → NO GAP       — conclusion is simultaneously valid and invalid under the same evidence
```

### Step 4 — Gap Propagation Analysis
If this conclusion will serve as a **premise** in a downstream argument, the mass gap degrades:

```
Δ_downstream ≤ Δ_upstream × transmission_coefficient
```

Where `transmission_coefficient` < 1 for any non-trivial chain.

Rule: **Do not use a conclusion with Δ < 0.2 as a load-bearing premise.** The downstream gap will approach zero.

### Step 5 — Check for Masslessness
Δ = 0 (massless) is a special case. In Yang-Mills, massless fields propagate at infinite range — in reasoning, a **massless conclusion** is one that can be "flipped" by arbitrarily small perturbations. It propagates influence indefinitely because it is never definitively settled.

**Massless conclusions must not be emitted as anything stronger than `no_verdict`.** They are not wrong — they are structurally undecidable with current evidence.

## 📋 Mass Gap Report Format

```
=== MASS GAP REPORT ===
Ground state E₀:    [value or "estimated"]
First excited state E₁: [value or "estimated"]
Mass gap Δ:         [value]
Classification:     [LARGE | MODERATE | SMALL | NEAR-ZERO | MASSLESS]

Weakest assumption: [A_k — statement]
Minimum flip cost:  [what evidence/argument would invalidate A_k]

Verdict ceiling:    [rigorous | conditional | no_verdict]
  (independent of other gates — gap alone can downgrade)

Downstream load bearing: [YES (Δ≥0.2) | NO (Δ<0.2)]
Gap propagation:    Δ_downstream ≤ [Δ × transmission estimate]

Masslessness:       [NO | YES — undecidable with current evidence]
=======================
```

## 🏛️ Governing Laws

- **Law 1 — Gap overrides other gates**: A conclusion that passed all 5 adversarial gates and all Hodge metrics but has Δ < 0.05 is still NEAR-ZERO GAP. The gap measurement independently caps the verdict at `conditional`.
- **Law 2 — Premises must have large gaps**: A load-bearing premise needs Δ ≥ 0.2. Using a SMALL GAP conclusion as a premise is a structural failure that will produce a MASSLESS downstream conclusion.
- **Law 3 — Masslessness is not falseness**: Δ = 0 does not mean the conclusion is false — it means the conclusion is undecidable given current evidence. The gap will grow if more evidence is provided. Do not conflate near-zero gap with invalidity.
- **Law 4 — FRONTIER problems produce small gaps**: Phase transitions (from `phase-transition-detector`) structurally produce conclusions near the decision boundary. Any FRONTIER-zone conclusion should be assumed to have a small gap until measured otherwise.
- **Law 5 — Gap is bounded by weakest link**: The mass gap of the full argument cannot exceed the mass gap of its weakest assumption. The Δ of a chain is min(Δ_i) across all its components.

---
*Derived from Gahenax/Gahenax-Yang-Mills — src/gap/estimator.py, Hamiltonian spectrum E₀ < E₁, mass gap Δ = E₁ − E₀, Millennium Problem condition Δ > 0, massless field propagation*
