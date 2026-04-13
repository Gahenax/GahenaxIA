from gahenax_spy_system.agents.seed_auditor import SeedAuditor

def forensic_replay():
    server_seed = "14eb9b16d909b73edbd7cafdac1a579e505d5186c4d404bd62f7a6cb1c9fb355"
    client_seed = "u5b0wmZEbFBVrYrSvLGEi9IHfIvSBAfdXcf6daiCEnHOAzrK1ZYMrjYTqi724yE4"
    
    auditor = SeedAuditor()
    print("Nonce | Result | Status (High) | Logic Target")
    print("-" * 45)
    
    wins_correct = 0
    losses_correct = 0
    
    for nonce in range(1, 151):
        res = auditor.verify(server_seed, client_seed, nonce)
        num = res["result_number"]
        
        # Umbral real de FaucetPay para "High" con 49.5% de chance es > 50.49
        actual_win = num > 50.49
        
        # Umbral usado en mi script anterior era > 49.5
        predicted_win = num > 49.5
        
        if actual_win: wins_correct += 1
        else: losses_correct += 1
        
        if actual_win != predicted_win:
            print(f"{nonce:5} | {num:6.2f} | MISMATCH! (Pred: Win, Act: Loss)")
        elif num > 90.0:
            print(f"{nonce:5} | {num:6.2f} | BIG WIN")

    print(f"\nTotal Real Wins: {wins_correct}")
    print(f"Total Real Losses: {losses_correct}")

if __name__ == "__main__":
    forensic_replay()
