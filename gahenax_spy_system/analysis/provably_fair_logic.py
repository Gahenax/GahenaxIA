import hashlib
import hmac
import math

def calculate_multiplier(server_seed, client_seeds_combined):
    """
    Calcula el multiplicador de Aviator usando la lógica Provably Fair.
    
    server_seed: El seed del servidor (hex o string).
    client_seeds_combined: La concatenación de los seeds de los primeros 3 jugadores.
    """
    # Spribe usa SHA-512 para mayor entropía en la combinación
    hash_object = hmac.new(
        server_seed.encode('utf-8'),
        client_seeds_combined.encode('utf-8'),
        hashlib.sha512
    )
    full_hash = hash_object.hexdigest()
    
    # Tomar los primeros 13 caracteres (52 bits) para la precisión decimal
    hex_precision = full_hash[:13]
    val = int(hex_precision, 16)
    
    # Fórmula estandarizada de Crash (99% RTP factor)
    # multiplier = (2^52) / (2^52 - val) * 0.99
    # Limitado a 2 decimales y mínimo 1.00
    m_pow = math.pow(2, 52)
    if m_pow == val:
        return 1000000.0 # Bote máximo teórico si el hash es exactamente el límite
        
    multiplier = (m_pow / (m_pow - val)) * 0.99
    
    # Redondear a 2 decimales y asegurar el piso de 1.0
    final_mult = math.floor(multiplier * 100) / 100
    return max(1.0, final_mult)

def verify_round(server_seed_hashed, server_seed_plain, client_seeds, result_observed):
    """
    Verifica si una ronda pasada fue justa y si coincide con nuestro motor.
    """
    # 1. Verificar integridad del server seed
    computed_hash = hashlib.sha256(server_seed_plain.encode('utf-8')).hexdigest()
    integrity = (computed_hash == server_seed_hashed)
    
    # 2. Calcular multiplicador teórico
    theoretical = calculate_multiplier(server_seed_plain, client_seeds)
    
    return {
        "integrity": integrity,
        "theoretical": theoretical,
        "observed": result_observed,
        "delta": abs(theoretical - result_observed)
    }

if __name__ == "__main__":
    # Test Bench (Valores ejemplo de documentación de Spribe)
    s_seed = "test_server_seed"
    c_seeds = "test_client_seeds_combined"
    print(f"🧬 Test Multiplier: {calculate_multiplier(s_seed, c_seeds)}x")
