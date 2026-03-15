"""
mcp_bridge/db.py

SQLite task queue for the Claude Code ↔ Google Antigravity bridge.
Supports multiple projects across the Gahenax ecosystem.

Schema
------
tasks
  id          TEXT PRIMARY KEY  (uuid4)
  created_at  TEXT              (ISO-8601 UTC)
  updated_at  TEXT
  project     TEXT              (project name, e.g. "GahenaxIA", "LimpiaMAX", "TRIKSTER-ORACLE")
  from_agent  TEXT              ("claude" | "antigravity")
  to_agent    TEXT              ("claude" | "antigravity")
  task_type   TEXT              (e.g. "deploy", "review", "fix", "build", "orchestrate")
  description TEXT
  payload     TEXT              (JSON)
  priority    INTEGER           (1=low, 2=normal, 3=high)
  status      TEXT              ("pending" | "running" | "done" | "failed")
  result      TEXT              (JSON, nullable)
  error       TEXT              (nullable)
  orch_job_id TEXT              (nullable — linked SingleWriterOrchestrator job_id)
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

AGENT_VALUES = {"claude", "antigravity"}
STATUS_VALUES = {"pending", "running", "done", "failed"}
PRIORITY_VALUES = {1, 2, 3}

DEFAULT_DB_PATH = Path(__file__).parent.parent / "bridge_tasks.sqlite"

DDL = """
CREATE TABLE IF NOT EXISTS tasks (
    id          TEXT    PRIMARY KEY,
    created_at  TEXT    NOT NULL,
    updated_at  TEXT    NOT NULL,
    project     TEXT    NOT NULL DEFAULT 'default',
    from_agent  TEXT    NOT NULL,
    to_agent    TEXT    NOT NULL,
    task_type   TEXT    NOT NULL,
    description TEXT    NOT NULL,
    payload     TEXT    NOT NULL DEFAULT '{}',
    priority    INTEGER NOT NULL DEFAULT 2,
    status      TEXT    NOT NULL DEFAULT 'pending',
    result      TEXT,
    error       TEXT,
    orch_job_id TEXT
);
CREATE INDEX IF NOT EXISTS idx_tasks_to_agent_status
    ON tasks(to_agent, status, priority DESC, created_at ASC);
CREATE INDEX IF NOT EXISTS idx_tasks_project
    ON tasks(project, status, created_at DESC);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class TaskDB:
    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(DDL)
        self._conn.commit()

    # ── write ──────────────────────────────────────────────────────────────

    def dispatch(
        self,
        *,
        from_agent: str,
        to_agent: str,
        task_type: str,
        description: str,
        payload: Dict[str, Any] | None = None,
        priority: int = 2,
        project: str = "default",
        orch_job_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Insert a new task. Returns the full task row."""
        if from_agent not in AGENT_VALUES:
            raise ValueError(f"from_agent must be one of {AGENT_VALUES}")
        if to_agent not in AGENT_VALUES:
            raise ValueError(f"to_agent must be one of {AGENT_VALUES}")
        if priority not in PRIORITY_VALUES:
            raise ValueError(f"priority must be 1 (low), 2 (normal) or 3 (high)")

        task_id = str(uuid.uuid4())
        now = _now()
        payload_json = json.dumps(payload or {}, ensure_ascii=True)

        self._conn.execute(
            """
            INSERT INTO tasks
              (id, created_at, updated_at, project, from_agent, to_agent,
               task_type, description, payload, priority, status, orch_job_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)
            """,
            (task_id, now, now, project, from_agent, to_agent,
             task_type, description, payload_json, priority, orch_job_id),
        )
        self._conn.commit()
        return self.get(task_id)  # type: ignore[return-value]

    def start(self, task_id: str) -> bool:
        """Mark task as running. Returns False if task not found or not pending."""
        now = _now()
        cur = self._conn.execute(
            "UPDATE tasks SET status='running', updated_at=? "
            "WHERE id=? AND status='pending'",
            (now, task_id),
        )
        self._conn.commit()
        return cur.rowcount > 0

    def complete(self, task_id: str, result: Dict[str, Any] | None = None) -> bool:
        """Mark task as done with optional result payload."""
        now = _now()
        result_json = json.dumps(result or {}, ensure_ascii=True)
        cur = self._conn.execute(
            "UPDATE tasks SET status='done', result=?, updated_at=? WHERE id=?",
            (result_json, now, task_id),
        )
        self._conn.commit()
        return cur.rowcount > 0

    def fail(self, task_id: str, error: str) -> bool:
        """Mark task as failed with error message."""
        now = _now()
        cur = self._conn.execute(
            "UPDATE tasks SET status='failed', error=?, updated_at=? WHERE id=?",
            (error, now, task_id),
        )
        self._conn.commit()
        return cur.rowcount > 0

    # ── read ───────────────────────────────────────────────────────────────

    def get(self, task_id: str) -> Optional[Dict[str, Any]]:
        row = self._conn.execute(
            "SELECT * FROM tasks WHERE id=?", (task_id,)
        ).fetchone()
        return _row_to_dict(row) if row else None

    def pending_for(
        self,
        agent: str,
        limit: int = 20,
        project: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Return pending tasks for an agent, ordered by priority DESC then created_at ASC."""
        if project:
            rows = self._conn.execute(
                "SELECT * FROM tasks WHERE to_agent=? AND status='pending' AND project=? "
                "ORDER BY priority DESC, created_at ASC LIMIT ?",
                (agent, project, limit),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM tasks WHERE to_agent=? AND status='pending' "
                "ORDER BY priority DESC, created_at ASC LIMIT ?",
                (agent, limit),
            ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def list_tasks(
        self,
        *,
        to_agent: Optional[str] = None,
        from_agent: Optional[str] = None,
        status: Optional[str] = None,
        project: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        clauses: List[str] = []
        params: List[Any] = []
        if to_agent:
            clauses.append("to_agent=?")
            params.append(to_agent)
        if from_agent:
            clauses.append("from_agent=?")
            params.append(from_agent)
        if status:
            clauses.append("status=?")
            params.append(status)
        if project:
            clauses.append("project=?")
            params.append(project)

        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        params.append(limit)
        rows = self._conn.execute(
            f"SELECT * FROM tasks {where} "
            "ORDER BY priority DESC, created_at DESC LIMIT ?",
            params,
        ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def close(self) -> None:
        self._conn.close()


# ── helpers ────────────────────────────────────────────────────────────────

def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    d = dict(row)
    for key in ("payload", "result"):
        if d.get(key):
            try:
                d[key] = json.loads(d[key])
            except (json.JSONDecodeError, TypeError):
                pass
    return d
