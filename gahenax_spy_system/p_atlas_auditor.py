import sys
import json
from collections import Counter

def audit_p_atlas_manifold(sequence_str):
    """
    Analiza una racha real (W,L,L,W...) para encontrar Gaps de Riemann.
    """
    seq = sequence_str.split(',')
    streaks = []
    current_loss_streak = 0
    
    for bet in seq:
        if bet == 'L':
            current_loss_streak += 1
        else:
            if current_loss_streak > 0:
                streaks.append(current_loss_streak)
            current_loss_streak = 0
            
    stats = Counter(streaks)
    total_samples = len(seq)
    
    print("="*60)
    print(" AUDITORIA FORENSE P-ATLAS (UX DATA) ")
    print("="*60)
    print(f"Total Muestras: {total_samples}")
    print(f"Max Racha de Rojos Detectada: {max(streaks) if streaks else 0}")
    print("\n[GAPS ESPECTRALES DETECTADOS]")
    
    for s in sorted(stats.keys()):
        freq = (stats[s] / total_samples) * 100
        # Probabilidad de ganar tras S rojos
        print(f"Racha {s} rojos -> Frecuencia: {freq:.2f}%")
        
    print("\n[DIAGNOSTICO TOPOLOGICO]")
    if max(streaks or [0]) > 8:
        print("ALERTA: Manifold Hostil detectado. Pared de defensa activa (>8 rojos).")
    else:
        print("ESTADO: Manifold Estable. La casa no esta aplicando Black Swans locales.")
    print("="*60)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        audit_p_atlas_manifold(sys.argv[1])
    else:
        print("Uso: python p_atlas_auditor.py W,L,L,W...")
