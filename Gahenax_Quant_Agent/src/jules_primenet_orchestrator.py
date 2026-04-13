import asyncio
import logging
from .primenet_v5_client import PrimeNetV5Client
from .config import config

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger("JulesOrchestrator")

class JulesPrimenetOrchestrator:
    """
    Orquestador para el laboratorio Jules que consume la API de PrimeNet.
    """
    
    def __init__(self):
        self.prime_client = PrimeNetV5Client(user_id="Gahenax_Jules")
        
    async def run_mission_burst(self):
        """
        Ejecuta una ráfaga de asignaciones enfocada en la 'Zona Fría' (81M).
        """
        logger.info("Iniciando Misión: Asalto a la Zona Fría (81M - 82.5M)")
        
        # 1. Registrar el nodo (Update Computer)
        if not await self.prime_client.update_computer_info():
            logger.error("No se pudo registrar en PrimeNet. Abortando.")
            return

        # 2. Solicitar asignación (Get Assignment)
        assignment = await self.prime_client.get_assignment(work_type=101) # Double-Check
        
        if assignment:
            exponent = assignment.get("n")
            key = assignment.get("k")
            logger.info(f"OBJETIVO ADQUIRIDO: Exponente M({exponent})")
            
            # 3. Generar el archivo .condor para Jules (Mock)
            condor_script = self._generate_condor_script(exponent, key)
            logger.info(f"Archivo .condor generado para Exponente {exponent}.")
            
            # 4. Despachar a Jules (HTCondor Submit)
            logger.info("Despachando tarea a los drones Katsina (Simulado).")
            # print(condor_script)
        else:
            logger.warning("No se obtuvieron asignaciones oficiales.")

    def _generate_condor_script(self, exponent: str, key: str) -> str:
        return f"""
# Jules HTCondor Submit File - Mersenne Mission
executable     = run_prime_test.sh
arguments      = --exponent {exponent} --key {key} --nodes 4
output         = logs/prime_{exponent}.out
error          = logs/prime_{exponent}.err
log            = logs/prime_{exponent}.log
request_cpus   = 4
request_memory = 16GB
queue 1
"""

if __name__ == "__main__":
    orchestrator = JulesPrimenetOrchestrator()
    asyncio.run(orchestrator.run_mission_burst())
