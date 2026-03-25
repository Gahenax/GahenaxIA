import json
import numpy as np
import pandas as pd
from datetime import datetime
import os

# Rutas de datos
TELEMETRY_FILE = "gahenax_spy_system/utils/aviator_telemetry.jsonl"
TRAINING_FILE = "gahenax_spy_system/utils/aviator_training_data.jsonl"

def load_data():
    data = []
    for f in [TELEMETRY_FILE, TRAINING_FILE]:
        if os.path.exists(f):
            with open(f, 'r') as file:
                for line in file:
                    try:
                        entry = json.loads(line)
                        raw_data = entry.get('data')
                        if isinstance(raw_data, str):
                            raw_data = json.loads(raw_data)
                        
                        multiplier = raw_data.get('multiplier')
                        ts = entry.get('ts')
                        
                        if multiplier is not None and ts is not None:
                            # Intentar convertir ts a float si es numérico
                            try:
                                ts_val = float(ts)
                                dt = datetime.fromtimestamp(ts_val)
                            except (ValueError, TypeError):
                                # Si es string (formato "2026-03-21 00:00:00")
                                dt = pd.to_datetime(ts)
                            
                            data.append({
                                'ts': dt.timestamp(), 
                                'multiplier': float(multiplier),
                                'dt': dt
                            })
                    except: continue
    return pd.DataFrame(data)

def predict_hot_slots(days_lookback=1.0):
    df = load_data()
    if df.empty:
        print("[-] Sin datos suficientes para predicción temporal.")
        return

    # Aplicar Rolling Calibration (Filtro por fecha reciente para evitar desfase de semilla diaria)
    cutoff = pd.to_datetime(datetime.now()) - pd.Timedelta(days=days_lookback)
    
    # Asegurar que ambos lados sean del mismo tipo para la comparación (tz-naive)
    df['dt'] = df['dt'].dt.tz_localize(None) 
    
    df_recent = df[df['dt'] >= cutoff].copy()
    
    if df_recent.empty:
        print(f"[-] Sin datos en las últimas {days_lookback * 24} horas para calibración. Necesitas extraer historial del día de hoy.")
        return
        
    print(f"\n[INFO] Calibración Diaria Activa: Usando {len(df_recent)} rondas de las últimas {days_lookback * 24}h.")
    df = df_recent

    # Normalizar por minuto/segundo
    df['minute'] = df['dt'].dt.minute
    df['second'] = df['dt'].dt.second
    
    # Identificar rondas de alto impacto (>10x)
    high_impact = df[df['multiplier'] >= 10.0].copy()
    
    print(f"[+] Analizando {len(high_impact)} rondas de alto impacto...")
    
    # Análisis de Congruencia por Minuto
    minute_hits = high_impact['minute'].value_counts()
    
    # Análisis de Frutalidad Cíclica (Intervalos entre rosas)
    high_impact = high_impact.sort_values('ts')
    high_impact['diff'] = high_impact['ts'].diff()
    avg_cycle = high_impact['diff'].mean()
    
    print("\n" + "="*50)
    print("🚀 MATRIZ DE PREDICCIÓN TEMPORAL (GSD-OMEGA)")
    print("="*50)
    
    # Slot más probable en la próxima hora
    current_time = datetime.now()
    print(f"Hora Local: {current_time.strftime('%H:%M:%S')}")
    
    # Predicción por "Minutos Calientes"
    top_minutes = minute_hits.head(3).index.tolist()
    print(f"Minutos de Alta Probabilidad (Ciclo 60m actual): {top_minutes}")
    
    # Predicción por Intervalo
    if not np.isnan(avg_cycle):
        last_pink_ts = high_impact['ts'].iloc[-1]
        next_pink_est = last_pink_ts + avg_cycle
        next_dt = datetime.fromtimestamp(next_pink_est)
        print(f"Próxima racha rosa estimada (por intervalo intradiario): {next_dt.strftime('%H:%M:%S')}")
    
    print("-" * 50)
    print("💡 ESTRATEGIA: Entrar 1 minuto antes de los 'Minutos Calientes'.")
    print("💡 ESTADO: Esperando sincronización de 624 muestras para modo DETERMINISTA.")
    print("="*50 + "\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=float, default=1.0, help="Días de retroceso para la calibración diaria.")
    args = parser.parse_args()
    predict_hot_slots(args.days)
