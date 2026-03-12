---
name: hodge-rigidity-detector
description: Evaluates the structural integrity of a reasoning chain using H/M/S metrics calibrated against OEDA_HodgeRigidity empirical data.
---

# 🧱 Hodge Rigidity Detector

This skill measures how well-anchored a reasoning chain is by computing three structural metrics — H (Rigidity), M (Monodromy), S (Singularity) — and emitting a Semaforo verdict before any conclusion is stated.

**Source calibration**: `Gahenax/OEDA_HodgeRigidity` — ChronosSemaforoModule, thresholds 1e-12 / 0.5.

## 🎯 When to Activate

Activate this skill before emitting any conclusion that:
- Involves causal claims ("X causes Y")
- Makes predictions about complex systems
- Synthesizes multiple sources into a single verdict
- Answers questions in high-stakes domains (legal, medical, financial, scientific)

## 📐 The H/M/S Metrics

**H — Rigidity (Roundoff Error)**
Measures accumulated logical imprecision across inference steps.
- Each step that infers beyond direct evidence adds +H
- Each step grounded in a cited source or observable fact subtracts H
- Threshold: GREEN ≤ 1e-2 | ORANGE (1e-2, 1e-1] | RED > 1e-1

**M — Monodromy (Circular Residue)**
Detects whether the argument loops back and relies on its own conclusion as evidence.
- Scan the argument graph: does any premise depend on the conclusion?
- Even indirect loops (A→B→C→A) count
- Threshold: GREEN = 0 loops | ORANGE = 1 indirect loop | RED ≥ 1 direct loop

**S — Singularity (Discreteness)**
Measures whether claims are falsifiable and discrete vs. continuous and unfalsifiable.
- "X is likely higher" → S = 0.2 (too continuous, hard to falsify)
- "X > threshold T under conditions C" → S = 0.9 (discrete, testable)
- Threshold: GREEN ≥ 0.7 | ORANGE [0.4, 0.7) | RED < 0.4

## 🚦 Semaforo Protocol

Before emitting the final response, compute:

```
H_score:  [value] → [GREEN | ORANGE | RED]
M_score:  [loops] → [GREEN | ORANGE | RED]
S_score:  [value] → [GREEN | ORANGE | RED]

Overall:  [GREEN | ORANGE | RED]
```

- **GREEN**: Emit conclusion normally.
- **ORANGE**: Emit conclusion with explicit caveats on the failing metric.
- **RED**: Do NOT emit conclusion. Return structured failure with reason.

## 🔑 Operational Laws

- **Law 1 — No silent degradation**: If any metric is RED, the response must say so explicitly.
- **Law 2 — H is additive**: Every hedge ("probably", "likely", "might") without evidence reference increments H.
- **Law 3 — M audit is mandatory**: Before concluding, trace the argument graph backwards once.
- **Law 4 — S minimum**: At least one claim in the response must be falsifiable (S ≥ 0.7).

---
*Calibrated against Gahenax/OEDA_HodgeRigidity | ChronosSemaforoModule v1.0*
