"""
gahenax_swarm.py — Ruflo-adapted swarm orchestrator for GahenaxAI

Adapts Ruflo's multi-agent swarm patterns to the Python/Gahenax stack.
Agents run in parallel, report via the bridge, results go to CMR.

Usage:
    python gahenax_swarm.py --task "refactor auth module" --agents coder,tester
    python gahenax_swarm.py --task "design new API" --agents all
    python gahenax_swarm.py --list-agents
"""
import argparse
import json
import multiprocessing
import os
import sys
import time
import urllib.request
import uuid
import yaml
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── Config ────────────────────────────────────────────────────────────────────

BRIDGE    = "http://localhost:8080"
AGENTS_DIR = Path(__file__).parent / "agents"
BACKEND_DIR = Path(__file__).parent / "backend"

# 3-Tier routing (adapted from Ruflo ADR-026)
TIER_1_MAX_COMPLEXITY = 0.0   # deterministic / mock
TIER_2_MAX_COMPLEXITY = 0.3   # Gemini Flash
TIER_3_MIN_COMPLEXITY = 0.3   # Gemini Pro

# ── Data types ────────────────────────────────────────────────────────────────

@dataclass
class AgentConfig:
    type: str
    version: str
    capabilities: list[str]
    ua_budget: float
    mode: str
    tier: int
    session_prefix: str
    reports_to: str

@dataclass
class SwarmJob:
    job_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    task: str = ""
    agents: list[str] = field(default_factory=list)
    complexity: float = 0.5
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

@dataclass
class AgentResult:
    agent_type: str
    job_id: str
    status: str         # "ok" | "error" | "skipped"
    output: Any
    latency_ms: float
    ua_spent: float

# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_agent(agent_type: str) -> AgentConfig | None:
    path = AGENTS_DIR / f"{agent_type}.yaml"
    if not path.exists():
        return None
    with open(path) as f:
        d = yaml.safe_load(f)
    return AgentConfig(
        type=d["type"],
        version=d["version"],
        capabilities=d.get("capabilities", []),
        ua_budget=d.get("contract", {}).get("ua_budget", 6.0),
        mode=d.get("contract", {}).get("mode", "everyday"),
        tier=d.get("routing", {}).get("tier", 2),
        session_prefix=d.get("bridge", {}).get("session_prefix", f"{agent_type}-"),
        reports_to=d.get("bridge", {}).get("reports_to", "antigravity"),
    )

def _list_agents() -> list[str]:
    return [p.stem for p in AGENTS_DIR.glob("*.yaml")]

def _post_bridge(path: str, body: dict) -> dict | None:
    try:
        data = json.dumps(body).encode()
        req  = urllib.request.Request(
            f"{BRIDGE}{path}", data=data,
            headers={"Content-Type": "application/json"}, method="POST"
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read())
    except Exception:
        return None

def _bridge_alive() -> bool:
    try:
        with urllib.request.urlopen(f"{BRIDGE}/heartbeat", timeout=3) as r:
            return r.status == 200
    except Exception:
        return False

# ── Agent runner (runs in subprocess) ────────────────────────────────────────

def _run_agent(agent_type: str, job: SwarmJob, result_queue: multiprocessing.Queue):
    t0 = time.perf_counter()
    cfg = _load_agent(agent_type)
    if not cfg:
        result_queue.put(AgentResult(agent_type, job.job_id, "error", "agent config not found", 0, 0))
        return

    session_id = f"{cfg.session_prefix}{job.job_id}"

    # Tier routing
    if job.complexity <= TIER_1_MAX_COMPLEXITY:
        tier, model = 1, "mock"
    elif job.complexity <= TIER_2_MAX_COMPLEXITY:
        tier, model = 2, "gemini-flash"
    else:
        tier, model = 3, "gemini-pro"

    print(f"  [{agent_type.upper()}] tier={tier} model={model} ua={cfg.ua_budget} | {job.task[:60]}")

    # Call Gahenax backend
    sys.path.insert(0, str(BACKEND_DIR))
    try:
        from gahenax_app.core.gahenax_engine import GahenaxGovernor, EngineMode
        mode    = EngineMode(cfg.mode)
        gov     = GahenaxGovernor(budget_ua=cfg.ua_budget, mode=mode)
        output  = gov.run_inference_cycle(
            f"[{agent_type.upper()} AGENT] {job.task}",
            {}
        )
        result_data = output.to_dict() if hasattr(output, "to_dict") else str(output)
        status  = "ok"
        ua_spent = float(gov.ua.spent)
    except Exception as e:
        result_data = str(e)
        status  = "error"
        ua_spent = 0.0

    latency_ms = (time.perf_counter() - t0) * 1000

    # Report to bridge → Antigravity reads it
    _post_bridge("/send", {
        "from_agent":   "claude",
        "to_agent":     cfg.reports_to,
        "session_id":   session_id,
        "content":      json.dumps({
            "agent":      agent_type,
            "job_id":     job.job_id,
            "task":       job.task,
            "status":     status,
            "latency_ms": round(latency_ms, 1),
            "ua_spent":   ua_spent,
        }),
        "message_type": "state_sync",
    })

    result_queue.put(AgentResult(agent_type, job.job_id, status, result_data, latency_ms, ua_spent))

