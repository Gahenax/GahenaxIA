"""
ruflo_bridge.py
================
Python bridge between GahenaxIA's CFT gateway and Ruflo's multi-agent
orchestration platform (https://github.com/ruvnet/ruflo).

Architecture:
    GahenaxIA Engine
        ↓ (SkillSpec dispatch)
    RufloBridge
        ↓ (HTTP/MCP JSON-RPC)
    Ruflo MCP Bridge (Node.js, :3001)
        ↓ (agent spawn / swarm / memory)
    Ruflo Agents (coder, architect, reviewer, security, tester)

The bridge maps GahenaxIA's UA-governed skill calls to Ruflo's MCP tool groups:
  - agents   → agent_spawn, swarm_create, hive_mind, task_dispatch
  - memory   → memory_store, memory_retrieve, embeddings_create
  - devtools → analyze_code, performance_profile, github_pr
  - security → aidefence_scan, claims_validate

Usage:
    bridge = RufloBridge(base_url="http://localhost:3001")
    result = await bridge.dispatch_tool("agents", "agent_spawn", {
        "type": "coder",
        "task": "Refactor LLL optimizer",
        "priority": "high"
    })
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ============================================================================
# RUFLO AGENT TYPES (mirrored from agents/*.yaml)
# ============================================================================

class RufloAgentType(str, Enum):
    CODER      = "coder"       # code-generation, refactoring, debugging
    ARCHITECT  = "architect"   # system-design, api-design, documentation
    REVIEWER   = "reviewer"    # code-review, quality-gates, best-practices
    TESTER     = "tester"      # test-generation, coverage, assertions
    SECURITY   = "security"    # vulnerability-scan, CVE-remediation, hardening


# ============================================================================
# RUFLO MCP TOOL GROUPS (from rvf.manifest.json TOOL_GROUPS)
# ============================================================================

class RufloToolGroup(str, Enum):
    CORE          = "core"
    INTELLIGENCE  = "intelligence"
    AGENTS        = "agents"
    MEMORY        = "memory"
    DEVTOOLS      = "devtools"
    SECURITY      = "security"
    BROWSER       = "browser"
    NEURAL        = "neural"
    AGENTIC_FLOW  = "agentic-flow"


# ============================================================================
# RUFLO SWARM TOPOLOGIES (from SwarmCoordinator.ts)
# ============================================================================

class SwarmTopology(str, Enum):
    HIERARCHICAL = "hierarchical"   # Queen-led, top-down task delegation
    MESH         = "mesh"           # Peer-to-peer, all agents can communicate
    RING         = "ring"           # Sequential pipeline topology
    STAR         = "star"           # Central hub with spoke agents


# ============================================================================
# DATA CONTRACTS
# ============================================================================

@dataclass
class RufloToolCall:
    """Canonical MCP tool call sent to ruflo bridge."""
    group:     RufloToolGroup
    tool_name: str
    params:    Dict[str, Any]
    request_id: str = field(default_factory=lambda: _generate_id("rtc"))


@dataclass
class RufloAgentJob:
    """
    GahenaxIA → Ruflo task dispatch.
    Maps a Gahenax Job to a Ruflo agent task.
    """
    agent_type:  RufloAgentType
    task:        str
    priority:    str = "normal"          # low | normal | high | critical
    topology:    SwarmTopology = SwarmTopology.HIERARCHICAL
    agent_count: int = 1
    context:     Dict[str, Any] = field(default_factory=dict)
    job_id:      str = field(default_factory=lambda: _generate_id("rjob"))

    def canonical_hash(self) -> str:
        body = {
            "agent_type": self.agent_type,
            "task": self.task,
            "priority": self.priority,
        }
        raw = json.dumps(body, sort_keys=True).encode()
        return "sha256:" + hashlib.sha256(raw).hexdigest()


@dataclass
class RufloResult:
    """Response from a ruflo MCP tool call."""
    ok:        bool
    tool_name: str
    group:     str
    payload:   Dict[str, Any]
    latency_ms: float
    request_id: str
    error:     Optional[str] = None


@dataclass
class RufloMemoryEntry:
    """Vector memory entry compatible with AgentDB."""
    key:      str
    content:  str
    agent_id: str
    tags:     List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# INTERNAL HELPERS
# ============================================================================

def _generate_id(prefix: str) -> str:
    return f"{prefix}_{int(time.time() * 1000) % 1_000_000_000:09d}"


def _build_mcp_request(tool_name: str, params: Dict[str, Any]) -> bytes:
    """Build a JSON-RPC 2.0 request for the ruflo MCP bridge."""
    rpc = {
        "jsonrpc": "2.0",
        "id": _generate_id("rpc"),
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": params,
        },
    }
    return json.dumps(rpc).encode("utf-8")


# ============================================================================
# BRIDGE
# ============================================================================

class RufloBridge:
    """
    Synchronous + async facade over the Ruflo MCP bridge REST interface.

    The bridge exposes three main call modes:
      1. dispatch_tool()    — generic MCP tool call
      2. spawn_agent()      — shortcut for agent_spawn
      3. store_memory()     — shortcut for memory_store
      4. retrieve_memory()  — shortcut for memory_retrieve

    All calls are logged with UA-compatible metrics.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:3001",
        timeout_s: float = 30.0,
        max_retries: int = 3,
    ):
        self.base_url    = base_url.rstrip("/")
        self.timeout_s   = timeout_s
        self.max_retries = max_retries
        self._call_count = 0
        self._fail_count = 0
        logger.info("RufloBridge initialized → %s", self.base_url)

    # ------------------------------------------------------------------
    # HEALTH
    # ------------------------------------------------------------------

    def health_check(self) -> bool:
        """Returns True if the ruflo MCP bridge is reachable."""
        try:
            req = urllib.request.Request(
                f"{self.base_url}/health",
                headers={"Accept": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except Exception:
            return False

    # ------------------------------------------------------------------
    # GENERIC TOOL DISPATCH
    # ------------------------------------------------------------------

    def dispatch_tool(
        self,
        group: RufloToolGroup,
        tool_name: str,
        params: Dict[str, Any],
    ) -> RufloResult:
        """
        Dispatch a single MCP tool call to the ruflo bridge.

        Maps to POST /mcp/{group} with JSON-RPC 2.0 body.
        """
        endpoint = f"{self.base_url}/mcp/{group.value}"
        body     = _build_mcp_request(tool_name, params)
        t0       = time.monotonic()
        request_id = _generate_id("disp")

        for attempt in range(1, self.max_retries + 1):
            try:
                req = urllib.request.Request(
                    endpoint,
                    data=body,
                    headers={
                        "Content-Type": "application/json",
                        "Accept":       "application/json",
                    },
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                    raw      = resp.read()
                    rpc_resp = json.loads(raw)
                    latency  = (time.monotonic() - t0) * 1000
                    self._call_count += 1

                    if "error" in rpc_resp:
                        self._fail_count += 1
                        return RufloResult(
                            ok=False,
                            tool_name=tool_name,
                            group=group.value,
                            payload={},
                            latency_ms=latency,
                            request_id=request_id,
                            error=str(rpc_resp["error"]),
                        )

                    content = rpc_resp.get("result", {}).get("content", [])
                    payload = content[0] if content else {}
                    return RufloResult(
                        ok=True,
                        tool_name=tool_name,
                        group=group.value,
                        payload=payload if isinstance(payload, dict) else {"text": payload},
                        latency_ms=latency,
                        request_id=request_id,
                    )

            except urllib.error.URLError as exc:
                logger.warning(
                    "RufloBridge call %s/%s attempt %d/%d failed: %s",
                    group.value, tool_name, attempt, self.max_retries, exc,
                )
                if attempt < self.max_retries:
                    time.sleep(2 ** (attempt - 1))   # 1s, 2s, 4s backoff

        self._fail_count += 1
        latency = (time.monotonic() - t0) * 1000
        return RufloResult(
            ok=False,
            tool_name=tool_name,
            group=group.value,
            payload={},
            latency_ms=latency,
            request_id=request_id,
            error=f"All {self.max_retries} attempts failed",
        )

    # ------------------------------------------------------------------
    # AGENT SHORTCUTS
    # ------------------------------------------------------------------

    def spawn_agent(self, job: RufloAgentJob) -> RufloResult:
        """Dispatch a Gahenax Job as a Ruflo agent task."""
        return self.dispatch_tool(
            group=RufloToolGroup.AGENTS,
            tool_name="agent_spawn",
            params={
                "type":     job.agent_type.value,
                "task":     job.task,
                "priority": job.priority,
                "context":  job.context,
                "jobId":    job.job_id,
            },
        )

    def create_swarm(
        self,
        jobs: List[RufloAgentJob],
        topology: SwarmTopology = SwarmTopology.HIERARCHICAL,
    ) -> RufloResult:
        """Launch a multi-agent swarm over a list of jobs."""
        return self.dispatch_tool(
            group=RufloToolGroup.AGENTS,
            tool_name="swarm_create",
            params={
                "topology": topology.value,
                "agents": [
                    {
                        "type":     j.agent_type.value,
                        "task":     j.task,
                        "priority": j.priority,
                    }
                    for j in jobs
                ],
            },
        )

    # ------------------------------------------------------------------
    # MEMORY SHORTCUTS
    # ------------------------------------------------------------------

    def store_memory(self, entry: RufloMemoryEntry) -> RufloResult:
        """Persist a memory entry in Ruflo's AgentDB / HNSW store."""
        return self.dispatch_tool(
            group=RufloToolGroup.MEMORY,
            tool_name="memory_store",
            params={
                "key":     entry.key,
                "content": entry.content,
                "agentId": entry.agent_id,
                "tags":    entry.tags,
                "metadata": entry.metadata,
            },
        )

    def retrieve_memory(
        self,
        query: str,
        agent_id: str,
        top_k: int = 5,
    ) -> RufloResult:
        """HNSW semantic search over agent memory (~61µs per query)."""
        return self.dispatch_tool(
            group=RufloToolGroup.MEMORY,
            tool_name="memory_retrieve",
            params={
                "query":   query,
                "agentId": agent_id,
                "topK":    top_k,
            },
        )

    # ------------------------------------------------------------------
    # DEVTOOLS SHORTCUTS
    # ------------------------------------------------------------------

    def analyze_code(self, code: str, language: str = "python") -> RufloResult:
        """Static analysis via the ruflo devtools group."""
        return self.dispatch_tool(
            group=RufloToolGroup.DEVTOOLS,
            tool_name="analyze_code",
            params={"code": code, "language": language},
        )

    # ------------------------------------------------------------------
    # METRICS
    # ------------------------------------------------------------------

    def metrics(self) -> Dict[str, Any]:
        """Return call statistics for UA accounting."""
        total = self._call_count
        return {
            "total_calls":  total,
            "failed_calls": self._fail_count,
            "success_rate": round((total - self._fail_count) / max(total, 1), 4),
            "base_url":     self.base_url,
        }


# ============================================================================
# MODULE-LEVEL SINGLETON (opt-in lazy init)
# ============================================================================

_bridge: Optional[RufloBridge] = None


def get_bridge(base_url: str = "http://localhost:3001") -> RufloBridge:
    """Return or create the module-level bridge singleton."""
    global _bridge
    if _bridge is None:
        _bridge = RufloBridge(base_url=base_url)
    return _bridge


# ============================================================================
# CLI SMOKE TEST
# ============================================================================

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)

    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3001"
    br  = RufloBridge(base_url=url)

    print(f"Ruflo bridge health @ {url} → {br.health_check()}")

    job = RufloAgentJob(
        agent_type=RufloAgentType.CODER,
        task="Optimize LLL lattice reduction loop in gahenax_engine.py",
        priority="high",
        context={"module": "gahenax_engine", "target": "lll_reduce"},
    )
    print(f"Canonical hash: {job.canonical_hash()}")
    result = br.spawn_agent(job)
    print(f"Result: ok={result.ok}  latency={result.latency_ms:.1f}ms  error={result.error}")
    print(f"Metrics: {br.metrics()}")
