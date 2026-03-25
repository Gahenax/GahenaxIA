"""
bridge_api.py — Bidirectional message bus between Claude.ai and Antigravity (Gemini CLI)

Agents:
  - "claude"       → Claude.ai (via userscript)
  - "antigravity"  → Gemini CLI local agent
  - "gahenax"      → Gahenax Core engine

Flow:
  Claude.ai userscript  →  POST /telemetry          (chat sync)
  Claude.ai userscript  →  GET  /messages/claude/pending  (poll for Antigravity replies)
  Antigravity           →  GET  /messages/antigravity/pending  (poll for Claude msgs)
  Antigravity           →  POST /send               (reply to Claude)
  Any agent             →  GET  /state/{session_id} (latest snapshot)
  Any agent             →  GET  /heartbeat          (ping)
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from gahenax_app.schemas.gahenax_contract import (
    BridgeTelemetryRequest,
    BridgeTelemetryResponse,
    BridgeSendRequest,
    BridgeMessage,
)
from gahenax_app.core.cmr import utc_now
import sqlite3
import json
import uuid
import os

bridge_router = APIRouter(tags=["Antigravity Bridge"])

_DB = os.path.join(os.getcwd(), "ua_ledger.sqlite")

KNOWN_AGENTS = {"claude", "antigravity", "gahenax", "broadcast"}


# ---------------------------------------------------------------------------
# DB init
# ---------------------------------------------------------------------------

def _init_tables() -> None:
    con = sqlite3.connect(_DB)
    try:
        con.executescript("""
            CREATE TABLE IF NOT EXISTS bridge_sessions (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id   TEXT NOT NULL,
                url          TEXT NOT NULL,
                messages     TEXT NOT NULL,
                received_at  TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS message_bus (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id   TEXT UNIQUE NOT NULL,
                session_id   TEXT NOT NULL,
                from_agent   TEXT NOT NULL,
                to_agent     TEXT NOT NULL,
                content      TEXT NOT NULL,
                message_type TEXT NOT NULL DEFAULT 'chat',
                status       TEXT NOT NULL DEFAULT 'pending',
                created_at   TEXT NOT NULL,
                delivered_at TEXT
            );
        """)
        con.commit()
    finally:
        con.close()


_init_tables()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _db():
    return sqlite3.connect(_DB)


def _insert_message(session_id: str, from_agent: str, to_agent: str,
                    content: dict, message_type: str = "chat") -> str:
    mid = str(uuid.uuid4())
    con = _db()
    try:
        con.execute(
            """INSERT INTO message_bus
               (message_id, session_id, from_agent, to_agent, content, message_type, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)""",
            (mid, session_id, from_agent, to_agent, json.dumps(content), message_type, utc_now()),
        )
        con.commit()
    finally:
        con.close()
    return mid


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@bridge_router.get("/heartbeat")
async def heartbeat():
    """Ping — Antigravity uses this to verify the bridge is alive."""
    return {"status": "alive", "bridge": "Gahenax-Antigravity v1.2", "time": utc_now()}


@bridge_router.post("/telemetry", response_model=BridgeTelemetryResponse)
async def receive_telemetry(payload: BridgeTelemetryRequest):
    """
    Receive conversation snapshot from the Claude.ai userscript.
    Stores the snapshot AND enqueues each message for Antigravity to consume.
    """
    now = utc_now()

    # 1. Persist full snapshot
    con = _db()
    try:
        con.execute(
            "INSERT INTO bridge_sessions (session_id, url, messages, received_at) VALUES (?, ?, ?, ?)",
            (payload.session_id, payload.url,
             json.dumps([m.model_dump() for m in payload.messages]), now),
        )
        con.commit()
    finally:
        con.close()

    # 2. Enqueue new messages for Antigravity
    for msg in payload.messages:
        if msg.role in ("user", "assistant"):
            _insert_message(
                session_id=payload.session_id,
                from_agent="claude",
                to_agent="antigravity",
                content={"role": msg.role, "text": msg.text, "ts": msg.ts, "url": payload.url},
                message_type="chat",
            )

    return BridgeTelemetryResponse(
        ok=True,
        session_id=payload.session_id,
        messages_received=len(payload.messages),
    )


@bridge_router.post("/send")
async def send_message(payload: BridgeSendRequest):
    """
    Send a directed message from one agent to another.
    Antigravity uses this to reply to Claude.ai.

    Body: { "from_agent": "antigravity", "to_agent": "claude",
            "session_id": "...", "content": "...", "message_type": "chat" }
    """
    if payload.from_agent not in KNOWN_AGENTS:
        raise HTTPException(400, f"Unknown from_agent: {payload.from_agent}")
    if payload.to_agent not in KNOWN_AGENTS:
        raise HTTPException(400, f"Unknown to_agent: {payload.to_agent}")

    mid = _insert_message(
        session_id=payload.session_id,
        from_agent=payload.from_agent,
        to_agent=payload.to_agent,
        content={"text": payload.content, "message_type": payload.message_type},
        message_type=payload.message_type,
    )
    return {"ok": True, "message_id": mid, "queued_for": payload.to_agent}


@bridge_router.get("/messages/{agent}/pending")
async def poll_pending(agent: str, session_id: str | None = None, limit: int = 20):
    """
    Poll pending messages for a specific agent.
    Antigravity calls: GET /messages/antigravity/pending
    Userscript calls:  GET /messages/claude/pending?session_id=<id>
    Marks returned messages as 'delivered'.
    """
    if agent not in KNOWN_AGENTS:
        raise HTTPException(400, f"Unknown agent: {agent}")

    con = _db()
    try:
        query = """SELECT id, message_id, session_id, from_agent, content, message_type, created_at
                   FROM message_bus
                   WHERE to_agent = ? AND status = 'pending'"""
        params: list = [agent]
        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)
        query += " ORDER BY id ASC LIMIT ?"
        params.append(limit)

        rows = con.execute(query, params).fetchall()
        ids = [r[0] for r in rows]

        if ids:
            placeholders = ",".join("?" * len(ids))
            con.execute(
                f"UPDATE message_bus SET status='delivered', delivered_at=? WHERE id IN ({placeholders})",
                [utc_now()] + ids,
            )
            con.commit()
    finally:
        con.close()

    messages = [
        {
            "message_id": r[1],
            "session_id": r[2],
            "from_agent": r[3],
            "content": json.loads(r[4]),
            "message_type": r[5],
            "created_at": r[6],
        }
        for r in rows
    ]
    return {"agent": agent, "pending": len(messages), "messages": messages}


@bridge_router.get("/state/{session_id}")
async def get_state(session_id: str):
    """
    Get the latest full conversation snapshot for a session.
    Compatible with Antigravity's expected GET /state/{session_id} endpoint.
    """
    con = _db()
    try:
        row = con.execute(
            "SELECT messages, url, received_at FROM bridge_sessions WHERE session_id = ? ORDER BY id DESC LIMIT 1",
            (session_id,),
        ).fetchone()
    finally:
        con.close()

    if row is None:
        raise HTTPException(404, "Session not found.")
    return {
        "session_id": session_id,
        "url": row[1],
        "messages": json.loads(row[0]),
        "received_at": row[2],
    }


@bridge_router.get("/sessions")
async def list_sessions(limit: int = 20):
    """List all known Claude.ai sessions."""
    con = _db()
    try:
        rows = con.execute(
            """SELECT session_id, url, received_at FROM bridge_sessions
               GROUP BY session_id ORDER BY MAX(id) DESC LIMIT ?""",
            (limit,),
        ).fetchall()
    finally:
        con.close()
    return [{"session_id": r[0], "url": r[1], "last_sync": r[2]} for r in rows]
