import json
from gahenax_spy_system.agents.seed_auditor import SeedAuditor

def calculate_mass_gap():
    server_seed = "14eb9b16d909b73edbd7cafdac1a579e505d5186c4d404bd62f7a6cb1c9fb355"
    client_seed = "u5b0wmZEbFBVrYrSvLGEi9IHfIvSBAfdXcf6daiCEnHOAzrK1ZYMrjYTqi724yE4"
    
    auditor = SeedAuditor()
    results = []
    for nonce in range(1, 501):
        res = auditor.verify(server_seed, client_seed, nonce)
        results.append(res["result_number"])
    
    # Encontrar el 'Gap' (secuencia máxima de pérdidas < 49.5)
    max_gap = 0
    current_gap = 0
    gap_start = 0
    best_gap_coords = (0, 0)
    
    for i, res in enumerate(results):
        if res < 49.5:
            current_gap += 1
        else:
            if current_gap > max_gap:
                max_gap = current_gap
                best_gap_coords = (i - current_gap + 1, i)
            current_gap = 0
            
    # Calcular el 'Mass Gap' (Eenergía de pérdida acumulada en el peor escenario)
    # Si apostamos 0.0001 por tiro, cuánta masa perdemos en el peor gap?
    mass_loss = max_gap * 0.0001
    
    print(f"[!] MASS GAP DETECTADO: {max_gap} giros de pérdida consecutiva.")
    print(f"[*] Coordenadas del Vacío: Nonce {best_gap_coords[0]} hasta {best_gap_coords[1]}")
    print(f"[*] Energía de Pérdida (Mass Loss): {mass_loss:.6f} USDT")
    
    if mass_loss > 0.10: # Si perdemos más del 5% del pool en un solo gap
        print("[WARNING] El sistema presenta un Mass Gap inestable. Se recomienda SKIP total en estas zonas.")

if __name__ == "__main__":
    calculate_mass_gap()
