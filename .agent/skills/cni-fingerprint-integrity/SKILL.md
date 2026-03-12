---
name: cni-fingerprint-integrity
description: Computes a Canonical Normalized Input (CNI) fingerprint for a reasoning task — a deterministic SHA256 of the cleaned, sorted input. Detects two failure modes: (1) same fingerprint, different output across sessions = output drift; (2) fingerprint changed when input was supposed to be stable = input tampering. Derived from compute_cni_fingerprint() and CMR.record_run() in gahenax_engine.py and cmr.py.
---

# 🔐 CNI Fingerprint Integrity

`compute_cni_fingerprint()` in `gahenax_engine.py`:
```python
def compute_cni_fingerprint(payload: Dict[str, Any]) -> str:
    def _clean(obj):
        if isinstance(obj, str): return obj.strip()
        if isinstance(obj, dict): return {k: _clean(v) for k, v in sorted(obj.items())}
        if isinstance(obj, list): return [_clean(x) for x in obj]
        return obj
    canon = _clean(payload)
    blob = json.dumps(canon, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()
```

The CMR (`cmr.py`) stores `input_fingerprint` alongside every engine run, with `prev_hash` chaining. The CMR is indexed on `input_fingerprint` — enabling lookup of all runs with the same canonical input.

This enables two invariant checks:
1. **Output reproducibility**: If two runs share the same CNI fingerprint, their outputs should be semantically equivalent. If they aren't, the engine has drifted.
2. **Input integrity**: If the CNI fingerprint of a supposedly stable input has changed, something has modified the input between sessions — normalization failure, injection, or version change.

In reasoning: the CNI fingerprint is the **identity** of a reasoning task. It is not the text — it is the canonical normalized form of the text, stripped of cosmetic variation. Two tasks that look different but have the same fingerprint are the same task. A task that looks the same but has a different fingerprint has changed in a meaningful way.

**Source calibration**: `Gahenax/OEDA_GahenaxIA` — `backend/gahenax_app/core/gahenax_engine.py:compute_cni_fingerprint`, `backend/gahenax_app/core/cmr.py:CMR.record_run`, CMR schema fields `input_fingerprint`, `evidence_hash`, `prev_hash`.

## 🎯 When to Activate

Activate when:
- The same reasoning task is run multiple times across sessions and the results must be consistent
- A prior result is being used as a premise — verify the fingerprint matches the session that produced it
- A task that was "stable" seems to be producing different conclusions — check for fingerprint drift
- An argument is being reproduced from a prior session — confirm the input is canonically identical

**Key distinction from `bsd-dual-measurement-checker`**: BSD dual measurement checks if two *methods* agree on the same quantity. CNI fingerprint checks if the *same method* produces consistent output for the *same input* across *time*. These are orthogonal.

## 📐 The CNI Fingerprint Protocol

### Step 1 — Canonicalize the Input
Apply the canonical normalization to the reasoning task:
```
1. Strip all strings: remove leading/trailing whitespace
2. Sort all dict keys alphabetically at every nesting level
3. Serialize to JSON with (sort_keys=True, separators=(",",":"))
4. Encode to UTF-8
```

This removes cosmetic variation:
- "Question: X" vs. "Question:  X " → same fingerprint
- `{"b": 1, "a": 2}` vs. `{"a": 2, "b": 1}` → same fingerprint
- Reordered fields in a task spec → same fingerprint

### Step 2 — Compute CNI Fingerprint
```
cni_fingerprint = sha256(canonical_form).hexdigest()
```

### Step 3 — Lookup in Ledger (if available)
Query the CMR for prior runs with this `input_fingerprint`:
```
prior_runs = [r for r in ledger if r.input_fingerprint == cni_fingerprint]
```

If `len(prior_runs) == 0`: first time this exact task has been run — no baseline.
If `len(prior_runs) > 0`: prior baseline exists — compare outputs.

