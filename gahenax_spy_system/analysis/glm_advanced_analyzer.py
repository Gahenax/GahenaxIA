# Gahenax Spy v20.0 - GLM Advanced Analyzer
# Author: Antigravity AI (Ported from Operator Baseline GLM 4.6)
# Purpose: Sequential Transition Analysis & Hourly Temporal Decryption.

import json
import os
import sys
import numpy as np
from datetime import datetime
import time

# Importar configuración
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

GLM_OUTPUT = os.path.join(config.BASE_DIR, "analysis", "glm_analysis.json")

def analyze_glm_multimodal():
    """Realiza el análisis multimodal de transiciones secuenciales y cubetas por hora."""
    if not os.path.exists(config.TELEMETRY_LOG):
        return
    
    try:
        with open(config.TELEMETRY_LOG, "r") as f:
            lines = f.readlines()[-200:] # Analizar las últimas 200 muestras
            data_points = []
            for l in lines:
                entry = json.loads(l)
                dt = datetime.fromtimestamp(entry.get("timestamp", time.time()))
                if '"multiplier":' in entry["data"]:
                    mult = float(entry["data"].split('"multiplier":')[1].split('}')[0].split(',')[0])
                    data_points.append({"val": mult, "hour": dt.hour, "ts": entry["timestamp"]})
            
            if len(data_points) < 10: return
            
            # 1. Matriz de Transiciones (Sequential Patterns)
            transitions = {}
            for i in range(1, len(data_points)):
                # Redondear para encontrar patrones de "clase" (ej: Bajo -> Alto)
                prev_class = "LOW" if data_points[i-1]["val"] < 2.0 else "HIGH"
                curr_class = "LOW" if data_points[i]["val"] < 2.0 else "HIGH"
                key = f"{prev_class} -> {curr_class}"
                transitions[key] = transitions.get(key, 0) + 1
            
            # 2. Análisis por Hora (Temporal Buckets)
            hourly_stats = {}
            curr_hour = datetime.now().hour
            hour_vals = [p["val"] for p in data_points if p["hour"] == curr_hour]
            
            if hour_vals:
                hourly_meta = {
                    "avg": float(np.mean(hour_vals)),
                    "max": float(np.max(hour_vals)),
                    "med": float(np.median(hour_vals)),
                    "count": len(hour_vals)
                }
            else:
                hourly_meta = {"avg": 0, "max": 0, "med": 0, "count": 0}
            
            # 3. Predicción GLM (Ponderación Simple)
            # Si el promedio de la hora es > 3.0, la probabilidad de un "salto" es mayor.
            glm_pred = float(np.mean([p["val"] for p in data_points[-10:]]))
            
            analysis = {
                "transitions": transitions,
                "current_hour_stats": hourly_meta,
                "recommended_threshold": 1.5 if hourly_meta["avg"] < 2.5 else 2.0,
                "status": "GLM ANALYZER ACTIVE"
            }
            
            with open(GLM_OUTPUT, "w") as gf:
                json.dump(analysis, gf, indent=4)
                
    except Exception as e:
        print(f"Error in GLM Analyzer: {e}")

if __name__ == "__main__":
    print(" Gahenax GLM Advanced Analyzer v20.0 ACTIVE...")
    while True:
        analyze_glm_multimodal()
        time.sleep(10)
