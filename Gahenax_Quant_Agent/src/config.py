import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Módulo de configuración centralizado para Gahenax Quant Agent."""
    
    # Venice AI Configuration
    VENICE_DISTINCT_ID = os.getenv("VENICE_DISTINCT_ID", "user_anon_gahenax")
    VENICE_API_URL = "https://outerface.venice.ai/api/inference/chat"
    VENICE_VERSION = os.getenv("VENICE_VERSION", "interface@20260326.180849+b2d53b2")
    
    # Binance Configuration
    BINANCE_WS_URL = "wss://festream.saasexch.com:8443/nats-fe"
    
    # Trading Parameters
    DEFAULT_SYMBOL = "BTCUSDT"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

config = Config()
