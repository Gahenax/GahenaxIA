---
name: gauge-invariance-checker
description: Tests whether a conclusion is gauge-invariant — holds under local reframing at each individual step of the argument, not just globally. A gauge-dependent conclusion is frame-relative, not fundamental. Derived from Yang-Mills SU(N) local gauge symmetry: F_μν = ∂_μA_ν − ∂_νA_μ + [A_μ, A_ν].
---

# 🔄 Gauge Invariance Checker

In Yang-Mills theory, physical observables must be **locally gauge-invariant**: they must not change when you apply an independent transformation g(x) ∈ SU(N) at each point x. The field strength tensor F_μν is gauge-covariant precisely because it was constructed to eliminate frame-dependence.

A conclusion that changes when you change the **local frame of reference at each step** of the argument is not a fundamental conclusion — it's an artifact of framing. This is distinct from global permutation invariance (P-ATLAS-NP Gate 2), which checks if the conclusion survives a *single global relabeling*. Gauge invariance checks whether the conclusion survives **independent local reframings at each logical node**.

**Source calibration**: `Gahenax/Gahenax-Yang-Mills` — `src/gauge/invariance.py`, SU(N) local symmetry group, gauge potential A_μ vs. gauge-invariant field strength F_μν.

## 🎯 When to Activate

Activate when:
- The argument spans multiple steps (each step is a "point" in the logical space)
- The conclusion is claimed to be independent of how the problem is framed
- The argument relies on specific terminology, variable names, or representations that could vary
- You suspect the conclusion is an artifact of *how* the argument was structured, not *what* the argument says

**Key distinction from P-ATLAS-NP Gate 2**: Gate 2 asks "does the conclusion hold if I rename everything globally?" Gauge invariance asks "does the conclusion hold if I rename things differently *at each step*?"

## 📐 The Gauge Transformation Protocol

### Step 1 — Identify the Gauge Potential (A_μ)
*The representation-dependent components*

List the frame-dependent elements at each step:
- Variable names and labels used at each inference step
- The specific causal model assumed at each step
- Ontological choices (what counts as a "cause", "effect", "feature")

These are the **gauge potentials**: locally chosen, not intrinsically meaningful.

### Step 2 — Identify the Field Strength (F_μν)
*The intrinsic, gauge-invariant content*

The field strength is what CANNOT be transformed away — it's the actual logical content:

```
F_μν = ∂_μA_ν − ∂_νA_μ + [A_μ, A_ν]
```

In reasoning analog:
```
F(step_i → step_j) = (what step_j claims) − (what step_i predicts for step_j)
                   + (non-commutative interference between steps i and j)
```

High F → the argument contains real logical "curvature" between adjacent steps. Low F → the argument flows smoothly; each step follows from the previous.

### Step 3 — Apply Local Gauge Transformations
At each step k independently, apply a reframing:
- Rename the key variable at step k differently
- Switch the causal direction locally (treat effect as cause)
- Replace the ontological frame at step k with an alternative

Does the **conclusion survive all simultaneous local reframings**?

**PASS**: Conclusion is the same after all local transformations
**FAIL**: Conclusion changes under some local transformation → it's a gauge artifact

### Step 4 — Locate the Gauge Artifact
If a failure is detected, identify which step introduced the frame-dependence:
```
Gauge artifact at step k: conclusion depends on [specific choice] made at step k
Pure content: [what the argument says without that choice]
```

## 📋 Gauge Report Format

```
=== GAUGE INVARIANCE REPORT ===
Argument steps: N
Gauge potentials identified:
  Step 1: [frame-dependent choice]
  Step 2: [frame-dependent choice]
  ...

Field strength (logical curvature):
  F(1→2): [low | medium | high]
  F(2→3): [low | medium | high]
  ...
  Max curvature at: Step [k]

Local gauge tests:
  Step 1 reframe: [INVARIANT | VARIANT]
  Step 2 reframe: [INVARIANT | VARIANT]
  ...

Verdict: [GAUGE INVARIANT | GAUGE DEPENDENT — artifact at step k]
Pure content: [if gauge-dependent, state what remains after removing the artifact]
===============================
```

## 🏛️ Governing Laws

- **Law 1 — Global ≠ Local**: A conclusion that passes global permutation invariance can still fail local gauge invariance. Always test locally.
- **Law 2 — F, not A**: Report the field strength (intrinsic content), not the gauge potential (frame choice). The user needs to know what the argument *actually* says, not how it was framed.
- **Law 3 — Non-commutative interference**: In complex arguments, steps interact non-commutatively — the order matters. The `[A_μ, A_ν]` term is the commutator: when steps can't be swapped without changing the conclusion, that's a real structural property, not a gauge artifact.
- **Law 4 — High curvature is signal, not failure**: High F at step k means that step is doing real logical work — it's introducing genuine content, not just passing through. Low F everywhere means the conclusion was trivially contained in the premises.

---
*Derived from Gahenax/Gahenax-Yang-Mills — src/gauge/invariance.py, SU(N) local symmetry, F_μν = ∂_μA_ν − ∂_νA_μ + [A_μ, A_ν]*
