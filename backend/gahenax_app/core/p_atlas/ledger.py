"""
Atlas Ledger
------------
Port from github.com/Gahenax/P-ATLAS-NP/src/ledger/ledger.py

Chain-validated JSONL audit log for the P-ATLAS-NP complexity atlas.
Records gate validation results, atlas rebuilds, and complexity classifications.
Separate from the main CMR — this is the atlas's own falsifiability trail.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Tuple


def _now_z() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class AtlasLedger:
    """
    Append-only, chain-validated JSONL ledger for atlas events.
    Direct port of P-ATLAS-NP's Ledger class — same hash-chain protocol.
    """

    def __init__(self, path: str = "evidence/atlas_ledger.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.prev_hash = "0" * 64
        if self.path.exists():
            self._load_tail()

    # ------------------------------------------------------------------

    def _load_tail(self) -> None:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                last_line = None
                for last_line in f:
                    pass
                if last_line:
                    last = json.loads(last_line)
                    self.prev_hash = last.get("self_hash", "0" * 64)
        except Exception:
            pass

    def record(self, event_type: str, data: Dict[str, Any]) -> str:
        """Append a chain-linked event. Returns the event's self_hash."""
        event = {
            "event_type": event_type,
            "ts": _now_z(),
            "prev_hash": self.prev_hash,
            **data,
        }
        # hash excludes self_hash (same protocol as P-ATLAS-NP)
        event_for_hash = {k: v for k, v in event.items() if k != "self_hash"}
        blob = json.dumps(event_for_hash, sort_keys=True, default=str).encode("utf-8")
        self_hash = hashlib.sha256(blob).hexdigest()
        event["self_hash"] = self_hash

        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, default=str) + "\n")

        self.prev_hash = self_hash
        return self_hash

    def record_rebuild(self, n_points: int, coords: list, frontier_frac: float) -> str:
        return self.record("ATLAS_REBUILD", {
            "n_points": n_points,
            "coords": coords,
            "frontier_fraction": round(frontier_frac, 6),
        })

    def record_gates(self, gate_results: Dict[str, Any], verdict: str) -> str:
        return self.record("GATE_VALIDATION", {
            "verdict": verdict,
            "gates": {
                k: {"status": v.get("status"), "score": v.get("score")}
                for k, v in gate_results.items()
                if isinstance(v, dict) and "status" in v
            },
        })

    def record_classification(
        self, complexity_class: str, frontier_score: float, predicted_ua: float
    ) -> str:
        return self.record("CLASSIFICATION", {
            "complexity_class": complexity_class,
            "frontier_score": round(frontier_score, 6),
            "predicted_ua": round(predicted_ua, 4),
        })

    def count_events(self) -> int:
        if not self.path.exists():
            return 0
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return sum(1 for _ in f)
        except Exception:
            return 0

    def validate_chain(self) -> Tuple[bool, str]:
        """Verify the integrity of the entire ledger chain."""
        if not self.path.exists():
            return True, "No ledger to validate"
        prev = "0" * 64
        errors = []
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError as e:
                        return False, f"Line {line_num}: invalid JSON ({e})"
                    if event.get("prev_hash") != prev:
                        errors.append(f"Line {line_num}: hash-chain break")
                    test = {k: v for k, v in event.items() if k != "self_hash"}
                    blob = json.dumps(test, sort_keys=True, default=str).encode("utf-8")
                    computed = hashlib.sha256(blob).hexdigest()
                    if computed != event.get("self_hash"):
                        errors.append(f"Line {line_num}: hash mismatch (tampering?)")
                    prev = event.get("self_hash", "0" * 64)
        except Exception as exc:
            return False, str(exc)
        if errors:
            return False, "; ".join(errors[:3])
        return True, f"Chain valid — {self.count_events()} events"
