import httpx
import logging
import uuid
import asyncio
from typing import Dict, Optional
from .config import config

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger("PrimeNetV5")

class PrimeNetV5Client:
    """
    Cliente para la API v5.0 de PrimeNet (Mersenne.org).
    Basado en la especificación v0.97(c) de Kurowski/Woltman.
    """
    
    BASE_URL = "https://v5.mersenne.org/v5/"
    PROJECT = "GIMPS"
    VERSION = "0.97"

    def __init__(self, user_id: Optional[str] = None):
        self.user_id = user_id or config.VENICE_DISTINCT_ID # Reusando ID por ahora
        self.guid = uuid.uuid4().hex.upper()
        self.hardware_hash = uuid.uuid4().hex.upper()
        logger.info(f"PrimeNet Client inicializado. GUID: {self.guid}")

    def _parse_response(self, text: str) -> Dict[str, str]:
        """Parsea la respuesta tipo token-valor de PrimeNet."""
        lines = text.strip().split("\n")
        result = {}
        for line in lines:
            if "=" in line and line != "=END=":
                key, value = line.split("=", 1)
                result[key.strip()] = value.strip()
        return result

    async def update_computer_info(self) -> bool:
        """
        Transacción 'uc': Registra el nodo en PrimeNet.
        Debe llamarse antes de solicitar asignaciones.
        """
        params = {
            "px": self.PROJECT,
            "v": self.VERSION,
            "t": "uc",
            "g": self.guid,
            "hg": self.hardware_hash,
            "wg": self.hardware_hash, # Simulando Windows GUID
            "a": "Linux, MPrime, v30.19, build 20",
            "c": "Intel, Xeon-Katsina",
            "f": "RDTSC,CMOV,MMX,SSE,SSE2,AVX,AVX2",
            "L1": 32,
            "L2": 1024,
            "np": 8, # 8 cores por drone
            "hp": 1,
            "h": 24,
            "m": 16384,
            "s": 3200,
            "u": self.user_id,
            "cn": f"Jules_Node_{str(self.guid)[:4]}",
            "ss": "",
            "sh": ""
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.BASE_URL, params=params)
                data = self._parse_response(response.text)
                
                if data.get("pnErrorResult") == "0":
                    logger.info("Registro en PrimeNet exitoso (UC).")
                    return True
                else:
                    logger.error(f"Error en UC: {data.get('pnErrorDetail')}")
                    return False
            except Exception as e:
                logger.error(f"Fallo en conexión UC: {e}")
                return False

    async def get_assignment(self, work_type: int = 101) -> Optional[Dict[str, str]]:
        """
        Transacción 'ga': Solicita una asignación de trabajo (Double-Check por defecto).
        """
        params = {
            "px": self.PROJECT,
            "v": self.VERSION,
            "t": "ga",
            "g": self.guid,
            "c": 0, # Primera CPU
            "ss": "",
            "sh": ""
        }
        
        # Primero configuramos la preferencia (po) para asegurar el work_type
        # (Opcional pero recomendado por la especificación)
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.BASE_URL, params=params)
                data = self._parse_response(response.text)
                
                if data.get("pnErrorResult") == "0":
                    logger.info(f"Asignación recibida (GA): Exponente {data.get('n')}")
                    return data
                elif data.get("pnErrorResult") == "40":
                    logger.warning("No hay asignaciones disponibles (GA).")
                    return None
                else:
                    logger.error(f"Error en GA: {data.get('pnErrorDetail')}")
                    return None
            except Exception as e:
                logger.error(f"Fallo en conexión GA: {e}")
                return None

if __name__ == "__main__":
    async def main():
        client = PrimeNetV5Client(user_id="Gahenax_Alpha")
        if await client.update_computer_info():
            assignment = await client.get_assignment()
            if assignment:
                print(f"TRABAJO ASIGNADO: M({assignment.get('n')})")
                print(f"CLAVE DE ASIGNACIÓN: {assignment.get('k')}")

    asyncio.run(main())
