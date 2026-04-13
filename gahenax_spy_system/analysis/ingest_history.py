# Script de Ingesta Manual Gahenax v5.2
# Transcribe datos de screenshots al dataset de entrenamiento

import json
import time
import os

LOG_FILE = "../utils/aviator_training_data.jsonl"

# Datos extraídos del historial visual
sequence = [
    4.67, 4.61, 102.45, 1.82, 2.19, 4.72, 2.09, 1.01, 2.03, 1.97, 
    8.44, 1.47, 3.81, 5.55, 1.47, 17.74, 1.27, 1.41, 5.53, 1.80, 
    1.07, 2.13, 5.41, 1.08, 3.73, 1.47, 2.92, 1.56
]

def ingest():
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    count = 0
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        for mult in sequence:
            # Simulamos el formato de captura de la extensión/spy
            data = {"ts": timestamp, "data": f'{{"multiplier": {mult}}}', "source": "MANUAL_INGEST_V5.2"}
            f.write(json.dumps(data) + "\n")
            count += 1
    
    print(f" Ingesta completada: {count} rounds añadidos al DNA de Gahenax.")

if __name__ == "__main__":
    ingest()
