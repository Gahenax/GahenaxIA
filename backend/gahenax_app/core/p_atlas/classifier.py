"""
GahenaxAtlasClassifier
----------------------
Main integration point between P-ATLAS-NP and GahenaxIA.

Lifecycle:
  1. Governor extracts a feature signature from the query text.
  2. Classifier looks up (or updates) the persistent atlas.
  3. Returns a ComplexityAssessment that tells the Governor how to calibrate UA.

After each atlas rebuild:
  - GahenaxAdversarialGates validates the feature space (7 gates)
  - Results recorded in AtlasLedger (chain-validated JSONL)

Complexity classes (mapped from P-ATLAS-NP's hardness spectrum):
  P_LOCAL    — well inside the easy region; retrieval/mock suffices
  FRONTIER   — high-variance zone; allocate conservatively, may need AUDIT mode
  NP_HARD    — consistently expensive; pre-authorize Ruflo swarm
  UNKNOWN    — atlas too thin to classify; use defaults

The atlas is persisted as a JSON file so it accumulates knowledge across sessions
(P-ATLAS-NP's "campaign memory" pattern).
"""
from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .extractor import GahenaxSignatureExtractor
from .compressor import VectorCompressor
from .atlas import build_frontier_knn, lookup_frontier_score, _zscore_normalize
from .ledger import AtlasLedger
from .gates import GahenaxAdversarialGates

logger = logging.getLogger(__name__)

# Minimum atlas data points before frontier detection kicks in
_MIN_ATLAS_POINTS = 8
# How often (in new data points) to rebuild the compressed atlas
_REBUILD_EVERY = 5
# Max raw text stored per record (chars) — for gate 2/5
_RAW_TEXT_MAX = 500
# Default atlas file
_DEFAULT_ATLAS_PATH = "evidence/gahenax_atlas.json"
_DEFAULT_LEDGER_PATH = "evidence/atlas_ledger.jsonl"


@dataclass
class ComplexityAssessment:
    complexity_class: str           # P_LOCAL | MODERATE | FRONTIER | NP_HARD | UNKNOWN
    frontier_score: float           # local_std(H) at query location [0..∞)
    predicted_ua: float             # estimated UA spend for this query
    recommended_mode: str           # everyday | audit | experiment
    ua_budget_override: Optional[float]  # None = use Governor default
    reasoning: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


_FALLBACK = ComplexityAssessment(
    complexity_class="UNKNOWN",
    frontier_score=0.0,
    predicted_ua=4.0,
    recommended_mode="everyday",
    ua_budget_override=None,
    reasoning="Atlas too thin to classify. Using defaults.",
)


