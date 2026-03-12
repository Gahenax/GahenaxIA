---
name: adversarial-gate-validator
description: Runs five adversarial validation tests on any conclusion before emission — directly derived from P-ATLAS-NP's five-gate protocol for rejecting structurally fragile findings.
---

# ⚔️ Adversarial Gate Validator

P-ATLAS-NP validates every discovered "v-vector" (structural signature) through five adversarial gates before accepting it as real. A conclusion that doesn't survive all five gates is an artifact, not a discovery.

This skill applies the same five gates to reasoning conclusions: if a conclusion is real, it must survive all five attacks.

**Source calibration**: `Gahenax/P-ATLAS-NP` — `src/gates/adversarial.py`, NPX-PROD-0.1 campaign.

## 🎯 When to Activate

Activate before emitting any conclusion that:
- Claims to identify a pattern, trend, or causal relationship
- Will be used as a basis for a decision or recommendation
- Emerged from a single line of analysis
- Feels "clean" or confirms prior expectations

## ⚔️ The Five Gates

### Gate 1 — Semantics
*Does the conclusion mean something, or is it noise?*

Test: Construct a null hypothesis — what would the data/argument look like if there were NO real pattern? Is the conclusion distinguishable from that null?

- **PASS**: Conclusion is clearly differentiated from the null case
- **FAIL**: Normalized discrimination score < 0.01 (as in NPX-PROD-0.1 — the campaign's semantic gate failed at 0.0065)

### Gate 2 — Permutation Invariance
*Does the conclusion hold regardless of how things are labeled?*

Test: Rename the key variables, swap the order of arguments, reframe the question differently. Does the same conclusion emerge?

- **PASS**: Conclusion is stable across relabeling
- **FAIL**: Conclusion depends on a specific framing or variable name

### Gate 3 — Scale Generalization
*Does it hold at different scales, or only in the tested range?*

Test: If the conclusion was reached on a small sample / simple case, does it hold for larger / more complex versions? If on large scale, does it hold for simpler cases?
(P-ATLAS-NP tests N=80 → N=120)

- **PASS**: Conclusion holds across at least 2 different scales
- **FAIL**: Conclusion is scale-specific without explanation

### Gate 4 — Generator Drift
*Does it hold regardless of how the problem was generated?*

Test: Was the evidence/problem produced by one specific method, source, or framing? Does the conclusion hold if the generating process changes?

- **PASS**: Conclusion validated against at least 2 independent data sources or generators
- **FAIL**: All evidence comes from a single generator / source family

### Gate 5 — Perturbation Robustness
*Does it survive small noise, or does it collapse at 2% change?*

Test: Introduce a small perturbation (change ~2% of the input conditions, add one counterexample, modify one assumption). Does the conclusion survive?

- **PASS**: Conclusion stable under minor perturbation
- **FAIL**: Conclusion collapses under minimal change (as in NPX-PROD-0.1 — vector collapsed at 2% graph modification)

## 📋 Gate Report Format

```
=== ADVERSARIAL GATE REPORT ===
Gate 1 — Semantics:      [PASS | FAIL] — [reason]
Gate 2 — Permutation:    [PASS | FAIL] — [reason]
Gate 3 — Scale:          [PASS | FAIL] — [reason]
Gate 4 — Generator:      [PASS | FAIL] — [reason]
Gate 5 — Perturbation:   [PASS | FAIL] — [reason]

Gates passed: N/5
Verdict: [ACCEPTED | PROVISIONAL (N/5) | REJECTED]
===============================
```

- **5/5**: Emit conclusion as ACCEPTED
- **3-4/5**: Emit as PROVISIONAL — name the failing gates
- **< 3/5**: REJECT — do not emit the conclusion; report gates failed

## 🏛️ Governing Laws

- **Law 1 — No cherry-gate**: All 5 gates must be run. Skipping a gate because it's "obvious" it will pass is not allowed.
- **Law 2 — Failure is informative**: A failed gate is not just a rejection — it tells you *what kind* of fragility the conclusion has. Always name it.
- **Law 3 — Semantics gate first**: If Gate 1 fails (conclusion is noise), stop. Do not run the other four.
- **Law 4 — Production standard**: NPX-PROD-0.1 was rejected for failing Gate 1 (score 0.0065) and Gate 5 (collapse at 2%). These are the real thresholds — being "close" is not passing.

---
*Derived from Gahenax/P-ATLAS-NP — adversarial.py, five-gate validation protocol*
