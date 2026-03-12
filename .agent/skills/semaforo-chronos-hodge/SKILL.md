---
name: semaforo-chronos-hodge
description: Longitudinal Hodge rigidity audit over a sliding window of N sessions. Classifies each session into GREEN/YELLOW/ORANGE/RED by H_rigidity thresholds. Population-level health monitoring triggers recalibration when ORANGE > 30% or any RED appears. Extends hodge-rigidity-detector (point-in-time) to temporal population tracking. Derived from the semaforo command in gahenax_ops.py (Chronos-Hodge v2.0).
---

# 🚦 Semáforo Chronos-Hodge

The `semaforo` command in `gahenax_ops.py` implements the **Chronos-Hodge v2.0** audit protocol. It queries the last N entries from the CMR ledger and classifies each by `h_rigidity`:

```python
if not valid or h > 1e-8:
    label = "RED   — GHOST"          # Contract invalid OR extreme drift
elif h <= 1e-14:
    label = "GREEN — STRUCTURAL"     # Maximum rigidity
elif h <= 1e-11:
    label = "YELLOW — ISLAND-T"      # Tidal island; drift warning
else:
    label = "ORANGE — DRIFT-WARN"    # Active drift; recalibration needed
```

Population-level triggers:
- Any RED: `"CRITICAL: Ghosts detected. Integrity compromised."` → exit code 2
- ORANGE > 30% of window: `"WARNING: High drift detected. Recalibration recommended."`
- Otherwise: `"SYSTEM HEALTH: OPTIMAL (Chronos-Hodge Stable)"`

**Key distinction from `hodge-rigidity-detector`**: `hodge-rigidity-detector` is point-in-time — it checks the current reasoning session's H, M, S values and produces a semáforo. **Semáforo Chronos-Hodge** is temporal — it tracks the distribution of H_rigidity over the last N sessions and detects systematic degradation that no single-session check would reveal.

A session can be GREEN individually but be part of a population trending toward ORANGE. The Chronos element captures this.

**Source calibration**: `Gahenax/OEDA_GahenaxIA` — `gahenax_ops.py:semaforo`, Chronos-Hodge v2.0, CMR `h_rigidity` field, `contract_valid` boolean, default window N=20.

## 🎯 When to Activate

Activate when:
- A reasoning session is being evaluated after multiple prior sessions on the same problem domain
- `hodge-rigidity-detector` has returned YELLOW/ORANGE recently — check if it's a trend
- Before committing a high-stakes conclusion that depends on a stable reasoning track record
- As a periodic audit (every 20 sessions) of the system's epistemic health
- When a user reports that recent conclusions "feel different" — check for systematic drift

## 📐 The Chronos-Hodge Protocol

### Step 1 — Define the Window
```
window_n: [N sessions to audit, default 20]
scope:    [specific problem domain | all sessions]
```

### Step 2 — Collect and Classify
For each session i in the last N sessions:
```
h_i         = H_rigidity of session i
valid_i     = contract_valid of session i
fingerprint = input_fingerprint[:8] (for identification)

Classification:
  if not valid_i OR h_i > 1e-8:  → RED    (GHOST)
  elif h_i ≤ 1e-14:               → GREEN  (STRUCTURAL)
  elif h_i ≤ 1e-11:               → YELLOW (ISLAND-T)
  else (h_i ≤ 1e-8):              → ORANGE (DRIFT-WARN)
```

**Band definitions:**
- `GREEN (H ≤ 1e-14)`: Structurally stable. Conclusions are well-supported, minimal drift. The system is in "Chronos-Hodge Stable" state.
- `YELLOW (H ≤ 1e-11)`: Tidal Island. Locally stable but exposed to drift forces. The next session may tip to ORANGE.
- `ORANGE (H ≤ 1e-8)`: Active drift. Significant structural weakening. Recalibration is needed before this session's conclusions can be used confidently.
- `RED (H > 1e-8 OR !valid)`: Ghost. The session produced an invalid contract or extreme drift. Its conclusions must be quarantined.

### Step 3 — Compute Population Statistics
```
count_GREEN  = |{i : classification_i = GREEN}|
count_YELLOW = |{i : classification_i = YELLOW}|
count_ORANGE = |{i : classification_i = ORANGE}|
count_RED    = |{i : classification_i = RED}|

pct_GREEN  = count_GREEN  / N
pct_ORANGE = count_ORANGE / N
pct_RED    = count_RED    / N
```

