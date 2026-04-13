import json
import time
import os

TELEMETRY_LOG = r"c:\Users\jotam\OneDrive\Desktop\GahenaxAI\gahenax_spy_system\utils\aviator_telemetry.jsonl"

# Datos extraídos manualmente del screenshot (v40.0)
# Orden: De arriba-izquierda a abajo-derecha (Histórico de Spribe)
history_raw = [
    2.68, 7.03, 1.36, 2.28, 2.72, 2.14, 2.31, 1.48, 3.14, 3.21, 3.22, 11.11, 2.40,
    2.97, 1.51, 2.25, 1.95, 1.92, 1.04, 1.73, 1.10, 1.56, 1.23, 1.25, 2.78, 5.42,
    5.86, 1.39, 4.46, 7.08, 1.00, 1.24, 1.66, 7.87, 2.50, 3.27, 1.75, 1.00, 19.37,
    1.87, 1.00, 1.10, 1.16, 1.84, 2.33, 5.37, 5.33, 1.76, 2.96, 1.31, 2.71, 1.17,
    4.81, 3.66, 6.01
]

def ingest_history():
    print(f" Inyectando {len(history_raw)} rondas en el motor de telemetría...")
    now = time.time()
    
    # Asegurar directorio
    os.makedirs(os.path.dirname(TELEMETRY_LOG), exist_ok=True)
    
    with open(TELEMETRY_LOG, "a", encoding="utf-8") as f:
        for val in reversed(history_raw): # Invertir para que los más viejos vayan primero en el log
            entry = {
                "ts": now - (len(history_raw) - history_raw.index(val)) * 10, # Timestamp simulado
                "data": json.dumps({"multiplier": val, "type": "outcome"})
            }
            f.write(json.dumps(entry) + "\n")
    
    print(" Inyección completada. Los motores de análisis se auto-actualizarán.")

if __name__ == "__main__":
    ingest_history()
