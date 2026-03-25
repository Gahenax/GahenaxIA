"""
start_bridge.py — Launcher canónico del Gahenax Claude Bridge v2.0

Uso (Windows):
    cd c:\\Users\\jotam\\OneDrive\\Desktop\\GahenaxAI\\gahenax_spy_system
    python start_bridge.py
"""
import os
import sys

# Asegurar que el directorio de gahenax_spy_system está en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from claude_bridge import app

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
