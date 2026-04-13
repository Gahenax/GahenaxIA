# Gahenax Spy v17.0 - Tactical Advisor Agent
# Author: Antigravity AI
# Purpose: Real-Time Manual-Play Advisor (DSS).

import time
import json
import os
import sys

# Importar configuración y lógica de análisis
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from analysis.riemann_spectral_mapper import calculate_pair_correlation

RECOMMENDATION_FILE = os.path.join(config.BASE_DIR, "dashboard", "recommendation.json")

def generate_recommendation():
    """Calcula y guarda la recomendación basada en 50 vuelos."""
    if not os.path.exists(config.TELEMETRY_LOG):
        return
    
    try:
        with open(config.TELEMETRY_LOG, "r") as f:
            lines = f.readlines()[-50:]
            multipliers = []
            for l in lines:
                entry = json.loads(l)
                if '"multiplier":' in entry["data"]:
                    part = entry["data"].split('"multiplier":')[1].split('}')[0].split(',')[0]
                    multipliers.append(float(part))
            
            conf = 0.0
            rec = "WAIT"
            if len(multipliers) >= 50:
                variance, _ = calculate_pair_correlation(multipliers)
                conf = 1.0 - (variance / 2.0)
                conf = max(0.0, min(1.0, conf))
                if conf > 0.8: rec = "BET"
            
            with open(RECOMMENDATION_FILE, "w") as rf:
                json.dump({"confidence": conf, "recommendation": rec}, rf)
                
    except Exception as e:
        print(f"Error in Advisor: {e}")

if __name__ == "__main__":
    print(" Gahenax Tactical Advisor v17.0 Active Listening...")
    while True:
        generate_recommendation()
        time.sleep(2)
