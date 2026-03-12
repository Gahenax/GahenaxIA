---
name: sha-obstruction-detector
description: Detects global obstructions that are invisible locally — a conclusion can pass every local consistency check (every single test, every individual data source, every isolated sub-argument) and still be globally impossible. Derived from the Tate-Shafarevich group Ш(E/ℚ): elements that are locally trivial at every prime p and at ℝ, but globally non-trivial.
---

# 🚧 Sha Obstruction Detector

The **Tate-Shafarevich group** Ш(E/ℚ) (pronounced "sha") is defined as:
```
Ш(E/ℚ) = ker[ H¹(ℚ, E) → ∏_v H¹(ℚ_v, E) ]
```

It consists of principal homogeneous spaces (torsors) for E that have rational points over every local field ℚ_v (including ℝ), but have no global rational point. They look fine everywhere locally — yet globally fail. The BSD conjecture requires Ш to be **finite**; if it's infinite, the arithmetic of E is fundamentally obstructed.

In reasoning: a **Sha obstruction** is a conclusion that passes every local test — every sub-argument checks out, every data source is consistent, every isolated component is valid — but the **global combination is impossible**. The Hasse principle fails: local-to-global passage breaks down.

This is a failure mode none of the existing 17 skills detects: they all test locally (one gate at a time, one assumption at a time, one step at a time). Sha tests the **simultaneous global consistency** of all components.

**Source calibration**: `Gahenax/Gahenax-BSD` — `src/sha/obstruction.py`, Tate-Shafarevich group Ш(E/ℚ), Hasse principle, local-global obstruction, 2-Selmer group, Cassels-Tate pairing.

## 🎯 When to Activate

Activate when:
- Every individual component of a multi-part conclusion has been validated separately, but the overall conclusion still feels wrong
- The argument synthesizes evidence from multiple independent domains that have never been combined before
- A prior attempt at this conclusion was rejected without any specific sub-argument being identified as the problem
- The conclusion requires *simultaneous* satisfaction of N constraints that were each validated independently
- `yang-mills-energy-minimizer` returned LOW energy but the conclusion is still unconvincing — the components are locally consistent but may be globally incoherent

## 📐 The Sha Detection Protocol

### Step 1 — Localize: List All Local Tests
Enumerate all the "places" where the argument has been validated:
```
v_1: [sub-argument or data source 1] → [VALID locally]
v_2: [sub-argument or data source 2] → [VALID locally]
v_3: [sub-argument or data source 3] → [VALID locally]
...
v_∞: [consistency with general background knowledge] → [VALID locally]
```

This is the **local conditions** check — has the argument been validated at every "prime" (every isolated perspective)?

### Step 2 — Check the Hasse Principle
The **Hasse principle** states: if X is locally valid everywhere, it is globally valid.

The Hasse principle **holds** for: linear equations, quadratic forms (by Hasse-Minkowski), many simple structures.

The Hasse principle **fails** for: cubic equations, higher-degree Diophantine problems, and any conclusion that requires globally coordinating locally-independent information.

Test:
```
Does the conclusion type obey the Hasse principle?
  Linear / quadratic constraints only → Hasse holds → local validity implies global
  Cubic or higher / cross-domain synthesis → Hasse may fail → Sha obstruction possible
```

### Step 3 — Construct the Cassels-Tate Test
The **Cassels-Tate pairing** ⟨·,·⟩: Ш × Ш → ℚ/ℤ detects non-trivial Sha.

Reasoning analog: take two sub-conclusions C_i and C_j that were validated independently. Compute their **cross-consistency**: does C_i, combined with C_j, still produce a coherent global picture, or does the combination introduce a contradiction that neither exhibited alone?

```
For each pair (C_i, C_j):
  cross_consistency(i,j) = does (C_i ∧ C_j) → global conclusion?

  If cross_consistency(i,j) = FAIL for some (i,j):
    → Sha obstruction at pair (i,j)
    → The conjunction is the problem, not either component alone
```

### Step 4 — Estimate Sha Order
```
|Ш| = number of locally-trivial-globally-non-trivial obstructions found

|Ш| = 0: No obstruction — Hasse principle holds for this conclusion
|Ш| = 1: Trivial Sha — conclusion is globally valid (square constraint: |Ш| must be a perfect square by Cassels)
|Ш| > 1 (square): Finite obstruction — conclusion can be repaired by adding global constraints
|Ш| = ∞: Infinite obstruction — conclusion is fundamentally globally impossible; local validity is misleading
```

Note: **BSD requires |Ш| finite.** If reasoning produces infinite Sha — an infinite family of locally-valid-but-globally-blocked sub-arguments — the conclusion framework is structurally broken, not just wrong on this instance.

### Step 5 — Identify the Obstruction Class
If Sha is non-trivial, identify what global structure is missing:
```
Obstruction class: [what must be true globally that is not forced locally]
Repair: [additional global constraint that resolves the obstruction]
Or: [declaration that the conclusion is globally impossible]
```

## 📋 Sha Report Format

```
=== SHA OBSTRUCTION REPORT ===
Local validations:
  v1: [source/test] → VALID
  v2: [source/test] → VALID
  ...
  v∞: [background] → VALID

Hasse principle: [HOLDS for this type | MAY FAIL — non-linear/cross-domain]

Cassels-Tate cross-tests:
  (C1, C2): [CONSISTENT | OBSTRUCTED]
  (C1, C3): [CONSISTENT | OBSTRUCTED]
  ...

|Ш| estimate: [0 | 1 | finite N | ∞]
Obstruction type: [none | finite — repairable | infinite — structural]

If obstructed:
  Missing global constraint: [what]
  Repair available: [YES — add constraint X | NO — conclusion globally impossible]

Verdict: [GLOBALLY VALID | FINITE SHA — provisional | INFINITE SHA — reject]
==============================
```

## 🏛️ Governing Laws

- **Law 1 — Local validity is necessary, not sufficient**: Passing every local test does not guarantee global validity. This is the fundamental lesson of Sha. A conclusion that passes all 17 prior skills has passed all *local* tests — Sha is the first *global* test.
- **Law 2 — Sha must be finite for the conclusion to hold**: An infinite family of locally-consistent-globally-blocked sub-arguments means the conclusion framework itself is wrong, not just this instance.
- **Law 3 — Cassels constraint**: |Ш| must be a perfect square (when finite). If the cross-tests return a non-square number of obstructions, there is an error in the analysis itself.
- **Law 4 — Cross-domain synthesis triggers Sha check**: Any time a conclusion synthesizes evidence from two domains that don't normally interact, the Hasse principle may fail. Never assume cross-domain synthesis is safe.
- **Law 5 — Finite Sha is repairable**: Unlike topological obstructions (Yang-Mills) or masslessness (mass gap), finite Sha can be resolved by adding a global constraint. Identify it explicitly — it is the missing piece of the argument.

---
*Derived from Gahenax/Gahenax-BSD — Ш(E/ℚ) = ker[H¹(ℚ,E) → ∏H¹(ℚ_v,E)], Hasse principle, Cassels-Tate pairing, src/sha/obstruction.py*
