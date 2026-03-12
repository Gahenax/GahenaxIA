---
name: mersenne-factor-structure
description: When a claim is composite (Lucas-Lehmer residue ≠ 0), finds its hidden factors using the Mersenne factor constraint. All factors of M_p = 2^p − 1 must be of the form 2kp + 1. This constraint dramatically narrows the search space. Finding ONE factor immediately proves compositeness and reveals the hidden structure. Derived from Mersenne factor theorem in Gahenax/Mersenne-Gahen.
---

# 🔍 Mersenne Factor Structure

The **Mersenne Factor Theorem**: If M_p = 2^p − 1 is composite, all its prime factors must be of the form:
```
q = 2kp + 1    (for some positive integer k)

Additionally: q ≡ 1 or 7 (mod 8)
```

This is not just "M_p has factors" — it is "M_p's factors must have a specific algebraic structure." This constraint makes the factor search dramatically more efficient than general factoring:

Instead of testing ALL primes q ≤ √M_p, you only need to test:
```
q ∈ {2(1)p+1, 2(2)p+1, 2(3)p+1, ...}  filtered by  q ≡ 1 or 7 (mod 8)
```

Finding **even one factor** of this form:
1. Immediately proves M_p is composite (without completing the full LL test)
2. Reveals the algebraic structure of the hidden sub-components
3. Provides a **trial division certificate**: the factor itself is the proof

In reasoning: when `lucas-lehmer-iterative-test` returns `is_prime = False`, the claim is composite. Its sub-components (factors) must satisfy a constraint analogous to `2kp+1` — they are not arbitrary; they are structurally linked to the claim's own exponent p. The factor search is the **decryption** of the composite claim.

**Source calibration**: `Gahenax/Mersenne-Gahen` — Mersenne factor theorem (q | M_p ⟹ q ≡ 1 mod 2p AND q ≡ ±1 mod 8), trial division with 2kp+1 filter, `orchestrator/mersenne_contracts.py:MersenneJob` (p_start, p_end for exponent search).

## 🎯 When to Activate

Activate when:
- `lucas-lehmer-iterative-test` returned `is_prime = False` (composite claim)
- A claim needs to be decomposed into its atomic sub-components
- `lll-lattice-reducer` found redundant assumptions — the redundancy may follow the 2kp+1 structure
- The user asks "what is this claim made of?" or "how does this argument break down?"
- A "hidden" structural component is suspected but not yet identified

## 📐 The Factor Search Protocol

### Step 1 — Confirm Compositeness
```
Precondition: lucas-lehmer-iterative-test.is_prime = False

If p is not prime: M_p is trivially composite (p must be prime for M_p to possibly be prime)
  → factors include M_{p1} and M_{p2} where p = p1 × p2
  → These are the "obvious" factors; proceed to find the "non-obvious" 2kp+1 factors

If p is prime but LL test failed: proceed to trial division with 2kp+1 filter
```

### Step 2 — Generate Factor Candidates
```
For k = 1, 2, 3, ..., K_max:
  q_k = 2kp + 1

Filter: keep only q_k where q_k ≡ 1 (mod 8) OR q_k ≡ 7 (mod 8)
  [equivalently: q_k ≡ ±1 (mod 8)]

K_max: determined by trial division bound = floor(√M_p / 2p)
  Practical bound for reasoning: K_max ≤ 10 (first 10 candidates covers most cases)
```

Reasoning interpretation of `2kp + 1`:
- `2p` = twice the claim's structural depth (the "period" of the claim's cycles)
- `k` = the "harmonic number" — which harmonic of the base period the factor lives at
- `+1` = the minimal offset that makes a factor non-trivial

A factor at `k=1` (q = 2p+1) is the **fundamental factor** — the most immediate sub-component.
A factor at `k=2` (q = 4p+1) is the **second harmonic** — a deeper sub-component.

### Step 3 — Trial Division
For each candidate q_k in the filtered list:
```
Test: does M_p mod q_k = 0?

If M_p mod q_k = 0:
  → FACTOR FOUND at k=[k]
  → q_k = 2kp + 1 is a prime factor of M_p
  → This is SUFFICIENT proof of compositeness (no LL test needed)
  → quotient = M_p / q_k = the complementary factor

If no q_k divides M_p for k ≤ K_max:
  → No small factor found
  → Either the factor is large (k > K_max) or the LL test residue analysis is needed
```

