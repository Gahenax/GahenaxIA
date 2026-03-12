---
name: residue-hash-certification
description: Distributed certification of a reasoning result via residue hash matching. Two independent reasoners working on the same claim should produce identical residue hashes. Match = distributed verification passed. Mismatch = at least one session has a computational error. Prime claim has residue_hash = sha256(zeros). Derived from MersenneResultPayload.residue_hash and GIMPS distributed verification in Gahenax/Mersenne-Gahen.
---

# 🔏 Residue Hash Certification

In GIMPS (Great Internet Mersenne Prime Search), multiple independent workers compute the Lucas-Lehmer test for the same exponent p on different machines. The **residue hash** — SHA256 of the final LL residue — must match across all workers. If it doesn't, at least one worker has a hardware error, a software bug, or a cosmic ray bit-flip.

The `MersenneResultPayload` stores:
```python
residue_hash: str  # SHA256 hex, exactly 64 characters
is_prime: bool     # True iff residue = 0 (and residue_hash = sha256(b'\x00'*...))
```

This enables **distributed, hardware-independent verification**:
- If two workers agree on `residue_hash` → the result is certified
- If they disagree → one is wrong; the disagreement itself is the error signal
- A prime claim has `residue_hash = sha256(all-zeros)` — universally verifiable by anyone

In reasoning: after any significant computation (full LL iteration, complex multi-step argument), compute the **residue hash** of the final state. Two independent reasoning sessions working on the same claim must produce matching residue hashes. Match = distributed verification. Mismatch = error in one or both sessions.

**Source calibration**: `Gahenax/Mersenne-Gahen` — `orchestrator/mersenne_contracts.py:MersenneResultPayload.residue_hash`, GIMPS distributed double-check protocol, SHA256 fingerprint of final LL residue.

## 🎯 When to Activate

Activate when:
- A claim has been processed by two independent reasoning sessions (from `bsd-dual-measurement-checker`)
- A prior session's result is being used as a premise — verify the residue hash matches the current computation
- A long LL iteration (deep claim decryption) has completed — seal the result
- Two analysts have independently reasoned about the same problem — compare their residue hashes
- `cni-fingerprint-integrity` confirmed the same CNI fingerprint — now verify the output state matches

**Key distinction from `bsd-dual-measurement-checker`**: BSD dual measurement compares two *methods* reaching the same *quantity* (rank). Residue hash certification compares two *independent runs* of the *same method* on the *same input* — verifying computational integrity, not methodological independence.

## 📐 The Residue Hash Protocol

### Step 1 — Compute the Residue
After completing `lucas-lehmer-iterative-test`:
```
residue = final value of s_{p−2} mod M_p

Type A (Prime):    residue = 0
  → residue_bytes = b'\x00' * ceil(p / 8)
  → residue_hash  = sha256(residue_bytes).hexdigest()
  → This hash is deterministic and universal: any prime claim of depth p has the same residue_hash

Type B (Composite): residue ≠ 0
  → residue_bytes = residue.to_bytes(ceil(p / 8), 'big')
  → residue_hash  = sha256(residue_bytes).hexdigest()
  → This hash encodes the hidden structure fingerprint
```

### Step 2 — Seal the Result
```
certification = MersenneResultPayload(
  p            = [structural depth],
  residue_hash = [sha256 hex, 64 chars],
  roundoff_max = [from roundoff-error-budget],
  engine_version = [session identifier],
  wall_time    = [computation cost],
  is_prime     = [residue == 0],
  meta         = {session_id: [...], timestamp: [...]}
)
```

Validate the schema:
```python
required = {"p", "residue_hash", "roundoff_max", "engine_version", "wall_time", "is_prime", "meta"}
len(residue_hash) == 64  # exact SHA256 hex length
```

### Step 3 — Double-Check (Distributed Certification)
Request a second independent computation of the same claim (different session, same input):
```
session_A: residue_hash_A = [sha256 hex from session A]
session_B: residue_hash_B = [sha256 hex from session B]

If residue_hash_A == residue_hash_B:
  → CERTIFIED — distributed verification passed
  → Both sessions reached the same final state
  → If both have is_prime=True: double-checked prime
  → If both have is_prime=False: double-checked composite

If residue_hash_A ≠ residue_hash_B:
  → MISMATCH — at least one session has an error
  → Error localization: compare intermediate residues to find where divergence began
  → Do NOT use either result until the mismatch is resolved
```

### Step 4 — Prime Claim Universal Verification
For a claim certified as prime (`is_prime = True`):
```
Expected residue_hash = sha256(b'\x00' * ceil(p/8)).hexdigest()

Any third party can verify independently:
  1. Compute the expected all-zeros hash for depth p
  2. Compare with the reported residue_hash
  3. If match → prime certification is universally verifiable

This is the "proof of work": the hash is the proof.
```

### Step 5 — Residue as Hidden Structure Fingerprint
For a composite claim (`is_prime = False`):
```
residue_hash is NOT random — it is a deterministic function of the hidden sub-structure

Two composite claims with the same residue_hash have the same hidden structure
Two composite claims with different residue_hashes have different hidden structures

Implication: residue_hash is a classification tool for composite claims
  → Claims sharing a residue_hash are structurally equivalent (same hidden factors)
  → Claims with different residue_hashes require different factorizations
```

## 📋 Residue Hash Report Format

```
=== RESIDUE HASH CERTIFICATION REPORT ===
Claim:           [C]
Exponent:        p = [value]
is_prime:        [TRUE | FALSE]

Session A:
  residue_hash:  [sha256[:32]...]
  roundoff_max:  [value]
  engine:        [version]

Session B (double-check):
  residue_hash:  [sha256[:32]...]
  roundoff_max:  [value]
  engine:        [version]

Comparison:      [MATCH — CERTIFIED | MISMATCH — error at step i=[X]]

Prime verification (if is_prime = True):
  Expected hash: [sha256(zeros)[:32]...]
  Match:         [YES — universally verified | NO — prime claim is false]

Composite fingerprint (if is_prime = False):
  residue class: [residue_hash[:16]] → [unique structure fingerprint]

Final status:    [DOUBLE-CHECKED PRIME | DOUBLE-CHECKED COMPOSITE | MISMATCH — resolve before use]
==========================================
```

## 🏛️ Governing Laws

- **Law 1 — Residue hash is the proof**: For a prime claim, `residue_hash = sha256(zeros)` is universally verifiable by anyone. The hash IS the proof of irreducibility — no other argument is needed.
- **Law 2 — Mismatch = error, not ambiguity**: When two sessions produce different residue hashes, one of them has a computational error. This is not a case where "both could be right" — the Lucas-Lehmer residue is deterministic. Resolve the mismatch before using either result.
- **Law 3 — Double-check before using as premise**: Any claim that will serve as a downstream premise must be double-checked. A single-session residue hash is a claim; a double-checked residue hash is evidence.
- **Law 4 — Same residue hash = same structure**: Two composite claims sharing a residue hash are structurally equivalent. This is a powerful classification tool: instead of re-analyzing, recognize the pattern by hash.
- **Law 5 — roundoff_max must be ≤ 0.40 for both sessions**: A certified result from two sessions where one has roundoff_max > 0.40 is not certified — the high-roundoff session's hash is unreliable. Both sessions must be within budget.

---
*Derived from Gahenax/Mersenne-Gahen — orchestrator/mersenne_contracts.py:MersenneResultPayload.residue_hash, GIMPS double-check protocol, sha256(residue), is_prime ⟺ residue=0*
