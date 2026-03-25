# Gahenax Spy v18.0 - Temporal Spectral Tracker
# Author: Antigravity AI
# Purpose: Reverse-engineer the RNG's Deterministic Clock and Time-Seed Correlation.

import json
import os
import sys
import numpy as np
import time

# Importar configuración
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

DECRYPTION_LOG = os.path.join(config.BASE_DIR, "analysis", "decryption_matrix.json")

def analyze_temporal_correlation():
    """Analiza la correlación entre el Timestamp y el Multiplicador en ventanas de 50 rondas."""
    if not os.path.exists(config.TELEMETRY_LOG):
        return
    
    try:
        with open(config.TELEMETRY_LOG, "r") as f:
            lines = f.readlines()[-50:]
            data_points = []
            for l in lines:
                entry = json.loads(l)
                ts = entry.get("timestamp", time.time())
                if '"multiplier":' in entry["data"]:
                    mult = float(entry["data"].split('"multiplier":')[1].split('}')[0].split(',')[0])
                    data_points.append((ts, mult))
            
            if len(data_points) < 50: return
            
            # 1. Análisis de Periodicidad (Fourier en el tiempo)
            times = np.array([p[0] for p in data_points])
            mults = np.array([p[1] for p in data_points])
            
            # Correlación de tiempo
            time_diffs = np.diff(times)
            avg_time_between_rounds = np.mean(time_diffs)
            
            # Coeficiente de correlación Pearson (Tiempo vs Multiplicador)
            correlation = np.corrcoef(times, mults)[0, 1]
            
            # 2. Identificación de "Viento de Cola" (Drift)
            drift = np.polyfit(times, mults, 1)[0]
            
            # Guardar matriz de descifrado
            matrix = {
                "correlation": float(correlation),
                "drift": float(drift),
                "avg_interval": float(avg_time_between_rounds),
                "entropy": float(np.std(mults)),
                "status": "ANÁLISIS DE RELOJ ACTIVO"
            }
            
            with open(DECRYPTION_LOG, "w") as df:
                json.dump(matrix, df)
                
    except Exception as e:
        print(f"Error in Temporal Tracker: {e}")

if __name__ == "__main__":
    print("🧬 Gahenax Temporal Spectral Tracker v18.0 ACTIVE...")
    while True:
        analyze_temporal_correlation()
        time.sleep(5)
