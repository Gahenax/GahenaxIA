"""
GahenaxAdversarialGates
-----------------------
Adapted from github.com/Gahenax/P-ATLAS-NP/src/gates/adversarial.py

Validates the GahenaxAtlasClassifier's feature space quality after each rebuild.
Uses only the stored dataset (features + raw text) — zero external dependencies.

7 Gates (mapped from P-ATLAS-NP's taxonomy):

  Gate 1 - Semantics        Easy queries (low UA) vs hard queries are distinguishable
                            in feature space (normalized centroid distance ≥ threshold).

  Gate 2 - Rephrase         Word-order permutation of stored query text produces
            Invariance      Δv ≤ threshold (invariance to surface form).

  Gate 3 - Scale            Feature drift between short (<10w) and long (>30w)
            Independence    queries is bounded on non-length-sensitive coordinates.

  Gate 4 - Mode             Records grouped by UA band (easy / hard) cluster
            Consistency     consistently — low intra-cluster CV vs inter-cluster.

  Gate 5 - Perturbation     Random word removal keeps Δv ≤ threshold
            Resistance      (stability under noise).

  Gate 6 - Camouflage       Deceptively simple queries (low spectral complexity
            Detection       but high UA) are NOT silently misclassified.

  Gate 7 - Falsifiability   No contradictory data: records that are in the same
            Check           neighborhood but have wildly different UA (poison detection).
"""
from __future__ import annotations

import math
import random
import re
from typing import Any, Dict, List, Optional, Tuple

from .extractor import GahenaxSignatureExtractor

_WORD = re.compile(r'\b\w+\b', re.UNICODE)


# ---------------------------------------------------------------------------
# Vector math helpers (stdlib only — no numpy)
# ---------------------------------------------------------------------------

def _mean_vec(records: List[Dict[str, float]], coords: List[str]) -> List[float]:
    if not records:
        return [0.0] * len(coords)
    n = len(records)
    return [sum(r.get(c, 0.0) for r in records) / n for c in coords]


def _std_scalar(values: List[float]) -> float:
    if len(values) < 2:
        return 0.0
    mu = sum(values) / len(values)
    return (sum((v - mu) ** 2 for v in values) / len(values)) ** 0.5


def _norm(v: List[float]) -> float:
    return math.sqrt(sum(x * x for x in v))


def _delta_v(va: List[float], vb: List[float]) -> float:
    return _norm([a - b for a, b in zip(va, vb)])


def _zscore_stats(records: List[Dict[str, float]], coords: List[str]) -> Dict[str, Tuple[float, float]]:
    """Returns {coord: (mean, std)} for each coord."""
    stats: Dict[str, Tuple[float, float]] = {}
    for c in coords:
        vals = [r.get(c, 0.0) for r in records]
        mu = sum(vals) / max(len(vals), 1)
        sd = _std_scalar(vals) + 1e-8
        stats[c] = (mu, sd)
    return stats


def _zscore_vec(row: Dict[str, float], coords: List[str],
                stats: Dict[str, Tuple[float, float]]) -> List[float]:
    result = []
    for c in coords:
        mu, sd = stats[c]
        result.append((row.get(c, 0.0) - mu) / sd)
    return result


def _shuffle_words(text: str, seed: int) -> str:
    """Shuffle words within each sentence (permutation invariance test)."""
    import re as _re
    sentences = _re.split(r'[.!?]+', text)
    rng = random.Random(seed)
    shuffled = []
    for s in sentences:
        words = _WORD.findall(s)
        if words:
            rng.shuffle(words)
            shuffled.append(" ".join(words))
    return ". ".join(shuffled) if shuffled else text


def _drop_words(text: str, rate: float, seed: int) -> str:
    """Drop ~rate fraction of words (perturbation test)."""
    words = _WORD.findall(text)
    if not words:
        return text
    rng = random.Random(seed)
    kept = [w for w in words if rng.random() > rate]
    return " ".join(kept) if kept else text