### Step 4 — Trigger Evaluation
```
If count_RED > 0:
  → CRITICAL — Ghost sessions detected
  → Quarantine all RED session conclusions
  → Do not use any downstream reasoning that depends on RED sessions
  → Diagnose root cause before continuing

Elif pct_ORANGE > 0.30:
  → WARNING — High drift population
  → Recalibration required: re-run the most recent sessions in AUDIT mode
  → Identify what changed between the last GREEN session and the first ORANGE session

Else:
  → SYSTEM HEALTH: OPTIMAL
  → Chronos-Hodge stable — no population-level intervention needed
```

### Step 5 — Trend Analysis (Chronos Component)
Beyond the current snapshot, track the direction of change:
```
For the last M sessions (M < N):
  is_trending_worse = (pct_ORANGE_last_M > pct_ORANGE_first_M)
  is_trending_better = (pct_GREEN_last_M > pct_GREEN_first_M)

STABLE:   no trend in either direction
WORSENING: ORANGE/RED percentage increasing over M
IMPROVING: GREEN percentage increasing over M
```

A system that is currently at 20% ORANGE but trending UP is more dangerous than one at 25% ORANGE trending DOWN.

### Step 6 — Recalibration Protocol
When triggered (RED detected or ORANGE > 30%):
```
1. Identify the first session that shifted from GREEN to YELLOW/ORANGE
2. Examine what changed in that session: engine_version, prompt_version, input_fingerprint
3. Determine if change is:
   - VERSIONED (expected — document and accept new baseline)
   - INJECTED (unexpected — revert and investigate)
   - ACCUMULATED (gradual drift — run LLL lattice reduction to clean assumptions)
4. Set new GREEN baseline from the most recent STRUCTURAL session
```

## 📋 Semáforo Report Format

```
=== SEMÁFORO CHRONOS-HODGE REPORT ===
Audit window:  N=[N] sessions
Domain:        [specific domain | all]

Session log:
  ID    H_RIGIDITY      FINGERPRINT STATUS
  ────  ──────────────  ─────────── ──────────────────────────
  N     [H value]       [fp[:8]]    [GREEN/YELLOW/ORANGE/RED — label]
  N-1   [H value]       [fp[:8]]    [...]
  ...
  N-19  [H value]       [fp[:8]]    [...]

Population summary:
  GREEN:  [count] ([pct]%)
  YELLOW: [count] ([pct]%)
  ORANGE: [count] ([pct]%)
  RED:    [count] ([pct]%)

Trend (last 5 vs. prior 15):
  [STABLE | WORSENING | IMPROVING]

Trigger status:
  RED detected:      [YES — CRITICAL | NO]
  ORANGE > 30%:      [YES — WARNING  | NO]

System health:       [OPTIMAL | RECALIBRATION REQUIRED | CRITICAL]

If recalibration needed:
  First degraded session: ID=[X] at [timestamp]
  Change detected:        [VERSION | INJECTION | ACCUMULATION]
  Action:                 [revert/document/reduce]
=======================================
```

## 🏛️ Governing Laws

- **Law 1 — Population health is not point-in-time**: A single GREEN session does not mean the system is healthy. Look at the last N — if 8/20 are ORANGE, the system is drifting even if today is GREEN.
- **Law 2 — Any RED quarantines the session**: A RED (Ghost) session produced invalid output or extreme drift. Any conclusion from it is quarantined until the root cause is identified and resolved. This is not optional.
- **Law 3 — ORANGE > 30% triggers recalibration**: The 30% threshold is not conservative — 6 out of 20 sessions with active drift is a systemic problem. Recalibration is not optional at this threshold.
- **Law 4 — Chronos precedes Hodge**: In a full audit sequence, Semáforo Chronos-Hodge runs BEFORE `hodge-rigidity-detector` in a new session — not after. The population context informs how to interpret the new session's H value.
- **Law 5 — WORSENING trend overrides current state**: A system at 15% ORANGE but trending to 30% is more dangerous than one at 25% ORANGE trending to 10%. The trend is the more important signal for planning.

---
*Derived from Gahenax/OEDA_GahenaxIA — gahenax_ops.py:semaforo (Chronos-Hodge v2.0), CMR h_rigidity thresholds 1e-14/1e-11/1e-8, window_n=20, population triggers*
