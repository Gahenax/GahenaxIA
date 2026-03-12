---
name: epistemic-blacklist
description: Maintains and enforces a registry of known-bad reasoning patterns — analogous to OEDA_HodgeRigidity's BLACKLIST.json — to prevent recurring logical failures from being re-examined as if they were new.
---

# 🚫 Epistemic Blacklist

`OEDA_HodgeRigidity` maintains a `BLACKLIST.json` of 37 exponent IDs that were evaluated, found invalid, and permanently excluded from re-examination without new evidence. This prevents wasting computational budget on known dead ends.

This skill applies the same principle to reasoning: known-bad argument patterns are registered, checked first, and blocked from re-entering as if fresh.

**Source calibration**: `Gahenax/OEDA_HodgeRigidity` — BLACKLIST.json, 37 entries, UA budget conservation.

## 🎯 When to Activate

Activate at the START of any reasoning task to check incoming arguments against the blacklist before investing UA budget. Also activate when:
- A familiar-sounding argument is being re-evaluated
- The same conclusion keeps emerging via different paths (may be a blacklisted attractor)
- A debate or question has a long history of failed resolution attempts

## 📋 The Blacklist Registry

Known-bad reasoning patterns, permanently flagged:

| ID | Pattern | Why Blacklisted | Failure Mode |
|----|---------|----------------|--------------|
| BL-01 | Appeal to complexity as proof | "This is too complex to be wrong" | Sophistication ≠ correctness |
| BL-02 | Consensus as truth | "Everyone agrees, therefore true" | Manufactured or survivor-biased consensus |
| BL-03 | Precision theater | Citing 6 decimal places on an estimate | False precision masks uncertainty |
| BL-04 | Absence of counter-evidence = confirmation | "No one has disproved it" | Unfalsifiable by design |
| BL-05 | Self-referential authority | "The system validates itself" | Monodromy loop (see monodromy-circuit-breaker) |
| BL-06 | Urgency collapse | "Decide now, no time to verify" | Bypasses H/M/S audit |
| BL-07 | Novelty bias | "New = better / more likely correct" | Recency as evidence |
| BL-08 | Analogy as proof | "It works like X, therefore it IS X" | Analogy is a map, not the territory |
| BL-09 | Hyperuniform evidence | All sources agree perfectly | Cherry-picking or source derivation (see spectral-anomaly-alert) |
| BL-10 | Single-path reasoning | Only one possible explanation explored | Ghost loci not scanned (see ghost-loci-reasoning) |

## 🔒 Blacklist Protocol

**Step 1 — Pre-scan incoming arguments**
Before beginning analysis, check if the core structure of the incoming argument matches any BL entry.

**Step 2 — Hard block**
If a BL pattern is detected:
- Name it explicitly: "This argument contains BL-[ID]: [pattern name]"
- Do NOT proceed to evaluate the argument on its merits
- Return: "This pattern is blacklisted. New evidence required to re-open."

**Step 3 — Conditional re-examination**
A blacklisted pattern may be re-examined ONLY if:
- New empirical evidence is provided that wasn't present when the pattern was first blacklisted
- The scope is materially different (different domain, different constraints)
- A formal falsification criterion is added that was absent before

## 🔧 Adding to the Blacklist

When a new pattern is identified as structurally invalid:
1. Assign next BL-ID
2. Name the pattern in one line
3. State why it fails (logical structure, not just intuition)
4. State the failure mode it produces

New entries require evidence of at least 2 independent failures before blacklisting.

## 🏛️ Governing Laws

- **Law 1 — Check first**: Blacklist scan runs before any other analysis. UA is not spent on dead ends.
- **Law 2 — No silent rehabilitation**: A blacklisted pattern cannot silently re-enter the reasoning chain. Re-examination must be declared.
- **Law 3 — Pattern, not conclusion**: Blacklist entries are structural patterns, not specific conclusions. The same conclusion can be valid via a non-blacklisted path.
- **Law 4 — Evidence threshold**: 2 independent documented failures required to add a new entry. Gut feeling is not evidence.

---
*Modeled on Gahenax/OEDA_HodgeRigidity — BLACKLIST.json, UA budget conservation protocol*
