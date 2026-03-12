---
name: bsd-dual-measurement-checker
description: Validates a conclusion by computing it via two structurally independent methods and comparing. Agreement strengthens confidence. Disagreement is itself the finding — one method is wrong, and the disagreement reveals which. Derived from the core BSD insight: rank(E(ℚ)) must equal ord_{s=1} L(E,s), two entirely different measurements of the same quantity.
---

# ⚖️ BSD Dual Measurement Checker

The Birch and Swinnerton-Dyer conjecture asserts that the **rank** of an elliptic curve — the number of independent rational points, computed by pure group theory — must equal the **order of vanishing** of the L-function at s=1, computed by complex analysis of an Euler product over primes. These are two completely different mathematical worlds measuring the same integer.

If they agree: the conjecture holds for this curve, and both measurements corroborate each other.
If they disagree: one of them is wrong — and the disagreement is precisely the falsifying evidence the BSD search engine is looking for.

This skill applies the same principle to reasoning: **never trust a single measurement of a critical quantity.** If a conclusion can be reached by two structurally independent methods, compute both. Agreement is evidence. Disagreement is a discovery.

**Source calibration**: `Gahenax/Gahenax-BSD` — `src/bsd/rank_estimator.py`, `src/lfunction/vanishing_order.py`, rank(E(ℚ)) vs. ord_{s=1} L(E,s), parity conjecture (root number), Cremona database cross-validation.

## 🎯 When to Activate

Activate when:
- A conclusion is high-stakes and rests on a single chain of reasoning
- Two different methods of reaching the conclusion are available (or can be constructed)
- A prior conclusion needs to be verified before it can serve as a downstream premise (Δ < 0.3 from `mass-gap-estimator`)
- The argument crosses domain boundaries — algebraic argument about something normally measured empirically, or vice versa

**Key distinction from Adversarial Gate 4 (generator drift)**: Gate 4 checks if the *same* conclusion holds across different data *sources*. BSD dual measurement requires two structurally *different computational methods* — not just different sources, but different formal approaches to the same quantity.

## 📐 The Dual Measurement Protocol

### Step 1 — Identify the Quantity
What is the core quantity being claimed? Express it as a single measurable value:

```
Q = [the specific quantity — a rank, a probability, a count, a threshold]
```

BSD analog: Q = rank(E(ℚ)) = ? and independently ord_{s=1} L(E,s) = ?

### Step 2 — Method A: Direct/Algebraic Measurement
Compute Q by the most direct available method — working directly with the objects in question.

```
Method A: [name the method]
  Computation: [how it works]
  Result: Q_A = [value]
  Confidence: [HIGH | MEDIUM | LOW]
  Assumptions required: [list]
```

BSD analog: count the independent generators of E(ℚ) via 2-descent.

### Step 3 — Method B: Indirect/Analytic Measurement
Compute Q by a structurally different method — one that encodes the same information differently.

```
Method B: [name the method]
  Computation: [how it works]
  Result: Q_B = [value]
  Confidence: [HIGH | MEDIUM | LOW]
  Assumptions required: [list]
```

BSD analog: compute ord_{s=1} L(E,s) via the functional equation and numerical approximation.

**Independence requirement**: Methods A and B must not share assumptions. If they share a key assumption, they are not independent measurements — they are the same measurement twice.

### Step 4 — Compare and Classify
```
If Q_A = Q_B:
  → AGREEMENT — mutual corroboration; confidence multiplied
  → Confidence = max(conf_A, conf_B) + corroboration bonus

If Q_A ≠ Q_B:
  → DISAGREEMENT — one method is wrong; the gap is the finding
  → Report: |Q_A − Q_B| = [gap]
  → Diagnose: which method's assumptions are more fragile?
  → The weaker method's failure reveals [what]
```

### Step 5 — Parity Check (BSD Bonus)
BSD has the **parity conjecture**: the root number W(E) ∈ {+1, −1} constrains the rank to be even (W=+1) or odd (W=−1). This is a *fast* pre-check before running full computation.

Reasoning analog: before running both full methods, check if there is a **parity constraint** — a fast necessary condition that the conclusion must satisfy. If the parity fails, full computation is unnecessary.

```
Parity constraint: [fast necessary condition for Q to be valid]
Parity test: [PASS | FAIL]
If FAIL → abort both methods; report parity violation as sufficient falsification
```

## 📋 Dual Measurement Report Format

```
=== BSD DUAL MEASUREMENT REPORT ===
Quantity Q: [description]

Method A: [name]
  Result:     Q_A = [value]
  Confidence: [HIGH | MEDIUM | LOW]
  Key assumptions: [list]

Method B: [name]
  Result:     Q_B = [value]
  Confidence: [HIGH | MEDIUM | LOW]
  Key assumptions: [list]

Independence: [CONFIRMED — no shared assumptions | PARTIAL — shared: X]

Parity check: [PASS | FAIL | N/A]

Comparison: Q_A [= | ≠] Q_B
  Gap: |Q_A − Q_B| = [value]

Verdict:
  [AGREEMENT — confidence reinforced]
  [DISAGREEMENT — gap = [value]; weaker method: [A|B]; failure reveals: [finding]]
====================================
```

## 🏛️ Governing Laws

- **Law 1 — Independence is mandatory**: Two methods that share a key assumption are not dual measurements — they are one measurement with extra steps. The independence check is not optional.
- **Law 2 — Disagreement is a finding, not a failure**: When Q_A ≠ Q_B, the dual measurement has succeeded at its actual job — it found a discrepancy. Report it as a discovery, not an error.
- **Law 3 — Parity first**: Always check fast necessary conditions before running expensive measurements. A parity violation makes both full computations unnecessary.
- **Law 4 — Agreement multiplies confidence**: Two independent methods agreeing is strictly stronger than one method's confidence. The probability that both are wrong in the same direction is the product of their individual error rates.
- **Law 5 — Weak before strong**: Like weak BSD before strong BSD, validate the qualitative agreement (same direction, same order of magnitude) before worrying about exact numerical agreement.

---
*Derived from Gahenax/Gahenax-BSD — rank(E(ℚ)) vs. ord_{s=1} L(E,s), parity conjecture W(E) ∈ {±1}, Cremona cross-validation, src/bsd/rank_estimator.py*
