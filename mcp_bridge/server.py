"""
mcp_bridge/server.py

MCP Server: Claude Code ↔ Google Antigravity Bridge

Exposes 5 tools via Model Context Protocol (stdio transport):

  dispatch_task   — enviar una tarea al otro agente
  get_pending     — obtener tareas pendientes para este agente
  complete_task   — marcar tarea como completada con resultado
  fail_task       — marcar tarea como fallida con error
  get_task        — consultar estado de una tarea específica

Both Claude Code and Antigravity connect to this server as an MCP client.
The server acts as the message broker with a persistent SQLite queue.

Integración con SingleWriterOrchestrator
-----------------------------------------
Cuando task_type es "orchestrate", el bridge puede delegar al orquestador
existente de GahenaxIA (SingleWriterOrchestrator) para tareas que requieran
gobernanza, ledger y validación de contratos.
"""
from __future__ import annotations

import json
import sys
from typing import Any, Dict

# MCP Python SDK — pip install mcp
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Tool,
        TextContent,
        CallToolResult,
    )
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

from mcp_bridge.db import TaskDB

# ── Tool schemas ───────────────────────────────────────────────────────────

TOOLS = [
    Tool(
        name="dispatch_task",
        description=(
            "Dispatch a task to the other agent (Claude Code or Antigravity). "
            "Use this to delegate work: Claude Code dispatches deploy/build tasks "
            "to Antigravity; Antigravity dispatches code/fix/review tasks to Claude Code."
        ),
        inputSchema={
            "type": "object",
            "required": ["to_agent", "task_type", "description"],
            "properties": {
                "to_agent": {
                    "type": "string",
                    "enum": ["claude", "antigravity"],
                    "description": "Which agent should handle this task.",
                },
                "task_type": {
                    "type": "string",
                    "description": (
                        "Category of the task. Examples: "
                        "'deploy', 'build', 'test', 'review', 'fix', "
                        "'refactor', 'document', 'orchestrate'"
                    ),
                },
                "description": {
                    "type": "string",
                    "description": "Clear description of what needs to be done.",
                },
                "payload": {
                    "type": "object",
                    "description": "Optional structured data for the task (branch, files, context, etc.).",
                    "default": {},
                },
                "priority": {
                    "type": "integer",
                    "enum": [1, 2, 3],
                    "description": "1=low, 2=normal (default), 3=high",
                    "default": 2,
                },
            },
        },
    ),
    Tool(
        name="get_pending",
        description=(
            "Get pending tasks assigned to a specific agent. "
            "Call this to check what work the other agent has sent you."
        ),
        inputSchema={
            "type": "object",
            "required": ["agent"],
            "properties": {
                "agent": {
                    "type": "string",
                    "enum": ["claude", "antigravity"],
                    "description": "Which agent's pending tasks to retrieve.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max tasks to return (default: 20).",
                    "default": 20,
                },
            },
        },
    ),
    Tool(
        name="complete_task",
        description="Mark a task as completed. Include a result summary.",
        inputSchema={
            "type": "object",
            "required": ["task_id"],
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "The task UUID to mark as done.",
                },
                "result": {
                    "type": "object",
                    "description": "Optional result payload (summary, artifacts, URLs, etc.).",
                    "default": {},
                },
            },
        },
    ),
    Tool(
        name="fail_task",
        description="Mark a task as failed with an error message.",
        inputSchema={
            "type": "object",
            "required": ["task_id", "error"],
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "The task UUID to mark as failed.",
                },
                "error": {
                    "type": "string",
                    "description": "Description of what went wrong.",
                },
            },
        },
    ),
    Tool(
        name="get_task",
        description="Get the current status and details of a specific task.",
        inputSchema={
            "type": "object",
            "required": ["task_id"],
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "The task UUID to look up.",
                },
            },
        },
    ),
]


# ── Server factory ─────────────────────────────────────────────────────────

def create_server(
    db: TaskDB,
    caller_agent: str,  # "claude" or "antigravity" — identifies who's calling
) -> "Server":
    if not MCP_AVAILABLE:
        raise RuntimeError(
            "MCP SDK not installed. Run: pip install mcp"
        )

    server = Server(name="gahenax-bridge", version="1.0.0")

    @server.list_tools()
    async def list_tools():
        return TOOLS

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
        try:
            result = _dispatch(name, arguments, db, caller_agent)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )
        except Exception as exc:
            return CallToolResult(
                content=[TextContent(type="text", text=f"ERROR: {exc}")],
                isError=True,
            )

    return server


def _dispatch(
    name: str,
    args: Dict[str, Any],
    db: TaskDB,
    caller_agent: str,
) -> Any:
    if name == "dispatch_task":
        task = db.dispatch(
            from_agent=caller_agent,
            to_agent=args["to_agent"],
            task_type=args["task_type"],
            description=args["description"],
            payload=args.get("payload"),
            priority=int(args.get("priority", 2)),
        )
        return {"ok": True, "task": task}

    elif name == "get_pending":
        agent = args["agent"]
        limit = int(args.get("limit", 20))
        tasks = db.pending_for(agent, limit=limit)
        return {"ok": True, "count": len(tasks), "tasks": tasks}

    elif name == "complete_task":
        ok = db.complete(args["task_id"], result=args.get("result"))
        return {"ok": ok, "task_id": args["task_id"], "status": "done"}

    elif name == "fail_task":
        ok = db.fail(args["task_id"], error=args["error"])
        return {"ok": ok, "task_id": args["task_id"], "status": "failed"}

    elif name == "get_task":
        task = db.get(args["task_id"])
        if task is None:
            return {"ok": False, "error": f"Task {args['task_id']} not found"}
        return {"ok": True, "task": task}

    else:
        raise ValueError(f"Unknown tool: {name}")


# ── Standalone runner ──────────────────────────────────────────────────────

async def run_server(caller_agent: str, db_path: str | None = None) -> None:
    """Run the MCP bridge server over stdio."""
    db = TaskDB(db_path) if db_path else TaskDB()
    server = create_server(db, caller_agent)

    print(
        f"[gahenax-bridge] Started. Agent: {caller_agent}. "
        f"DB: {db.db_path}",
        file=sys.stderr,
    )

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )
