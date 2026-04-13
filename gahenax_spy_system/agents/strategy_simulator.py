from .seed_auditor import SeedAuditor

class StrategySimulator:
    """
    Simulador de escenarios para maximizar ganancias mediante pre-computación de Seeds.
    """
    def __init__(self, auditor=None):
        self.auditor = auditor or SeedAuditor()

    def simulate_500_spins(self, server_seed, client_seed, start_nonce=1):
        """
        Simula 500 giros y detecta oportunidades de 'Big Win'.
        """
        history = []
        for i in range(500):
            nonce = start_nonce + i
            result = self.auditor.verify(server_seed, client_seed, nonce)
            history.append({
                "nonce": nonce,
                "number": result["result_number"]
            })
        
        return self._find_best_windows(history)

    def _find_best_windows(self, history):
        """
        Encuentra rachas de victorias (ej. > 50.0) para recomendar apuestas grandes.
        """
        recommendations = []
        for h in history:
            if h["number"] > 90.0: # High Payout Area
                recommendations.append(f"Nonce {h['nonce']}: CRITICAL WIN ({h['number']}) - Bet MAX.")
            elif h["number"] > 50.0:
                recommendations.append(f"Nonce {h['nonce']}: WIN ({h['number']}) - Bet Standard.")
        
        return {
            "total_wins": len([h for h in history if h["number"] > 49.5]),
            "big_wins": len([h for h in history if h["number"] > 90.0]),
            "map": recommendations[:10] # Top 10 para no saturar
        }

if __name__ == "__main__":
    sim = StrategySimulator()
    # Dummy run
    results = sim.simulate_500_spins("test_seed", "client_123")
    print(f"[+] Simulación completada. Victorias totales: {results['total_wins']}")
    print(f"[+] Recomendaciones: {results['map']}")
