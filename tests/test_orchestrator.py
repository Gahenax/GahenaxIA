"""
Unit tests for orchestrator/orchestrator.py and orchestrator/contracts.py
Run with: pytest tests/test_orchestrator.py -v
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from orchestrator.contracts import (
    Job, ResultPayload, LedgerEvent,
    sha256_json, to_jsonl_line, now_iso,
)
from orchestrator.orchestrator import SingleWriterOrchestrator


# ─────────────────────────── helpers ────────────────────────────────

def make_orch(tmp_path: str) -> SingleWriterOrchestrator:
    return SingleWriterOrchestrator(
        run_dir=os.path.join(tmp_path, "run"),
        run_id="test_run_001",
        eps_root=1e-6,
        max_attempts=2,
        checkpoint_every=3,
    )


def valid_payload() -> dict:
    return {"t": 1.5, "root_val": 0.0, "meta": {"method": "bisect"}}


def _make_job(job_id: str = "J001") -> Job:
    return Job(job_id=job_id, t_start=0.0, t_end=1.0, stride=0.1)


# ─────────────────────────── contracts ──────────────────────────────

class TestSha256Json:
    def test_deterministic(self):
        d = {"a": 1, "b": 2}
        assert sha256_json(d) == sha256_json(d)

    def test_key_order_irrelevant(self):
        assert sha256_json({"a": 1, "b": 2}) == sha256_json({"b": 2, "a": 1})

    def test_different_dicts_differ(self):
        assert sha256_json({"a": 1}) != sha256_json({"a": 2})

    def test_prefix(self):
        assert sha256_json({"x": 1}).startswith("sha256:")


class TestResultPayloadValidate:
    def test_valid_payload(self):
        assert ResultPayload.validate(valid_payload()) is True

    def test_missing_t(self):
        assert ResultPayload.validate({"root_val": 0.0, "meta": {}}) is False

    def test_missing_root_val(self):
        assert ResultPayload.validate({"t": 1.0, "meta": {}}) is False

    def test_missing_meta(self):
        assert ResultPayload.validate({"t": 1.0, "root_val": 0.0}) is False

    def test_non_numeric_t(self):
        assert ResultPayload.validate({"t": "bad", "root_val": 0.0, "meta": {}}) is False

    def test_non_dict_meta(self):
        assert ResultPayload.validate({"t": 1.0, "root_val": 0.0, "meta": "bad"}) is False

    def test_non_dict_input(self):
        assert ResultPayload.validate("not a dict") is False


class TestLedgerEvent:
    def test_from_parts_computes_hash(self):
        evt = LedgerEvent.from_parts("run1", 1, "J001", 1, valid_payload())
        assert evt.hash.startswith("sha256:")
        assert len(evt.hash) > 10

    def test_serializable(self):
        evt = LedgerEvent.from_parts("run1", 1, "J001", 1, valid_payload())
        line = to_jsonl_line(evt)
        obj = json.loads(line)
        assert obj["run_id"] == "run1"
        assert obj["seq"] == 1


# ─────────────────────────── orchestrator ───────────────────────────

class TestLocking:
    def test_acquire_and_release(self, tmp_path):
        orch = make_orch(str(tmp_path))
        orch.acquire_lock()
        assert os.path.exists(orch.lock_path)
        orch.release_lock()
        assert not os.path.exists(orch.lock_path)

    def test_double_acquire_raises(self, tmp_path):
        orch = make_orch(str(tmp_path))
        orch.acquire_lock()
        with pytest.raises(RuntimeError, match="Lock exists"):
            orch.acquire_lock()
        orch.release_lock()

    def test_release_idempotent(self, tmp_path):
        orch = make_orch(str(tmp_path))
        orch.release_lock()  # should not raise even if no lock


class TestJobManagement:
    def test_register_jobs(self, tmp_path):
        orch = make_orch(str(tmp_path))
        orch.register_jobs([_make_job("J001"), _make_job("J002")])
        assert "J001" in orch.state["jobs"]
        assert "J002" in orch.state["jobs"]

    def test_register_idempotent(self, tmp_path):
        orch = make_orch(str(tmp_path))
        orch.register_jobs([_make_job("J001")])
        orch.register_jobs([_make_job("J001")])  # second time is no-op
        assert len([j for j in orch.state["jobs"] if j == "J001"]) == 1

    def test_get_next_job_fifo(self, tmp_path):
        orch = make_orch(str(tmp_path))
        orch.register_jobs([_make_job("J001"), _make_job("J002")])
        j = orch.get_next_job()
        assert j.job_id == "J001"
        assert orch.state["jobs"]["J001"]["status"] == "RUNNING"

    def test_get_next_job_none_when_empty(self, tmp_path):
        orch = make_orch(str(tmp_path))
        assert orch.get_next_job() is None

    def test_mark_job_done(self, tmp_path):
        orch = make_orch(str(tmp_path))
        orch.register_jobs([_make_job("J001")])
        orch.get_next_job()
        orch.mark_job_done("J001")
        assert orch.state["jobs"]["J001"]["status"] == "DONE"
        assert orch.state["done"] == 1

    def test_mark_job_failed_retry(self, tmp_path):
        orch = make_orch(str(tmp_path))
        orch.register_jobs([_make_job("J001")])
        orch.get_next_job()
        orch.mark_job_failed("J001", "some error")
        assert orch.state["jobs"]["J001"]["status"] == "PENDING"  # retried

    def test_mark_job_failed_max_attempts(self, tmp_path):
        orch = make_orch(str(tmp_path))
        orch.register_jobs([_make_job("J001")])
        for _ in range(2):
            orch.get_next_job()
            orch.mark_job_failed("J001", "error")
        assert orch.state["jobs"]["J001"]["status"] == "FAILED"
        assert orch.state["failed"] == 1


class TestAcceptResult:
    def test_accept_valid_result(self, tmp_path):
        orch = make_orch(str(tmp_path))
        orch.register_jobs([_make_job("J001")])
        verdict = orch.accept_result(1, "J001", valid_payload())
        assert verdict == "ACCEPTED"
        assert orch.state["seq"] == 1

    def test_reject_schema_invalid(self, tmp_path):
        orch = make_orch(str(tmp_path))
        orch.register_jobs([_make_job("J001")])
        verdict = orch.accept_result(1, "J001", {"bad": "schema"})
        assert verdict == "REJECTED_SCHEMA"

    def test_reject_tolerance(self, tmp_path):
        orch = make_orch(str(tmp_path))
        orch.register_jobs([_make_job("J001")])
        p = {"t": 1.0, "root_val": 999.0, "meta": {}}
        verdict = orch.accept_result(1, "J001", p)
        assert verdict == "REJECTED_TOL"

    def test_reject_duplicate(self, tmp_path):
        orch = make_orch(str(tmp_path))
        orch.register_jobs([_make_job("J001")])
        orch.accept_result(1, "J001", valid_payload())
        verdict = orch.accept_result(1, "J001", valid_payload())
        assert verdict == "REJECTED_DUP"

    def test_ledger_written(self, tmp_path):
        orch = make_orch(str(tmp_path))
        orch.register_jobs([_make_job("J001")])
        orch.accept_result(1, "J001", valid_payload())
        assert os.path.exists(orch.ledger_path)
        with open(orch.ledger_path) as f:
            lines = [l for l in f if l.strip()]
        assert len(lines) == 1


class TestLedgerReplay:
    def test_resume_reconstructs_dedup(self, tmp_path):
        orch1 = make_orch(str(tmp_path))
        orch1.register_jobs([_make_job("J001")])
        orch1.accept_result(1, "J001", valid_payload())

        # New orchestrator replays the ledger
        orch2 = make_orch(str(tmp_path))
        orch2.replay_ledger_for_dedup()
        verdict = orch2.accept_result(1, "J001", valid_payload())
        assert verdict == "REJECTED_DUP"

    def test_seq_restored_from_ledger(self, tmp_path):
        orch1 = make_orch(str(tmp_path))
        orch1.register_jobs([_make_job("J001"), _make_job("J002")])
        orch1.accept_result(1, "J001", valid_payload())
        p2 = {"t": 2.0, "root_val": 0.0, "meta": {}}
        orch1.accept_result(2, "J002", p2)

        orch2 = make_orch(str(tmp_path))
        orch2.replay_ledger_for_dedup()
        assert orch2.seq == 2


class TestStatePersistence:
    def test_save_and_load(self, tmp_path):
        orch = make_orch(str(tmp_path))
        orch.state["done"] = 5
        orch.save_state()

        orch2 = make_orch(str(tmp_path))
        orch2.load_state()
        assert orch2.state["done"] == 5
