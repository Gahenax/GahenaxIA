---
name: lll-lattice-reducer
description: Reduces a set of reasoning assumptions to its minimal non-redundant basis using LLL/Deep-LLL lattice reduction logic — finding the Shortest Vector (most parsimonious path from evidence to conclusion) and marking redundant assumptions as REDUCED. Core algorithm of Gahenax OEDA_Kernel.
---

# ⚙️ LLL Lattice Reducer

Gahenax Core treats reasoning as a high-dimensional lattice L. Each assumption is a basis vector. The LLL optimizer applies unimodular transformations to find short, near-orthogonal basis vectors — the most independent and rigorous logical paths. Redundant assumptions are collapsed (`AssumptionStatus.REDUCED`) to increase precision and reduce UA spend.

The goal: find the **Shortest Vector** — the most direct, evidentially supported path from premises to conclusion.

**Source calibration**: `Gahenax/OEDA_Kernel` — `gahenax_engine.py::GahenaxOptimizer.reduce_lattice()`, `GahenaxOptimizer.reduce_lattice()`, `AssumptionStatus.REDUCED`. Complexity: O(n⁴ log B) where n = number of assumptions.

## 🎯 When to Activate

Activate when:
- A chain of reasoning has more than 3 assumptions
- Multiple assumptions seem to be saying "the same thing" differently
- The argument has grown complex and the conclusion feels buried
- Prior reasoning failed (verdict too weak) — reduction may reveal it

Also activate after `structural-signature-extractor` if algebraic family shows high propagation potential.

## 📐 The Reduction Algorithm

### Step 1 — Enumerate All Assumptions
List every assumption explicitly. Give each a stable ID (A1, A2, A3...). Format:
```
A1: [statement] → unlocks: [which conclusion this enables]
A2: [statement] → unlocks: [which conclusion this enables]
...
```

### Step 2 — Compute Redundancy
For each pair (Ai, Aj): are they logically equivalent, or does one subsume the other?
- If Ai logically implies Aj and vice versa → **REDUCE** the weaker one
- If Ai implies Aj but not vice versa → Ai is stronger; **REDUCE** Aj
- If they're independent and both required → **KEEP** both

Mark status:
- `OPEN`: Unresolved, required
- `VALIDATED`: Confirmed by evidence
- `INVALIDATED`: Shown false
- `REDUCED`: Subsumed — logically unnecessary given another assumption

### Step 3 — Find the Shortest Vector
After reduction: what is the minimum set of OPEN/VALIDATED assumptions that, together, are sufficient to reach the conclusion?

This is the **Shortest Vector (SV)** — the most parsimonious explanation.

```
SV = {Ai : i ∈ minimal_sufficient_set}
```

If multiple minimal sets exist, select the one with the most VALIDATED members.

### Step 4 — Compute Entropy Reduction
```
ΔS = entropy_before - entropy_after
   = |original_assumptions| × 10 - |reduced_assumptions| × 10

efficiency = ΔS / UA_spent
```

If ΔS ≤ 0 (no reduction achieved): the assumptions are already minimal — report as-is.

## 📋 Reduction Report Format

```
=== LLL LATTICE REDUCTION ===
Original basis: N assumptions
  A1: [statement] → [conclusion] | Status: OPEN
  A2: [statement] → [conclusion] | Status: REDUCED (subsumed by A1)
  A3: [statement] → [conclusion] | Status: VALIDATED
  ...

Reduced basis: M assumptions (M < N)
Shortest Vector: {A1, A3, ...}
ΔS = [value]
Efficiency = ΔS / UA_spent = [value]
Verdict unlocked by SV: [YES / CONDITIONAL / NO]
=============================
```

## 🏛️ Governing Laws

- **Law 1 — Enumerate first**: Never reduce without first explicitly listing ALL assumptions. Hidden assumptions survive if not surfaced.
- **Law 2 — REDUCED ≠ false**: A REDUCED assumption is not wrong — it's subsumed. Do not treat it as invalidated.
- **Law 3 — SV is the target**: The goal is not to eliminate all assumptions; it's to find the minimum sufficient set. Stopping at 2 when 1 is sufficient is a lattice reduction failure.
- **Law 4 — MAX_CRITICAL = 3**: `gahenax_engine.py` hard-codes `MAX_CRITICAL_ASSUMPTIONS = 3`. If the reduced basis still has > 3 open assumptions, the problem is under-specified. Flag it as `no_verdict` territory.
- **Law 5 — Speculation is debt**: Any assumption that cannot be validated or invalidated with available evidence is **computational debt**. Name it as OPEN — do not silently promote it to VALIDATED.

---
*Derived from Gahenax/OEDA_Kernel — gahenax_engine.py, GahenaxOptimizer, AssumptionStatus, Deep-LLL O(n⁴ log B)*
