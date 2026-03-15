"""
mcp_bridge/orchestrator_bridge.py

Integración entre el MCP Bridge y el SingleWriterOrchestrator de GahenaxIA.

Cuando un agente (Claude Code o Antigravity) despacha una tarea con
task_type="orchestrate", esta capa:

  1. Convierte la tarea MCP en un Job del orquestador
  2. Lo registra en el SingleWriterOrchestrator (con ledger + dedup)
  3. Devuelve el orch_job_id para trazabilidad
  4. Acepta resultados de workers y los sella en el ledger

Esto permite que cualquier tarea del pipeline multi-agente quede registrada
en el ledger de auditoría con hash e integridad garantizada.

Multi-proyecto
--------------
Cada proyecto tiene su propio run_dir y ledger. El OrchestratorRegistry
mantiene una instancia por proyecto, creándola on-demand.
"""
from __future__ import annotations

import os
import sys
import threading
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

# GahenaxIA root on path
_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from orchestrator.orchestrator import SingleWriterOrchestrator
from orchestrator.contracts import Job, now_iso


# ── Registry ──────────────────────────────────────────────────────────────

class OrchestratorRegistry:
    """
    Manages one SingleWriterOrchestrator instance per project.
    All instances share the same GahenaxIA root but have separate run dirs.
    Thread-safe.
    """

    def __init__(self, base_run_dir: str | Path | None = None) -> None:
        self._base = Path(base_run_dir or (_ROOT / "orchestrator_runs"))
        self._base.mkdir(parents=True, exist_ok=True)
        self._instances: Dict[str, SingleWriterOrchestrator] = {}
        self._lock = threading.Lock()

    def get(self, project: str) -> SingleWriterOrchestrator:
        """Return (or create) the orchestrator for a given project."""
        with self._lock:
            if project not in self._instances:
                run_dir = str(self._base / _sanitize(project))
                orch = SingleWriterOrchestrator(
                    run_dir=run_dir,
                    run_id=f"{project}-bridge",
                )
                try:
                    orch.acquire_lock()
                    orch.load_state()
                    orch.replay_ledger_for_dedup()
                except RuntimeError:
                    # Another process holds the lock — read-only mode
                    orch.load_state()
                self._instances[project] = orch
            return self._instances[project]

    def release_all(self) -> None:
        with self._lock:
            for orch in self._instances.values():
                try:
                    orch.release_lock()
                except Exception:
                    pass
            self._instances.clear()


# ── Bridge adapter ─────────────────────────────────────────────────────────

class OrchestratorBridge:
    """
    Adapter: MCP task → Orchestrator Job

    Usage:
        bridge = OrchestratorBridge(registry)

        # When a task arrives with task_type="orchestrate":
        job_id = bridge.submit_task(project, task_id, description, payload)

        # When a worker completes the work:
        bridge.accept_result(project, worker_id, job_id, result_payload)
    """

    def __init__(self, registry: OrchestratorRegistry) -> None:
        self._registry = registry

    def submit_task(
        self,
        project: str,
        task_id: str,
        description: str,
        payload: Dict[str, Any],
    ) -> str:
        """
        Register a governed job in the orchestrator for the given project.
        Returns the orch_job_id (same as task_id for traceability).
        """
        orch = self._registry.get(project)

        # Use the MCP task_id as the job_id for end-to-end traceability
        job = Job(
            job_id=task_id,
            t_start=0.0,
            t_end=1.0,   # abstract range — real semantics in payload
            stride=1.0,
        )
        orch.register_jobs([job])
        return task_id

    def accept_result(
        self,
        project: str,
        worker_id: int,
        job_id: str,
        result_payload: Dict[str, Any],
    ) -> str:
        """
        Submit a result from a worker. The orchestrator validates, deduplicates,
        and seals the event in the append-only ledger.

        Returns the AcceptVerdict: "ACCEPTED" | "REJECTED_SCHEMA" | etc.
        """
        orch = self._registry.get(project)

        # Wrap in the schema the orchestrator expects
        # (ResultPayload: t, root_val, meta)
        normalized = _normalize_result(result_payload)
        verdict = orch.accept_result(
            worker_id=worker_id,
            job_id=job_id,
            payload=normalized,
        )
        if verdict == "ACCEPTED":
            orch.mark_job_done(job_id)

        return verdict

    def get_job_status(self, project: str, job_id: str) -> Optional[Dict[str, Any]]:
        """Return the orchestrator's view of a job."""
        orch = self._registry.get(project)
        return orch.state["jobs"].get(job_id)

    def project_stats(self, project: str) -> Dict[str, Any]:
        """Return summary stats for a project's orchestrator."""
        orch = self._registry.get(project)
        return {
            "project": project,
            "run_id": orch.run_id,
            "done": orch.state.get("done", 0),
            "failed": orch.state.get("failed", 0),
            "rejected": orch.state.get("rejected", 0),
            "seq": orch.state.get("seq", 0),
            "total_jobs": len(orch.state.get("jobs", {})),
        }


# ── Helpers ────────────────────────────────────────────────────────────────

def _sanitize(name: str) -> str:
    """Make a project name safe for use as a directory."""
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)


def _normalize_result(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert an arbitrary task result into the ResultPayload schema
    expected by SingleWriterOrchestrator (t, root_val, meta).

    If the payload already has these fields, pass through.
    Otherwise, wrap it: root_val=0.0 (success signal), meta=payload.
    """
    if "t" in payload and "root_val" in payload and "meta" in payload:
        return payload

    return {
        "t": float(payload.get("t", 0.0)),
        "root_val": float(payload.get("root_val", 0.0)),  # 0.0 = success
        "meta": {k: v for k, v in payload.items() if k not in ("t", "root_val")},
    }


# ── Module-level singleton ─────────────────────────────────────────────────

_default_registry: Optional[OrchestratorRegistry] = None
_registry_lock = threading.Lock()


def get_default_registry() -> OrchestratorRegistry:
    global _default_registry
    with _registry_lock:
        if _default_registry is None:
            _default_registry = OrchestratorRegistry()
        return _default_registry


def get_default_bridge() -> OrchestratorBridge:
    return OrchestratorBridge(get_default_registry())