class GahenaxAtlasClassifier:
    """
    Persistent complexity classifier backed by a P-ATLAS-NP-style kNN atlas.

    Usage:
        classifier = GahenaxAtlasClassifier()

        # Before LLM call:
        assessment = classifier.classify(query_text, context)
        # → use assessment.recommended_mode, assessment.ua_budget_override

        # After CMR record_run():
        classifier.update(query_text, context, ua_spend=3.5, h_rigidity=0.1)
    """

    def __init__(
        self,
        atlas_path: str = _DEFAULT_ATLAS_PATH,
        ledger_path: str = _DEFAULT_LEDGER_PATH,
    ):
        self._path = Path(atlas_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

        self._extractor = GahenaxSignatureExtractor()
        self._compressor = VectorCompressor()
        self._ledger = AtlasLedger(ledger_path)
        self._gates = GahenaxAdversarialGates(self._extractor)

        # Dataset: list of {features..., target_H, target_D, _raw_text}
        self._dataset: List[Dict[str, Any]] = []
        # Current compressed state
        self._coords: List[str] = []
        self._atlas_vmat_z: List[List[float]] = []
        self._local_std: List[float] = []
        self._frontier_threshold: float = 0.0
        self._H_values: List[float] = []
        self._new_since_rebuild: int = 0
        # Last gate validation verdict
        self._gate_verdict: str = "UNVALIDATED"

        self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def classify(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ComplexityAssessment:
        """Classify the complexity of a query before the Governor runs."""
        try:
            result = self._classify_internal(text, context)
            # Record in ledger (background-safe: ledger writes are fast)
            self._ledger.record_classification(
                result.complexity_class, result.frontier_score, result.predicted_ua
            )
            return result
        except Exception as exc:
            logger.debug("Atlas classify failed (non-critical): %s", exc)
            return _FALLBACK

    def update(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None,
        ua_spend: float = 0.0,
        h_rigidity: Optional[float] = None,
    ) -> None:
        """Record a completed inference cycle into the atlas dataset."""
        try:
            features, _ = self._extractor.extract_all(text, context)
            features["target_H"] = float(ua_spend)
            features["target_D"] = float(h_rigidity or 0.0)
            # Store truncated raw text for gate 2/5 (rephrase + perturbation)
            features["_raw_text"] = text[:_RAW_TEXT_MAX]
            self._dataset.append(features)
            self._new_since_rebuild += 1
            if (
                len(self._dataset) >= _MIN_ATLAS_POINTS
                and self._new_since_rebuild >= _REBUILD_EVERY
            ):
                self._rebuild_atlas()
            self._save()
        except Exception as exc:
            logger.debug("Atlas update failed (non-critical): %s", exc)

    def get_gate_verdict(self) -> str:
        """Last adversarial gate validation result."""
        return self._gate_verdict

    def validate_ledger(self) -> Tuple[bool, str]:
        """Check chain integrity of the atlas ledger."""
        return self._ledger.validate_chain()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _classify_internal(
        self,
        text: str,
        context: Optional[Dict[str, Any]],
    ) -> ComplexityAssessment:
        if len(self._dataset) < _MIN_ATLAS_POINTS or not self._coords:
            return _FALLBACK

        features, _ = self._extractor.extract_all(text, context)
        query_raw = [float(features.get(c, 0.0)) for c in self._coords]

        query_z = self._zscore_query(query_raw)
        frontier_score = lookup_frontier_score(
            query_z, self._atlas_vmat_z, self._local_std, k=min(5, len(self._dataset) - 1)
        )

        predicted_ua = self._predict_ua(query_z)
        complexity_class, mode, budget_override, reasoning = self._classify_from_score(
            frontier_score, predicted_ua
        )

        return ComplexityAssessment(
            complexity_class=complexity_class,
            frontier_score=round(frontier_score, 6),
            predicted_ua=round(predicted_ua, 4),
            recommended_mode=mode,
            ua_budget_override=budget_override,
            reasoning=reasoning,
        )

    def _predict_ua(self, query_z: List[float]) -> float:
        """Weighted average of H values of k nearest neighbours."""
        if not self._H_values or not self._atlas_vmat_z:
            return 4.0
        from .atlas import _euclidean_sq
        k = min(5, len(self._atlas_vmat_z))
        dists = [(i, _euclidean_sq(query_z, v)) for i, v in enumerate(self._atlas_vmat_z)]
        dists.sort(key=lambda x: x[1])
        neighbours = [i for i, _ in dists[:k]]
        return sum(self._H_values[i] for i in neighbours) / max(len(neighbours), 1)

    def _classify_from_score(
        self, frontier_score: float, predicted_ua: float
    ) -> Tuple[str, str, Optional[float], str]:
        """
        Returns (complexity_class, recommended_mode, ua_budget_override, reasoning).
        Thresholds calibrated to Gahenax UA scale (everyday budget = 6.0 UA).
        """
        thr = self._frontier_threshold

        if frontier_score < thr * 0.5 and predicted_ua <= 3.0:
            return (
                "P_LOCAL",
                "everyday",
                4.0,
                f"Low frontier_score ({frontier_score:.3f}) + predicted_ua {predicted_ua:.2f}. "
                "Query is in easy region — retrieval may suffice.",
            )
        if frontier_score >= thr:
            return (
                "FRONTIER",
                "audit",
                8.0,
                f"High frontier_score ({frontier_score:.3f} ≥ threshold {thr:.3f}). "
                "Query sits in high-variance zone — UA cost is unpredictable. "
                "Using AUDIT mode with expanded budget.",
            )
        if predicted_ua > 5.0:
            return (
                "NP_HARD",
                "audit",
                12.0,
                f"Predicted UA {predicted_ua:.2f} exceeds everyday budget. "
                "Query is consistently expensive — consider Ruflo swarm pre-authorization.",
            )
        return (
            "MODERATE",
            "everyday",
            None,
            f"frontier_score {frontier_score:.3f}, predicted_ua {predicted_ua:.2f}. "
            "Normal inference path.",
        )

    def _zscore_query(self, raw: List[float]) -> List[float]:
        """Z-score using the stored dataset statistics for each coord."""
        if not self._dataset or not self._coords:
            return raw
        n = len(self._dataset)
        result = []
        for i, c in enumerate(self._coords):
            vals = [r.get(c, 0.0) for r in self._dataset]
            mu = sum(vals) / n
            sd = (sum((v - mu) ** 2 for v in vals) / n) ** 0.5 + 1e-8
            result.append((raw[i] - mu) / sd)
        return result

    def _rebuild_atlas(self) -> None:
        """Refit compressor + rebuild kNN frontier from current dataset."""
        target_H = [r["target_H"] for r in self._dataset]
        target_D = [r["target_D"] for r in self._dataset]

        v = self._compressor.compress(self._dataset, target_H, target_D, max_dims=7)
        self._coords = v["coordinates"]
        if not self._coords:
            return

        frontier = build_frontier_knn(self._dataset, self._coords, k=min(5, len(self._dataset) - 1))
        vmat_raw = [[float(r.get(c, 0.0)) for c in self._coords] for r in self._dataset]
        self._atlas_vmat_z = _zscore_normalize(vmat_raw)
        self._local_std = frontier["local_std"]
        self._frontier_threshold = frontier["threshold"]
        self._H_values = target_H
        self._new_since_rebuild = 0

        # Log rebuild to ledger
        self._ledger.record_rebuild(
            n_points=len(self._dataset),
            coords=self._coords,
            frontier_frac=frontier["frontier_fraction"],
        )

        # Run adversarial gates — validate the feature space
        try:
            gate_results = self._gates.run_all(self._dataset, self._coords)
            self._gate_verdict = gate_results.get("final_verdict", "UNKNOWN")
            self._ledger.record_gates(gate_results, self._gate_verdict)
            logger.info(
                "P-ATLAS rebuilt: %d points, coords=%s, frontier_frac=%.2f, gates=%s",
                len(self._dataset), self._coords,
                frontier["frontier_fraction"], self._gate_verdict,
            )
        except Exception as exc:
            logger.debug("Atlas gate validation failed (non-critical): %s", exc)

    def _save(self) -> None:
        try:
            # Don't serialize _raw_text into the JSON (keep it in-memory only for perf)
            clean_dataset = [
                {k: v for k, v in r.items() if k != "_raw_text"}
                for r in self._dataset
            ]
            state = {
                "version": "gahenax_atlas_v2",
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "dataset": clean_dataset,
                "coords": self._coords,
                "frontier_threshold": self._frontier_threshold,
                "gate_verdict": self._gate_verdict,
            }
            self._path.write_text(json.dumps(state, indent=2), encoding="utf-8")
        except Exception as exc:
            logger.debug("Atlas save failed: %s", exc)

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            state = json.loads(self._path.read_text(encoding="utf-8"))
            self._dataset = state.get("dataset", [])
            self._coords = state.get("coords", [])
            self._frontier_threshold = state.get("frontier_threshold", 0.0)
            self._gate_verdict = state.get("gate_verdict", "UNVALIDATED")
            if len(self._dataset) >= _MIN_ATLAS_POINTS and self._coords:
                self._rebuild_atlas()
            logger.info(
                "P-ATLAS loaded: %d data points from %s (gates: %s)",
                len(self._dataset), self._path, self._gate_verdict,
            )
        except Exception as exc:
            logger.debug("Atlas load failed: %s", exc)