### Step 4 — Output Reproducibility Check
For each pair of runs with the same fingerprint:
```
For each (run_i, run_j) with same fingerprint:
  outputs_equivalent = semantic_compare(run_i.output, run_j.output)

  If outputs_equivalent: STABLE — no drift
  If not: DRIFT DETECTED
    drift_magnitude = distance(run_i.output, run_j.output)
    drift_type = [VERSION_CHANGE | SEMANTIC_DRIFT | NONDETERMINISM | INJECTION]
```

**Expected drift causes:**
- `VERSION_CHANGE`: `engine_version` differs between runs — expected, document it
- `SEMANTIC_DRIFT`: Same version, same input, different output — the engine is not deterministic on this input
- `NONDETERMINISM`: `seed` differs — acceptable only if randomness is documented
- `INJECTION`: `prompt_version` changed between runs — a prompt modification changed behavior

### Step 5 — Input Integrity Check
If a task is claimed to be "the same as" a prior run:
```
claimed_fingerprint: [fingerprint from prior run]
current_fingerprint: [freshly computed]

If claimed == current: IDENTICAL — input unchanged
If claimed ≠ current:
  diff: [what changed in the canonical form]
  severity: [COSMETIC (whitespace only) | SEMANTIC (content changed) | STRUCTURAL (schema changed)]
```

### Step 6 — Hash Chain Verification (CMR)
The CMR links every entry with `prev_hash`. Verify the chain:
```
For consecutive entries e_i, e_{i+1}:
  e_{i+1}.prev_hash should equal e_i.evidence_hash

Any break: CHAIN_TAMPERED — ledger integrity compromised
```

## 📋 CNI Fingerprint Report Format

```
=== CNI FINGERPRINT INTEGRITY REPORT ===
Task:             [description]
CNI fingerprint:  [sha256 hex]
Canonical form:   [first 80 chars of the canonical JSON]

Prior runs in ledger: [N]
  Latest:  [timestamp] engine=[version] seed=[seed]
  ...

Output reproducibility:
  [STABLE — all N runs semantically consistent]
  [DRIFT DETECTED — magnitude=[X], type=[type], between runs [i] and [j]]

Input integrity:
  [IDENTICAL — fingerprint unchanged]
  [CHANGED — [COSMETIC | SEMANTIC | STRUCTURAL] diff: [what changed]]

Hash chain: [INTACT | BREAK at entry ID=X]

Verdict:
  [REPRODUCIBLE — safe to use as premise]
  [DRIFT — re-run required before using as premise]
  [TAMPERED — chain break; do not trust prior results]
=========================================
```

## 🏛️ Governing Laws

- **Law 1 — Same fingerprint ≠ same output (necessarily)**: The fingerprint guarantees canonical identity of the INPUT. It does not guarantee the output is deterministic. Output reproducibility must be checked separately via ledger comparison.
- **Law 2 — Drift is not always a defect**: `VERSION_CHANGE` drift is expected and should be documented. `NONDETERMINISM` with different seeds is acceptable if randomness is declared. Only `SEMANTIC_DRIFT` (same version, same seed, same input, different output) is a genuine defect.
- **Law 3 — Fingerprint before using as premise**: Any conclusion from a prior session used as a downstream premise must have its CNI fingerprint verified against the current context. A fingerprint mismatch means the "same" task is actually different.
- **Law 4 — Chain breaks invalidate downstream results**: If the CMR chain is broken at entry X, all entries after X cannot be trusted. The integrity of the ledger depends on the unbroken chain.
- **Law 5 — Cosmetic changes are safe; semantic changes are not**: A fingerprint change caused by whitespace stripping is cosmetic — same content. A fingerprint change caused by a different word or changed number is semantic — different task.

---
*Derived from Gahenax/OEDA_GahenaxIA — backend/gahenax_app/core/gahenax_engine.py:compute_cni_fingerprint, backend/gahenax_app/core/cmr.py:CMR (input_fingerprint, evidence_hash, prev_hash chaining)*
