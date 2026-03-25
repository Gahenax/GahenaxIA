# Gahenax Spy Dashboard v19.0 (Ultra-Reliable Diagnostic Edition)
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import os
import sys
import time
from collections import deque

# Inject paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
if BASE_DIR not in sys.path: sys.path.insert(0, BASE_DIR)

import config

app = Flask(__name__)
CORS(app)

# Persistent State
STATE = {
    "last_multiplier": "0.00",
    "last_update": 0,
    "packet_count": 0,
    "buffer": deque(maxlen=50),
    "logs": deque(maxlen=10)
}

@app.route("/")
def index():
    return """
    <html>
    <head>
        <title>GAHENAX DIAGNOSTIC</title>
        <style>
            body { background: #000; color: #0f0; font-family: monospace; padding: 20px; }
            .stat { font-size: 5em; font-weight: bold; }
            #logs { border-top: 1px solid #0f0; margin-top: 20px; color: #0a0; }
            .label { color: #888; font-size: 0.8em; }
        </style>
    </head>
    <body>
        <div class="label">LIVE MULTIPLIER</div>
        <div id="mult" class="stat">0.00x</div>
        <div class="label">PACKETS: <span id="count">0</span> | LAST: <span id="ts">---</span></div>
        <div id="logs">
            <div class="label">SYSTEM LOGS</div>
            <div id="log-list"></div>
        </div>
        <script>
            async function update() {
                try {
                    const r = await fetch("/api/status");
                    const d = await r.json();
                    document.getElementById("mult").innerText = d.last_multiplier + "x";
                    document.getElementById("count").innerText = d.packet_count;
                    document.getElementById("ts").innerText = new Date(d.last_update*1000).toLocaleTimeString();
                    
                    document.getElementById("log-list").innerHTML = d.logs.map(l => `<div>${l}</div>`).reverse().join("");
                } catch(e) {}
                setTimeout(update, 500);
            }
            update();
        </script>
    </body>
    </html>
    """

@app.route("/api/status")
def status():
    return jsonify({
        "last_multiplier": STATE["last_multiplier"],
        "last_update": STATE["last_update"],
        "packet_count": STATE["packet_count"],
        "logs": list(STATE["logs"])
    })

@app.route("/telemetry", methods=["POST"])
def telemetry():
    data = request.json
    STATE["packet_count"] += 1
    STATE["last_update"] = time.time()
    
    # Extract data
    raw = data.get("data", "")
    ts = data.get("ts", time.time())
    
    # Support for both single multiplier and list (history_harvest)
    if isinstance(raw, str) and "multiplier" in raw:
        try:
            payload = json.loads(raw)
            mult = payload.get("multiplier")
            
            if isinstance(mult, list):
                # Batch processing
                for m in mult:
                    entry = {"ts": ts, "data": json.dumps({"multiplier": m, "type": "history_harvest"})}
                    with open(config.TELEMETRY_LOG, "a", encoding="utf-8") as f:
                        f.write(json.dumps(entry) + "\n")
                STATE["last_multiplier"] = str(mult[0])
                msg = f"[{time.strftime('%H:%M:%S')}] Batch Received: {len(mult)} rounds"
            else:
                # Single round
                STATE["last_multiplier"] = str(mult)
                entry = {"ts": ts, "data": raw}
                with open(config.TELEMETRY_LOG, "a", encoding="utf-8") as f:
                        f.write(json.dumps(entry) + "\n")
                msg = f"[{time.strftime('%H:%M:%S')}] Packet Received: {mult}x"
        except: 
            msg = f"[{time.strftime('%H:%M:%S')}] Malformed Packet"
    else:
        msg = f"[{time.strftime('%H:%M:%S')}] Heartbeat/Generic Received"
    
    STATE["logs"].append(msg)
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(port=config.DASHBOARD_PORT, debug=False)
