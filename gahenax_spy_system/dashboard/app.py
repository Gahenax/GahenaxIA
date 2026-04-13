# GAHENAX DASHBOARD v20.4 - GROUND CONTROL
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import time
import os
import sys

app = Flask(__name__)
CORS(app)

# ESTADO GLOBAL - CENTRO DE MANDO
STATE = {
    "usdc_profit": 0.0,
    "last_update": 0,
    "packet_count": 0,
    "mcp_active": True,
    "risk": 0,
    "wins": 0,
    "losses": 0,
    "streak": 0,
    "mode": "INITIALIZING",
    "active_seeds": {
        "server": "65e0c8d56fe22b36574f0a57e48d5d93775d241f3a746dde87e949abef9cd2a6",
        "client": "rs8GnZl6HxhBcbYeRitaLkmiGA1TNOkxhYuwkYzDZiwi3rsnFdzdnI7KpjksuHTm",
        "nonce": 2673
    }
}

@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>GAHENAX GROUND CONTROL v20.4</title>
        <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --neon-green: #00ff66;
                --bg-dark: #0a0a0a;
                --panel-bg: #151515;
                --text-main: #e0e0e0;
                --accent: #ff00ff;
            }
            body { 
                background-color: var(--bg-dark); 
                color: var(--text-main); 
                font-family: 'JetBrains Mono', monospace;
                margin: 0; padding: 20px;
                display: flex; flex-direction: column; align-items: center;
            }
            .dashboard {
                width: 900px;
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }
            .panel {
                background: var(--panel-bg);
                border: 1px solid #333;
                padding: 24px;
                border-radius: 8px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);
                position: relative;
                overflow: hidden;
            }
            .panel::before {
                content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: var(--accent); opacity: 0.5;
            }
            .full-width { grid-column: span 2; }
            .profit { font-size: 3.5em; color: var(--neon-green); text-shadow: 0 0 15px var(--neon-green); font-weight: bold; }
            .risk-bar {
                width: 100%; background: #222; height: 12px; border-radius: 6px; overflow: hidden; margin-top: 20px; border: 1px solid #333;
            }
            .risk-fill { height: 100%; background: var(--neon-green); transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: 0 0 10px var(--neon-green); }
            .status-tag { font-size: 0.7em; letter-spacing: 2px; color: #666; margin-bottom: 15px; }
            .online { color: var(--neon-green); text-shadow: 0 0 5px var(--neon-green); }
            
            /* Ground Control UI */
            .control-panel h2 { color: var(--accent); margin-top: 0; font-size: 1.2em; text-transform: uppercase; letter-spacing: 3px; }
            .input-group { margin-bottom: 15px; }
            label { display: block; font-size: 0.7em; color: #666; margin-bottom: 8px; text-transform: uppercase; }
            input { 
                width: 100%; background: #000; border: 1px solid #333; color: var(--neon-green); 
                padding: 12px; border-radius: 4px; box-sizing: border-box; font-family: inherit; font-size: 0.9em;
                transition: border-color 0.3s;
            }
            input:focus { border-color: var(--accent); outline: none; }
            button {
                width: 100%; padding: 15px; background: var(--accent); border: none; color: white;
                font-weight: bold; border-radius: 4px; cursor: pointer; transition: 0.3s;
                text-transform: uppercase; letter-spacing: 2px; margin-top: 10px;
            }
            button:hover { background: #d400d4; transform: translateY(-2px); box-shadow: 0 5px 15px rgba(255,0,255,0.3); }
            #inject-msg { font-size: 0.8em; margin-bottom: 15px; height: 1em; }
        </style>
    </head>
    <body>
        <div style="margin-bottom: 40px; text-align: center;">
            <h1 style="margin:0; letter-spacing: 5px;">GAHENAX <span style="color:var(--accent)">GROUND CONTROL</span></h1>
            <div style="font-size: 0.8em; color: #444;">DETERMINISTIC ORACLE INTERFACE v20.4</div>
        </div>
        
        <div class="dashboard">
            <div class="panel">
                <div class="status-tag">SYSTEM // <span id="status" class="online">CONNECTED</span></div>
                <div class="label" style="font-size: 0.8em; color: #666; margin-bottom: 5px;">LIVE PROFIT (USDC)</div>
                <div id="profit" class="profit">0.00000000</div>
                <p style="font-size: 0.8em; color: #444; margin-top: 20px;">TELEMETRY BRIDGE: <span id="packets" style="color:var(--accent)">0</span> PKTS</p>
            </div>
            
            <div class="panel">
                <div class="status-tag">STREAK RADAR // <span id="mode" style="color:var(--accent)">VACUUM</span></div>
                <div class="label" style="font-size: 0.8em; color: #666; margin-bottom: 5px;">RISK PROBABILITY</div>
                <div id="risk" style="font-size: 2.5em; font-weight: bold;">0%</div>
                <div class="risk-bar"><div id="risk-fill" class="risk-fill"></div></div>
                <p style="font-size: 0.8em; color: #444; margin-top: 20px;">CURRENT NONCE: <span id="nonce" style="color: #fff">0</span></p>
            </div>

            <div class="panel full-width control-panel">
                <h2>SEED INFILTRATOR</h2>
                <div id="inject-msg"></div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
                    <div>
                        <div class="input-group">
                            <label>SERVER SEED (REVEALED)</label>
                            <input type="text" id="in-server" value="65e0c8d56fe22b36574f0a57e48d5d93775d241f3a746dde87e949abef9cd2a6" placeholder="Paste unhashed server seed...">
                        </div>
                        <div class="input-group">
                            <label>CLIENT SEED</label>
                            <input type="text" id="in-client" value="rs8GnZl6HxhBcbYeRitaLkmiGA1TNOkxhYuwkYzDZiwi3rsnFdzdnI7KpjksuHTm" placeholder="Current client seed...">
                        </div>
                    </div>
                    <div>
                        <div class="input-group">
                            <label>STARTING NONCE</label>
                            <input type="number" id="in-nonce" value="2673">
                        </div>
                        <button onclick="injectSeeder()">INJECT TO ORACLE</button>
                    </div>
                </div>
            </div>
        </div>

        <script>
            async function injectSeeder() {
                const msg = document.getElementById('inject-msg');
                msg.style.color = "var(--accent)";
                msg.innerText = ">> INJECTING SEED PACKET...";
                
                const data = {
                    server: document.getElementById('in-server').value,
                    client: document.getElementById('in-client').value,
                    nonce: document.getElementById('in-nonce').value
                };
                
                try {
                    const res = await fetch('/api/seeds', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    if (res.ok) {
                        msg.style.color = "var(--neon-green)";
                        msg.innerText = ">> SUCCESS: ORACLE CALIBRATED AT NONCE " + data.nonce;
                        setTimeout(() => { msg.innerText = ""; }, 4000);
                    }
                } catch(e) {
                    msg.style.color = "red";
                    msg.innerText = ">> ERROR: REFUSED BY GROUND CONTROL";
                }
            }

            async function updateStats() {
                try {
                    const res = await fetch('/api/status');
                    const data = await res.json();
                    
                    document.getElementById('profit').innerText = data.usdc_profit.toFixed(8);
                    document.getElementById('packets').innerText = data.packet_count;
                    document.getElementById('nonce').innerText = data.streak;
                    document.getElementById('mode').innerText = data.mode;
                    
                    let riskVal = minMax((data.streak / 800) * 100, 0, 100);
                    document.getElementById('risk').innerText = riskVal.toFixed(1) + "%";
                    document.getElementById('risk-fill').style.width = riskVal + "%";
                    
                    if (riskVal > 85) {
                        document.getElementById('risk-fill').style.background = "red";
                        document.getElementById('risk-fill').style.boxShadow = "0 0 15px red";
                    } else if (riskVal > 50) {
                        document.getElementById('risk-fill').style.background = "orange";
                        document.getElementById('risk-fill').style.boxShadow = "0 0 10px orange";
                    } else {
                        document.getElementById('risk-fill').style.background = "var(--neon-green)";
                        document.getElementById('risk-fill').style.boxShadow = "0 0 10px var(--neon-green)";
                    }
                } catch(e) {}
            }
            
            function minMax(val, min, max) { return Math.min(Math.max(val, min), max); }
            setInterval(updateStats, 800);
        </script>
    </body>
    </html>
    """

@app.route("/api/telemetry", methods=["POST"])
def telemetry():
    data = request.json
    if data:
        STATE["usdc_profit"] = data.get("profit", STATE["usdc_profit"])
        STATE["streak"] = data.get("streak", STATE["streak"])
        STATE["mode"] = data.get("mode", STATE["mode"])
        STATE["packet_count"] += 1
        STATE["last_update"] = time.time()
    return jsonify({"status": "ok"})

@app.route("/api/status")
def status():
    return jsonify(STATE)

@app.route("/api/seeds", methods=["GET", "POST"])
def seeds():
    if request.method == "POST":
        STATE["active_seeds"] = request.json
        return jsonify({"status": "injected"})
    return jsonify(STATE["active_seeds"])

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
