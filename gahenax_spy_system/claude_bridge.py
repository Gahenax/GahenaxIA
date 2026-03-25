# gahenax_spy_system/claude_bridge.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import time
from datetime import datetime

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "spy_data", "claude_chats")
os.makedirs(DATA_DIR, exist_ok=True)

app = Flask(__name__)
CORS(app)

# Portfolio of active sessions
SESSIONS = {}

@app.route("/telemetry", methods=["POST"])
def telemetry():
    """
    Recibe datos de la inyección de Claude.
    Estructura esperada:
    {
        "session_id": "...",
        "messages": [{"role": "user", "content": "..."}, ...],
        "url": "..."
    }
    """
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No data"}), 400
    
    session_id = data.get("session_id", "default")
    messages = data.get("messages", [])
    
    # Persistencia
    filename = f"chat_{session_id}.json"
    filepath = os.path.join(DATA_DIR, filename)
    
    payload = {
        "last_sync": datetime.now().isoformat(),
        "url": data.get("url"),
        "messages": messages
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    
    SESSIONS[session_id] = payload
    print(f"[BRIDGE_SYNC] Session {session_id} synchronized. Messages: {len(messages)}")
    
    return jsonify({"status": "ok", "synced_messages": len(messages)})

@app.route("/state/<session_id>", methods=["GET"])
def get_state(session_id):
    """Retorna el estado actual de una sesión."""
    state = SESSIONS.get(session_id)
    if not state:
        # Intentar cargar de disco
        filepath = os.path.join(DATA_DIR, f"chat_{session_id}.json")
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                state = json.load(f)
                SESSIONS[session_id] = state
    
    if state:
        return jsonify(state)
    return jsonify({"status": "error", "message": "Session not found"}), 404

@app.route("/heartbeat", methods=["GET"])
def heartbeat():
    return jsonify({"status": "alive", "time": time.time()})

if __name__ == "__main__":
    # Usamos el puerto 8080 como es estándar en Gahenax, 
    # pero se puede cambiar si hay conflicto.
    print("GAHENAX CLAUDE BRIDGE ACTIVE on Port 8080")
    app.run(host="127.0.0.1", port=8080, debug=False)
