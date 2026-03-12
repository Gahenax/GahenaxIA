"""
Unit tests for cmr.py (Canonical Measurement Recorder)
Run with: pytest tests/test_cmr.py -v
"""
from __future__ import annotations

import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest
from gahenax_app.core.cmr import CMR, CMRConfig, canonical_hash, utc_now


# ─────────────────────────── helpers ────────────────────────────────

def make_cmr(tmp_path: str) -> CMR:
    db = os.path.join(tmp_path, "test_ledger.sqlite")
    return CMR(CMRConfig(db_path=db, chain_hash=True))


def record_one(cmr: CMR, **overrides) -> str:
    defaults = dict(
        user_id="test_user",
        session_id="test_session",
        request_id="REQ_001",
        engine_version="test-v1",
        contract_version="contract-v1",
        prompt_version="prompt-v1",
        input_fingerprint="abc123",
        seed=42,
        latency_ms=10.5,
        contract_valid=True,
        contract_fail_reason=None,
        ua_spend=3,
        delta_s=0.5,
        delta_s_per_ua=0.167,
        h_rigidity=1e-15,
        work_units=6,
        timestamp_start=utc_now(),
        timestamp_end=utc_now(),
    )
    defaults.update(overrides)
    return cmr.record_run(**defaults)


# ─────────────────────────── tests ──────────────────────────────────

class TestCanonicalHash:
    def test_deterministic(self):
        p = {"a": 1, "b": "x"}
        assert canonical_hash(p) == canonical_hash(p)

    def test_excludes_evidence_hash(self):
        p1 = {"a": 1, "evidence_hash": "old"}
        p2 = {"a": 1, "evidence_hash": "new"}
        assert canonical_hash(p1) == canonical_hash(p2)

    def test_different_payloads_differ(self):
        assert canonical_hash({"a": 1}) != canonical_hash({"a": 2})


class TestCMRInit:
    def test_creates_table(self, tmp_path):
        import sqlite3
        cmr = make_cmr(str(tmp_path))
        con = sqlite3.connect(cmr.cfg.db_path)
        tables = [r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()]
        con.close()
        assert "ua_ledger" in tables

    def test_creates_indexes(self, tmp_path):
        import sqlite3
        cmr = make_cmr(str(tmp_path))
        con = sqlite3.connect(cmr.cfg.db_path)
        indexes = [r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='index'"
        ).fetchall()]
        con.close()
        assert any("time" in idx for idx in indexes)
        assert any("fingerprint" in idx for idx in indexes)


class TestCMRRecordRun:
    def test_returns_sha256_hex(self, tmp_path):
        cmr = make_cmr(str(tmp_path))
        h = record_one(cmr)
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_row_inserted(self, tmp_path):
        import sqlite3
        cmr = make_cmr(str(tmp_path))
        record_one(cmr)
        con = sqlite3.connect(cmr.cfg.db_path)
        count = con.execute("SELECT COUNT(*) FROM ua_ledger").fetchone()[0]
        con.close()
        assert count == 1

    def test_contract_valid_stored_as_int(self, tmp_path):
        import sqlite3
        cmr = make_cmr(str(tmp_path))
        record_one(cmr, contract_valid=True)
        con = sqlite3.connect(cmr.cfg.db_path)
        val = con.execute("SELECT contract_valid FROM ua_ledger").fetchone()[0]
        con.close()
        assert val == 1

    def test_contract_invalid_stored_as_zero(self, tmp_path):
        import sqlite3
        cmr = make_cmr(str(tmp_path))
        record_one(cmr, contract_valid=False, contract_fail_reason="test reason")
        con = sqlite3.connect(cmr.cfg.db_path)
        val = con.execute("SELECT contract_valid FROM ua_ledger").fetchone()[0]
        con.close()
        assert val == 0


class TestCMRChainHashing:
    def test_first_row_no_prev_hash(self, tmp_path):
        import sqlite3
        cmr = make_cmr(str(tmp_path))
        record_one(cmr)
        con = sqlite3.connect(cmr.cfg.db_path)
        prev = con.execute("SELECT prev_hash FROM ua_ledger ORDER BY id LIMIT 1").fetchone()[0]
        con.close()
        assert prev is None

    def test_second_row_has_prev_hash(self, tmp_path):
        import sqlite3
        cmr = make_cmr(str(tmp_path))
        h1 = record_one(cmr)
        record_one(cmr, request_id="REQ_002")
        con = sqlite3.connect(cmr.cfg.db_path)
        prev = con.execute(
            "SELECT prev_hash FROM ua_ledger ORDER BY id DESC LIMIT 1"
        ).fetchone()[0]
        con.close()
        assert prev == h1

    def test_no_chain_when_disabled(self, tmp_path):
        import sqlite3
        db = os.path.join(str(tmp_path), "nohash.sqlite")
        cmr = CMR(CMRConfig(db_path=db, chain_hash=False))
        record_one(cmr)
        record_one(cmr, request_id="REQ_002")
        con = sqlite3.connect(db)
        prev = con.execute(
            "SELECT prev_hash FROM ua_ledger ORDER BY id DESC LIMIT 1"
        ).fetchone()[0]
        con.close()
        assert prev is None

    def test_multiple_records_form_valid_chain(self, tmp_path):
        import sqlite3
        cmr = make_cmr(str(tmp_path))
        hashes = []
        for i in range(5):
            h = record_one(cmr, request_id=f"REQ_{i:03d}")
            hashes.append(h)

        con = sqlite3.connect(cmr.cfg.db_path)
        rows = con.execute(
            "SELECT evidence_hash, prev_hash FROM ua_ledger ORDER BY id"
        ).fetchall()
        con.close()

        assert rows[0][1] is None  # genesis
        for i in range(1, len(rows)):
            assert rows[i][1] == rows[i - 1][0], f"Chain broken at row {i}"
