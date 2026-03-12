---
name: spectral-anomaly-alert
description: Detects when a reasoning chain or dataset is suspiciously over-consistent — a signal of motivated reasoning, cherry-picking, or confirmation bias — using spectral variance analysis calibrated against GUE/RMT baselines.
---

# 📡 Spectral Anomaly Alert

The OEDA_HodgeRigidity lab detected that Riemann zeros in T ∈ [6340, 6640] showed **41.6% less variance than Random Matrix Theory predicts** — too ordered, anomalous. Paradoxically, anomalies cut both ways: things can be wrong by being too chaotic *or* too clean.

This skill applies the same logic to reasoning: if an argument is suspiciously consistent, it may be cherry-picking. If a dataset shows no outliers, something is being hidden.

**Source calibration**: `Gahenax/OEDA_HodgeRigidity` — Hyperuniformity analysis, GUE baseline comparison.

## 🎯 When to Activate

Activate when:
- All evidence points in the same direction without a single counter-signal
- A chain of reasoning has no internal tensions or trade-offs
- Sources all agree perfectly (too much consensus can be manufactured)
- A conclusion feels airtight — zero loose ends
- Summarizing a large corpus and noticing no contradictions

## 📊 Variance Audit Protocol

**Step 1 — Compute Expected Variance**
For the domain at hand, ask: *how much disagreement, noise, or contradiction should normally exist?*
- Well-studied domains (physics, math): low natural variance expected
- Complex social/economic domains: high natural variance expected
- Empirical data with measurement: variance must be present

**Step 2 — Measure Observed Variance**
Scan the inputs/sources:
- Are there any outliers, dissenting studies, or edge cases?
- Are there any conditions under which C fails?
- Does the evidence span different methodologies, timeframes, or populations?

**Step 3 — Compute Compression Ratio**
```
CR = 1 - (observed_variance / expected_variance)

CR < 0.2  → NORMAL  — variance is within expected range
CR ∈ [0.2, 0.4) → WATCH  — mildly compressed, note it
CR ≥ 0.4  → ALERT  — hyperuniform, investigate source of compression
```

The 41.6% compression detected in OEDA is the RED threshold for this skill.

## 🚨 Alert Response

When CR ≥ 0.4:
1. **Name the compression**: What is being consistently absent from the picture?
2. **Hypothesize the cause**: Survivorship bias? Publication bias? Motivated framing? Scope limitation?
3. **Flag in output**: The response must explicitly note the anomalous consistency.
4. Do NOT treat over-consistent evidence as stronger evidence. Treat it as potentially filtered evidence.

## 🏛️ Governing Laws

- **Law 1 — Absence is data**: Missing counter-evidence is not neutral — it must be explained.
- **Law 2 — Too clean = suspicious**: A perfectly consistent argument is a weaker argument, not stronger.
- **Law 3 — Spectral echo check**: If the same pattern recurs at regular intervals across sources, investigate whether the sources are independent or derivative of each other.
- **Law 4 — GUE baseline**: In domains with known random baselines (markets, language, social behavior), deviation > 2σ from expected variance triggers the alert automatically.

---
*Calibrated against Gahenax/OEDA_HodgeRigidity — Hyperuniformity Signature, Riemann Spectral Analysis*
