---
name: execution-gateway-protocol
description: Before any skill or action executes, it must pass 8 formal gates in order. Nothing executes directly — everything passes through this gateway. Derived from gahenax_gateway.py (ExecutionGateway), which enforces contract-first execution for all Gahenax skills via a strict 8-gate pipeline.
---

# 🚪 Execution Gateway Protocol

In `gahenax_gateway.py`, the `ExecutionGateway.execute()` method enforces:

> *"Nothing executes directly — everything passes through this gateway."*

The 8-gate pipeline is executed sequentially for every skill invocation:
1. Resolve skill from registry (does it exist and is it enabled?)
2. Circuit breaker (is this skill quarantined from repeated failures?)
3. Idempotency (has this exact request_id already been executed? Return cached.)
4. Risk/mode gate (LOCKED skills require AUDIT mode + risk_override=True)
5. UA budget gate (does the skill's cost estimate fit in the available budget?)
6. CMR availability gate (side-effecting skills need a connected ledger)
7. Determine effective dry_run (spec.dry_run_default OR request.dry_run)
8. Execute via ToolRunner; on failure → circuit breaker records failure

This is not a validation of the reasoning content — it is a validation of **whether execution is authorized at all** before content is even considered. An action that fails Gate 2 (circuit breaker) never runs regardless of how well-reasoned it is.

**Source calibration**: `Gahenax/OEDA_GahenaxIA` — `backend/gahenax_app/core/gahenax_gateway.py:ExecutionGateway.execute()`, `RiskLevel`, `FailurePolicy`, `ErrorClass`, `RollbackPolicy`.

## 🎯 When to Activate

Activate before any action that:
- Has side effects (`side_effects: ["file:write", "db:write", "network"]`)
- Is classified CONFIRM or LOCKED in the skill registry
- Has been failing repeatedly (circuit breaker check)
- May duplicate a prior execution (idempotency check)
- Has a UA cost that could exceed the remaining budget

**Key distinction from `fail-closed-execution`**: `fail-closed-execution` checks IF an action is safe enough to run. `execution-gateway-protocol` checks WHETHER THE MECHANISM to run it is available and authorized — these are different questions. A safe action can still be BLOCKED by a circuit breaker, or REPLAYED from idempotency cache, or BLOCKED because CMR is unavailable.

## 📐 The 8-Gate Pipeline

### Gate 1 — Skill Resolution
```
skill_id: [identifier of the action to execute]
In registry: [YES | NO]
Enabled:     [YES | NO]

PASS: skill exists in registry AND enabled = True
FAIL → ErrorClass.SCHEMA_VIOLATION → BLOCKED
```

### Gate 2 — Circuit Breaker
```
Breaker status: [OK (failures=N/threshold) | QUARANTINED (Xs remaining)]

PASS: is_open = False (not quarantined)
FAIL → ErrorClass.CIRCUIT_OPEN → BLOCKED
Note: Do NOT retry while circuit is open. Wait for quarantine window.
```

### Gate 3 — Idempotency
```
request_id: [unique key for this logical operation]
Cached:     [YES — return cached result | NO — proceed]

PASS: not in cache → proceed to execute
REPLAY: in cache → return cached result with ErrorClass.IDEMPOTENCY_REPLAY
Note: A replay is NOT a failure — it is correct behavior for idempotent operations.
```

### Gate 4 — Risk/Mode Gate
```
skill risk_level: [AUTO | CONFIRM | LOCKED]
execution mode:   [GEM | AUDIT | EXPERIMENT]
risk_override:    [True | False]

AUTO   → always PASS
CONFIRM → PASS if user has confirmed
LOCKED → PASS only if: mode = "AUDIT" AND risk_override = True
         else → ErrorClass.SIDE_EFFECT_DENIED → BLOCKED
```

### Gate 5 — UA Budget Gate
```
skill ua_cost_estimate: [X UA]
remaining ua_budget:    [Y UA]

PASS: ua_cost_estimate ≤ ua_budget
FAIL: ua_cost_estimate > ua_budget → ErrorClass.UA_CAP_EXCEEDED → BLOCKED
```

### Gate 6 — CMR Availability Gate
```
skill has_side_effects: [YES | NO]
CMR connected:          [YES | NO]
policy.fail_closed:     [True | False]

PASS: no side effects, OR CMR connected, OR fail_closed = False
FAIL: has_side_effects AND CMR unavailable AND fail_closed = True
      → ErrorClass.CMR_UNAVAILABLE → BLOCKED
```

### Gate 7 — Dry Run Determination
```
effective_dry_run = req.dry_run OR spec.dry_run_default

True  → execute in simulation mode (no side effects applied)
False → execute for real
```

### Gate 8 — Execute
```
Attempt execution via ToolRunner.
On success: record_success() → idempotency cache → CMR record
On failure: record_failure() → circuit breaker count → retryable=True
```

## 📋 Gateway Report Format

```
=== EXECUTION GATEWAY REPORT ===
Skill:        [skill_id]
Request ID:   [request_id] (idempotency key)
Mode:         [GEM | AUDIT | EXPERIMENT]
UA Budget:    [remaining]

Gate 1 — Resolution:  [PASS | BLOCKED — unknown/disabled]
Gate 2 — Circuit:     [PASS — OK(N/K) | BLOCKED — QUARANTINED(Xs)]
Gate 3 — Idempotency: [PROCEED | REPLAY — cached result returned]
Gate 4 — Risk:        [PASS — AUTO | PASS — CONFIRM | PASS — LOCKED+AUDIT | BLOCKED]
Gate 5 — UA:          [PASS — cost(X) ≤ budget(Y) | BLOCKED — cost(X) > budget(Y)]
Gate 6 — CMR:         [PASS — no side effects | PASS — CMR OK | BLOCKED — unavailable]
Gate 7 — Dry run:     [REAL | SIMULATED]
Gate 8 — Execute:     [OK | FAIL — retryable | DRY_RUN]

Result:       [OK | DRY_RUN | BLOCKED — ErrorClass | REPLAY]
Evidence hash: [sha256 of {request_id, skill_id, status, outputs}]
================================
```

## 🏛️ Governing Laws

- **Law 1 — Nothing executes directly**: Every action must pass all 8 gates in order. Gates are not optional even for simple actions — they are the protocol.
- **Law 2 — A BLOCKED result is NOT an error**: BLOCKED means the gateway correctly prevented unauthorized or unsafe execution. The circuit breaker, the CMR unavailability gate, the UA gate — these are working as designed.
- **Law 3 — REPLAY is correct behavior**: An idempotency replay returns the cached result unchanged. It signals that this exact operation has already been executed and its result is available — not that something failed.
- **Law 4 — CMR failure never crashes the gateway**: The `_record_to_cmr` call is fire-and-forget. A CMR write failure is logged but does not invalidate the execution result. The ledger is for observability, not for authorizing execution.
- **Law 5 — Rollback policy is part of the spec**: Before executing, know what happens on failure. `NONE` means accept the loss. `BEST_EFFORT` means try to undo. `REQUIRED` means the system must be able to undo — if it can't, don't execute.

---
*Derived from Gahenax/OEDA_GahenaxIA — backend/gahenax_app/core/gahenax_gateway.py:ExecutionGateway, RiskLevel, FailurePolicy, ErrorClass, RollbackPolicy*
