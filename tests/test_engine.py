"""
Unit tests for gahenax_engine.py
Run with: pytest tests/test_engine.py -v
"""
from __future__ import annotations

import sys
import os

# Allow running from repo root without installing the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest
from gahenax_app.core.gahenax_engine import (
    compute_cni_fingerprint,
    UAMetrics,
    GahenaxOptimizer,
    GahenaxGovernor,
    GahenaxOutput,
    Assumption, AssumptionStatus,
    Finding, FindingStatus,
    Reframe, Exclusions,
    ValidationQuestion, ValidationAnswerType,
    NextStep, FinalVerdict,
    VerdictStrength, RenderProfile, EngineMode,
    H_RIGIDITY_PERFECT,
    UA_BUDGET_EVERYDAY,
)


# ──────────────────────────── CNI fingerprint ────────────────────────────

class TestComputeCniFingerprint:
    def test_deterministic(self):
        payload = {"a": 1, "b": "hello"}
        assert compute_cni_fingerprint(payload) == compute_cni_fingerprint(payload)

    def test_key_order_irrelevant(self):
        p1 = {"a": 1, "b": 2}
        p2 = {"b": 2, "a": 1}
        assert compute_cni_fingerprint(p1) == compute_cni_fingerprint(p2)

    def test_different_payloads_differ(self):
        assert compute_cni_fingerprint({"a": 1}) != compute_cni_fingerprint({"a": 2})

    def test_strips_whitespace(self):
        p1 = {"text": "hello world"}
        p2 = {"text": "  hello world  "}
        assert compute_cni_fingerprint(p1) == compute_cni_fingerprint(p2)

    def test_returns_sha256_hex(self):
        fp = compute_cni_fingerprint({"x": 1})
        assert len(fp) == 64
        assert all(c in "0123456789abcdef" for c in fp)


# ──────────────────────────── UAMetrics ─────────────────────────────────

class TestUAMetrics:
    def test_consume_within_budget(self):
        ua = UAMetrics(budget=10.0)
        ua.consume(5.0)
        assert ua.spent == 5.0

    def test_consume_exceeds_budget_raises(self):
        ua = UAMetrics(budget=3.0)
        with pytest.raises(ResourceWarning):
            ua.consume(4.0)

    def test_cumulative_consume(self):
        ua = UAMetrics(budget=10.0)
        ua.consume(3.0)
        ua.consume(3.0)
        assert ua.spent == 6.0

    def test_consume_exactly_at_budget_raises(self):
        ua = UAMetrics(budget=5.0)
        ua.consume(3.0)
        with pytest.raises(ResourceWarning):
            ua.consume(2.1)  # 3 + 2.1 > 5


# ──────────────────────────── Optimizer ─────────────────────────────────

class TestGahenaxOptimizer:
    def _make_assumption(self, aid: str, statement: str) -> Assumption:
        return Assumption(
            assumption_id=aid,
            statement=statement,
            unlocks_conclusion="conclusion",
            status=AssumptionStatus.OPEN,
        )

    def test_deduplicates_assumptions(self):
        a1 = self._make_assumption("A1", "same statement")
        a2 = self._make_assumption("A2", "same statement")
        reduced, _, delta = GahenaxOptimizer.reduce_lattice([a1, a2], [])
        assert len(reduced) == 1
        assert delta > 0

    def test_unique_assumptions_unchanged(self):
        a1 = self._make_assumption("A1", "statement one")
        a2 = self._make_assumption("A2", "statement two")
        reduced, _, delta = GahenaxOptimizer.reduce_lattice([a1, a2], [])
        assert len(reduced) == 2
        assert delta == 0

    def test_empty_assumptions(self):
        reduced, findings, delta = GahenaxOptimizer.reduce_lattice([], [])
        assert reduced == []
        assert delta == 0


# ──────────────────────────── Governor ──────────────────────────────────

class TestGahenaxGovernor:
    def test_default_budget_everyday(self):
        gov = GahenaxGovernor()
        assert gov.ua.budget == UA_BUDGET_EVERYDAY
        assert gov.mode == EngineMode.EVERYDAY

    def test_custom_budget(self):
        gov = GahenaxGovernor(budget_ua=100.0)
        assert gov.ua.budget == 100.0

    def test_session_id_is_uuid(self):
        import uuid
        gov = GahenaxGovernor()
        uuid.UUID(gov.session_id)  # raises ValueError if invalid

    def test_mock_run_no_api_key(self, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        gov = GahenaxGovernor()
        out = gov.run_inference_cycle("test question")
        assert isinstance(out, GahenaxOutput)
        assert "[MOCK]" in out.reframe.statement

    def test_mock_run_audit_mode(self, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        gov = GahenaxGovernor(mode=EngineMode.AUDIT, budget_ua=200.0)
        out = gov.run_inference_cycle("test question")
        assert isinstance(out, GahenaxOutput)


# ──────────────────────────── GahenaxOutput ─────────────────────────────

def _make_output() -> GahenaxOutput:
    return GahenaxOutput(
        reframe=Reframe(statement="Reframe test"),
        exclusions=Exclusions(items=["exclusion 1"]),
        findings=[Finding("finding 1", FindingStatus.PROVISIONAL)],
        assumptions=[
            Assumption("A1", "assumption text", "unlocks conclusion", AssumptionStatus.OPEN)
        ],
        interrogatory=[
            ValidationQuestion("Q1", "A1", "Is this valid?", ValidationAnswerType.BINARY)
        ],
        next_steps=[NextStep("Do X", "Evidence Y")],
        verdict=FinalVerdict(
            strength=VerdictStrength.CONDITIONAL,
            statement="Verdict text",
            ua_audit={"spent": 3.0, "efficiency": 0.5},
        ),
    )


class TestGahenaxOutputToDict:
    def test_returns_dict(self):
        out = _make_output()
        d = out.to_dict()
        assert isinstance(d, dict)

    def test_top_level_keys(self):
        d = _make_output().to_dict()
        assert set(d.keys()) == {
            "reframe", "exclusions", "findings",
            "assumptions", "interrogatory", "next_steps", "verdict"
        }

    def test_enum_values_are_strings(self):
        d = _make_output().to_dict()
        assert d["verdict"]["strength"] == "conditional"
        assert d["findings"][0]["status"] == "provisional"
        assert d["assumptions"][0]["status"] == "open"
        assert d["interrogatory"][0]["answer_type"] == "binary"

    def test_nested_structures(self):
        d = _make_output().to_dict()
        assert d["reframe"]["statement"] == "Reframe test"
        assert d["exclusions"]["items"] == ["exclusion 1"]
        assert isinstance(d["findings"], list)


class TestGahenaxOutputToMarkdown:
    def test_daily_profile_has_header(self):
        md = _make_output().to_markdown(RenderProfile.DAILY)
        assert "Gahenax Core" in md

    def test_dense_profile_no_header(self):
        md = _make_output().to_markdown(RenderProfile.DENSE)
        assert "Gahenax Core" not in md

    def test_contains_sections(self):
        md = _make_output().to_markdown(RenderProfile.DAILY)
        assert "Reencuadre" in md
        assert "Exclusiones" in md
        assert "Hallazgos" in md
        assert "Veredicto" in md


# ──────────────────────────── Constants ─────────────────────────────────

def test_h_rigidity_perfect_value():
    assert H_RIGIDITY_PERFECT == 1e-15
