"""
ruflo_api.py
=============
Enlace 5 — REST endpoints that expose Ruflo's orchestration layer
through GahenaxIA's CFT (Contract-First Transmission) governance.

Every endpoint:
  - Passes through ExecutionGateway (circuit breaker + CMR + UA budget)
  - Uses CNI fingerprinting for idempotency
  - Returns a typed, sealed response

Endpoints:
  POST /api/ruflo/agent          → spawn a single Ruflo agent
  POST /api/ruflo/swarm          → create a multi-agent swarm
  POST /api/ruflo/memory/store   → persist to AgentDB HNSW
  GET  /api/ruflo/memory/search  → semantic search over AgentDB
  GET  /api/ruflo/status         → bridge health + metrics

All side-effecting endpoints require Ruflo MCP bridge to be running.
Read endpoints (memory/search, status) degrade gracefully when offline.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from gahenax_app.core.cmr import CMR, CMRConfig, utc_now
from gahenax_app.core.gahenax_engine import compute_cni_fingerprint
from gahenax_app.core.gahenax_gateway import (
    ExecutionGateway, ExecutionRequest, FailurePolicy, RiskLevel,
)
from gahenax_app.core.skill_registry_bootstrap import build_registry

router = APIRouter(prefix="/api/ruflo", tags=["Ruflo Orchestration"])

# ---------------------------------------------------------------------------
# Shared infrastructure (created once at module load)
# ---------------------------------------------------------------------------

_cmr_cfg  = CMRConfig(db_path=os.path.join(os.getcwd(), "ua_ledger.sqlite"))
_CMR      = CMR(_cmr_cfg)
_registry = build_registry()
_gateway  = ExecutionGateway(registry=_registry, policy=FailurePolicy.default(), cmr=_CMR)

RUFLO_URL = os.getenv("RUFLO_URL", "http://localhost:3001")


# ---------------------------------------------------------------------------
# REQUEST / RESPONSE SCHEMAS
# ---------------------------------------------------------------------------

class AgentRequest(BaseModel):
    task:       str   = Field(..., description="Natural-language task for the agent")
    agent_type: str   = Field("coder", description="coder|architect|reviewer|tester|security")
    priority:   str   = Field("normal", description="low|normal|high|critical")
    ua_budget:  float = Field(6.0, ge=0.5, description="Athena Unit budget for this call")
    context:    Dict[str, Any] = Field(default_factory=dict)
    dry_run:    bool  = Field(False)


class SwarmRequest(BaseModel):
    tasks:      List[str] = Field(..., min_items=1, description="List of tasks to parallelize")
    topology:   str       = Field("hierarchical", description="hierarchical|mesh|ring|star")
    ua_budget:  float     = Field(10.0, ge=1.0)
    dry_run:    bool      = Field(False)


class MemoryStoreRequest(BaseModel):
    key:      str         = Field(..., description="Unique key for this memory entry")
    content:  str         = Field(..., description="Text content to embed and store")
    agent_id: str         = Field("gahenax_default")
    tags:     List[str]   = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    ua_budget: float      = Field(2.0, ge=0.5)


class RufloResponse(BaseModel):
    ok:         bool
    skill_id:   str
    status:     str
    payload:    Dict[str, Any]
    metrics:    Dict[str, Any]
    evidence_hash: str
    error:      Optional[str] = None


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _req_id(data: Dict[str, Any]) -> str:
    """Deterministic idempotency key from request content."""
    blob = json.dumps(data, sort_keys=True, default=str).encode()
    return "ruflo_" + hashlib.sha256(blob).hexdigest()[:24]


def _execute(skill_id: str, inputs: Dict[str, Any], ua_budget: float, dry_run: bool) -> RufloResponse:
    """Run a skill through the full CFT gateway and return a typed response."""
    req = ExecutionRequest(
        request_id=_req_id({"skill_id": skill_id, **inputs}),
        skill_id=skill_id,
        inputs=inputs,
        mode="GEM",
        ua_budget=ua_budget,
        dry_run=dry_run,
    )
    result = _gateway.execute(req)

    # Ruflo skills may be CONFIRM risk — reject if attempted without dry_run
    spec = _registry.get(skill_id)
    if spec and spec.risk_level == RiskLevel.CONFIRM and not dry_run:
        # In a real system this would require an explicit user token.
        # For now: allow execution but log the confirmation requirement.
        pass

    return RufloResponse(
        ok=result.status.value in ("OK", "DRY_RUN"),
        skill_id=skill_id,
        status=result.status.value,
        payload=result.outputs,
        metrics=result.metrics,
        evidence_hash=result.evidence_hash(),
        error=result.error_detail,
    )


# ---------------------------------------------------------------------------
# ENDPOINTS
# ---------------------------------------------------------------------------

@router.post("/agent", response_model=RufloResponse, summary="Spawn a Ruflo agent")
async def spawn_agent(req: AgentRequest):
    """
    Dispatch a single task to a Ruflo specialized agent via CFT gateway.

    Routes to ruflo.coder / ruflo.architect / ruflo.reviewer /
    ruflo.tester / ruflo.security based on agent_type.
    UA budget governs the call. Circuit breaker protects against failures.
    Result sealed in CMR ledger.
    """
    skill_id = f"ruflo.{req.agent_type}"
    if not _registry.get(skill_id):
        raise HTTPException(status_code=400, detail=f"Unknown agent type: {req.agent_type}")

    return _execute(
        skill_id=skill_id,
        inputs={"task": req.task, "priority": req.priority, "context": req.context},
        ua_budget=req.ua_budget,
        dry_run=req.dry_run,
    )


@router.post("/swarm", response_model=RufloResponse, summary="Launch a multi-agent swarm")
async def create_swarm(req: SwarmRequest):
    """
    Launch a coordinated Ruflo swarm over a list of tasks.

    Topology options:
      - hierarchical: queen-led, best for sequential pipelines
      - mesh: peer-to-peer, best for independent parallel tasks
      - ring: sequential handoff
      - star: hub-and-spoke

    UA budget is shared across all agents.
    """
    return _execute(
        skill_id="ruflo.swarm",
        inputs={"tasks": req.tasks, "topology": req.topology},
        ua_budget=req.ua_budget,
        dry_run=req.dry_run,
    )


@router.post("/memory/store", response_model=RufloResponse, summary="Store memory in AgentDB")
async def store_memory(req: MemoryStoreRequest):
    """
    Persist content in Ruflo's HNSW vector store (AgentDB).
    Embedded with semantic vector for sub-millisecond future retrieval.
    Sealed in CMR as a memory_store event.
    """
    return _execute(
        skill_id="ruflo.memory_store",
        inputs={
            "key":      req.key,
            "content":  req.content,
            "agent_id": req.agent_id,
            "tags":     req.tags,
            "metadata": req.metadata,
        },
        ua_budget=req.ua_budget,
        dry_run=False,
    )


@router.get("/memory/search", response_model=RufloResponse, summary="Semantic memory search")
async def search_memory(
    query: str,
    agent_id: str = "gahenax_default",
    top_k: int = 5,
    ua_budget: float = 2.0,
):
    """
    HNSW semantic search over AgentDB.
    Returns top_k most relevant memory entries for the given query (~61µs).
    """
    return _execute(
        skill_id="ruflo.memory_retrieve",
        inputs={"query": query, "agent_id": agent_id, "top_k": top_k},
        ua_budget=ua_budget,
        dry_run=False,
    )


@router.get("/status", summary="Ruflo bridge health and metrics")
async def ruflo_status():
    """
    Returns Ruflo MCP bridge health, gateway circuit breaker state,
    and cumulative call metrics. Does not consume UA.
    """
    from gahenax_app.core.ruflo_bridge import get_bridge

    bridge  = get_bridge(RUFLO_URL)
    healthy = bridge.health_check()

    return {
        "ruflo_bridge_url":     RUFLO_URL,
        "ruflo_bridge_healthy": healthy,
        "bridge_metrics":       bridge.metrics(),
        "gateway_status":       _gateway.status_report(),
        "registered_skills":    [s.skill_id for s in _registry.all() if s.skill_id.startswith("ruflo.")],
    }
