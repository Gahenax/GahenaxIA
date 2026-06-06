import httpx
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from .dice_engine import DiceEngine
from .combat_engine import CombatEngine
from .game_state import GameStateManager

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://cripta-ollama:11434")
MODEL = "qwen2.5:3b"
CONTEXT_WINDOW = 10

SYSTEM_PROMPT = """Eres el Dungeon Master de CRIPTA. Narra en español, segunda persona, tiempo presente.
Tono: oscuro, brutal, atmosférico. Sin humor. Máximo 4 oraciones.
Usa el estado mecánico para anclar la narrativa — menciona HP, dados, nombres de enemigos cuando sea relevante.
Nunca repitas descripciones. Cada turno debe avanzar la situación."""

class Orchestrator:
    def __init__(self, database):
        self.db = database
        self.dice_engine = DiceEngine()
        self.combat_engine = CombatEngine()
        self.game_state = GameStateManager()
        self._conversation: List[Dict[str, str]] = self.db.get_recent_context("campaign_1", CONTEXT_WINDOW)
        self._world_context = self._load_world_context()

    def _load_world_context(self) -> str:
        path = Path(__file__).parent.parent / "world_context.txt"
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    def _build_system_prompt(self) -> str:
        parts = [SYSTEM_PROMPT]
        if self._world_context:
            parts.append(f"\n--- CONTEXTO DEL MUNDO ---\n{self._world_context}")
        parts.append(f"\n--- ESTADO ACTUAL ---\n{self.game_state.to_prompt_context()}")
        return "\n".join(parts)

    def _add_to_context(self, role: str, content: str):
        self._conversation.append({"role": role, "content": content})
        if len(self._conversation) > CONTEXT_WINDOW * 2:
            self._conversation = self._conversation[-(CONTEXT_WINDOW * 2):]

    def _persist_turn(self, campaign_id: str, role: str, description: str, result: str = ""):
        self.db.log_action(campaign_id, {
            "character_id": role,
            "action_type": role,
            "description": description,
            "result": result
        })

    async def process_action(self, action) -> Dict[str, Any]:
        print(f"🎮 [{self.game_state.turn}] {action.action_type}: {action.description}")

        try:
            action_type = action.action_type.value.upper()

            if action_type == "COMBAT":
                result = await self._handle_combat(action)
            elif action_type == "EXPLORATION":
                result = self._handle_exploration(action)
            elif action_type == "REST":
                result = self._handle_rest(action)
            else:
                result = {"action_type": action_type, "message": "Acción registrada"}

            narrative = await self._generate_narrative(action, result)
            self.game_state.turn += 1

            self._persist_turn("campaign_1", "player", action.description, str(result))
            self._persist_turn("campaign_1", "narrator", narrative)

            return {
                "message": "Action processed",
                "state": {**result, **self.game_state.to_api_state()},
                "narrative": narrative,
                "audio_url": None
            }

        except Exception as e:
            print(f"❌ {e}")
            return {
                "message": "Error",
                "state": self.game_state.to_api_state(),
                "narrative": "La mazmorra permanece en silencio...",
                "audio_url": None
            }

    async def _handle_combat(self, action) -> Dict[str, Any]:
        enemy_entry = self.game_state.get_first_active_enemy()

        if not enemy_entry:
            return {"action_type": "combat", "message": "No hay enemigos en esta sala"}

        enemy_id, enemy = enemy_entry

        # Ataque del jugador
        attack_roll = self.dice_engine.roll("1d20+3")
        player_hit = attack_roll["total"] >= enemy["ac"]
        player_damage = 0
        enemy_defeated = False

        if player_hit:
            dmg_roll = self.dice_engine.roll("1d8+2")
            player_damage = dmg_roll["total"]
            enemy_defeated = self.game_state.apply_damage_to_enemy(enemy_id, player_damage)

        # Contraataque del enemigo si sigue vivo
        enemy_damage = 0
        enemy_hit = False
        if not enemy_defeated:
            enemy_attack = self.dice_engine.roll(f"1d20+{enemy['attack_bonus']}")
            enemy_hit = enemy_attack["total"] >= 12  # AC del jugador
            if enemy_hit:
                enemy_dmg_roll = self.dice_engine.roll(enemy["damage"])
                enemy_damage = enemy_dmg_roll["total"]

        return {
            "action_type": "combat",
            "enemy_name": enemy["name"],
            "enemy_description": enemy["description"],
            "player_attack_roll": attack_roll["total"],
            "player_hit": player_hit,
            "player_damage": player_damage,
            "enemy_hp_remaining": self.game_state.enemies[enemy_id]["hp"],
            "enemy_defeated": enemy_defeated,
            "enemy_counterattack": enemy_hit,
            "enemy_damage_to_player": enemy_damage,
            "xp_gained": enemy["xp"] if enemy_defeated else 0
        }

    def _handle_exploration(self, action) -> Dict[str, Any]:
        room = self.game_state.current_room_id
        active_enemies = self.game_state.get_active_enemies()
        return {
            "action_type": "exploration",
            "room": room,
            "enemies_present": len(active_enemies) > 0,
            "exits": self.game_state.to_api_state()["exits"]
        }

    def _handle_rest(self, action) -> Dict[str, Any]:
        active_enemies = self.game_state.get_active_enemies()
        if active_enemies:
            return {
                "action_type": "rest",
                "success": False,
                "message": "No puedes descansar con enemigos presentes"
            }
        return {
            "action_type": "rest",
            "success": True,
            "hp_recovered": 4
        }

    async def _generate_narrative(self, action, result) -> str:
        user_msg = (
            f"Acción del jugador: {action.description}\n"
            f"Resultado mecánico: {result}"
        )
        self._add_to_context("user", user_msg)

        messages = [{"role": "system", "content": self._build_system_prompt()}]
        messages += self._conversation

        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                resp = await client.post(
                    f"{OLLAMA_HOST}/api/chat",
                    json={
                        "model": MODEL,
                        "messages": messages,
                        "stream": False,
                        "options": {
                            "temperature": 0.85,
                            "num_predict": 250,
                            "repeat_penalty": 1.2
                        }
                    }
                )
                if resp.status_code == 200:
                    narrative = resp.json().get("message", {}).get("content", "").strip()
                    if narrative:
                        self._add_to_context("assistant", narrative)
                        return narrative
        except Exception as e:
            print(f"⚠️ Ollama error: {e}")

        return "La mazmorra permanece en silencio..."
