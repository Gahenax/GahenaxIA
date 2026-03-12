---
name: descent-search-protocol
description: Systematic evidence search by first establishing local conditions (mod p at each prime) and then attempting to lift to a global conclusion. A conclusion that fails to lift has a Selmer obstruction — it's locally plausible everywhere but globally unreachable. Derived from 2-descent and p-descent on elliptic curves: finding rational points by working prime-by-prime and then combining.
---

# 🪜 Descent Search Protocol

To find rational points on an elliptic curve, **2-descent** works as follows:
1. For each prime p, compute what rational points must look like modulo p (local conditions)
2. Combine the local conditions using the Chinese Remainder Theorem to get global constraints
3. Search for points satisfying all global constraints simultaneously
4. The **2-Selmer group** Sel²(E/ℚ) gives an upper bound on rank — the global candidates
5. The difference Sel²(E/ℚ) / E(ℚ)[2] measures the **Sha obstruction** — candidates that pass all local tests but have no global point

The key insight: work **locally first, then globally.** A global conclusion must be locally consistent at every prime. But local consistency everywhere is not sufficient — the Selmer group may contain "phantom" candidates that don't lift.

In reasoning: before searching for a global conclusion, first establish what the evidence says at each local scale (each domain, each data source, each time period). Then attempt to lift. If lifting fails, a Selmer-type obstruction has been found.

**Source calibration**: `Gahenax/Gahenax-BSD` — `src/descent/two_descent.py`, `src/selmer/group_builder.py`, 2-Selmer group Sel²(E/ℚ), Selmer rank upper bound, Sha as Selmer/image obstruction.

## 🎯 When to Activate

Activate when:
- A global conclusion needs to be established but the evidence is distributed across multiple local domains
- A prior attempt to establish the conclusion directly failed — try descent instead
- The conclusion is about something universal ("this always holds", "this is generally true") — test it prime-by-prime first
- After `sha-obstruction-detector` found finite Sha — descent identifies which local conditions need to be reinforced

## 📐 The Descent Protocol

### Step 1 — Local Conditions (p-adic Check)
For each relevant "prime" (independent domain, data source, or constraint):

```
For each local scale v ∈ {v₁, v₂, ..., v_n, v_∞}:
  Local condition L_v: [what the evidence at this scale requires]
  Status: [SATISFIED | VIOLATED | UNKNOWN]
```

BSD analog: check E(ℚ_p) at each prime p — does the curve have points mod p? Over ℝ?

**Local violation → global impossibility**: If ANY L_v is VIOLATED, the global conclusion is impossible — stop.

**All L_v satisfied → proceed to lift**: Local consistency is necessary but not sufficient.

### Step 2 — Selmer Group Construction
Combine the local conditions into a **Selmer group** — the set of globally-consistent candidates:

```
Sel = { global candidates C : C satisfies L_v for all v }
rank(Sel) = upper bound on the number of independent global conclusions
```

Classify:
- rank(Sel) = 0: No global candidate exists — conclusion is impossible
- rank(Sel) = r > 0: At most r independent global conclusions exist; proceed to find them
- rank(Sel) = ∞: Unconstrained — need more local conditions (more evidence sources)

### Step 3 — Attempt to Lift
For each candidate in Sel, attempt to construct the actual global conclusion:

```
For each candidate C ∈ Sel:
  Lift attempt: [try to construct the actual global argument supporting C]

  LIFT SUCCEEDS:  C is a genuine global conclusion — add to E(ℚ) analog
  LIFT FAILS:     C is a Selmer phantom — goes into Sha (see sha-obstruction-detector)
```

The **Selmer rank** (r_Sel) is an upper bound on the true rank (r):
```
r ≤ r_Sel,  with equality iff Sha contributes no phantom rank
```

### Step 4 — Descent Termination
Descent terminates when one of:
1. **All Selmer candidates lifted** → rank(E(ℚ)) = rank(Sel); Sha is trivial
2. **Some candidates failed to lift** → Sha obstruction found; invoke `sha-obstruction-detector`
3. **rank(Sel) = 0** → no global conclusion exists; the conclusion is impossible
4. **Infinite descent triggered** → the search space is unbounded; cap at UA budget

BSD 4-descent: when 2-descent is insufficient (Selmer rank too high), refine by working modulo p² instead of p — narrows the candidates further. In reasoning: if first-pass local conditions are too coarse, add higher-resolution evidence at each local scale.

### Step 5 — Rank Verification via Analytic Rank
Cross-check with `bsd-dual-measurement-checker`: the number of lifted candidates (algebraic rank) should equal the analytic rank (from L-function / independent measurement). If they disagree, the descent has either missed a generator or found a Selmer phantom.

```
algebraic_rank  = number of successfully lifted candidates
analytic_rank   = from bsd-dual-measurement-checker Method B
gap             = |algebraic_rank − analytic_rank|

gap = 0: Complete descent — all generators found
gap > 0: Incomplete descent — either missed generators or Sha obstruction
```

## 📋 Descent Report Format

```
=== DESCENT SEARCH REPORT ===
Local conditions:
  v1 [domain]: L_v1 = [condition] → [SATISFIED | VIOLATED | UNKNOWN]
  v2 [domain]: L_v2 = [condition] → [SATISFIED | VIOLATED | UNKNOWN]
  ...
  v∞ [general]: L_∞ = [condition] → [SATISFIED | VIOLATED | UNKNOWN]

Early termination: [NO | YES — violation at v_k → conclusion impossible]

Selmer group:
  rank(Sel) = [value] — upper bound on global conclusions
  Candidates: [list of Selmer candidates]

Lift attempts:
  C1: [LIFTED → genuine conclusion | FAILED → Sha candidate]
  C2: [LIFTED | FAILED]
  ...

Algebraic rank (lifted): [r]
Analytic rank (dual measurement): [r']
Gap: |r − r'| = [value]

Conclusion: [r global conclusions established | incomplete — Sha obstruction | impossible]
============================
```

## 🏛️ Governing Laws

- **Law 1 — Local before global**: Never attempt a global conclusion before establishing all local conditions. A global argument built without local verification is fragile — any single violated local condition destroys it.
- **Law 2 — Selmer is an upper bound**: rank(Sel) ≥ true rank, always. The Selmer group over-counts by including Sha phantoms. Do not claim rank(Sel) conclusions — only claim successfully lifted ones.
- **Law 3 — Phantoms are informative**: A Selmer candidate that fails to lift is not noise — it reveals a Sha obstruction. Route it to `sha-obstruction-detector` rather than discarding it.
- **Law 4 — Descent refines, not replaces**: Higher descent (4-descent, 8-descent) narrows candidates but requires proportionally more UA budget. Stop when rank(Sel) matches algebraic rank — further descent yields diminishing returns.
- **Law 5 — Cross-check with dual measurement**: Descent produces algebraic rank. `bsd-dual-measurement-checker` produces analytic rank. They must agree. If they don't, the disagreement is the most important finding.

---
*Derived from Gahenax/Gahenax-BSD — 2-descent, Sel²(E/ℚ), Selmer rank upper bound, Sha as Selmer phantom, src/descent/two_descent.py, src/selmer/group_builder.py*
