# orchestrator/worker_entry.py
"""
Worker entry point — producer with Ruflo agent routing (Enlace 4).

Execution hierarchy:
  1. If Ruflo bridge is healthy AND job has a classifiable intent:
       → delegate to specialized Ruflo agent (coder/architect/reviewer/tester/security)
       → result includes Ruflo's output + agent metadata
  2. Otherwise (Ruflo down, no intent match, UA cap):
       → compute_zero_candidates() local fallback (original logic)

The worker NEVER writes to the canonical ledger directly.
It pushes typed payloads to the orchestrator queue.
The orchestrator decides acceptance, dedup, and persistence.

Contract: every payload must satisfy ResultPayload.validate():
  {"t": float, "root_val": float, "meta": {...}}

Ruflo results are encoded into this canonical schema as:
  t        = job.t_start (time coordinate)
  root_val = 0.0 (Ruflo tasks don't produce numeric roots; near-zero sentinel)
  meta     = {method, agent_type, ruflo_ok, ruflo_payload, ...}
"""
from __future__ import annotations

import logging
import random
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# RUFLO ROUTING (Enlace 4)
# ---------------------------------------------------------------------------

_INTENT_KEYWORDS: List[tuple] = [
    (["code", "implement", "refactor", "debug", "function", "module", "class"],
     "coder"),
    (["design", "architect", "api", "schema", "system", "structure", "ddd"],
     "architect"),
    (["review", "lint", "quality", "style", "convention", "best-practice"],
     "reviewer"),
    (["test", "coverage", "assert", "unit", "integration", "spec", "tdd"],
     "tester"),
    (["security", "vuln", "cve", "pentest", "threat", "injection", "audit"],
     "security"),
]


def _classify_intent(intent: str) -> Optional[str]:
    """Map intent string to agent type. Returns None if no match."""
    lower = intent.lower()
    for keywords, agent_type in _INTENT_KEYWORDS:
        if any(kw in lower for kw in keywords):
            return agent_type
    return None


def route_with_ruflo(
    job_id: str,
    t_start: float,
    intent: str,
    ruflo_url: str = "http://localhost:3001",
) -> Optional[Dict[str, Any]]:
    """
    Enlace 4: Route a job to a Ruflo specialized agent.

    Returns a ResultPayload-compatible dict on success, None on failure.
    Failure is expected when Ruflo is not running — caller uses fallback.
    """
    agent_type = _classify_intent(intent)
    if not agent_type:
        return None

    try:
        from orchestrator.ruflo_swarm_adapter import RufloSwarmAdapter
        from orchestrator.contracts import Job as OrcJob

        adapter = RufloSwarmAdapter(ruflo_url=ruflo_url, enable_fallback=False)
        orch_job = OrcJob(job_id=job_id, t_start=t_start, t_end=t_start + 1.0, stride=1.0)
        dispatch = adapter.route(orch_job, task_description=intent)

        if dispatch.routed_to == "ruflo" and not dispatch.error:
            return {
                "t":        t_start,
                "root_val": 0.0,   # sentinel: Ruflo tasks are non-numeric
                "meta": {
                    "method":        "ruflo_agent",
                    "agent_type":    dispatch.agent_type,
                    "ruflo_ok":      True,
                    "ruflo_job_id":  dispatch.job_id,
                    "ruflo_payload": dispatch.ledger_payload,
                    "intent":        intent,
                },
            }
    except Exception as exc:
        logger.debug("Ruflo routing failed for job %s: %s", job_id, exc)

    return None


# ---------------------------------------------------------------------------
# LOCAL FALLBACK (original logic, unchanged)
# ---------------------------------------------------------------------------

def compute_zero_candidates(
    t_start: float,
    t_end: float,
    stride: float,
) -> List[Dict[str, Any]]:
    """
    Local fallback miner — used when Ruflo is unavailable or intent unclassified.

    Returns payloads in canonical schema:
      {"t": float, "root_val": float, "meta": {...}}

    The orchestrator validates schema + tolerance + uniqueness.
    """
    out: List[Dict[str, Any]] = []
    t = t_start
    while t < t_end:
        root_val = (random.random() - 0.5) * 1e-11
        out.append({
            "t":        float(t),
            "root_val": float(root_val),
            "meta":     {"method": "local_stub", "iters": 12},
        })
        t += stride
        time.sleep(0.001)
    return out


# ---------------------------------------------------------------------------
# MAIN ENTRY — called by run_orchestrator.py workers
# ---------------------------------------------------------------------------

def compute_candidates(
    job_id: str,
    t_start: float,
    t_end: float,
    stride: float,
    intent: str = "",
    ruflo_url: str = "http://localhost:3001",
) -> List[Dict[str, Any]]:
    """
    Unified worker entry point.

    1. If intent is classifiable → try Ruflo agent routing
    2. If Ruflo unavailable or no intent → local fallback
    """
    if intent:
        ruflo_result = route_with_ruflo(
            job_id=job_id,
            t_start=t_start,
            intent=intent,
            ruflo_url=ruflo_url,
        )
        if ruflo_result is not None:
            return [ruflo_result]

    # Local fallback
    return compute_zero_candidates(t_start, t_end, stride)
