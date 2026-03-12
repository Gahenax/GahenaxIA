---
name: fail-closed-execution
description: Enforces the fail-closed principle for action-oriented conclusions — blocks any recommendation, side-effecting decision, or irreversible action unless explicit evidence is available. Derived from OEDA_Kernel's gateway architecture: "nothing executes directly, no evidence = no execution."
---

# 🔒 Fail-Closed Execution

The OEDA_Kernel `ExecutionGateway` implements a non-negotiable rule: **fail_closed = True by default**. In the absence of evidence, confirmation, or explicit authorization, the system blocks — it does not proceed optimistically. A gate that defaults to OPEN when information is missing is not a gate; it's a liability.

This skill operationalizes that principle at the reasoning level: before committing to any action-oriented conclusion, verify that all required gates pass.

**Source calibration**: `Gahenax/OEDA_Kernel` — `gahenax_gateway.py::ExecutionGateway`, `FailurePolicy.fail_closed=True`, `RiskLevel`, `ErrorClass`, `RollbackPolicy`. The gateway has 6 sequential gates before any skill executes.

## 🎯 When to Activate

Activate before any output that is:
- A recommendation for action ("do X", "use Y", "deploy Z")
- Irreversible (delete, publish, send, commit, purchase)
- Affecting shared state (other people, systems, or data)
- In a domain with asymmetric downside (security, legal, financial, medical)
- Based on a single source or unconfirmed assumption

**In doubt: fail closed.** The cost of blocking a valid action is low. The cost of executing an invalid one is high.

## 🚦 The Six Gateway Gates

Mirroring `ExecutionGateway.execute()` flow:

### Gate 1 — Skill Resolution (Evidence of Applicability)
*Is the requested action actually applicable to this situation?*

- Does the recommended action match the problem type?
- Is there explicit evidence that this action class solves this problem class?
- **BLOCK if**: Action is generic advice being applied without evidence of fit

→ `ErrorClass.SCHEMA_VIOLATION` analog: *"Action type does not match problem schema"*

### Gate 2 — Circuit Breaker (Domain Failure History)
*Has this approach already failed in this domain?*

- Has the same action/recommendation been tried and failed in similar contexts?
- Is the domain one where common approaches have high failure rates?
- **BLOCK if**: Same approach failed ≥ 3 times in this domain without new evidence

→ `ErrorClass.CIRCUIT_OPEN` analog: *"Domain approach quarantined — 3 prior failures"*

### Gate 3 — Idempotency Check (Replay Detection)
*Is this the same conclusion being reached for the second time without new evidence?*

- Has this exact recommendation already been made in this session?
- Is new evidence actually present, or is this a loop?
- **BLOCK if**: Identical conclusion reached twice without new inputs

→ `ErrorClass.IDEMPOTENCY_REPLAY` analog: *"Conclusion replayed without new evidence"*

### Gate 4 — Risk / Mode Gate (Authorization Level)
*Is the risk level of this action appropriate for the current authorization mode?*

Risk levels (from `RiskLevel`):
- `AUTO`: Low-stakes, reversible — proceed without confirmation
- `CONFIRM`: Medium-stakes — state the action explicitly and require acknowledgment
- `LOCKED`: High-stakes, irreversible — require explicit AUDIT mode + risk_override

**BLOCK if**: LOCKED-level action attempted without explicit authorization

→ `ErrorClass.SIDE_EFFECT_DENIED` analog

### Gate 5 — UA Budget Gate (Cost vs. Available Budget)
*Does the cost of this action/analysis fit within the declared budget?*

- Has the effort required been explicitly estimated?
- Does that estimate fit the session's UA budget?
- **BLOCK if**: Estimated cost > available budget — do not begin actions that cannot complete

→ `ErrorClass.UA_CAP_EXCEEDED` analog

### Gate 6 — CMR Availability (Auditability Requirement)
*Can this action be recorded and audited?*

- For side-effecting decisions: is there a way to log what was decided and why?
- For irreversible actions: is the decision documented with evidence hash?
- **BLOCK if**: Side-effecting action with no audit trail possible

→ `ErrorClass.CMR_UNAVAILABLE` analog

## 📋 Gate Report Format

```
=== FAIL-CLOSED GATE CHECK ===
Gate 1 — Applicability:   [PASS | BLOCK] — [reason]
Gate 2 — Circuit Breaker: [PASS | BLOCK] — [reason]
Gate 3 — Idempotency:     [PASS | BLOCK] — [reason]
Gate 4 — Risk Level:      [AUTO | CONFIRM | LOCKED] — [reason]
Gate 5 — UA Budget:       [PASS | BLOCK] — est=[X] UA, budget=[Y] UA
Gate 6 — Auditability:    [PASS | BLOCK] — [reason]

Gates passed: N/6
Verdict: [EXECUTE | EXECUTE (CONFIRM REQUIRED) | BLOCK]
Error class: [if blocked]
Rollback policy: [none | best_effort | required]
==============================
```

## 🏛️ Governing Laws

- **Law 1 — Fail closed is the default**: When in doubt about whether to block, block. Recoverability matters more than throughput.
- **Law 2 — Dry-run before irreversible**: Any action classified as LOCKED must be described in dry-run form first: "what would happen if executed" before "execute."
- **Law 3 — Rollback policy is declared upfront**: Before executing any CONFIRM or LOCKED action, declare the rollback policy: `none`, `best_effort`, or `required`. Never realize post-hoc that an action was unrollbackable.
- **Law 4 — Circuit stays open after 3 failures**: Three failures in a domain without new evidence = quarantine. The same approach tried a 4th time without new evidence is not persistence; it's a loop.
- **Law 5 — CONFIRM is not LOCKED**: Requiring acknowledgment is not the same as requiring full AUDIT authorization. Don't over-escalate — it makes the gates meaningless if everything is LOCKED.

---
*Derived from Gahenax/OEDA_Kernel — gahenax_gateway.py::ExecutionGateway, FailurePolicy, RiskLevel, ErrorClass, RollbackPolicy, CircuitBreaker*
