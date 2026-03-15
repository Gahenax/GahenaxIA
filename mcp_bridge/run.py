#!/usr/bin/env python3
"""
mcp_bridge/run.py — Entrypoint del MCP Bridge

Uso:
  python -m mcp_bridge.run claude                  # Claude Code se conecta
  python -m mcp_bridge.run antigravity             # Antigravity se conecta
  python -m mcp_bridge.run claude --db /ruta/db    # DB personalizada

Configuración en Claude Code (~/.claude/mcp.json o .mcp.json en el repo):
  {
    "mcpServers": {
      "gahenax-bridge": {
        "command": "python",
        "args": ["-m", "mcp_bridge.run", "claude"],
        "cwd": "/ruta/a/GahenaxIA"
      }
    }
  }

Configuración en Antigravity (Settings > MCP Servers):
  Name:    gahenax-bridge
  Command: python -m mcp_bridge.run antigravity
  CWD:     /ruta/a/GahenaxIA
"""
from __future__ import annotations

import argparse
import asyncio
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gahenax MCP Bridge — Claude Code ↔ Google Antigravity"
    )
    parser.add_argument(
        "agent",
        choices=["claude", "antigravity"],
        help="Which agent is connecting to this server instance.",
    )
    parser.add_argument(
        "--db",
        default=None,
        help="Path to the SQLite database file (default: GahenaxIA/bridge_tasks.sqlite)",
    )
    args = parser.parse_args()

    try:
        from mcp_bridge.server import run_server
    except ImportError as e:
        print(f"[gahenax-bridge] Import error: {e}", file=sys.stderr)
        print(
            "[gahenax-bridge] Make sure 'mcp' is installed: pip install mcp",
            file=sys.stderr,
        )
        sys.exit(1)

    asyncio.run(run_server(caller_agent=args.agent, db_path=args.db))


if __name__ == "__main__":
    main()
