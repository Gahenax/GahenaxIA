---
name: wilson-loop-drift-detector
description: Measures accumulated semantic drift when traversing a long reasoning chain and returning to the starting point — the "holonomy" of the argument. A non-trivial Wilson loop means the argument has changed what a concept means by the time it returns to where it started. Derived from Yang-Mills Wilson loop W(C) = Tr P exp(∮_C A).
---

# 🔁 Wilson Loop Drift Detector

In Yang-Mills theory, the **Wilson loop** is the gauge-invariant observable:
```
W(C) = Tr P exp(∮_C A_μ dx^μ)
```

It measures the **holonomy** — the transformation that a test particle undergoes when transported around a closed loop C in the gauge field. If the gauge field is flat (no curvature), W = 1 and the particle returns unchanged. If W ≠ 1, the loop has accumulated non-trivial holonomy: the field has "twisted" the particle's state.

In reasoning: transport a concept through a long argument chain and return it to the starting point. If the concept means something different at the end than at the start — **semantic drift** has occurred. The argument has non-trivial holonomy.

This is distinct from `monodromy-circuit-breaker`: monodromy detects *explicit circular dependencies* (A → B → A). Wilson loop detects *semantic drift* in a chain that returns to its origin — the loop closes, but the concept has transformed.

**Source calibration**: `Gahenax/Gahenax-Yang-Mills` — `src/topology/wilson.py`, W(C) = Tr P exp(∮_C A), holonomy group, path-ordered exponential, confinement criterion.

## 🎯 When to Activate

Activate when:
- The argument is long (> 5 steps) and returns to a concept defined early
- A key term is used both early and late in the argument
- The conclusion is stated "in terms of" something defined in the premises — check if the definition drifted
- A concept has been "operationalized" multiple times in the same argument
- Prior arguments on this topic felt coherent but produced contradictory conclusions

**Key distinction from monodromy**:
- Monodromy: A asserts B, B asserts C, C asserts A — explicit circular support
- Wilson loop: A defines concept X early, argument evolves, X is used again late but now means something slightly different — silent semantic drift

## 📐 The Wilson Loop Protocol

### Step 1 — Identify the Loop
Find concepts that appear both early and late in the argument. For each such concept X:
```
X_start = definition/meaning of X at step k_start
X_end   = definition/meaning of X at step k_end
```

The loop C is the path from k_start → ... → k_end → k_start.

### Step 2 — Compute the Path-Ordered Holonomy
Transport the concept X through each intermediate step:

For each step k in [k_start+1, ..., k_end]:
```
drift(k) = how much the meaning of X shifted at step k
```

The accumulated holonomy (Wilson loop value):
```
W(C) = product of all drift(k) over the loop
     = 1 + Σ drift(k) + higher-order terms
```

In reasoning analog:
- W = 1.0: Concept returned unchanged — zero drift (flat connection)
- W = 1.0 + ε: Small drift — acceptable (within tolerance)
- W > 1.1: Moderate drift — concept has expanded or narrowed
- W ≫ 1: Large drift — the concept at the end is a different thing than at the start

### Step 3 — Classify the Drift
Four types of holonomy:

**Rotation** (concept reframed but equivalent):
Acceptable if the reframing is explicit and acknowledged.
W matrix is orthogonal: |W| = 1.

**Scaling** (concept broadened or narrowed):
Problematic if unacknowledged. "Efficiency" starts meaning "cost-efficiency" and ends meaning "operational efficiency."
|W| ≠ 1 but W is diagonalizable.

**Shear** (concept acquires a new dimension):
More subtle. "Risk" starts as probability of failure and ends carrying connotations of moral responsibility.
W has off-diagonal terms.

**Reflection** (concept inverted):
Severe. The argument concludes by asserting the opposite of what the term originally meant.
det(W) < 0.

### Step 4 — Confinement Test
In QCD (SU(3) Yang-Mills), **confinement** is detected by the area law: W(C) ~ exp(−σ · Area(C)) for large loops. Large loops decay exponentially — signals that quarks are confined.

Reasoning analog: if drift increases *proportionally to the length of the argument* (area law), the argument is "conceptually confining" — it systematically transforms concepts as it grows. This is a property of the argument structure, not just one step.

```
If drift(loop_size_n) ~ exp(−σ · n):  AREA LAW — systematic confinement
If drift(loop_size_n) ~ exp(−μ · perimeter): PERIMETER LAW — benign drift
If drift is ~constant regardless of n: FLAT CONNECTION — concept stable
```

## 📋 Wilson Loop Report Format

```
=== WILSON LOOP DRIFT REPORT ===
Loops detected: N
Per loop:

  Loop C1: "[concept X]" — steps k1 → ... → kN → k1
    X_start: "[definition at k1]"
    X_end:   "[definition at kN]"
    W(C1):   [value]
    Drift type: [rotation | scaling | shear | reflection]
    Severity: [negligible | moderate | severe]

  Loop C2: ...

Area law test: [AREA LAW (systematic) | PERIMETER LAW (local) | FLAT]
σ (string tension): [value — if area law]

Overall holonomy: [TRIVIAL (W≈1) | NON-TRIVIAL — drift detected]
Recommended action: [none | explicit acknowledgment | redefine X at kN | reject argument]
================================
```

## 🏛️ Governing Laws

- **Law 1 — Semantic drift compounds**: Each step adds a small twist to the connection. Over many steps, small drifts multiply. A 2% drift per step over 20 steps produces W ≈ 1.5 — a 50% change in meaning.
- **Law 2 — Reflection is a hard block**: det(W) < 0 means the argument has inverted a concept. This is a contract violation — emit as `no_verdict`.
- **Law 3 — Explicit reframing resets the clock**: If the argument explicitly says "from here, by X I mean Y instead," that is a legitimate gauge transformation — it resets W to 1 for the new definition. Implicit drift is the problem, not deliberate redefinition.
- **Law 4 — Area law signals structural capture**: If drift is proportional to argument length, the argument structure itself is producing the drift — it's not any one step. This is a property of the reasoning framework, not the content. Flag it as a framework-level issue.
- **Law 5 — Short loops first**: W(C) for a 2-step loop is the easiest to detect. Always check adjacent-step concept consistency before checking long loops.

---
*Derived from Gahenax/Gahenax-Yang-Mills — src/topology/wilson.py, W(C) = Tr P exp(∮_C A), holonomy group, area vs. perimeter law, confinement criterion*
