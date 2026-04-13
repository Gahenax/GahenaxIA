import json
import pandas as pd
from datetime import datetime
import os

TELEMETRY_FILE = "gahenax_spy_system/utils/aviator_telemetry.jsonl"
TRAINING_FILE = "gahenax_spy_system/utils/aviator_training_data.jsonl"

def load_data(days_lookback=1.0):
    data = []
    for f in [TELEMETRY_FILE, TRAINING_FILE]:
        if os.path.exists(f):
            with open(f, 'r') as file:
                for line in file:
                    try:
                        entry = json.loads(line)
                        raw = entry.get('data')
                        if isinstance(raw, str):
                            raw = json.loads(raw)
                        
                        mult = raw.get('multiplier')
                        ts = entry.get('ts')
                        if mult is not None and ts is not None:
                            try:
                                ts_val = float(ts)
                                dt = datetime.fromtimestamp(ts_val)
                            except:
                                dt = pd.to_datetime(ts)
                            data.append({'ts': dt.timestamp(), 'multiplier': float(mult), 'dt': dt})
                    except: pass
    
    df = pd.DataFrame(data)
    if not df.empty:
        cutoff = pd.to_datetime(datetime.now()) - pd.Timedelta(days=days_lookback)
        df['dt'] = df['dt'].dt.tz_localize(None)
        df = df[df['dt'] >= cutoff].copy()
        df = df.sort_values('ts').reset_index(drop=True)
    return df

def find_pre_pink_patterns(lookback=5):
    df = load_data()
    if df.empty:
        print("[-] No hay datos recientes.")
        return

    pinks = df[df['multiplier'] >= 10.0]
    print("\n" + "="*60)
    print(" RECONOCIMIENTO DE FIRMAS PRE-PINK (HOY)")
    print("="*60)
    print(f"Total de premios >10x detectados en las últimas 24h: {len(pinks)}\n")

    for idx, row in pinks.iterrows():
        # Get preceding rounds
        start_idx = max(0, idx - lookback)
        preceding = df.iloc[start_idx:idx]
        
        seq = [f"{m:.2f}x" for m in preceding['multiplier']]
        time_str = row['dt'].strftime('%H:%M:%S')
        
        print(f" PINK [{time_str}] | Premio: {row['multiplier']:.2f}x")
        print(f"   Secuencia previa ({len(seq)} rondas): {' -> '.join(seq)}")
        
        # Clasificador básico
        mults = preceding['multiplier'].tolist()
        if len(mults) >= 3 and all(m < 1.25 for m in mults[-3:]):
            print("   ↳ FIRMA DETECTADA: Poda Constante (3+ Instacrashes)")
        elif len(mults) >= 3 and any(m > 2.0 for m in mults[-3:-1]) and mults[-1] < 1.15:
            print("   ↳ FIRMA DETECTADA: Bait & Hook (Cebo alto + Trampa)")
        elif len(mults) >= 3 and sum(m < 1.5 for m in mults) >= 3:
            print("   ↳ FIRMA DETECTADA: Agotamiento Rítmico")
        else:
            print("   ↳ FIRMA DETECTADA: Orgánica / Mixta")
        print("-" * 60)

if __name__ == "__main__":
    find_pre_pink_patterns()
