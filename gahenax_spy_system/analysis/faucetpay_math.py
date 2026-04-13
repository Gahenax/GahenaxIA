import hmac
import hashlib

def calculate_faucetpay_roll(server_seed, client_seed, nonce):
    """
    Official FaucetPay Dice Provably Fair Algorithm
    1. HMAC_SHA256(server_seed, client_seed + "-" + nonce)
    2. Hex to Number (first 2.5 bytes)
    3. Roll = (val % 10000) / 100
    """
    message = f"{client_seed}-{nonce}".encode()
    hash_obj = hmac.new(server_seed.encode(), message, hashlib.sha256)
    hash_res = hash_obj.hexdigest()
    
    # Try the first 5 characters (up to 999,999)
    # FaucetPay uses the first 5 chars, if result is > 999,999 it takes next 5.
    # But since 16^5 = 1,048,576, we usually stay within limits.
    index = 0
    val = int(hash_res[index:index+5], 16)
    while val >= 1000000 and index < 60:
        index += 5
        val = int(hash_res[index:index+5], 16)
        
    roll = (val % 10000) / 100
    return roll

# User-Provided Data (Previous Seed)
SERVER_SEED = "65e0c8d56fe22b36574f0a57e48d5d93775d241f3a746dde87e949abef9cd2a6"
CLIENT_SEED = "rs8GnZl6HxhBcbYeRitaLkmiGA1TNOkxhYuwkYzDZiwi3rsnFdzdnI7KpjksuHTm"

print(f"--- GAHENAX DETERMINISTIC PREDICTOR ---")
print(f"Server Seed: {SERVER_SEED}")
print(f"Client Seed: {CLIENT_SEED}")
print("-" * 40)

for n in range(1, 11):
    roll = calculate_faucetpay_roll(SERVER_SEED, CLIENT_SEED, n)
    print(f"Nonce {n:4} | Result: {roll:5.2f}")
