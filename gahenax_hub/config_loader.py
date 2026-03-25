import json
import os

# Base configuration for Cabal AI v1
DEFAULT_CONFIG = {
    "engine": {
        "name": "TreeOfLifeEngine",
        "version": "1.0.0-operativa",
        "audit_mode": True
    },
    "policies": {
        "forbidden_keywords": ["unsafe", "malware", "leak"],
        "min_confidence_threshold": 0.6
    },
    "memory": {
        "type": "json_file",
        "path": "gahenax_hub/sessions/episode_memory.json"
    }
}

def load_config():
    config_path = "gahenax_hub/config/cabal_v1.json"
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)
    return DEFAULT_CONFIG

if __name__ == "__main__":
    os.makedirs("gahenax_hub/config", exist_ok=True)
    with open("gahenax_hub/config/cabal_v1.json", "w") as f:
        json.dump(DEFAULT_CONFIG, f, indent=4)
    print("Config created at gahenax_hub/config/cabal_v1.json")
