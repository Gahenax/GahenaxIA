import requests
from typing import Dict, Any, List, Optional

import threading

# Preferred model priority list (first available wins)
# magicworld-gm: custom model with DM system prompt baked in (best quality)
# qwen2.5:1.5b / llama3.2:3b: fallbacks
PREFERRED_MODELS = [
    "magicworld-gm",          # Custom GM model — best for narrative
    "magicworld-gm:latest",
    "llama3.2:3b",            # Good quality, 2GB
    "llama3.2:3b:latest",
    "qwen2.5:1.5b",           # Fast fallback
    "qwen2.5:latest",
    "llama3.2:1b",            # Minimal fallback
    "llama3.2:latest",
]

class OllamaClient:
    def __init__(self, host: Optional[str] = None, default_model: Optional[str] = None):
        from config import LLM_PROVIDER, LLM_HOST, LLM_MODEL, LLM_API_KEY
        self.provider = LLM_PROVIDER
        self.host = host or LLM_HOST
        self.default_model = default_model or LLM_MODEL
        self.target_model = self.default_model
        self.api_key = LLM_API_KEY
        self.pulling_in_progress = False
        
        if self.provider == "ollama":
            self._auto_detect_model()
        else:
            print(f"[LLM Client] Interface running under provider '{self.provider}' pointing to '{self.host}' with model '{self.default_model}'")

    def _auto_detect_model(self):
        try:
            res = requests.get(f"{self.host}/api/tags", timeout=2.0)
            if res.status_code == 200:
                models = res.json().get("models", [])
                if models:
                    model_names = [m.get("name") for m in models]
                    # Pick best model from priority list
                    selected = None
                    for preferred in PREFERRED_MODELS:
                        for name in model_names:
                            if name == preferred or name.startswith(preferred.split(":")[0] + ":"):
                                selected = name
                                break
                        if selected:
                            break
                    
                    if selected:
                        self.default_model = selected
                        print(f"[Ollama] ✅ Active model: '{self.default_model}'")
                    else:
                        # Absolute fallback: use whatever is installed
                        self.default_model = model_names[0]
                        print(f"[Ollama] ⚠️ No preferred model found. Using: '{self.default_model}'")
        except Exception as e:
            print(f"[Ollama] Auto-detect models failed: {e}")
            pass

    def _pull_target_model(self):
        print(f"[Ollama] Background pulling target model '{self.target_model}'...")
        try:
            url = f"{self.host}/api/pull"
            # Non-streaming call, this blocks until download completes, so we run in background thread
            res = requests.post(url, json={"name": self.target_model, "stream": False}, timeout=600.0)
            if res.status_code == 200:
                self.default_model = self.target_model
                print(f"[Ollama] Target model '{self.target_model}' downloaded successfully and set as default.")
            else:
                print(f"[Ollama] Pull failed with status: {res.status_code}")
        except Exception as e:
            print(f"[Ollama] Error pulling target model: {e}")
        finally:
            self.pulling_in_progress = False

    def is_available(self) -> bool:
        """Checks if the local Ollama service is up and running."""
        if self.provider != "ollama":
            try:
                # Ping base url or models list
                res = requests.get(self.host, timeout=2.0)
                return True
            except Exception:
                return False
        try:
            res = requests.get(f"{self.host}/api/tags", timeout=2.0)
            return res.status_code == 200
        except Exception:
            return False

    def generate_chat(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
        """Sends chat messages to Ollama/Odysseus and returns the narrative response text."""
        model_name = model or self.default_model
        
        # Option A: Connect via OpenAI-compatible endpoint (Odysseus)
        if self.provider in ("odysseus", "openai_compatible"):
            url = f"{self.host.rstrip('/')}/chat/completions"
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
                
            payload = {
                "model": model_name,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 512
            }
            
            try:
                res = requests.post(url, json=payload, headers=headers, timeout=60.0)
                if res.status_code == 200:
                    data = res.json()
                    choices = data.get("choices", [])
                    if choices:
                        return choices[0].get("message", {}).get("content", "").strip()
                    return ""
                else:
                    return f"[Error de conexión con Odysseus: {res.status_code} - {res.text}]"
            except Exception as e:
                print(f"[Odysseus] Connection error: {e}.")
                return "El Dungeon Master necesita un momento para recomponerse... (Odysseus no disponible)"

        # Option B: Direct Ollama endpoint
        url = f"{self.host}/api/chat"
        payload = {
            "model": model_name,
            "messages": messages,
            "stream": False,
            "keep_alive": "10m",
            "options": {
                "temperature": 0.7,      # Lower = more focused/coherent
                "top_p": 0.9,
                "repeat_penalty": 1.1,   # Avoid repetition
                "num_predict": 512,      # Max tokens in response
            }
        }
        
        try:
            res = requests.post(url, json=payload, timeout=60.0)
            if res.status_code == 200:
                data = res.json()
                return data.get("message", {}).get("content", "").strip()
            else:
                return f"[Error de conexión con el modelo: {res.status_code}]"
        except Exception as e:
            print(f"[Ollama] Connection error: {e}.")
            return "El Dungeon Master necesita un momento para recomponerse... (modelo no disponible)"

    def generate_embeddings(self, text: str) -> List[float]:
        """Generates embedding vector for a given text block."""
        if self.provider in ("odysseus", "openai_compatible"):
            url = f"{self.host.rstrip('/')}/embeddings"
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            payload = {
                "model": self.default_model,
                "input": text
            }
            try:
                res = requests.post(url, json=payload, headers=headers, timeout=20.0)
                if res.status_code == 200:
                    return res.json().get("data", [{}])[0].get("embedding", [])
            except Exception as e:
                print(f"[LLM Client] Failed to generate OpenAI embeddings: {e}")
                return []
        else:
            url = f"{self.host}/api/embeddings"
            payload = {
                "model": self.default_model,
                "prompt": text,
                "keep_alive": "10m"
            }
            try:
                res = requests.post(url, json=payload, timeout=20.0)
                if res.status_code == 200:
                    return res.json().get("embedding", [])
            except Exception as e:
                print(f"[LLM Client] Failed to generate Ollama embeddings: {e}")
                return []
        return []

    def classify_intent(self, user_text: str, model: Optional[str] = None) -> str:
        """
        Classifies the player's intent using structured prompting.
        Returns one of: 'combat_action', 'social_action', 'exploration_action', 'inventory_action', 'meta_question'
        """
        model_name = model or self.default_model
        system_prompt = (
            "Eres un clasificador de intenciones experto de D&D 5e. "
            "Clasifica el mensaje del jugador en una sola palabra clave de entre las siguientes:\n"
            "- combat_action: Si ataca, se defiende o inicia pelea.\n"
            "- social_action: Si habla con PNJs, intimida, persuade o engaña.\n"
            "- exploration_action: Si investiga una habitación, abre puertas, busca trampas.\n"
            "- inventory_action: Si equipa objetos, consume pociones o revisa inventario.\n"
            "- meta_question: Si pregunta sobre reglas, historia u opciones de juego.\n"
            "Responde ÚNICAMENTE con la palabra clave elegida, nada más."
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Mensaje del jugador: '{user_text}'"}
        ]
        
        classification = self.generate_chat(messages, model=model_name)
        classification_clean = classification.lower().strip()
        
        valid_intents = ["combat_action", "social_action", "exploration_action", "inventory_action", "meta_question"]
        for vi in valid_intents:
            if vi in classification_clean:
                return vi
                
        # Simple heuristic fallback if model goes off-script
        user_lower = user_text.lower()
        if any(w in user_lower for w in ["ataco", "golpeo", "lanzo", "espada", "arco", "iniciativa"]):
            return "combat_action"
        elif any(w in user_lower for w in ["hablo", "pregunto", "digo", "grito"]):
            return "social_action"
        elif any(w in user_lower for w in ["miro", "busco", "investigo", "abro", "puerta"]):
            return "exploration_action"
        elif any(w in user_lower for w in ["equipo", "tomo", "pocion", "oro", "inventario"]):
            return "inventory_action"
            
        return "meta_question"
