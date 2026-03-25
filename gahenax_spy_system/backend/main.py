"""
Gahenax Claude Bridge — Bidirectional Channel
Run: python backend/main.py

API:
  POST /telemetry                      <- userscript sends Claude messages
  GET  /messages/antigravity/pending   <- Antigravity reads msgs from Claude
  POST /send                           <- Antigravity writes to Claude
  GET  /messages/claude/pending        <- userscript polls for Antigravity replies
  GET  /state/<session_id>             <- full session snapshot
  GET  /heartbeat                      <- ping
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from collections import deque
import json, os, time
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "..", "spy_data", "claude_chats")
os.makedirs(DATA_DIR, exist_ok=True)

app = Flask(__name__)
CORS(app)

# In-memory queues — keyed by session_id
SESSIONS  = {}                          # session_id -> full payload
INBOX     = {}                          # session_id -> deque (Claude -> Antigravity)
OUTBOX    = {}                          # session_id -> deque (Antigravity -> Claude)

def _get_queue(store, session_id):
    if session_id not in store:
        store[session_id] = deque(maxlen=200)
    return store[session_id]

# ─── Userscript → Bridge ───────────────────────────────────────────────────────
@app.route("/telemetry", methods=["POST"])
def telemetry():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No data"}), 400

    session_id = data.get("session_id", "default")
    messages   = data.get("messages", [])

    payload = {
        "last_sync": datetime.now().isoformat(),
        "url": data.get("url"),
        "messages": messages
    }
    filepath = os.path.join(DATA_DIR, f"chat_{session_id}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    SESSIONS[session_id] = payload

    # Forward new messages into Antigravity inbox
    inbox = _get_queue(INBOX, session_id)
    for msg in messages:
        inbox.append({"ts": time.time(), **msg})

    print(f"[BRIDGE] /telemetry | Session {session_id} | {len(messages)} msgs")
    return jsonify({"status": "ok", "synced": len(messages)})


# ─── Antigravity reads Claude's messages ──────────────────────────────────────
@app.route("/messages/antigravity/pending", methods=["GET"])
def antigravity_pending():
    session_id = request.args.get("session_id", "default")
    inbox = _get_queue(INBOX, session_id)
    msgs = list(inbox)
    inbox.clear()   # consume
    print(f"[BRIDGE] /messages/antigravity/pending | {len(msgs)} msgs delivered")
    return jsonify({"session_id": session_id, "messages": msgs, "count": len(msgs)})


# ─── Antigravity writes to Claude ─────────────────────────────────────────────
@app.route("/send", methods=["POST"])
def send():
    data = request.json
    if not data:
        return jsonify({"status": "error"}), 400

    session_id = data.get("session_id", "default")
    content    = data.get("content", "")
    from_agent = data.get("from_agent", "antigravity")

    entry = {
        "ts": time.time(),
        "from": from_agent,
        "to":   data.get("to_agent", "claude"),
        "content": content
    }
    _get_queue(OUTBOX, session_id).append(entry)
    print(f"[BRIDGE] /send | {from_agent} -> claude | {content[:60]}")
    return jsonify({"status": "queued", "session_id": session_id})


# ─── Userscript polls for Antigravity replies ──────────────────────────────────
@app.route("/messages/claude/pending", methods=["GET"])
def claude_pending():
    session_id = request.args.get("session_id", "default")
    outbox = _get_queue(OUTBOX, session_id)
    msgs = list(outbox)
    outbox.clear()   # consume
    return jsonify({"session_id": session_id, "messages": msgs, "count": len(msgs)})


# ─── Snapshot ─────────────────────────────────────────────────────────────────
@app.route("/state/<session_id>", methods=["GET"])
def get_state(session_id):
    state = SESSIONS.get(session_id)
    if not state:
        filepath = os.path.join(DATA_DIR, f"chat_{session_id}.json")
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                state = json.load(f)
                SESSIONS[session_id] = state
    return jsonify(state) if state else (jsonify({"status": "not_found"}), 404)


@app.route("/heartbeat")
def heartbeat():
    return jsonify({"status": "alive", "time": time.time()})


if __name__ == "__main__":
    print("=" * 52)
    print(" GAHENAX CLAUDE BRIDGE v2.0 — Port 8080")
    print(" POST /telemetry                   <- userscript")
    print(" GET  /messages/antigravity/pending <- Antigravity reads")
    print(" POST /send                         <- Antigravity writes")
    print(" GET  /messages/claude/pending      <- userscript polls")
    print(" GET  /state/<session_id>           <- snapshot")
    print(" GET  /heartbeat                    <- ping")
    print("=" * 52)
    app.run(host="127.0.0.1", port=8080, debug=False)
