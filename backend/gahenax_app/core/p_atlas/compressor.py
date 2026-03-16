"""
VectorCompressor
----------------
Verbatim port from github.com/Gahenax/P-ATLAS-NP/src/signatures/compressor.py
Selects the most informative feature dimensions based on correlation with
target_H (hardness / ua_spend) and target_D (difficulty / h_rigidity).
"""
from __future__ import annotations

from typing import Any, Dict, List


def _safe_corr(xs: List[float], ys: List[float]) -> float:
    """Pearson correlation without pandas/numpy dependency."""
    n = len(xs)
    if n < 2:
        return 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = (sum((x - mx) ** 2 for x in xs)) ** 0.5
    dy = (sum((y - my) ** 2 for y in ys)) ** 0.5
    if dx < 1e-9 or dy < 1e-9:
        return 0.0
    return num / (dx * dy)


class VectorCompressor:
    """
    Selects up to max_dims feature columns that are most correlated with
    both target_H and target_D, following P-ATLAS-NP's selection logic.
    """

    def compress(
        self,
        records: List[Dict[str, float]],
        target_H: List[float],
        target_D: List[float],
        max_dims: int = 7,
    ) -> Dict[str, Any]:
        if not records:
            return {"coordinates": [], "stability_score": 0.0,
                    "correlation_H": {}, "correlation_D": {}, "interpretation": "no data"}

        feature_cols = [
            k for k in records[0].keys()
            if k not in ("instance_id", "target_H", "target_D")
            and not k.startswith("_")  # exclude private fields like _raw_text
            and isinstance(records[0][k], (int, float))
        ]

        cors_H: List[tuple] = []
        cors_D: List[tuple] = []
        for col in feature_cols:
            vals = [r.get(col, 0.0) for r in records]
            h = abs(_safe_corr(vals, target_H))
            d = abs(_safe_corr(vals, target_D))
            cors_H.append((col, h))
            cors_D.append((col, d))

        cors_H.sort(key=lambda x: x[1], reverse=True)
        cors_D.sort(key=lambda x: x[1], reverse=True)

        top_H = [c for c, _ in cors_H[: max_dims * 2]]
        top_D = [c for c, _ in cors_D[: max_dims * 2]]

        selected = list(set(top_H) & set(top_D))
        if len(selected) < 3:
            selected = top_H[:max_dims]
        selected = selected[:max_dims]

        # stability proxy: 1 / (1 + cv)
        stability_scores = {}
        for col in selected:
            vals = [r.get(col, 0.0) for r in records]
            n = len(vals)
            mu = sum(vals) / n
            sd = (sum((v - mu) ** 2 for v in vals) / n) ** 0.5
            cv = sd / (abs(mu) + 1e-8)
            stability_scores[col] = 1 / (1 + abs(cv))

        mean_stability = (
            sum(stability_scores.values()) / len(stability_scores)
            if stability_scores else 0.0
        )

        cors_H_map = dict(cors_H)
        cors_D_map = dict(cors_D)

        return {
            "coordinates": selected,
            "formula": {c: f"zscore({c})" for c in selected},
            "stability_score": round(mean_stability, 6),
            "correlation_H": {c: round(cors_H_map.get(c, 0.0), 6) for c in selected},
            "correlation_D": {c: round(cors_D_map.get(c, 0.0), 6) for c in selected},
            "interpretation": self._interpret(selected),
        }

    def _interpret(self, coords: List[str]) -> str:
        fam = []
        if any("spectral" in c or "structural" in c or "concept" in c for c in coords):
            fam.append("Espectral/estructura")
        if any("thermo" in c or "uncertainty" in c or "negation" in c for c in coords):
            fam.append("Termodinámica/incertidumbre")
        if any("algebra" in c or "horn" in c or "reducible" in c for c in coords):
            fam.append("Álgebra/reducibilidad")
        return " | ".join(fam) if fam else "Señales mixtas"
