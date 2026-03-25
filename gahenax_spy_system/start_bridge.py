"""
start_bridge.py — Launcher canónico del Gahenax Claude Bridge

Uso (Windows):
    cd c:\\Users\\jotam\\OneDrive\\Desktop\\GahenaxAI\\gahenax_spy_system
    python start_bridge.py
"""
import sys
import os

# Añadir backend/ al path sin importar desde dónde se ejecute
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND = os.path.join(ROOT, "backend")

if BACKEND not in sys.path:
    sys.path.insert(0, BACKEND)

os.chdir(BACKEND)  # uvicorn necesita estar en backend/ para resolver imports

from main import app, BANNER
import uvicorn

if __name__ == "__main__":
    print(BANNER)
    uvicorn.run(app, host="0.0.0.0", port=8080)