# ── Swarm coordinator ─────────────────────────────────────────────────────────

def run_swarm(task: str, agent_types: list[str], complexity: float = 0.5) -> list[AgentResult]:
    job = SwarmJob(task=task, agents=agent_types, complexity=complexity)

    print(f"\n{'='*60}")
    print(f" GAHENAX SWARM — job {job.job_id}")
    print(f" Task: {task[:70]}")
    print(f" Agents: {', '.join(agent_types)}")
    print(f" Complexity: {complexity} | Bridge: {BRIDGE}")
    print(f"{'='*60}")

    bridge_ok = _bridge_alive()
    if not bridge_ok:
        print("  ⚠  Bridge offline — results won't be relayed to Antigravity")

    # Announce swarm start to bridge
    if bridge_ok:
        _post_bridge("/send", {
            "from_agent":   "claude",
            "to_agent":     "antigravity",
            "session_id":   f"swarm-{job.job_id}",
            "content":      f"SWARM START | job={job.job_id} | agents={','.join(agent_types)} | task={task[:80]}",
            "message_type": "command",
        })

    # Run all agents in parallel
    result_queue: multiprocessing.Queue = multiprocessing.Queue()
    processes = []
    for at in agent_types:
        p = multiprocessing.Process(target=_run_agent, args=(at, job, result_queue))
        p.start()
        processes.append(p)

    for p in processes:
        p.join(timeout=120)

    results = []
    while not result_queue.empty():
        results.append(result_queue.get())

    # Summarize
    print(f"\n{'─'*60}")
    print(f" SWARM RESULTS — job {job.job_id}")
    total_ua = 0.0
    for r in results:
        icon = "✓" if r.status == "ok" else "✗"
        print(f"  {icon} [{r.agent_type.upper()}] status={r.status} latency={r.latency_ms:.0f}ms ua={r.ua_spent:.1f}")
        total_ua += r.ua_spent
    print(f"  Total UA spent: {total_ua:.1f}")
    print(f"{'='*60}\n")

    # Announce swarm end to bridge
    if bridge_ok:
        _post_bridge("/send", {
            "from_agent":   "claude",
            "to_agent":     "antigravity",
            "session_id":   f"swarm-{job.job_id}",
            "content":      f"SWARM DONE | job={job.job_id} | agents={len(results)} | total_ua={total_ua:.1f}",
            "message_type": "command",
        })

    return results

# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="GahenaxAI Swarm Orchestrator")
    parser.add_argument("--task",       type=str, help="Task description")
    parser.add_argument("--agents",     type=str, default="coder,tester", help="Comma-separated agent types or 'all'")
    parser.add_argument("--complexity", type=float, default=0.5, help="Task complexity 0.0-1.0")
    parser.add_argument("--list-agents", action="store_true", help="List available agents")
    args = parser.parse_args()

    if args.list_agents:
        agents = _list_agents()
        print("Available agents:")
        for a in agents:
            cfg = _load_agent(a)
            print(f"  {a:20} tier={cfg.tier} ua={cfg.ua_budget} caps={','.join(cfg.capabilities[:2])}")
        return

    if not args.task:
        parser.error("--task is required")

    agent_list = _list_agents() if args.agents == "all" else [a.strip() for a in args.agents.split(",")]
    run_swarm(args.task, agent_list, args.complexity)

if __name__ == "__main__":
    main()
