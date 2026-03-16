from __future__ import annotations

import hashlib
import json
import logging
import os
import sqlite3
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_hash(payload: Dict[str, Any]) -> str:
    canon = dict(payload)
    canon.pop("evidence_hash", None)
    blob = json.dumps(canon, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


@dataclass
class CMRConfig:
    db_path: str = "ua_ledger.sqlite"
    table: str = "ua_ledger"
    chain_hash: bool = True                          # add prev_hash chaining
    ruflo_sync: bool = True                          # Enlace 3: sync to AgentDB
    ruflo_url: str = "http://localhost:3001"         # Ruflo MCP bridge URL


class CMR:
    """
    Canonical Measurement Recorder (append-only).
    Captures falsifiable evidence for each engine run.
    """

    def __init__(self, cfg: CMRConfig):
        self.cfg = cfg
        self._init_db()

    def _init_db(self) -> None:
        con = sqlite3.connect(self.cfg.db_path)
        try:
            con.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.cfg.table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp_start TEXT NOT NULL,
                timestamp_end TEXT NOT NULL,
                user_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                request_id TEXT NOT NULL,

                engine_version TEXT NOT NULL,
                contract_version TEXT NOT NULL,
                prompt_version TEXT,
                input_fingerprint TEXT,
                git_commit TEXT,
                host_id TEXT,

                seed INTEGER,
                latency_ms REAL NOT NULL,

                contract_valid INTEGER NOT NULL,
                contract_fail_reason TEXT,

                ua_spend INTEGER NOT NULL,
                delta_s REAL,
                delta_s_per_ua REAL,
                h_rigidity REAL,
                work_units INTEGER NOT NULL,

                prev_hash TEXT,
                evidence_hash TEXT NOT NULL
            )
            """)
            con.execute(f"CREATE INDEX IF NOT EXISTS idx_{self.cfg.table}_time ON {self.cfg.table}(timestamp_end)")
            con.execute(f"CREATE INDEX IF NOT EXISTS idx_{self.cfg.table}_fingerprint ON {self.cfg.table}(input_fingerprint)")
            con.commit()
        finally:
            con.close()

    def _last_hash(self) -> Optional[str]:
        if not self.cfg.chain_hash:
            return None
        con = sqlite3.connect(self.cfg.db_path)
        try:
            row = con.execute(
                f"SELECT evidence_hash FROM {self.cfg.table} ORDER BY id DESC LIMIT 1"
            ).fetchone()
            return row[0] if row else None
        finally:
            con.close()

    def record_run(
        self,
        *,
        user_id: str,
        session_id: str,
        request_id: str,
        engine_version: str,
        contract_version: str,
        prompt_version: Optional[str] = None,
        input_fingerprint: Optional[str] = None,
        seed: Optional[int],
        latency_ms: float,
        contract_valid: bool,
        contract_fail_reason: Optional[str],
        ua_spend: int,
        delta_s: Optional[float],
        delta_s_per_ua: Optional[float],
        h_rigidity: Optional[float],
        work_units: int,
        timestamp_start: str,
        timestamp_end: str,
        git_commit: Optional[str] = None,
        host_id: Optional[str] = None,
    ) -> str:
        prev = self._last_hash()

        payload = {
            "timestamp_start": timestamp_start,
            "timestamp_end": timestamp_end,
            "user_id": user_id,
            "session_id": session_id,
            "request_id": request_id,
            "engine_version": engine_version,
            "contract_version": contract_version,
            "prompt_version": prompt_version,
            "input_fingerprint": input_fingerprint,
            "git_commit": git_commit,
            "host_id": host_id,
            "seed": seed,
            "latency_ms": float(latency_ms),
            "contract_valid": bool(contract_valid),
            "contract_fail_reason": contract_fail_reason,
            "ua_spend": int(ua_spend),
            "delta_s": delta_s,
            "delta_s_per_ua": delta_s_per_ua,
            "h_rigidity": h_rigidity,
            "work_units": int(work_units),
            "prev_hash": prev,
            "evidence_hash": "",
        }
        payload["evidence_hash"] = canonical_hash(payload)

        con = sqlite3.connect(self.cfg.db_path)
        try:
            con.execute(
                f"""
                INSERT INTO {self.cfg.table} (
                    timestamp_start, timestamp_end, user_id, session_id, request_id,
                    engine_version, contract_version, prompt_version, input_fingerprint,
                    git_commit, host_id,
                    seed, latency_ms,
                    contract_valid, contract_fail_reason,
                    ua_spend, delta_s, delta_s_per_ua, h_rigidity, work_units,
                    prev_hash, evidence_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["timestamp_start"], payload["timestamp_end"],
                    payload["user_id"], payload["session_id"], payload["request_id"],
                    payload["engine_version"], payload["contract_version"],
                    payload["prompt_version"], payload["input_fingerprint"],
                    payload["git_commit"], payload["host_id"],
                    payload["seed"], payload["latency_ms"],
                    1 if payload["contract_valid"] else 0, payload["contract_fail_reason"],
                    payload["ua_spend"], payload["delta_s"], payload["delta_s_per_ua"],
                    payload["h_rigidity"], payload["work_units"],
                    payload["prev_hash"], payload["evidence_hash"],
                )
            )
            con.commit()
        finally:
            con.close()

        # Enlace 3 (write side): fire-and-forget sync to Ruflo AgentDB
        if self.cfg.ruflo_sync:
            self._async_sync_to_ruflo(
                evidence_hash=payload["evidence_hash"],
                session_id=session_id,
                verdict_strength=payload.get("contract_valid"),
                ua_spend=payload["ua_spend"],
                h_rigidity=payload.get("h_rigidity"),
                summary=(
                    f"session={session_id} ua={ua_spend} "
                    f"valid={contract_valid} latency={latency_ms:.0f}ms"
                ),
            )

        return payload["evidence_hash"]

    # ------------------------------------------------------------------
    # ENLACE 3 — Ruflo AgentDB sync
    # ------------------------------------------------------------------

    def _async_sync_to_ruflo(
        self,
        evidence_hash: str,
        session_id: str,
        verdict_strength: Optional[bool],
        ua_spend: int,
        h_rigidity: Optional[float],
        summary: str,
    ) -> None:
        """
        Fire-and-forget thread: push CMR event into Ruflo AgentDB HNSW store.
        Never raises — CMR integrity is independent of Ruflo availability.
        """
        def _push():
            try:
                from gahenax_app.core.ruflo_bridge import get_bridge, RufloMemoryEntry
                bridge = get_bridge(self.cfg.ruflo_url)
                entry = RufloMemoryEntry(
                    key=evidence_hash,
                    content=summary,
                    agent_id="gahenax_cmr",
                    tags=[
                        "cmr_event",
                        f"valid={'true' if verdict_strength else 'false'}",
                        f"ua={ua_spend}",
                    ],
                    metadata={
                        "evidence_hash": evidence_hash,
                        "session_id": session_id,
                        "ua_spend": ua_spend,
                        "h_rigidity": h_rigidity,
                        "contract_valid": verdict_strength,
                    },
                )
                bridge.store_memory(entry)
            except Exception as exc:
                logger.debug("CMR→Ruflo sync failed (non-critical): %s", exc)

        t = threading.Thread(target=_push, daemon=True)
        t.start()

    def retrieve_ruflo_context(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Enlace 3 (read side): semantic search over past CMR events in AgentDB.
        Returns enriched context for the Governor's next inference cycle.
        Returns empty list if Ruflo unavailable (never raises).
        """
        try:
            from gahenax_app.core.ruflo_bridge import get_bridge
            bridge = get_bridge(self.cfg.ruflo_url)
            result = bridge.retrieve_memory(
                query=query,
                agent_id="gahenax_cmr",
                top_k=top_k,
            )
            if result.ok:
                return result.payload.get("results", [])
        except Exception as exc:
            logger.debug("CMR Ruflo context retrieve failed: %s", exc)
        return []
