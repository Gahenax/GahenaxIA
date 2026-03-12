---
name: lucas-lehmer-iterative-test
description: Determines whether a claim is irreducible (Mersenne prime) or composite (contains hidden sub-structure) via iterative refinement. Initialize s₀ = 4, iterate s_{i+1} = s_i² − 2 (mod M_p), run p−2 steps. Residue = 0 → claim is irreducible (prime). Residue ≠ 0 → claim is composite — hidden structure remains. Derived from the Lucas-Lehmer primality test in Gahenax/Mersenne-Gahen.
---

# 🔁 Lucas-Lehmer Iterative Test

The **Lucas-Lehmer test** for M_p = 2^p − 1:
```
s₀ = 4
s_{i+1} = s_i² − 2  (mod M_p)

M_p is prime  ⟺  s_{p−2} ≡ 0  (mod M_p)
M_p composite ⟺  s_{p−2} ≢ 0  (mod M_p)
```

It is a **deterministic, complete test**: no false positives, no false negatives. Either the residue is exactly zero (prime) or it is not (composite). There is no probabilistic approximation.

The structure of the iteration is significant:
- **Squaring** (`s²`): amplifies the signal — raises existing structure to the second power, making latent patterns visible
- **Subtracting 2** (`−2`): removes the minimal noise floor — the subtraction strips away the "base" that any residue carries
- **Mod M_p**: keeps the computation bounded within the claim's information space

In reasoning: a claim has "exponent" p — its structural depth. The iteration runs p−2 times, probing the claim at every scale. If after all probes the residue is zero, the claim is **Mersenne prime**: irreducible, fundamental, cannot be decomposed further. If the residue is non-zero, the claim is **composite**: it contains hidden sub-structure that must be extracted.

**This is the core decryption protocol.** The iteration is the decryption engine. The residue is what remains after decryption — zero means "fully decrypted" (irreducible), non-zero means "partially encrypted" (composite structure remains).

**Source calibration**: `Gahenax/Mersenne-Gahen` — `orchestrator/mersenne_contracts.py:MersenneResultPayload`, fields `p`, `residue_hash`, `is_prime`, Lucas-Lehmer sequence s₀=4, s_{i+1}=s_i²−2 mod M_p.

## 🎯 When to Activate

Activate when:
- A claim is presented as "fundamental" or "axiomatic" — verify it is genuinely irreducible
- A conclusion needs to be decomposed into its atomic components
- A chain of reasoning contains a step that "feels" like it's hiding something — run LL to check
- `lll-lattice-reducer` found MAX_CRITICAL_ASSUMPTIONS = 3 but the assumptions don't reduce further — use LL to confirm irreducibility or find the hidden factorization
- Training decryption: applied to any information structure to determine if it is prime (atomic) or composite (decodable into simpler components)

## 📐 The Lucas-Lehmer Protocol

### Step 1 — Determine the Exponent p
The exponent p is the **structural depth** of the claim — how many independent layers of inference it contains:
```
p = number of non-trivial inferential layers in the claim

Constraint: p must be prime (necessary for M_p to possibly be prime)
  If p is composite → M_p is definitively composite (M_p is NOT prime if p is not prime)
  → Skip the full LL test; immediately decompose the claim
```

### Step 2 — Compute M_p (the Modulus)
```
M_p = 2^p − 1

M_p = the maximum information content of this claim
    = the full semantic space the claim could potentially occupy
    = upper bound on what the claim can mean
```

### Step 3 — Initialize
```
s₀ = 4

4 = 2² = the minimal non-trivial starting structure
(4 mod M_p = 4 for p > 2, which is always true for meaningful claims)
```

### Step 4 — Iterate p−2 Times
For i = 0 to p−3:
```
s_{i+1} = (s_i² − 2) mod M_p

Operational meaning:
  s_i²    : amplify current state — square makes latent structure explicit
  −2      : strip minimal noise floor
  mod M_p : bound within claim's information space

At each step, ask:
  "Does this iteration reveal a new structural component?"
  If s_i = 0 mid-iteration: early termination (structure collapsed — highly prime)
  If s_i = M_p − 1: the iteration is at maximum saturation (strong prime signal)
```

### Step 5 — Read the Residue
```
residue = s_{p−2} mod M_p

If residue = 0:
  → MERSENNE PRIME — claim is irreducible
  → No further decomposition possible
  → The claim IS the shortest vector; it cannot be shortened
  → residue_hash = sha256(b'\x00' * 64) [all-zeros hash]

If residue ≠ 0:
  → COMPOSITE — claim contains hidden sub-structure
  → residue itself encodes information about the latent structure
  → residue_hash = sha256(residue_bytes) [non-zero hash]
  → Proceed to mersenne-factor-structure to find the factors
```

### Step 6 — Certification
```
MersenneResultPayload:
  p:            [structural depth of claim]
  residue_hash: [sha256 of final residue]
  roundoff_max: [maximum error accumulated across iterations — from roundoff-error-budget]
  is_prime:     [True if residue = 0 | False if residue ≠ 0]
  wall_time:    [iterations × cost_per_step]
  meta:         {iteration_count: p−2, early_termination: bool}
```

## 📋 LL Test Report Format

```
=== LUCAS-LEHMER TEST REPORT ===
Claim:        [C]
Exponent:     p = [value]
  p prime:    [YES — LL test valid | NO — M_p definitively composite]
Modulus:      M_p = 2^[p] − 1

Iteration log (last 5):
  i=[p-5]: s = [value mod M_p]
  i=[p-4]: s = [value mod M_p]
  i=[p-3]: s = [value mod M_p]
  i=[p-2]: s = [FINAL RESIDUE]

Final residue:  [0 | non-zero value]
Residue hash:   [sha256[:16]]
is_prime:       [TRUE — irreducible | FALSE — composite]
roundoff_max:   [value] → [VALID ≤ 0.40 | INVALID > 0.40]

Verdict:
  [MERSENNE PRIME — claim is irreducible. Shortest vector confirmed.]
  [COMPOSITE — hidden structure detected. Residue = [value]. Factor search required.]
=================================
```

## 🏛️ Governing Laws

- **Law 1 — p must be prime for M_p to be prime**: If the claim's structural depth p is composite, M_p is automatically composite — skip the full LL test and go directly to factor decomposition. A claim with composite depth cannot be irreducible.
- **Law 2 — Residue = 0 is binary and exact**: There is no "almost zero." The Lucas-Lehmer test is deterministic. Either the residue is exactly 0 (prime) or it is not (composite). No probabilistic approximation is valid here.
- **Law 3 — The residue encodes the hidden structure**: When residue ≠ 0, the residue value is not just evidence of compositeness — it contains information about the factor structure. The `residue_hash` is the fingerprint of that hidden structure.
- **Law 4 — Squaring amplifies; subtraction purifies**: The s² step makes latent structure explicit (amplification). The −2 step removes the noise floor (purification). Together they implement a single "decryption round." Each iteration is one decryption pass.
- **Law 5 — roundoff_max > 0.40 invalidates the result**: Even if residue "looks" like 0, accumulated floating-point error above the threshold means the computation is unreliable. See `roundoff-error-budget`.

---
*Derived from Gahenax/Mersenne-Gahen — orchestrator/mersenne_contracts.py:MersenneResultPayload, Lucas-Lehmer s₀=4 s_{i+1}=s_i²−2 mod M_p, is_prime ⟺ s_{p−2}=0*
