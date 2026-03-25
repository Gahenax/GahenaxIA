import hmac
import hashlib
import sys

def calculate_roll(server_seed, client_seed, nonce):
    """
    Simula la generacion de roll de FaucetPay (Provably Fair).
    """
    message = f"{client_seed}-{nonce}".encode()
    hash_obj = hmac.new(server_seed.encode(), message, hashlib.sha512).hexdigest()
    
    # FaucetPay usa bloques de 5 caracteres hex
    index = 0
    while True:
        hex_chunk = hash_obj[index:index+5]
        val = int(hex_chunk, 16)
        if val < 1000000:
            return (val % 10000) / 100
        index += 5
        if index > 125: # Fallback de seguridad
            return 0

def run_recalc(server_seed, client_seed, start_nonce, end_nonce, chance=49.5):
    print("="*60)
    print(" RECALCULO DETERMINISTICO RNG (P-ATLAS v13.0) ")
    print("="*60)
    print(f"Server Seed: {server_seed}")
    print(f"Client Seed: {client_seed}")
    print(f"Target Chance: {chance}%")
    print("-" * 60)
    
    wins = 0
    win_list = []
    
    for n in range(start_nonce, end_nonce + 1):
        roll = calculate_roll(server_seed, client_seed, n)
        # En FaucetPay 'Under' 49.5 significa ganar si roll < 49.5
        is_win = roll < chance
        if is_win:
            wins += 1
            win_list.append(n)
        
        status = "WIN" if is_win else "LOSS"
        if n < start_nonce + 10 or n > end_nonce - 5: # No inundar la consola
            print(f"Nonce {n}: Roll {roll:.2f} -> {status}")
        elif n == start_nonce + 10:
            print("...")

    print("-" * 60)
    print(f"Resultado en {end_nonce - start_nonce + 1} tiros: {wins} victorias ({(wins/(end_nonce - start_nonce + 1))*100:.2f}%)")
    print(f"Nonces Favorables (Strike Zones): {win_list[:15]}...")
    print("="*60)

if __name__ == "__main__":
    s_seed = "jRh38OztPKReKos6gHuu7w49L2yfOhTnlAfe0Q5fny8AGNpL1fBpf0NzCZJpvSan"
    c_seed = "Rando"
    
    # Asumimos que el Nonce actual es ~1-100 si acaban de rotar
    run_recalc(s_seed, c_seed, 1, 100)