# ---------------------------------------------------------------------------
# Gate runner
# ---------------------------------------------------------------------------

class GahenaxAdversarialGates:
    """
    Validates the current atlas dataset's feature-space quality.
    Call run_all() after every atlas rebuild.
    """

    def __init__(self, extractor: Optional[GahenaxSignatureExtractor] = None):
        self._ext = extractor or GahenaxSignatureExtractor()

    def run_all(
        self,
        records: List[Dict[str, Any]],
        coords: List[str],
        plan: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Run all 7 gates on the current atlas dataset.
        Returns a dict with per-gate results and a final_verdict.
        """
        plan = plan or {}
        gate_cfg = plan.get("adversarial_gates", {})
        stats = _zscore_stats(records, coords)

        results: Dict[str, Any] = {}
        results["gate_1_semantics"] = self._gate_semantics(records, coords, stats, gate_cfg)
        results["gate_2_rephrase"] = self._gate_rephrase(records, coords, stats, gate_cfg)
        results["gate_3_scale"] = self._gate_scale(records, coords, stats, gate_cfg)
        results["gate_4_mode_consistency"] = self._gate_mode(records, coords, gate_cfg)
        results["gate_5_perturbation"] = self._gate_perturbation(records, coords, stats, gate_cfg)
        results["gate_6_camouflage"] = self._gate_camouflage(records, coords, stats, gate_cfg)
        results["gate_7_falsifiability"] = self._gate_falsifiability(records, gate_cfg)

        all_pass = all(
            v.get("status") in ("PASS", "INCONCLUSIVE")
            for v in results.values()
            if isinstance(v, dict)
        )
        results["final_verdict"] = "ATLAS_VALIDATED" if all_pass else "ATLAS_WARNING"
        return results

    # ------------------------------------------------------------------
    # Gate 1 — Semantics: easy vs hard separation
    # ------------------------------------------------------------------

    def _gate_semantics(
        self,
        records: List[Dict[str, Any]],
        coords: List[str],
        stats: Dict[str, Tuple[float, float]],
        cfg: Dict[str, Any],
    ) -> Dict[str, Any]:
        gate_cfg = cfg.get("gate_1_semantics", {})
        min_dist = float(gate_cfg.get("min_normalized_dist", 0.15))

        H = [r.get("target_H", 0.0) for r in records]
        if len(H) < 4:
            return {"status": "INCONCLUSIVE", "score": 0.5,
                    "details": "Insufficient data (need ≥ 4 records)"}

        median_H = sorted(H)[len(H) // 2]
        easy = [r for r in records if r.get("target_H", 0.0) < median_H]
        hard = [r for r in records if r.get("target_H", 0.0) >= median_H]

        if not easy or not hard:
            return {"status": "INCONCLUSIVE", "score": 0.5,
                    "details": "Cannot split into easy/hard groups"}

        easy_z = [_zscore_vec(r, coords, stats) for r in easy]
        hard_z = [_zscore_vec(r, coords, stats) for r in hard]
        easy_mean = [sum(v[i] for v in easy_z) / len(easy_z) for i in range(len(coords))]
        hard_mean = [sum(v[i] for v in hard_z) / len(hard_z) for i in range(len(coords))]

        dist = _delta_v(easy_mean, hard_mean)
        score = min(1.0, dist / (min_dist + 1e-8))
        status = "PASS" if dist >= min_dist else "FAIL"
        return {
            "status": status,
            "score": round(score, 6),
            "details": f"centroid dist easy/hard = {dist:.4f} (min {min_dist})",
        }

    # ------------------------------------------------------------------
    # Gate 2 — Rephrase invariance: word shuffle → Δv bounded
    # ------------------------------------------------------------------

    def _gate_rephrase(
        self,
        records: List[Dict[str, Any]],
        coords: List[str],
        stats: Dict[str, Tuple[float, float]],
        cfg: Dict[str, Any],
    ) -> Dict[str, Any]:
        gate_cfg = cfg.get("gate_2_rephrase", {})
        threshold = float(gate_cfg.get("delta_v_threshold", 5.0))
        n_shuffles = int(gate_cfg.get("n_shuffles", 3))
        sample_n = int(gate_cfg.get("sample_n", 20))

        text_records = [r for r in records if r.get("_raw_text")]
        if len(text_records) < 3:
            return {"status": "INCONCLUSIVE", "score": 0.5,
                    "details": "No stored raw text — run more inferences first"}

        sampled = text_records[:sample_n]
        deltas = []
        for rec in sampled:
            text = rec["_raw_text"]
            base_feat, _ = self._ext.extract_all(text)
            base_v = _zscore_vec(base_feat, coords, stats)

            worst = 0.0
            for j in range(n_shuffles):
                shuffled = _shuffle_words(text, seed=hash(text) + j)
                shuf_feat, _ = self._ext.extract_all(shuffled)
                shuf_v = _zscore_vec(shuf_feat, coords, stats)
                dv = _delta_v(base_v, shuf_v)
                worst = max(worst, dv)
            deltas.append(worst)

        worst_case = max(deltas) if deltas else 999.0
        score = max(0.0, 1.0 - worst_case / (threshold + 1e-8))
        status = "PASS" if worst_case <= threshold else "FAIL"
        return {
            "status": status,
            "score": round(score, 6),
            "details": (
                f"worst Δv (word-shuffle) = {worst_case:.4f}, "
                f"threshold = {threshold}, samples = {len(deltas)}"
            ),
        }

    # ------------------------------------------------------------------
    # Gate 3 — Scale independence: short vs long text drift bounded
    # ------------------------------------------------------------------

    def _gate_scale(
        self,
        records: List[Dict[str, Any]],
        coords: List[str],
        stats: Dict[str, Tuple[float, float]],
        cfg: Dict[str, Any],
    ) -> Dict[str, Any]:
        gate_cfg = cfg.get("gate_3_scale", {})
        max_drift = float(gate_cfg.get("max_relative_drift", 2.0))

        # Use spectral_complexity_proxy as length proxy
        by_complexity = sorted(records, key=lambda r: r.get("spectral_complexity_proxy", 0.0))
        n = len(by_complexity)
        if n < 6:
            return {"status": "INCONCLUSIVE", "score": 0.5,
                    "details": "Need ≥ 6 records for scale gate"}

        short = by_complexity[: n // 3]
        long_ = by_complexity[n - n // 3:]

        # Exclude structural feature (naturally correlated with text length)
        non_structural = [c for c in coords if "spectral" not in c and "structural" not in c]
        if not non_structural:
            non_structural = coords

        sm = [sum(r.get(c, 0.0) for r in short) / len(short) for c in non_structural]
        lg = [sum(r.get(c, 0.0) for r in long_) / len(long_) for c in non_structural]

        overall_mean = abs(sum(sm) / max(len(sm), 1)) + 1e-8
        drift = _delta_v(sm, lg) / overall_mean

        score = max(0.0, 1.0 - drift / (max_drift + 1e-8))
        status = "PASS" if drift <= max_drift else "FAIL"
        return {
            "status": status,
            "score": round(score, 6),
            "details": f"relative drift short/long = {drift:.4f} (max {max_drift})",
        }

    # ------------------------------------------------------------------
    # Gate 4 — Mode consistency: UA bands cluster in feature space
    # ------------------------------------------------------------------

    def _gate_mode(
        self,
        records: List[Dict[str, Any]],
        coords: List[str],
        cfg: Dict[str, Any],
    ) -> Dict[str, Any]:
        gate_cfg = cfg.get("gate_4_mode", {})
        max_cv = float(gate_cfg.get("max_intra_cv", 0.80))

        H = [r.get("target_H", 0.0) for r in records]
        if not H or len(H) < 4:
            return {"status": "INCONCLUSIVE", "score": 0.5,
                    "details": "Need ≥ 4 records"}

        h_sorted = sorted(H)
        lo_thr = h_sorted[len(h_sorted) // 3]
        hi_thr = h_sorted[2 * len(h_sorted) // 3]

        low_ua = [r for r in records if r.get("target_H", 0.0) <= lo_thr]
        high_ua = [r for r in records if r.get("target_H", 0.0) >= hi_thr]

        if not low_ua or not high_ua:
            return {"status": "INCONCLUSIVE", "score": 0.5,
                    "details": "Cannot form UA bands"}

        cvs = []
        for group in (low_ua, high_ua):
            for c in coords:
                vals = [r.get(c, 0.0) for r in group]
                mu = sum(vals) / len(vals)
                sd = _std_scalar(vals)
                cvs.append(sd / (abs(mu) + 1e-8))

        mean_cv = sum(cvs) / max(len(cvs), 1)
        score = max(0.0, 1.0 - mean_cv / (max_cv + 1e-8))
        status = "PASS" if mean_cv <= max_cv else "FAIL"
        return {
            "status": status,
            "score": round(score, 6),
            "details": f"mean intra-band CV = {mean_cv:.4f} (max {max_cv})",
        }

    # ------------------------------------------------------------------
    # Gate 5 — Perturbation resistance: word drop → Δv bounded
    # ------------------------------------------------------------------

    def _gate_perturbation(
        self,
        records: List[Dict[str, Any]],
        coords: List[str],
        stats: Dict[str, Tuple[float, float]],
        cfg: Dict[str, Any],
    ) -> Dict[str, Any]:
        gate_cfg = cfg.get("gate_5_perturbation", {})
        rate = float(gate_cfg.get("perturbation_rate", 0.15))
        threshold = float(gate_cfg.get("delta_v_threshold", 5.0))
        sample_n = int(gate_cfg.get("sample_n", 20))

        text_records = [r for r in records if r.get("_raw_text")]
        if len(text_records) < 3:
            return {"status": "INCONCLUSIVE", "score": 0.5,
                    "details": "No stored raw text — run more inferences first"}

        sampled = text_records[:sample_n]
        deltas = []
        for rec in sampled:
            text = rec["_raw_text"]
            base_feat, _ = self._ext.extract_all(text)
            base_v = _zscore_vec(base_feat, coords, stats)

            perturbed = _drop_words(text, rate=rate, seed=hash(text) ^ 0xDEAD)
            pert_feat, _ = self._ext.extract_all(perturbed)
            pert_v = _zscore_vec(pert_feat, coords, stats)
            deltas.append(_delta_v(base_v, pert_v))

        worst = max(deltas) if deltas else 999.0
        score = max(0.0, 1.0 - worst / (threshold + 1e-8))
        status = "PASS" if worst <= threshold else "FAIL"
        return {
            "status": status,
            "score": round(score, 6),
            "details": (
                f"worst Δv (word-drop {int(rate*100)}%) = {worst:.4f}, "
                f"threshold = {threshold}, samples = {len(deltas)}"
            ),
        }

    # ------------------------------------------------------------------
    # Gate 6 — Camouflage detection: deceptively simple hard queries
    # ------------------------------------------------------------------

    def _gate_camouflage(
        self,
        records: List[Dict[str, Any]],
        coords: List[str],
        stats: Dict[str, Tuple[float, float]],
        cfg: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Detects "spectral camouflage": queries that look structurally simple
        (low spectral_complexity_proxy) but are genuinely hard (high target_H).
        These should NOT cluster with easy queries in the feature space —
        at least one discriminating coordinate must separate them.
        """
        gate_cfg = cfg.get("gate_6_camouflage", {})
        max_frac = float(gate_cfg.get("max_camouflage_fraction", 0.30))

        if not records:
            return {"status": "INCONCLUSIVE", "score": 0.5, "details": "No data"}

        H = [r.get("target_H", 0.0) for r in records]
        sc = [r.get("spectral_complexity_proxy", 0.0) for r in records]
        median_H = sorted(H)[len(H) // 2]
        median_sc = sorted(sc)[len(sc) // 2]

        # Camouflaged: low structural complexity but high UA cost
        camouflaged = [
            r for r in records
            if r.get("spectral_complexity_proxy", 0.0) < median_sc
            and r.get("target_H", 0.0) > median_H
        ]
        frac = len(camouflaged) / max(len(records), 1)

        # It's OK to have some camouflaged — they're real. The concern is
        # whether they're misclassified as P_LOCAL due to structural naivety.
        # We check that at least one algebraic/thermodyn feature separates them.
        separating = False
        for coord in coords:
            if "algebra" in coord or "thermo" in coord:
                cam_mean = (sum(r.get(coord, 0.0) for r in camouflaged) / max(len(camouflaged), 1)
                            if camouflaged else 0.0)
                rest = [r for r in records if r not in camouflaged]
                rest_mean = (sum(r.get(coord, 0.0) for r in rest) / max(len(rest), 1)
                             if rest else 0.0)
                # zscore both
                mu, sd = stats.get(coord, (0.0, 1.0))
                cam_z = (cam_mean - mu) / (sd + 1e-8)
                rest_z = (rest_mean - mu) / (sd + 1e-8)
                if abs(cam_z - rest_z) >= 0.3:
                    separating = True
                    break

        if not camouflaged:
            return {"status": "PASS", "score": 1.0,
                    "details": "No camouflaged instances detected"}
        if frac <= max_frac and separating:
            return {"status": "PASS", "score": round(1.0 - frac, 6),
                    "details": f"Camouflage fraction {frac:.2%} within limit; feature separation confirmed"}
        status = "FAIL" if not separating and frac > 0.1 else "PASS"
        return {
            "status": status,
            "score": round(max(0.0, 1.0 - frac), 6),
            "details": (
                f"Camouflage fraction = {frac:.2%} (max {max_frac:.0%}), "
                f"separating_coord = {separating}"
            ),
        }

    # ------------------------------------------------------------------
    # Gate 7 — Falsifiability: contradiction / poison detection
    # ------------------------------------------------------------------

    def _gate_falsifiability(
        self,
        records: List[Dict[str, Any]],
        cfg: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Detects contradictory records: two records whose feature vectors are
        very similar (likely same query) but have wildly different UA costs.
        This indicates either data poisoning or a systematic measurement error.
        Based on P-ATLAS-NP Gate 7 (unit-clause contradiction detection).
        """
        gate_cfg = cfg.get("gate_7_falsifiability", {})
        max_ratio = float(gate_cfg.get("max_ua_ratio", 5.0))  # max allowed ua_a/ua_b

        text_records = [r for r in records if r.get("_raw_text") and r.get("target_H", 0.0) > 0]
        if len(text_records) < 4:
            return {"status": "INCONCLUSIVE", "score": 1.0,
                    "details": "Insufficient records for contradiction check"}

        # Group by text fingerprint (first 60 chars, lowercased)
        by_fp: Dict[str, List[float]] = {}
        for r in text_records:
            fp = r["_raw_text"][:60].lower().strip()
            by_fp.setdefault(fp, []).append(r.get("target_H", 0.0))

        contradictions = []
        for fp, ua_vals in by_fp.items():
            if len(ua_vals) < 2:
                continue
            hi = max(ua_vals)
            lo = min(ua_vals)
            if lo > 0 and hi / lo >= max_ratio:
                contradictions.append(fp[:30])

        if contradictions:
            return {
                "status": "FAIL",
                "score": 0.0,
                "details": (
                    f"Contradiction detected in {len(contradictions)} query fingerprint(s): "
                    f"same query, UA ratio ≥ {max_ratio}x. "
                    f"First: '{contradictions[0]}...'"
                ),
            }
        return {
            "status": "PASS",
            "score": 1.0,
            "details": f"No contradictions found in {len(text_records)} text-records",
        }
