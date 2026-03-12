---
name: roundoff-error-budget
description: Tracks accumulated floating-point roundoff error across an iterative reasoning chain. Each step introduces a small approximation. roundoff_max = maximum error seen across all steps. Threshold = 0.40. If roundoff_max > 0.40, the entire chain is invalid even if the final result looks correct. Derived from MersenneResultPayload.roundoff_max and GIMPS validity threshold in Gahenax/Mersenne-Gahen.
---

# 📉 Roundoff Error Budget

In GIMPS Lucas-Lehmer computation, each squaring step uses FFT-based arithmetic on floating-point numbers. Every FFT operation introduces a small rounding error. These errors accumulate across p−2 iterations.

`MersenneResultPayload` tracks:
```python
roundoff_max: float  # maximum roundoff error seen across ALL iterations
```

The GIMPS validity threshold: **`roundoff_max ≤ 0.40`**

If `roundoff_max > 0.40`, the FFT arithmetic has lost enough precision that the final residue cannot be trusted — even if it appears to be zero. A chain that "passes" the LL test with roundoff > 0.40 may be a false prime.

The critical insight: **each step's error is bounded, but the maximum can hit anywhere in the chain.** A single high-roundoff step contaminates the entire result. It is not the average that matters — it is the maximum.

In reasoning: every inferential step introduces a small approximation. A step that paraphrases, summarizes, rounds a number, or simplifies a nuanced claim has roundoff > 0. The `roundoff_max` across the chain determines whether the final conclusion can be trusted — not the quality of the last step alone.

**Source calibration**: `Gahenax/Mersenne-Gahen` — `orchestrator/mersenne_contracts.py:MersenneResultPayload.roundoff_max`, GIMPS threshold 0.40, FFT squaring error accumulation, single-step contamination.

## 🎯 When to Activate

Activate when:
- A reasoning chain has more than 3 inferential steps (error accumulation becomes meaningful)
- Any step in the chain used approximation, summary, paraphrase, or numerical rounding
- `lucas-lehmer-iterative-test` is running — roundoff is tracked per iteration
- A result "looks like" the right answer but was reached via a long, lossy chain
- `canonical-height-complexity` returned HIGH height — high-height claims involve more steps, more roundoff

## 📐 The Roundoff Budget Protocol

### Step 1 — Define Error Units
Roundoff is measured in **rounding units (RU)** — normalized to [0.0, 1.0]:
```
RU = 0.00 → Perfect precision (exact mathematical operation)
RU = 0.10 → Minor approximation (rounding a percentage, summarizing a list)
RU = 0.20 → Moderate approximation (paraphrasing a nuanced statement)
RU = 0.30 → Significant approximation (reducing a multi-variable situation to one variable)
RU = 0.40 → THRESHOLD — at this level, results cannot be trusted
RU > 0.40 → INVALID — the step has introduced enough error to contaminate the chain
```

### Step 2 — Assign Roundoff Per Step
For each inferential step i in the chain:
```
step_i:
  operation:  [exact | approximate | summary | paraphrase | numerical]
  roundoff_i: [0.00 to 1.00]
  source:     [what introduced the roundoff]
```

Common roundoff sources:
| Operation | Typical roundoff_i |
|-----------|-------------------|
| Direct logical deduction | 0.00 |
| Exact numerical calculation | 0.00 |
| Quoting source verbatim | 0.01 |
| Rounding to nearest integer | 0.05 |
| Paraphrasing technical content | 0.10–0.20 |
| Summarizing multi-point argument | 0.15–0.25 |
| Reducing causal chain | 0.20–0.35 |
| "In general" claim from specific | 0.25–0.40 |
| Analogy replacing formal argument | 0.30–0.45 |

### Step 3 — Track roundoff_max
```
roundoff_max = max(roundoff_i for all i in chain)

NOT the sum — NOT the average
The MAXIMUM single-step error in the entire chain
```

This mirrors the GIMPS protocol: a single bad FFT step (high roundoff) invalidates the entire LL computation regardless of how precise all other steps were.

