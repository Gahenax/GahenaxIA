---
name: monodromy-circuit-breaker
description: Detects and breaks circular reasoning loops in argument graphs — including indirect circularity — before a conclusion is emitted. Inspired by the monodromy residue metric (M) from Hodge structure analysis.
---

# 🔄 Monodromy Circuit Breaker

In Hodge theory, monodromy measures what happens when you traverse a loop in a parameter space and return to the start — if the system doesn't return to exactly the same state, there's a residue. In reasoning, a monodromy residue is a circular dependency: premise P depends, even indirectly, on conclusion C.

This skill builds an explicit argument graph and traverses it to detect loops before they contaminate the output.

**Source calibration**: `Gahenax/OEDA_HodgeRigidity` — M metric, residue detection threshold 1e-12.

## 🎯 When to Activate

Activate when:
- The argument has more than 3 inferential steps
- The conclusion is being used to justify one of its own premises
- The reasoning has been refined multiple times (risk of drift into self-reinforcement)
- Answering "why does X happen?" style questions (causal chains loop easily)
- Validating a complex system's own design (the system's logic auditing itself)

## 🗺️ Argument Graph Protocol

**Step 1 — Map the Graph**
Label every distinct claim in the reasoning chain:
```
P1, P2, P3 ... Pn → C
```
For each Pi, identify what it depends on (evidence, prior claims, assumptions).

**Step 2 — Traverse for Loops**
Starting from C, walk backwards through dependencies:
- Does any path from C lead back to C?
- Does any Pi depend on C, directly or through another Pk?

**Step 3 — Compute M**
```
M = number of detected dependency loops (direct + indirect)

M = 0         → GREEN  — no circular residue
M = 1 indirect → ORANGE — loop exists but is non-direct; caveat required
M ≥ 1 direct  → RED    — conclusion is self-referential; halt emission
```

## 🔧 Breaking the Loop

When M ≥ 1:
1. **Identify the loop node**: Which premise Pi is circularly dependent?
2. **Reclassify**: If Pi cannot be grounded without C, reclassify it as an *assumption*, not a premise.
3. **State the assumption explicitly**: "This conclusion holds if we assume [Pi], which is not independently verified."
4. **Re-evaluate**: With Pi as assumption rather than premise, is C still the best conclusion?

## 🏛️ Governing Laws

- **Law 1 — Halt on direct loop**: If C appears in its own premise chain, do NOT emit C as a fact. Emit it as a conditional.
- **Law 2 — Indirect loops require disclosure**: Indirect loops (A→B→C→A) must be named in the response.
- **Law 3 — Refinement amplifies loops**: Each time reasoning is iterated, re-run the graph traversal. Loops can emerge during refinement.
- **Law 4 — Definitions are not premises**: Be careful not to confuse tautologies (true by definition) with circular reasoning. M only counts empirical/inferential loops.

---
*Inspired by Gahenax/OEDA_HodgeRigidity — Monodromy M metric, residue detection protocol*
