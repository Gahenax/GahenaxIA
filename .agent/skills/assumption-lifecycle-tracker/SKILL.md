---
name: assumption-lifecycle-tracker
description: Tracks every assumption through its full lifecycle (OPEN → VALIDATED / INVALIDATED / REDUCED) across a multi-step reasoning session, preventing assumption drift — the silent promotion of unverified premises to facts. Derived from OEDA_Kernel's AssumptionStatus state machine and CMR append-only ledger.
---

# 📊 Assumption Lifecycle Tracker

In a long reasoning session, assumptions accumulate. If their status isn't tracked explicitly, two failure modes occur:
1. **Silent promotion**: An OPEN assumption is treated as VALIDATED downstream — conclusions are built on unverified premises.
2. **Zombie assumptions**: An INVALIDATED assumption continues influencing reasoning because its invalidation was never propagated.

OEDA_Kernel prevents this via the `AssumptionStatus` state machine and the CMR append-only ledger — every state transition is hashed and recorded.

This skill operationalizes that tracking discipline at the reasoning level.

**Source calibration**: `Gahenax/OEDA_Kernel` — `gahenax_engine.py::AssumptionStatus`, `Assumption` dataclass, `cmr.py::CMR.record_run()`, `input_fingerprint`, `evidence_hash`.

## 🎯 When to Activate

Activate at the start of any multi-step analysis where:
- More than 2 assumptions are required
- The analysis spans multiple rounds or tools
- A prior conclusion is being used as a premise in a new analysis
- The problem was classified as FRONTIER or HARD by `phase-transition-detector`

Also activate proactively when `lll-lattice-reducer` has run — the reduction output is the initial assumption register.

## 📐 Assumption States

Four states from `AssumptionStatus`:

### `OPEN`
The assumption is required but unverified. No evidence has been provided to validate or invalidate it. Every new assumption starts here.

**Rule**: An OPEN assumption can unlock a `conditional` verdict but never a `rigorous` one.

### `VALIDATED`
The assumption has been confirmed by explicit evidence. State the evidence source when transitioning to VALIDATED.

Transition: `OPEN → VALIDATED`
Requires: specific evidence reference (source, data point, logical proof)

### `INVALIDATED`
The assumption has been shown to be false. Any conclusions that depended on it must be re-evaluated.

Transition: `OPEN → INVALIDATED` or `VALIDATED → INVALIDATED`
Action required: propagate invalidation — mark all findings that depended on this assumption as `PROVISIONAL` or invalid.

### `REDUCED`
The assumption has been subsumed by a stronger assumption in the set (via `lll-lattice-reducer`). It is logically unnecessary.

Transition: `OPEN → REDUCED` (only during reduction)
Note: REDUCED is not false — it's redundant given another assumption.

## 📋 The Assumption Register

Maintain a live register throughout the session:

```
=== ASSUMPTION REGISTER ===
Session: [session_id / fingerprint]

ID  | Statement                          | Unlocks         | Status      | Evidence
----|------------------------------------|-----------------|-----------  |--------
A1  | [statement]                        | [conclusion]    | OPEN        | —
A2  | [statement]                        | [conclusion]    | VALIDATED   | [source]
A3  | [statement]                        | [conclusion]    | REDUCED     | subsumed by A2
A4  | [statement]                        | [conclusion]    | INVALIDATED | [counter-evidence]
===========================
Open assumptions: N
Validated: N
Reduced: N
Invalidated: N

Current verdict ceiling: [no_verdict | conditional | rigorous]
```

**Verdict ceiling rule**:
- Any OPEN assumptions → ceiling = `conditional`
- Any INVALIDATED assumptions with unresolved dependents → ceiling = `no_verdict` or `conditional`
- All assumptions VALIDATED or REDUCED → ceiling = `rigorous`

## 🔗 Propagation Protocol

When an assumption changes state, propagate the impact:

**On VALIDATED**:
- Check if this resolves the last OPEN assumption → upgrade verdict ceiling

**On INVALIDATED**:
- Find all findings that list this assumption in `depends_on`
- Downgrade them from `RIGOROUS` to `PROVISIONAL`
- Check if the verdict is now unsupported → downgrade to `conditional` or `no_verdict`
- Flag explicitly: *"A[N] invalidated — findings F[X], F[Y] retroactively downgraded to PROVISIONAL"*

**On REDUCED**:
- No propagation needed — a REDUCED assumption contributed nothing unique

## 📌 Session Fingerprinting (CNI)

For sessions with multiple turns, compute a session fingerprint before each round:
```
fingerprint = SHA256(sorted(assumption_ids + statuses + evidence_refs))
```

If the fingerprint is identical to a prior round: no new evidence has been processed. Do not re-run the same analysis — return the cached result (`IDEMPOTENCY_REPLAY`).

## 🏛️ Governing Laws

- **Law 1 — Every assumption is born OPEN**: No assumption enters the register as VALIDATED. It must earn that status.
- **Law 2 — Invalidation propagates immediately**: The moment A[N] is invalidated, its dependents are downgraded. No grace period, no deferred propagation.
- **Law 3 — Speculation is debt**: OPEN assumptions are computational debt. Name them explicitly and charge them against the verdict ceiling. Never let them hide.
- **Law 4 — MAX_CRITICAL = 3**: More than 3 OPEN assumptions after reduction → verdict must be `no_verdict`. This is a hard system limit from `gahenax_engine.py`.
- **Law 5 — Append-only ledger**: State transitions are recorded, not overwritten. A VALIDATED assumption that becomes INVALIDATED gets a new ledger entry — the VALIDATED entry stays, showing the full history.

---
*Derived from Gahenax/OEDA_Kernel — gahenax_engine.py::AssumptionStatus, Assumption dataclass, cmr.py::CMR, canonical_hash(), input_fingerprint*
