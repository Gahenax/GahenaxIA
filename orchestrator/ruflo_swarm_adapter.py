"""
ruflo_swarm_adapter.py
=======================
Bridges GahenaxIA's Single-Orchestrator / Multi-Worker system with
Ruflo's swarm coordination layer.

Flow:
    GahenaxIA Job (contracts.py)
        ↓ route()
    RufloSwarmAdapter
        ↓ classify_job()  → picks agent type + topology
        ↓ dispatch()       → RufloBridge.spawn_agent() or create_swarm()
        ↓ result_to_ledger_payload()
    LedgerEvent (orchestrator.py)

Design rules:
    - Adapter is stateless; all state lives in the CMR ledger.
    - Every dispatch is idempotent via job.canonical_hash().
    - If Ruflo bridge is unreachable the adapter falls back to LOCAL mode
      (existing worker_entry.py path) without crashing the orchestrator.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from contracts import Job

try:
    from gahenax_app.core.ruflo_bridge import (
        RufloBridge,
        RufloAgentJob,
        RufloAgentType,
        RufloResult,
        SwarmTopology,
        get_bridge,
    )
    _RUFLO_AVAILABLE = True
except ImportError:
    _RUFLO_AVAILABLE = False

logger = logging.getLogger(__name__)


# ============================================================================
# JOB CLASSIFICATION
# ============================================================================

# Maps intent keywords in job metadata to Ruflo agent types.
_KEYWORD_MAP: List[Tuple[List[str], RufloAgentType]] = []

if _RUFLO_AVAILABLE:
    _KEYWORD_MAP = [
        (["code", "implement", "refactor", "debug", "function", "class", "module"],
         RufloAgentType.CODER),
        (["design", "architect", "api", "schema", "system", "structure"],
         RufloAgentType.ARCHITECT),
        (["review", "lint", "quality", "style", "convention", "best-practice"],
         RufloAgentType.REVIEWER),
        (["test", "coverage", "assert", "unit", "integration", "spec"],
         RufloAgentType.TESTER),
        (["security", "vuln", "cve", "pentest", "threat", "injection", "audit"],
         RufloAgentType.SECURITY),
    ]


def classify_job(job: Job) -> Optional["RufloAgentType"]:
    """
    Infer the best Ruflo agent type from a GahenaxIA Job.
    Returns None if no match (fall back to local worker).
    """
    if not _RUFLO_AVAILABLE:
        return None

    # Use intent tag from job metadata if present
    meta = job.__dict__ if hasattr(job, "__dict__") else {}
    intent: str = str(meta.get("intent", "") + " " + meta.get("description", "")).lower()

    for keywords, agent_type in _KEYWORD_MAP:
        if any(kw in intent for kw in keywords):
            return agent_type

    return None


def pick_topology(agent_count: int) -> "SwarmTopology":
    """Select swarm topology based on concurrency requirements."""
    if not _RUFLO_AVAILABLE:
        return None  # type: ignore
    if agent_count == 1:
        return SwarmTopology.STAR
    if agent_count <= 3:
        return SwarmTopology.HIERARCHICAL
    return SwarmTopology.MESH


# ============================================================================
# ADAPTER
# ============================================================================

@dataclass
class DispatchResult:
    """Result of a ruflo swarm dispatch."""
    routed_to: str         # "ruflo" | "local"
    job_id: str
    agent_type: Optional[str]
    ruflo_result: Optional[Any]    # RufloResult if routed to ruflo
    ledger_payload: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class RufloSwarmAdapter:
    """
    Translates GahenaxIA Jobs into Ruflo agent tasks and returns results
    as LedgerEvent-compatible payloads.

    The adapter is safe to instantiate even when ruflo is not running;
    it degrades gracefully to local mode in that case.
    """

    def __init__(
        self,
        ruflo_url: str = "http://localhost:3001",
        enable_fallback: bool = True,
    ):
        self.ruflo_url       = ruflo_url
        self.enable_fallback = enable_fallback
        self._bridge: Optional["RufloBridge"] = None

        if _RUFLO_AVAILABLE:
            self._bridge = get_bridge(ruflo_url)
            alive = self._bridge.health_check()
            if alive:
                logger.info("RufloSwarmAdapter: bridge healthy @ %s", ruflo_url)
            else:
                logger.warning(
                    "RufloSwarmAdapter: bridge unreachable @ %s — fallback=%s",
                    ruflo_url, enable_fallback,
                )
        else:
            logger.warning("RufloSwarmAdapter: ruflo_bridge module not found — fallback mode only")

    # ------------------------------------------------------------------
    # SINGLE JOB DISPATCH
    # ------------------------------------------------------------------

    def route(self, job: Job, task_description: str = "") -> DispatchResult:
        """
        Route a single GahenaxIA Job.

        If Ruflo is available and the job can be classified, dispatches to
        the appropriate agent. Otherwise returns a LOCAL routing signal.
        """
        if self._bridge is None or not self._bridge.health_check():
            return DispatchResult(
                routed_to="local",
                job_id=job.job_id,
                agent_type=None,
                ruflo_result=None,
                ledger_payload={"mode": "local", "job_id": job.job_id},
            )

        agent_type = classify_job(job)
        if agent_type is None:
            return DispatchResult(
                routed_to="local",
                job_id=job.job_id,
                agent_type=None,
                ruflo_result=None,
                ledger_payload={"mode": "local", "reason": "no_agent_match"},
            )

        ruflo_job = RufloAgentJob(
            agent_type=agent_type,
            task=task_description or f"Process job {job.job_id}",
            priority="normal",
            topology=SwarmTopology.STAR,
            context={"gahenax_job_id": job.job_id},
        )

        result: RufloResult = self._bridge.spawn_agent(ruflo_job)

        return DispatchResult(
            routed_to="ruflo",
            job_id=job.job_id,
            agent_type=agent_type.value,
            ruflo_result=result,
            ledger_payload=self._to_payload(result, agent_type.value),
            error=result.error,
        )

    # ------------------------------------------------------------------
    # MULTI-JOB SWARM DISPATCH
    # ------------------------------------------------------------------

    def route_swarm(
        self,
        jobs: List[Job],
        task_descriptions: Optional[List[str]] = None,
        topology: Optional["SwarmTopology"] = None,
    ) -> List[DispatchResult]:
        """Route multiple jobs as a coordinated swarm."""
        if self._bridge is None or not self._bridge.health_check():
            return [
                DispatchResult(
                    routed_to="local",
                    job_id=j.job_id,
                    agent_type=None,
                    ruflo_result=None,
                    ledger_payload={"mode": "local"},
                )
                for j in jobs
            ]

        descriptions = task_descriptions or [""] * len(jobs)
        ruflo_jobs = []
        for job, desc in zip(jobs, descriptions):
            agent_type = classify_job(job) or RufloAgentType.CODER
            ruflo_jobs.append(RufloAgentJob(
                agent_type=agent_type,
                task=desc or f"Process {job.job_id}",
                priority="normal",
                context={"gahenax_job_id": job.job_id},
            ))

        topo  = topology or pick_topology(len(ruflo_jobs))
        swarm = self._bridge.create_swarm(ruflo_jobs, topology=topo)

        return [
            DispatchResult(
                routed_to="ruflo",
                job_id=j.job_id,
                agent_type=rj.agent_type.value,
                ruflo_result=swarm,
                ledger_payload=self._to_payload(swarm, rj.agent_type.value),
                error=swarm.error,
            )
            for j, rj in zip(jobs, ruflo_jobs)
        ]

    # ------------------------------------------------------------------
    # PRIVATE
    # ------------------------------------------------------------------

    @staticmethod
    def _to_payload(result: "RufloResult", agent_type: str) -> Dict[str, Any]:
        return {
            "source":       "ruflo",
            "ok":           result.ok,
            "agent_type":   agent_type,
            "tool_name":    result.tool_name,
            "latency_ms":   result.latency_ms,
            "request_id":   result.request_id,
            "payload":      result.payload,
            "error":        result.error,
        }


# ============================================================================
# CLI SMOKE TEST
# ============================================================================

if __name__ == "__main__":
    import sys
    from contracts import Job

    logging.basicConfig(level=logging.INFO)

    url     = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3001"
    adapter = RufloSwarmAdapter(ruflo_url=url)

    fake_job = Job(
        job_id="test-001",
        t_start=0.0,
        t_end=1.0,
        stride=0.1,
    )

    res = adapter.route(fake_job, task_description="refactor the LLL reducer")
    print(f"Routed to : {res.routed_to}")
    print(f"Agent type: {res.agent_type}")
    print(f"Payload   : {res.ledger_payload}")
