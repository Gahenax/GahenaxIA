import asyncio
import httpx
import json
from typing import Dict, Any, List
from .dice_engine import DiceEngine
from .combat_engine import CombatEngine

OLLAMA_HOST = "http://cripta-ollama:11434"
MODEL = "qwen2.5:1.5b"
CONTEXT_WINDOW = 8  # turnos a mantener en memoria

SYSTEM_PROMPT = """Eres el Dungeon Master de CRIPTA, una mazmorra oscura de D&D 5.5.
Narra en español con tono sombrío y atmosférico. Sé conciso: 2-4 oraciones por turno.
Mantén coherencia con los eventos anteriores. Nunca repitas la misma descripción.
Incluye consecuencias mecánicas cuando aplique (golpes, daño, efectos)."""

class Orchestrator:
    def __init__(self, database):
        self.db = database
        self.dice_engine = DiceEngine()
        self.combat_engine = CombatEngine(self.dice_engine)
        self._conversation: List[Dict[str, str]] = []

    def _add_to_context(self, role: str, content: str):
        self._conversation.append({"role": role, "content": content})
        if len(self._conversation) > CONTEXT_WINDOW * 2:
            self._conversation = self._conversation[-(CONTEXT_WINDOW * 2):]

    async def process_action(self, action) -> Dict[str, Any]:
        print(f"🎮 {action.action_type}: {action.description}")
        try:
            if action.action_type.value.upper() == "COMBAT":
                result = await self._handle_combat(action)
            else:
                result = {"action_type": action.action_type.value, "message": "Action recorded"}

            narrative = await self._generate_narrative(action, result)

            self.db.log_action("campaign_1", {
                "character_id": action.character_id,
                "action_type": action.action_type,
                "description": action.description,
                "result": str(result)
            })

            return {
                "message": "Action processed",
                "state": result,
                "narrative": narrative,
                "audio_url": None
            }
        except Exception as e:
            print(f"❌ {e}")
            return {
                "message": "Error",
                "state": {},
                "narrative": "La mazmorra permanece en silencio...",
                "audio_url": None
            }

    async def _handle_combat(self, action) -> Dict[str, Any]:
        roll = self.dice_engine.roll("1d20+2")
        hit = roll['total'] >= 12
        damage = self.dice_engine.roll("1d8+2")['total'] if hit else 0
        return {
            "action_type": "attack",
            "roll": roll['total'],
            "hit": hit,
            "damage": damage
        }

    async def _generate_narrative(self, action, result) -> str:
        hit_text = ""
        if result.get("action_type") == "attack":
            if result.get("hit"):
                hit_text = f"El ataque conecta causando {result.get('damage')} de daño (tirada: {result.get('roll')})."
            else:
                hit_text = f"El ataque falla (tirada: {result.get('roll')})."

        user_msg = f"Acción: {action.description}\nResultado mecánico: {hit_text or str(result)}"
        self._add_to_context("user", user_msg)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self._conversation

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.post(
                    f"{OLLAMA_HOST}/api/chat",
                    json={
                        "model": MODEL,
                        "messages": messages,
                        "stream": False,
                        "options": {"temperature": 0.85, "num_predict": 200}
                    }
                )
                if resp.status_code == 200:
                    narrative = resp.json().get("message", {}).get("content", "").strip()
                    if narrative:
                        self._add_to_context("assistant", narrative)
                        return narrative
        except Exception as e:
            print(f" Ollama: {e}")

        return "La mazmorra permanece en silencio..."
