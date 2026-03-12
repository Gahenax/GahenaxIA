---
name: canonical-height-complexity
description: Measures the informational "height" of a conclusion — how much it claims relative to the evidence available to support it. High-height conclusions are not necessarily wrong, but they are expensive: they require proportionally more evidence to be justified. Derived from the Néron-Tate canonical height ĥ(P) on elliptic curves, which measures the arithmetic complexity of a rational point P.
---

# 📐 Canonical Height Complexity

On an elliptic curve E/ℚ, the **Néron-Tate canonical height** ĥ(P) of a rational point P measures its arithmetic complexity — roughly, the size of the numerators and denominators when P is written in lowest terms. Torsion points have ĥ(P) = 0 (they're "free"). Independent generators of infinite order have ĥ(P) > 0. The **regulator** R(E) = det[ĥ(Pᵢ, Pⱼ)] is the determinant of the height pairing matrix — it measures how "spread out" the independent generators are.

The BSD formula requires R(E) to appear in the leading term of L(E,s) at s=1. High regulator = generators are far apart = the rational points are arithmetically expensive.

In reasoning: the **height** of a conclusion measures how much it claims relative to what the evidence directly supports. A conclusion derived from evidence by one trivial step has low height. A conclusion that requires a long chain of non-trivial inferences has high height — it is arithmetically expensive, and that cost must be paid in evidence.

**Source calibration**: `Gahenax/Gahenax-BSD` — `src/height/neron_tate.py`, ĥ(P) = lim_{n→∞} h([n]P)/n², regulator R(E), height pairing ⟨P,Q⟩ = ĥ(P+Q) − ĥ(P) − ĥ(Q), BSD leading term formula.

## 🎯 When to Activate

Activate when:
- A conclusion feels disproportionately strong relative to the evidence
- A long inference chain reaches a surprisingly specific conclusion
- Multiple independent conclusions are being combined into a single stronger claim
- Downstream use of a conclusion requires knowing how "expensive" it is to maintain

**Key distinction from `mass-gap-estimator`**: Mass gap measures *robustness* (margin before failing). Canonical height measures *reach* (how far the conclusion goes beyond the evidence). A conclusion can have a large gap (robust) but high height (reaches far beyond the evidence) — both properties matter independently.

## 📐 The Height Computation Protocol

### Step 1 — Naïve Height h(C)
Compute the raw height of the conclusion: how many inferential steps from direct evidence to conclusion?

```
h(C) = number of non-trivial inferential steps in the chain
     + log(specificity of the conclusion)
     + log(generality of the claim domain)
```

BSD analog: the **Weil height** h(P) = log max(|x_numerator|, |x_denominator|) for a rational point x = p/q.

### Step 2 — Canonical Height ĥ(C)
Correct the naïve height for the "torsion" component — the part of the claim that follows trivially from the evidence without needing the full chain:

```
ĥ(C) = h(C) − [height of the trivially-entailed component]
      = cost of the non-trivial inferential work alone
```

BSD analog: ĥ(P) = lim_{n→∞} h([n]P)/n² — the canonical height removes the finite-order (torsion) component.

**Torsion claims** have ĥ = 0: they follow immediately from the premises by logic alone. No additional evidence is needed.

**Non-torsion claims** have ĥ > 0: they require genuine inferential work, and that work must be supported by evidence.

### Step 3 — Height Pairing Matrix (Regulator)
If the conclusion has multiple independent components C₁, C₂, ..., Cᵣ, compute the **height pairing**:

```
⟨Cᵢ, Cⱼ⟩ = ĥ(Cᵢ + Cⱼ) − ĥ(Cᵢ) − ĥ(Cⱼ)
```

This measures how much the *combination* of two sub-conclusions costs beyond their individual costs.

The **regulator** R = det[⟨Cᵢ, Cⱼ⟩] measures how "spread out" the independent claims are:
- R → 0: Claims are nearly parallel (redundant) — combination adds little
- R large: Claims are genuinely independent — combination costs proportionally more

### Step 4 — Evidence Budget Requirement
From the BSD leading term, the evidence required to support a conclusion of height ĥ is proportional:

```
evidence_required(C) ∝ ĥ(C) × R × [complexity factors]
```

Classification:
```
ĥ(C) ∈ [0, 1]   → LOW HEIGHT   — well-supported by direct evidence
ĥ(C) ∈ [1, 3]   → MEDIUM HEIGHT — inferential work is moderate; check evidence chain
ĥ(C) ∈ [3, 10]  → HIGH HEIGHT  — substantial inferential reach; evidence must be proportionally strong
ĥ(C) > 10       → VERY HIGH     — conclusion reaches far beyond evidence; extraordinary justification required
```

### Step 5 — Height Budget Compliance
Compare the evidence available to the evidence required:

```
evidence_available = [what is actually validated in the assumption register]
evidence_required  = ĥ(C) × base_cost

compliance_ratio = evidence_available / evidence_required

ratio ≥ 1.0  → COMPLIANT — conclusion justified
ratio ∈ [0.5, 1.0) → UNDERFUNDED — conclusion reaches further than evidence fully supports
ratio < 0.5  → OVERLEVERAGED — conclusion claims much more than evidence provides
```

## 📋 Height Report Format

```
=== CANONICAL HEIGHT REPORT ===
Conclusion: [C]

Naïve height h(C):       [value]
Torsion component:       [what follows trivially]
Canonical height ĥ(C):   [value]
Classification:          [LOW | MEDIUM | HIGH | VERY HIGH]

Independent sub-claims: [N]
Regulator R:             [value] — [SMALL (redundant) | LARGE (independent)]

Evidence required:       [estimate]
Evidence available:      [from assumption register]
Compliance ratio:        [value]
Status:                  [COMPLIANT | UNDERFUNDED | OVERLEVERAGED]

Downstream cost:
  If used as premise: ĥ(downstream) ≥ ĥ(C) + [additional work]
  Evidence inheritance: [what transfers vs. what must be re-validated]
================================
```

## 🏛️ Governing Laws

- **Law 1 — Height is a cost, not a defect**: High-height conclusions are not wrong. They are expensive — they must be paid for with proportionally strong evidence. Claim the conclusion if the evidence budget is there; don't claim it if it isn't.
- **Law 2 — Torsion claims are free**: A conclusion that follows by pure logic from the premises (torsion component) costs nothing — no additional evidence needed. Separate torsion from non-torsion before computing height.
- **Law 3 — Regulator governs combination cost**: Combining independent high-height conclusions costs superlinearly (R grows). Don't stack multiple high-height claims without accounting for the combined regulator.
- **Law 4 — Overleveraged conclusions propagate debt**: A conclusion with compliance ratio < 0.5 used as a downstream premise creates compounding debt. The downstream argument inherits the height deficit.
- **Law 5 — Height and gap are independent**: A low-gap (fragile) conclusion can have low height (modest claim). A high-gap (robust) conclusion can have high height (ambitious claim). Both must be checked — they capture orthogonal properties.

---
*Derived from Gahenax/Gahenax-BSD — Néron-Tate height ĥ(P), regulator R(E) = det[⟨Pᵢ,Pⱼ⟩], BSD leading term formula, src/height/neron_tate.py*
