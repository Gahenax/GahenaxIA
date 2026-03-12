---
name: ghost-loci-reasoning
description: Scans the neighborhood of a proposed conclusion for near-miss alternatives that are plausible but structurally wrong, before committing to an answer.
---

# 👻 Ghost Loci Reasoning

In Mersenne prime search, "ghost loci" are exponent neighborhoods that look like prime candidates but fail certification. In reasoning, ghost conclusions are answers that *feel* right and cluster near the correct one — but are subtly wrong.

This skill mandates an explicit neighborhood scan before committing to any non-trivial conclusion.

**Source calibration**: `Gahenax/OEDA_HodgeRigidity` — `mersenne-ghost-discovery` skill, BLACKLIST.json protocol.

## 🎯 When to Activate

Activate when:
- The answer feels obvious or came too quickly
- The question has a well-known "trap" answer (common misconceptions)
- The domain has many near-synonyms or near-correct alternatives
- The conclusion is binary (yes/no, true/false) and high-stakes

## 🔍 Ghost Scan Protocol

For every proposed conclusion C, execute a 3-step neighborhood scan:

**Step 1 — Generate Ghost Candidates**
List 2-4 conclusions that are:
- Superficially similar to C (same domain, similar wording)
- Commonly confused with C
- C shifted by one variable, one timeframe, or one condition

**Step 2 — Apply Differential Test**
For each ghost candidate G:
- What evidence would distinguish C from G?
- Does the available evidence actually rule out G?
- If not: G is still live, do not commit to C yet.

**Step 3 — Commit or Escalate**
- If all ghosts are ruled out by evidence → commit to C, note the ghosts examined
- If one or more ghosts survive → report C as provisional, list surviving ghosts explicitly

## 📋 Ghost Report Format

```
Proposed conclusion: [C]

Ghost candidates scanned:
  G1: [description] → RULED OUT by [evidence]
  G2: [description] → RULED OUT by [evidence]
  G3: [description] → LIVE — cannot distinguish from available evidence

Verdict: PROVISIONAL / COMMITTED
```

## 🏛️ Governing Laws

- **Law 1 — Minimum 2 ghosts**: Every non-trivial conclusion must examine at least 2 ghost candidates.
- **Law 2 — BLACKLIST**: Known ghost patterns that recur in a domain must be logged and checked first. Never re-examine a ruled-out ghost from a prior session without new evidence.
- **Law 3 — No silent commitment**: If a ghost survives the differential test, the response must surface it — never bury it in confidence.
- **Law 4 — Speed is a red flag**: If the conclusion arrived in under one reasoning step, ghost scan is mandatory.

---
*Inspired by Gahenax/OEDA_HodgeRigidity — Mersenne Ghost Discovery Protocol*
