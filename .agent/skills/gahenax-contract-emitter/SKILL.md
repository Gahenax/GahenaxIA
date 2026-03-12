---
name: gahenax-contract-emitter
description: Structures any conclusion as a valid Gahenax Contract output — 6 mandatory blocks (Technical Reframe, Rigor Exclusions, Lattice Status, Critical Assumptions, Closure Interrogatory, Verdict) with UA audit. Enforces the Imperative Filter. Core emission standard of OEDA_Kernel.
---

# 📋 Gahenax Contract Emitter

Every emission from Gahenax Core must pass through the Contract Module — a "Hardware Filter" that blocks narrative and imperative language, structures findings as falsifiable claims, and reports computational cost. A conclusion that bypasses the contract is a contract violation.

This skill enforces that structure at the reasoning level.

**Source calibration**: `Gahenax/OEDA_Kernel` — `docs/CONTRACT.md`, `gahenax_engine.py::GahenaxOutput`, `VerdictStrength`, `IMPERATIVE_BLOCKLIST`, UA audit format.

## 🎯 When to Activate

Activate before **any final emission** in domains where precision matters:
- Technical analysis or diagnostics
- Causal claims ("X causes Y")
- Recommendations (especially where the imperative filter applies)
- Any conclusion produced by FRONTIER or HARD zone processing
- When the user needs a structured deliverable, not a narrative response

## 📐 The Six Mandatory Blocks

### Block I — Technical Reframe
Restate the user's question using variables, relations, and neutral technical terminology. Strip all emotional, aesthetic, and narrative framing.

Bad: *"This is a fascinating question about whether AI will take over."*
Good: *"Let X = AI capability trajectory. Let Y = human task displacement rate. Query: does X → Y imply systemic displacement within bounded time T?"*

**Hard rule**: No metaphors, no adjectives of quality ("interesting", "important"), no first-person positioning.

### Block II — Rigor Exclusions
Explicitly declare the boundaries of the current analysis. What CANNOT be concluded and why.

Format:
```
- Cannot conclude [X] because [variable/evidence Y] is unavailable.
- NP-Hard components are not solved; they are governed within budget.
- [Anything that could be inferred but isn't evidentially supported]
```

**Hard rule**: This block is never empty. If it's empty, you haven't looked for the exclusions.

### Block III — Lattice Status (Findings)
List all findings with their status:
- `[PROVISIONAL]` — depends on unresolved assumptions
- `[RIGOROUS]` — reduced and validated against known basis

Format:
```
- [PROVISIONAL] F1: [finding statement]
- [RIGOROUS]    F2: [finding statement] (validated via [evidence])
```

### Block IV — Critical Assumptions (Shortest Vector Candidates)
The output of `lll-lattice-reducer` — the minimal set of OPEN assumptions that remain after reduction.

Format:
```
A1: [statement] → unlocks: [conclusion it enables]
A2: [statement] → unlocks: [conclusion it enables]
```

**Hard rule**: Maximum 3 assumptions (from `MAX_CRITICAL_ASSUMPTIONS = 3`). If more than 3 survive reduction, verdict must be `no_verdict`.

### Block V — Closure Interrogatory
Questions designed for immediate assumption resolution. Each question targets a specific assumption in Block IV. Must be structured — no open-ended narrative questions.

Types (from `ValidationAnswerType`):
- `BINARY`: Yes/No
- `NUMERIC`: Requires a number with unit
- `FACT`: Requires a source-backed factual answer
- `CHOICE`: One of N options

Format:
```
Q1 (BINARY → A1): [precise yes/no question that would validate A1]
Q2 (NUMERIC → A2): [what number, in what unit, would validate A2?]
```

### Block VI — Gahenax Verdict
The final verdict with strength declaration and UA audit.

Strength levels (from `VerdictStrength`):
- `no_verdict` — High entropy, no closure possible without interrogatory resolution
- `conditional` — Closure possible if Q1/Q2/... are resolved
- `rigorous` — Shortest Vector found and validated, no open assumptions remain

Format:
```
[CONDITIONAL] [Verdict statement — declarative, no imperatives]
UA Audit: spent=[X] | efficiency=[ΔS/UA]
Conditions: [A1 resolved as X, A2 resolved as Y]
```

## 🚫 The Imperative Filter

**BLOCKLIST** (from `IMPERATIVE_BLOCKLIST`): `deberías`, `compra`, `vende`, `haz`, `recomiendo`, `invierte` — and English equivalents: `should`, `buy`, `sell`, `do`, `recommend`, `invest`.

Any imperative verb in the Verdict is a **Hard Violation**. The contract only reports conditions and logical coherency — it does not issue directives.

Violation detection: scan Block VI for any of these before emitting.

## 📋 Full Contract Template

```
## Technical Reframe
[Variables, relations, neutral restatement]

## Rigor Exclusions
- [Cannot conclude X because Y missing]
- [...]

## Lattice Status (Findings)
- [PROVISIONAL] F1: [...]
- [RIGOROUS]    F2: [...]

## Critical Assumptions (Shortest Vector Candidates)
A1: [...] → unlocks: [...]
A2: [...] → unlocks: [...]

## Closure Interrogatory
Q1 (BINARY → A1): [...]
Q2 (NUMERIC → A2): [...]

## Gahenax Verdict
[no_verdict | conditional | rigorous]
[Statement — no imperatives]
UA Audit: spent=[X] | efficiency=[Y]
Conditions: [if conditional]
```

## 🏛️ Governing Laws

- **Law 1 — Contract always last**: The contract wraps the output — it doesn't replace the analysis. Run all prior skills first, then emit through the contract.
- **Law 2 — Exclusions are mandatory**: An emission with empty Block II is a contract violation. The system always has boundaries.
- **Law 3 — Verdict strength is earned**: `rigorous` requires zero OPEN assumptions in Block IV. Claiming `rigorous` with open assumptions is the most common contract violation.
- **Law 4 — UA audit is mandatory**: Every contract emission includes `spent_ua` and `efficiency` (ΔS/UA). No exceptions — this is the falsifiability guarantee.
- **Law 5 — Mode alignment**: In `EVERYDAY` mode (budget=6.0 UA, target=4.0 UA), prefer `conditional` verdicts over forcing `rigorous` with insufficient evidence.

---
*Derived from Gahenax/OEDA_Kernel — CONTRACT.md, gahenax_engine.py::GahenaxOutput, VerdictStrength, IMPERATIVE_BLOCKLIST, ValidationAnswerType*
