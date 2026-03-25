# Gahenax Spy System v2.0 - Pattern Analyzer
# Author: Antigravity AI
# Purpose: Statistical analysis of Aviator (Spribe) Hourly Patterns

import json
import os
from collections import defaultdict
from datetime import datetime

import sys

# Añadir el path base para importar config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from mersenne_state_recovery import MersenneRecoverer

FILES = [config.TELEMETRY_LOG, config.TRAINING_DATA]
recoverer = MersenneRecoverer()

def analyze_patterns():
    hourly_stats: dict[int, list[float]] = defaultdict(list)
    
    print("🧠 Analizando patrones horarios en los datasets...")
    
    for file_path in FILES:
        if not os.path.exists(file_path):
            print(f"⚠️ No se encontró: {file_path}")
            continue
            
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    ts = entry["ts"]
                    
                    if isinstance(ts, (int, float)):
                        dt = datetime.fromtimestamp(ts)
                    else:
                        dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                    
                    hour = dt.hour
                    
                    # Buscamos el multiplicador final
                    data = entry["data"]
                    if isinstance(data, str):
                        data_obj = json.loads(data)
                    else:
                        data_obj = data
                        
                    mult = float(data_obj.get("multiplier", 0))
                    if mult > 0:
                        hourly_stats[hour].append(mult)
                    
                    # Alimentar el motor de Mersenne v12.0
                    try:
                        raw_int = int(mult * 1000000) & 0xFFFFFFFF
                        if recoverer.submit_value(raw_int):
                            pred = recoverer.predict_next()
                            if pred:
                                print(f"🔮 PREDICCIÓN ALGEBRAICA (Mersenne): Prox mult ~ {pred % 5:.2f}x")
                    except:
                        pass
                except Exception as e:
                    # print(f"Error parsing line: {e}")
                    continue

    if not hourly_stats:
        print("⚠️ No hay suficientes datos para extraer patrones aún.")
        return

    print("\n" + "="*60)
    print(f"{'HORA':<10} | {'ROUNDS':<10} | {'AVG MULT':<10} | {'MAX MULT':<10} | {'CRASH %':<10}")
    print("-" * 60)

    for hour in sorted(hourly_stats.keys()):
        results = hourly_stats[hour]
        count = len(results)
        avg = sum(results) / count
        mx = max(results)
        crashes = len([r for r in results if r < 1.10])
        crash_p = (crashes / count) * 100
        
        # Heurística de Patrón
        pattern_type = "🔥 CALIENTE" if avg > 2.0 else "❄️ FRÍO"
        if mx > 50: pattern_type += " 🌋 BURST"
        
        print(f"{hour:02d}:00      | {count:<10} | {avg:<10.2f} | {mx:<10.2f} | {crash_p:<9.1f}% -> {pattern_type}")

    print("="*60 + "\n")

if __name__ == "__main__":
    analyze_patterns()
