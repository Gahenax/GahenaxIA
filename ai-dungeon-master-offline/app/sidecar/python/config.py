import os
from pathlib import Path

# Simple parser for .env files to avoid installing python-dotenv
def load_env_file():
    base_dir = Path(__file__).resolve().parent
    env_path = base_dir / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    if key not in os.environ:
                        os.environ[key] = val.strip()

# Load environment
load_env_file()

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "ollama")  # "ollama" or "odysseus" (openai_compatible)
LLM_HOST = os.environ.get("LLM_HOST", "http://127.0.0.1:11434")
LLM_MODEL = os.environ.get("LLM_MODEL", "qwen2.5:1.5b")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