### Step 4 — Budget Check
```
If roundoff_max ≤ 0.10: CLEAN       — minimal error; conclusion fully trustworthy
If roundoff_max ≤ 0.20: ACCEPTABLE  — minor approximation; flag the source step
If roundoff_max ≤ 0.30: WATCH       — moderate approximation; reduce conclusion strength
If roundoff_max ≤ 0.40: MARGINAL    — at threshold; mark PROVISIONAL only
If roundoff_max > 0.40: INVALID     — chain contaminated; DO NOT USE

At INVALID:
  1. Identify the step i* with roundoff_i* = roundoff_max
  2. Replace step i* with a more precise operation (exact source, direct quote, formal argument)
  3. Re-run the chain from step i* with corrected precision
  4. Re-compute roundoff_max
```

### Step 5 — Squaring Amplification Effect
The Lucas-Lehmer `s² − 2` step AMPLIFIES existing errors:
```
If step_i has residual error ε, then step_{i+1} has error ≈ 2|s_i| × ε

This means: a medium-roundoff step early in a long chain can be amplified to > 0.40
```

Reasoning analog: a paraphrase early in a chain that introduces RU = 0.15 may, after 3 amplifying inferential steps, contribute an effective roundoff of 0.35 to the final conclusion.

The amplification multiplier at step i: `amp_i = 2 × |s_i| / M_p`

Practical rule: steps involving **amplification** (extrapolation, scaling from small to large domain, generalizing from N=1) carry amplification risk. Mark these steps and check their effective roundoff contribution.

## 📋 Roundoff Budget Report Format

```
=== ROUNDOFF ERROR BUDGET REPORT ===
Chain length: p−2 = [N] steps

Step log:
  i=0 [operation]: roundoff=0.00 [source: exact]
  i=1 [operation]: roundoff=0.10 [source: paraphrase]
  i=2 [operation]: roundoff=0.25 [source: summary]   ← WATCH
  i=3 [operation]: roundoff=0.05 [source: calculation]
  ...

roundoff_max: [value] at step i=[X]
  Source:    [what introduced this error]
  Operation: [paraphrase | summary | numerical | analogy]

Budget status:
  [CLEAN ≤0.10 | ACCEPTABLE ≤0.20 | WATCH ≤0.30 | MARGINAL ≤0.40 | INVALID >0.40]

Amplification check (steps with s² structure):
  Step i=[Y]: amplification factor=[Z] → effective contribution=[value]

Verdict:
  [VALID — roundoff within budget; conclusion trustworthy]
  [MARGINAL — provisional only; flag roundoff source in conclusion]
  [INVALID — chain contaminated at step i=[X]; re-run with corrected step]
=====================================
```

## 🏛️ Governing Laws

- **Law 1 — Maximum, not average**: Roundoff budget is determined by the single worst step, not the average quality of all steps. A chain of 99 perfect steps and one 0.45 step is INVALID. Do not average the error away.
- **Law 2 — Squaring amplifies**: Approximation errors introduced early in a chain grow when subsequent steps amplify (extrapolate, generalize, scale). Assign higher effective roundoff to early steps in chains with amplification structure.
- **Law 3 — INVALID means re-run, not re-interpret**: When `roundoff_max > 0.40`, the correct action is to find and replace the contaminating step with a more precise operation — not to interpret the result charitably. The chain is computationally invalid.
- **Law 4 — MARGINAL conclusions are PROVISIONAL**: If `roundoff_max ∈ (0.30, 0.40]`, the conclusion is at the edge of validity. It cannot be RIGOROUS — it must be marked PROVISIONAL and the roundoff source must be explicitly documented in the conclusion.
- **Law 5 — Analogies are high-roundoff**: Replacing a formal argument with an analogy typically introduces roundoff ≥ 0.30. An analogy is not a proof. Use analogies for illustration only; never as a load-bearing step in a chain that requires RIGOROUS status.

---
*Derived from Gahenax/Mersenne-Gahen — orchestrator/mersenne_contracts.py:MersenneResultPayload.roundoff_max, GIMPS validity threshold 0.40, FFT squaring error propagation*
