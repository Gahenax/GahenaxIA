# Gahenax Core — Skill System Reference

## Overview

Skills are the atomic units of governed execution in Gahenax Core. Every capability that produces a side effect or consumes UA budget must be registered as a `SkillSpec` in the `SkillRegistry` and executed exclusively through the `ExecutionGateway`.

**Invariant**: Nothing executes directly. All skill invocations pass through the gateway.

---

## Risk Levels

Skills are classified into three risk tiers that control execution authorization:

| Level | Behavior | Use Case |
|-------|----------|----------|
| `AUTO` | Executes without confirmation | Read-only, zero side effects |
| `CONFIRM` | Requires explicit user confirmation | Writes to filesystem or external state |
| `LOCKED` | Never auto-executes; requires `AUDIT` mode + `risk_override=true` | Schema migrations, irreversible operations |

---

## Registered Skills (v1.1.1)

### `gahenax.query_ledger`
- **Risk**: `AUTO`
- **Description**: Read-only query of the CMR ledger. Returns stats and latest hash.
- **Inputs**: `window_n`
- **Output Schema**: `LedgerQueryResult`
- **UA Cost**: 0.5
- **Timeout**: 2000 ms
- **Side Effects**: none
- **Rollback**: none
- **Idempotent**: yes

### `gahenax.generate_snapshot`
- **Risk**: `CONFIRM`
- **Description**: Generates a signed CMR snapshot JSON and writes it to `snapshots/`.
- **Inputs**: `snapshot_label`
- **Output Schema**: `Snapshot`
- **UA Cost**: 1.5
- **Timeout**: 5000 ms
- **Side Effects**: `file:write`
- **Rollback**: best_effort
- **Idempotent**: yes

### `gahenax.migrate_ledger_schema`
- **Risk**: `LOCKED`
- **Description**: Applies a migration to the CMR SQLite schema. Irreversible without backup.
- **Inputs**: `migration_id`, `sql_patch`
- **Output Schema**: `MigrationResult`
- **UA Cost**: 4.0
- **Timeout**: 15000 ms
- **Side Effects**: `db:write`, `db:schema`
- **Rollback**: required
- **Idempotent**: yes (migration_id prevents double-application)
- **Dry Run Default**: yes (always starts simulated)

---

## Execution Flow

```
User → ExecutionRequest → ExecutionGateway
    1. Resolve skill from SkillRegistry
    2. Check circuit breaker (quarantine on repeated failure)
    3. Check idempotency cache (replay if duplicate request_id)
    4. Validate risk level vs. execution mode
    5. Validate UA budget vs. skill cost estimate
    6. Check CMR availability (required for side-effecting skills)
    7. Determine effective dry_run flag
    8. Delegate to ToolRunner
    9. Record result in CMR ledger
    10. Return ExecutionResult
```

---

## ExecutionRequest Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `request_id` | str | required | Idempotency key — unique per logical operation |
| `skill_id` | str | required | Target skill identifier |
| `inputs` | dict | `{}` | Input parameters matching `required_inputs` |
| `mode` | str | `GEM` | `GEM` \| `AUDIT` \| `EXPERIMENT` |
| `ua_budget` | float | `6.0` | Maximum UA spend allowed |
| `risk_override` | bool | `false` | Required for `LOCKED` skills in `AUDIT` mode |
| `dry_run` | bool | `false` | Simulate execution without applying side effects |

---

## ExecutionResult Fields

| Field | Description |
|-------|-------------|
| `status` | `OK` \| `FAIL` \| `PARTIAL` \| `BLOCKED` \| `DRY_RUN` |
| `outputs` | Skill-specific output payload |
| `evidence` | Result hash and any paths/diffs |
| `metrics` | `latency_ms`, `ua_spend`, `work_units` |
| `error_class` | Canonical error enum (see below) |
| `retryable` | Whether the caller may safely retry |
| `rollback_status` | Present if a rollback was attempted |

### Error Classes

| Class | Meaning |
|-------|---------|
| `SCHEMA_VIOLATION` | Unknown skill or malformed request |
| `UA_CAP_EXCEEDED` | Skill cost estimate exceeds `ua_budget` |
| `TIMEOUT` | Execution exceeded `timeout_ms` |
| `SIDE_EFFECT_DENIED` | Risk/mode gate blocked execution |
| `CIRCUIT_OPEN` | Skill quarantined by circuit breaker |
| `IDEMPOTENCY_REPLAY` | Result replayed from cache |
| `TOOL_ERROR` | Handler raised an exception |
| `CMR_UNAVAILABLE` | CMR not connected for side-effecting skill |

---

## Circuit Breaker Policy

Each skill has an independent circuit breaker:

- **Threshold**: 3 consecutive failures → skill quarantined
- **Quarantine window**: 300 seconds
- **Half-open reset**: automatic after window expires
- **Override**: none — quarantine is enforced by the gateway

To inspect circuit breaker status:
```python
gateway.status_report()
```

---

## Registering a New Skill

```python
from gahenax_app.core.gahenax_gateway import SkillSpec, RiskLevel, RollbackPolicy

registry.register(SkillSpec(
    skill_id="gahenax.my_skill",
    intent_tags=["tag1", "tag2"],
    description="One-sentence description.",
    risk_level=RiskLevel.CONFIRM,
    required_inputs=["input_a"],
    output_schema="MyOutputModel",
    ua_cost_estimate=1.0,
    timeout_ms=5000,
    idempotent=True,
    side_effects=["file:write"],
    rollback=RollbackPolicy.BEST_EFFORT,
    enabled=True,
    dry_run_default=False,
))
```

Then register a handler with the ToolRunner:
```python
gateway._tool_runner.register_handler("gahenax.my_skill", my_handler_fn)
```

Where `my_handler_fn(inputs: dict, dry_run: bool) -> dict`.

---

## Rollback Policies

| Policy | Behavior |
|--------|----------|
| `none` | No rollback defined; side effects are permanent |
| `best_effort` | Rollback attempted but not guaranteed (e.g., delete written file) |
| `required` | Rollback must succeed; skill cannot be executed without a valid undo path |

`LOCKED` skills with destructive side effects (`db:schema`, `db:write`) must use `required`.

---

## Viewing the Registry

```bash
cd backend
python -m gahenax_app.core.skill_registry_bootstrap
```

Output includes the skill summary table and tamper-evident spec hashes.
