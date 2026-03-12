---
name: circuit-breaker-quarantine
description: Detects repeated failures of the same reasoning pattern and quarantines it for a window. After K consecutive failures of the same type, stop attempting and wait. When the quarantine window expires, enter half-open state — reset failure count and allow one probe attempt. Derived from CircuitBreaker in gahenax_gateway.py.
---

# ⚡ Circuit Breaker Quarantine

The `CircuitBreaker` in `gahenax_gateway.py` works as follows:
- Every skill has its own circuit breaker instance
- Each failure calls `record_failure()` — when `_failures ≥ threshold`, the circuit opens and `_quarantine_until = now + quarantine_window_s`
- While `time.time() < _quarantine_until`: the circuit is open — execution is BLOCKED for this skill
- When the window expires: **half-open** — `_failures` resets to 0, `_quarantine_until` resets to 0. One probe is allowed. Success → full reset. Failure → re-quarantine.

The critical insight: a skill that fails repeatedly is not just failing — it's **evidence that something systemic is wrong**. Continuing to retry burns UA budget and accumulates noise. The circuit breaker stops the waste and forces a diagnostic pause.

In reasoning: if the same type of reasoning step fails K times consecutively, it is quarantined. The system stops attempting that approach and enters a mandatory pause — during which the failure must be diagnosed, not retried.

**Source calibration**: `Gahenax/OEDA_GahenaxIA` — `backend/gahenax_app/core/gahenax_gateway.py:CircuitBreaker`, `FailurePolicy` (default threshold=3, quarantine=300s; strict: threshold=1, quarantine=600s).

## 🎯 When to Activate

Activate when:
- The same inferential step has failed 2+ times in the current session
- A sub-agent or external source has returned errors repeatedly
- A validation check (`mass-gap-estimator`, `hodge-rigidity-detector`) has returned RED consecutively
- Any loop of "attempt → fail → retry" is detected — this is the circuit breaker condition

**Key distinction from `monodromy-circuit-breaker`**: Monodromy detects circular reasoning (the argument loops back to its own premises). Circuit breaker detects repeated *execution failures* of a reasoning step — the step is not circular, it is genuinely blocked by external conditions or structural impossibility.

## 📐 The Circuit Breaker Protocol

### Step 1 — Per-Pattern Failure Tracking
Each reasoning pattern type has its own counter:
```
For each pattern_type P:
  failures[P] = [consecutive failure count]
  quarantine_until[P] = [timestamp or None]
```

Failure types include:
- `TOOL_ERROR`: A tool call returned an error
- `SCHEMA_VIOLATION`: The result didn't match the expected contract
- `UA_CAP_EXCEEDED`: Ran out of budget trying this pattern
- `TIMEOUT`: The step exceeded its time limit
- `SIDE_EFFECT_DENIED`: Authorization was denied
- `VALIDATION_RED`: Repeated RED from a skill like `hodge-rigidity-detector`

### Step 2 — Record Failure
```
On failure of pattern P:
  failures[P] += 1
  if failures[P] ≥ threshold:
    quarantine_until[P] = now + quarantine_window
    → CIRCUIT OPEN for P
```

**Default policy**: threshold=3, quarantine=300s (5 minutes)
**Strict policy**: threshold=1, quarantine=600s (10 minutes) — use when any failure is diagnostic

### Step 3 — Check Before Attempt
```
Before attempting pattern P:
  if now < quarantine_until[P]:
    remaining = quarantine_until[P] − now
    → BLOCKED — "Pattern P quarantined ({remaining}s remaining)"
    → DO NOT RETRY — wait or diagnose
```

### Step 4 — Half-Open After Window Expiry
```
if quarantine_until[P] > 0 AND now ≥ quarantine_until[P]:
  → HALF-OPEN: reset failures[P] = 0, quarantine_until[P] = None
  → Allow ONE probe attempt of P

  If probe succeeds: circuit fully closed — record_success()
  If probe fails:   circuit re-opens — quarantine_until[P] = now + quarantine_window
```

### Step 5 — Diagnostic During Quarantine
When a circuit is open, use the quarantine window to diagnose, not to wait passively:
```
Required diagnosis:
  1. What invariant is pattern P assuming that is being violated?
  2. Is the failure in the pattern itself or in its dependencies?
  3. Is an alternative pattern (Q) available that bypasses the failure?
  4. Should this circuit use STRICT policy (threshold=1)?

Diagnosis output:
  root_cause: [identified | unidentified]
  alternative_pattern: [P' | none available]
  policy_recommendation: [DEFAULT | STRICT | LOCKED]
```

## 📋 Circuit Breaker Report Format

```
=== CIRCUIT BREAKER STATUS ===
Pattern registry:
  P1 [type]:    failures=N/K  status=[CLOSED | OPEN (Xs) | HALF-OPEN]
  P2 [type]:    failures=N/K  status=[CLOSED | OPEN (Xs) | HALF-OPEN]
  ...

Active quarantines:
  P_k: QUARANTINED — Xs remaining
       Failure type: [error_class]
       Last error:   [detail]
       Diagnosis:    [root_cause | pending]
       Alternative:  [pattern Q | none]

Policy in use: [DEFAULT (threshold=3, 300s) | STRICT (threshold=1, 600s)]

Blocked attempts since session start: [N]
UA saved by blocking retries: [estimate]
================================
```

## 🏛️ Governing Laws

- **Law 1 — Never retry an open circuit**: When the circuit is open, executing the same pattern again is not persistence — it is burning UA on a known-blocked path. Block immediately and diagnose.
- **Law 2 — Half-open means one probe only**: After the quarantine window, one probe is allowed. Not a full resumption — a single test. If it fails, the circuit re-opens.
- **Law 3 — Per-pattern, not global**: Each reasoning pattern type has its own circuit breaker. A failure in pattern P does not quarantine pattern Q. The circuit breaker is specific, not catastrophic.
- **Law 4 — STRICT for any consequential failure**: If a single failure of a pattern is diagnostic (e.g., a security check failing once is enough reason to stop), use STRICT policy (threshold=1). The default (threshold=3) is for transient failures.
- **Law 5 — Circuit open = mandatory diagnosis**: The quarantine window is not idle time — it is required diagnostic time. An undiagnosed open circuit that just waits and then retries at half-open has learned nothing.

---
*Derived from Gahenax/OEDA_GahenaxIA — backend/gahenax_app/core/gahenax_gateway.py:CircuitBreaker, FailurePolicy.default() threshold=3/300s, FailurePolicy.strict() threshold=1/600s*
