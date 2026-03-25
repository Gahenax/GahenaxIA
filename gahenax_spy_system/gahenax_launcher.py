import subprocess
import time
import sys
import os
import requests
import json
import threading

# Pathing
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_SCRIPT = os.path.join(BASE_DIR, "dashboard", "app.py")
AGENT_SCRIPT = os.path.join(BASE_DIR, "agents", "selenium_spy.py")

def stream_output(pipe, prefix):
    try:
        for line in iter(pipe.readline, ''):
            if not line: break
            clean_line = line.strip()
            if clean_line:
                print(f"{prefix} {clean_line}")
    except: pass

def launch():
    print("="*60)
    print(" GAHENAX TACTICAL LAUNCHER v1.2 (CHROME-ONLY SYNC) ")
    print("="*60)
    
    # Check if Chrome is listening on 9222
    try:
        requests.get("http://localhost:9222/json", timeout=1)
        print("✅ DETECTADO: Navegador Chrome con puerto 9222 activo.")
    except:
        print("⚠️ AVISO: No se detecta Chrome en puerto 9222. Abre Chrome con el launcher primero.")

    # 1. Start Dashboard
    dash_proc = subprocess.Popen([sys.executable, DASHBOARD_SCRIPT], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.STDOUT,
                                 text=True,
                                 bufsize=1)
    threading.Thread(target=stream_output, args=(dash_proc.stdout, "[DASH]"), daemon=True).start()
    
    time.sleep(2)
    
    # 2. Start Agent
    agent_proc = subprocess.Popen([sys.executable, AGENT_SCRIPT],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT,
                                  text=True,
                                  bufsize=1)
    threading.Thread(target=stream_output, args=(agent_proc.stdout, "[AGENT]"), daemon=True).start()
    
    print("🚀 SISTEMA EN ESCUCHA PASIVA. ESPERANDO SEÑAL DE VUELO...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo...")
        dash_proc.terminate()
        agent_proc.terminate()
        sys.exit(0)

if __name__ == "__main__":
    launch()
