import requests
import time
import json
import random

PORT = 5000

def run_diagnostic():
    print(f"📡 Iniciando Diagnóstico de Señal hacia Puerto {PORT}...")
    for i in range(5):
        val = round(1.0 + (i * 0.5) + random.random(), 2)
        payload = {
            "ts": time.time(),
            "data": json.dumps({"multiplier": str(val), "type": "diagnostic_test"})
        }
        try:
            res = requests.post(f"http://localhost:{PORT}/telemetry", json=payload, timeout=1)
            print(f"✅ [Test {i+1}] {val}x enviado. Status: {res.status_code}")
        except Exception as e:
            print(f"❌ [Test {i+1}] Fallo de conexión: {e}")
        time.sleep(1)

if __name__ == "__main__":
    run_diagnostic()
