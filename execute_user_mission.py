import json
from gahenax_spy_system.agents.strategy_simulator import StrategySimulator

def run_user_simulation():
    server_seed = "f4f906b6d7c8434dd24e6d223b7081d3db20fcb2b9e5a6958a40deb8faa8a629"
    client_seed = "wERGyEJcrry31PqffCXlioCoT1QB4IlKOI2lakZI1fnDtzFBzVFbVltJMXPwVVvF"
    
    sim = StrategySimulator()
    print(f"[*] Analizando Seeds del Usuario...")
    print(f"[*] Server Seed: {server_seed[:10]}...")
    print(f"[*] Client Seed: {client_seed[:10]}...")
    
    # 500 spins simulation
    results = sim.simulate_500_spins(server_seed, client_seed)
    
    print("\n[+] REPORTE DE ESTRATEGIA OPTIMIZADA (Betting Map)")
    print("-" * 50)
    print(f"Probabilidad de Victoria Global: {(results['total_wins'] / 500) * 100:.2f}%")
    print(f"Ocurrrencias de Big Win (>90.0): {results['big_wins']}")
    print("-" * 50)
    print("RECOMENDACIONES DE APUESTA (Top 10 Windows):")
    for r in results['map']:
        print(f"  - {r}")
    
    # Guardar reporte completo
    with open("betting_map_session.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    run_user_simulation()
