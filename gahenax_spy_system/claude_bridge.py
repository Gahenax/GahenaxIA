from flask import Flask, request, jsonify
from flask_cors import CORS
import json, os, time
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "spy_data", "claude_chats")
os.makedirs(DATA_DIR, exist_ok=True)

app = Flask(__name__)
CORS(app)

SESSIONS = {}

@app.route("/telemetry", methods=["POST"])
def telemetry():
    data = request.json
    if not data:
        return jsonify({"status": "error"}), 400
    session_id = data.get("session_id", "default")
    messages = data.get("messages", [])
    payload = {"last_sync": datetime.now().isoformat(), "url": data.get("url"), "messages": messages}
    filepath = os.path.join(DATA_DIR, f"chat_{session_id}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    SESSIONS[session_id] = payload
    print(f"[BRIDGE_SYNC] Session {session_id} | Messages: {len(messages)}")
    return jsonify({"status": "ok", "synced_messages": len(messages)})

@app.route("/state/<session_id>", methods=["GET"])
def get_state(session_id):
    state = SESSIONS.get(session_id)
    if not state:
        filepath = os.path.join(DATA_DIR, f"chat_{session_id}.json")
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                state = json.load(f)
    return jsonify(state) if state else (jsonify({"status": "error"}), 404)

@app.route("/heartbeat")
def heartbeat():
    return jsonify({"status": "alive", "time": time.time()})

if __name__ == "__main__":
    print("GAHENAX CLAUDE BRIDGE — Port 8080")
    app.run(host="127.0.0.1", port=8080, debug=False)
