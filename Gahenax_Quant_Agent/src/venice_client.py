import json
import httpx
import asyncio
import logging
from .config import config

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger("VeniceBridge")

class VeniceClient:
    """Cliente asíncrono para interactuar con la inferencia de Venice.ai."""
    
    def __init__(self):
        self.headers = {
            "Accept": "text/event-stream",
            "Content-Type": "application/json",
            "x-venice-distinct-id": config.VENICE_DISTINCT_ID,
            "x-venice-version": config.VENICE_VERSION,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    async def get_trading_signal(self, market_data: dict) -> str:
        """
        Envía datos del mercado a Venice y devuelve una señal de trading.
        """
        prompt = (
            f"Actúa como un experto en Trading Algorítmico de Gahenax. "
            f"Analiza los siguientes datos de {market_data['s']}: "
            f"Precio: {market_data['c']}, Cambio 24h: {market_data['P']}%. "
            f"Responde solo con: BUY, SELL o HOLD y una breve justificación técnica."
        )
        
        payload = {
            "modelId": "zai-org-glm-4.6",
            "prompt": [{"content": prompt, "role": "user"}],
            "conversationType": "text",
            "requestId": "gahenax_" + str(int(asyncio.get_event_loop().time())),
            "userId": config.VENICE_DISTINCT_ID,
            "webEnabled": True,
            "webScrapeEnabled": False,
            "simpleMode": True
        }

        full_response = ""
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("POST", config.VENICE_API_URL, json=payload, headers=self.headers) as response:
                if response.status_code != 200:
                    logger.error(f"Error en API de Venice: {response.status_code}")
                    return "ERROR"

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        try:
                            data = json.loads(data_str)
                            if data.get("kind") == "content":
                                content = data.get("content", "")
                                full_response += content
                                # logger.debug(f"Chunk recibido: {content}")
                        except json.JSONDecodeError:
                            continue
        
        return full_response.strip()

if __name__ == "__main__":
    # Test rápido de conexión
    async def test():
        client = VeniceClient()
        mock_data = {"s": "BTCUSDT", "c": "68412.06", "P": "-3.51"}
        print(f"Solicitando señal para {mock_data['s']}...")
        signal = await client.get_trading_signal(mock_data)
        print(f"Respuesta de Venice AI:\n{signal}")

    asyncio.run(test())