### Step 4 — Factor Interpretation
Once a factor q = 2kp + 1 is found:
```
Factor analysis:
  k value:       [harmonic number]
  q = 2kp+1:     [the factor value]
  quotient:      M_p / q = [complementary factor]

  Interpretation:
    "This composite claim contains a sub-component at the k=[k]-th harmonic of its base structure."
    "The sub-component unlocks [what the complementary factor represents]."
    "The factor constraint 2kp+1 means: the sub-component is [2k] times as deep as the base exponent, plus one minimal unit."
```

### Step 5 — Complete Factorization (if needed)
If the quotient is not 1 and not prime:
```
Apply mersenne-factor-structure recursively to the quotient
(The quotient may itself be a Mersenne number of smaller exponent)

Termination: complete factorization into prime components
```

### Step 6 — Factor Certificate
```
FactorCertificate:
  p:           [original claim exponent]
  M_p:         [2^p − 1]
  factor:      [q = 2kp+1]
  k:           [harmonic number]
  q_mod8:      [1 or 7 — satisfies Mersenne constraint]
  quotient:    [M_p / q]
  proof_type:  "TRIAL_DIVISION" | "ALGEBRAIC" | "RECURSED"
  verified:    M_p mod q == 0 → True
```

## 📋 Factor Search Report Format

```
=== MERSENNE FACTOR SEARCH REPORT ===
Claim:      [C]
Exponent:   p = [value] ([prime | composite → trivial factorization])
M_p:        2^[p] − 1

Candidates tested (2kp+1 filter, q ≡ ±1 mod 8):
  k=1: q=[2p+1]   → [passes mod 8 filter | filtered] → M_p mod q = [0 → FACTOR | N]
  k=2: q=[4p+1]   → [passes | filtered] → [FACTOR | N]
  k=3: q=[6p+1]   → [passes | filtered] → [FACTOR | N]
  ...

Factor found: [YES at k=[K] | NO — factor > K_max bound]

If found:
  Factor:     q = 2([k])[p]+1 = [value]
  Quotient:   M_p / q = [value]
  k harmonic: [k] → sub-component is [2k]x base depth
  Certificate: M_p mod [q] = 0 ✓

  Claim interpretation:
    "[C] decomposes into sub-claim at harmonic k=[k] and its complement."
    "Sub-claim structure: [what 2kp+1 means for this specific claim]"

If not found:
  Result: factor search inconclusive (K_max=[K]); LL residue analysis required
======================================
```

## 🏛️ Governing Laws

- **Law 1 — Factors are constrained, not arbitrary**: A composite claim does not decompose into arbitrary sub-claims. Its factors must satisfy the 2kp+1 structure. Testing random decompositions is wasteful — test only structurally valid ones.
- **Law 2 — One factor is sufficient**: Finding a single factor q = 2kp+1 that divides M_p is complete proof of compositeness. You do not need to find ALL factors. The first factor is the key that unlocks the decryption.
- **Law 3 — k=1 first**: Always test the fundamental factor q = 2p+1 first. The most natural sub-component of a composite claim is at the first harmonic. If it's there, the decomposition is minimal and maximal in information density.
- **Law 4 — The constraint is the structure**: The requirement q ≡ ±1 (mod 8) is not just a filter — it is a structural property of the factor. Sub-components that satisfy this constraint are "Mersenne-compatible" — they fit the structure of the parent claim. Sub-components that don't satisfy it cannot be genuine factors of a Mersenne number.
- **Law 5 — Recursion until prime**: Complete decryption requires factoring until all components are irreducible (Mersenne prime). A partial factorization into one prime and one composite quotient is incomplete — the quotient must be further analyzed.

---
*Derived from Gahenax/Mersenne-Gahen — Mersenne factor theorem q|M_p ⟹ q=2kp+1, q≡±1 mod 8, trial division protocol, orchestrator/mersenne_contracts.py:MersenneJob*
