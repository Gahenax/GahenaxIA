import time
import random
import uuid

def generate_uuidv7() -> str:
    """
    Genera un ID compatible con el orden temporal (UUIDv7-ish).
    Utiliza el timestamp en milisegundos como prefijo.
    """
    msecs = int(time.time() * 1000)
    # 48 bits para el tiempo (12 hex chars)
    time_hex = f"{msecs:012x}"
    # El resto es aleatoriedad pura (20 hex chars)
    random_hex = uuid.uuid4().hex[:20]
    return f"{time_hex}-{random_hex[:4]}-{random_hex[4:8]}-{random_hex[8:12]}-{random_hex[12:]}"

if __name__ == "__main__":
    print(f"UUIDv7: {generate_uuidv7()}")
