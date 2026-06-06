import os
import uuid
import re
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from memory.db_manager import DatabaseManager
from memory.repositories import CampaignRepository, CharacterRepository, DiceRollRepository, MessageRepository
from rules.dice_engine import DiceEngine
from rules.combat_engine import CombatEngine
from rules.map_generator import ProceduralDungeon
from voice.whisper_service import WhisperService
from voice.piper_service import PiperService
from llm.ollama_client import OllamaClient
from memory.pruner import ContextPruner

# XP rewards by encounter difficulty
XP_BY_DIFFICULTY = {"trivial": 0, "easy": 25, "medium": 50, "hard": 100, "deadly": 200}

def classify_intent_fast(text: str) -> str:
    """Deterministic keyword-based intent classifier. Fast and reliable."""
    t = text.lower().strip()

    # Out-of-game / meta questions (handle FIRST — highest priority)
    meta_keywords = [
        "quiero crear", "nueva campaña", "nuevo personaje", "cómo", "como jugar",
        "qué es", "que es", "reglas", "ayuda", "help", "opciones", "comandos",
        "inventario", "ficha", "stats", "habilidades", "nivel", "experiencia",
        "cuánto", "cuanto", "qué hago", "que hago", "explica", "dime",
        "nueva partida", "empezar", "comenzar", "reiniciar"
    ]
    if any(kw in t for kw in meta_keywords):
        return "meta_question"

    # Movement
    movement_keywords = ["norte", "sur", "este", "oeste", "north", "south", "east", "west", "mover", "ir al", "ir hacia"]
    if any(kw in t for kw in movement_keywords):
        return "movement_action"

    # Combat
    combat_keywords = [
        "atac", "golpe", "golpeo", "hiero", "dispar", "lanzo", "lanza",
        "espada", "arco", "hacha", "daga", "magia", "hechiz", "iniciativa",
        "peleo", "pelea", "mato", "matar", "destruyo", "defiend", "bloqueo",
        "fight", "attack", "strike"
    ]
    if any(kw in t for kw in combat_keywords):
        return "combat_action"

    # Inventory
    inventory_keywords = [
        "equipo", "equipar", "uso", "usar", "tomo", "tomar", "poción", "pocion",
        "bebo", "beber", "mochila", "bolsa", "oro", "compro", "vendo", "objeto",
        "item", "arma", "armadura", "escudo"
    ]
    if any(kw in t for kw in inventory_keywords):
        return "inventory_action"

    # Social
    social_keywords = [
        "hablo", "hablar", "pregunto", "preguntar", "digo", "decir", "grito",
        "gritar", "persuado", "engaño", "intimido", "negocio", "mercader",
        "tabernero", "aldeano", "npc", "personaje"
    ]
    if any(kw in t for kw in social_keywords):
        return "social_action"

    # Exploration
    exploration_keywords = [
        "miro", "busco", "buscar", "investigo", "exploro", "abro", "abrir",
        "puerta", "cofre", "trampa", "escondite", "registro", "examino",
        "observo", "voy", "camino", "entro", "entrar", "salgo", "salir",
        "sigo", "norte", "sur", "este", "oeste", "arriba", "abajo"
    ]
    if any(kw in t for kw in exploration_keywords):
        return "exploration_action"

    return "exploration_action"  # safest default


class Orchestrator:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.campaign_repo = CampaignRepository(db_manager)
        self.character_repo = CharacterRepository(db_manager)
        self.roll_repo = DiceRollRepository(db_manager)
        self.message_repo = MessageRepository(db_manager)
        from memory.repositories import MemoryVectorRepository
        self.vector_repo = MemoryVectorRepository(db_manager)

        self.whisper = WhisperService()
        self.piper = PiperService()
        self.ollama = OllamaClient()
        self.pruner = ContextPruner(self.ollama)

    # ─── Prompt builder ───────────────────────────────────────────────────────
    def _build_messages(
        self,
        campaign: Dict,
        character: Dict,
        user_message: str,
        mechanics_summary: str,
        history: List[Dict],
        room_desc: str,
        campaign_summary: str = "",
        is_boss_cleared: bool = False,
        relevant_past_events: str = ""
    ) -> List[Dict[str, str]]:
        is_custom_model = self.ollama.default_model.startswith("magicworld-gm")
        messages = []

        # Compact system prompt for both models to inject room context
        tone_map = {
            "Epic & Dark Fantasy": "oscuro y épico",
            "High Fantasy Comedy": "humorístico y mágico",
            "Grimdark & Gritty": "brutal y realista",
        }
        tone_instructions = {
            "Epic & Dark Fantasy": "Adopta un estilo literario y cinematográfico de fantasía oscura y sombría. Usa descripciones sensoriales ricas, metáforas solemnes sobre el destino y detalla el eco de las sombras en las ruinas antiguas.",
            "High Fantasy Comedy": "Adopta un estilo literario dinámico, mágico y ligeramente satírico. Resalta el absurdo de las situaciones, las descripciones coloridas y los detalles extravagantes o cómicos de los enemigos.",
            "Grimdark & Gritty": "Adopta un estilo crudo, visceral y sumamente realista. Describe textures ásperas, el frío húmedo, el olor de la sangre, la herrumbre y el agotamiento físico del personaje. Evita el tono heroico clásico.",
        }
        tone = tone_map.get(campaign.get("tone", "Epic & Dark Fantasy"), "épico")
        style_instruction = tone_instructions.get(campaign.get("tone", "Epic & Dark Fantasy"), "Usa una prosa descriptiva e inmersiva.")
        char = character
        summary_block = f" RESUMEN ANTERIOR: {campaign_summary}." if campaign_summary else ""
        rag_block = f" ACONTECIMIENTOS PASADOS RELEVANTES: {relevant_past_events}." if relevant_past_events else ""
        boss_instruction = " ¡EL ARCHIMAGO ESQUELETO (JEFE FINAL) HA SIDO DERROTADO! Narra la gran victoria del héroe en tono triunfal y dale un cierre autoconclusivo y definitivo a esta aventura en la cripta." if is_boss_cleared else ""
        system = (
            f"Eres el Dungeon Master de D&D 5e. Tono: {tone}. {style_instruction} "
            f"Campaña: '{campaign.get('name', 'La Cripta')}' (Estilo Infinite Book/Novela interactiva).{summary_block}{rag_block} "
            f"Personaje: {char.get('name','Héroe')} ({char.get('race','?')} {char.get('class','?')}, "
            f"Nv{char.get('level',1)}, HP {char.get('hp_current',10)}/{char.get('hp_max',10)}, CA {char.get('armor_class',10)}). "
            f"LUGAR ACTUAL: {room_desc}. {boss_instruction} "
            "REGLAS DE NARRACIÓN:\n"
            "1) Escribe exclusivamente en español y en segunda persona ('Tú/Te mueves/Ves...').\n"
            "2) Sé inmersivo y dramático, incorporando sutilmente los resultados mecánicos en las descripciones sin romper la cuarta pared (evita mencionar nombres de variables o tiradas directas de dados en la prosa, traduce el valor numérico a consecuencias narrativas).\n"
            "3) Mantén el tono del narrador de manera constante y no salgas jamás de tu rol.\n"
            "4) Máximo 3 párrafos descriptivos y envolventes.\n"
            "5) Obligatorio: Al final de tu narración, escribe la etiqueta exacta '[OPCIONES]' y luego lista de 3 a 4 opciones de acción personalizadas de respuesta para el jugador (una por línea, empezando con guion '- '). Ej:\n[OPCIONES]\n- Opción A\n- Opción B\n- Opción C"
        )
        messages.append({"role": "system", "content": system})

        # Add limited history (last 6 messages)
        recent = history[-6:] if len(history) > 6 else history
        messages.extend(recent)

        # Build user turn
        user_turn = user_message
        if mechanics_summary:
            user_turn = f"{user_message}\n\n[RESULTADO MECÁNICO: {mechanics_summary}]"
        messages.append({"role": "user", "content": user_turn})
        return messages

    def _handle_meta_question(self, user_message: str, character: Dict, campaign: Dict) -> str:
        t = user_message.lower()

        if any(kw in t for kw in ["crear campaña", "nueva campaña", "nueva partida"]):
            return (
                "⚙️ Para crear una nueva campaña, vuelve al Lobby usando el botón 'Volver al Lobby' "
                "en la esquina superior derecha. Desde ahí puedes crear una nueva gesta con su propio nombre y tono narrativo."
            )

        if any(kw in t for kw in ["nuevo personaje", "crear personaje", "crear héroe"]):
            return (
                "⚙️ Para crear un nuevo personaje, selecciona una campaña desde el Lobby. "
                "En el panel derecho aparecerá la opción de 'Iniciar Entrevista' (estilo Pokémon Mystery Dungeon) "
                "o crear una ficha manualmente."
            )

        if any(kw in t for kw in ["inventario", "ficha", "stats", "habilidades"]):
            stats = character.get("stats", {})
            stat_str = " | ".join([f"{k}: {v}" for k, v in stats.items()]) if stats else "N/A"
            return (
                f"📋 **Ficha de {character.get('name', 'tu personaje')}**\n"
                f"Raza/Clase: {character.get('race','?')} {character.get('class','?')} Nv.{character.get('level',1)}\n"
                f"HP: {character.get('hp_current',0)}/{character.get('hp_max',0)} | CA: {character.get('armor_class',0)}\n"
                f"Stats: {stat_str}\n"
                f"Trasfondo: {character.get('background','?')}"
            )

        if any(kw in t for kw in ["cómo", "como", "ayuda", "help", "reglas", "qué puedo", "que puedo"]):
            return (
                "🎲 **Comandos disponibles en juego:**\n"
                "• Escribe tu acción en el campo de texto (ej: 'Ataco al orco con mi espada')\n"
                "• Usa el botón 🎙️ para hablar directamente\n"
                "• Los dados se tiran automáticamente según tu acción\n"
                "• Puedes pedir: 'miro alrededor', 'hablo con el tabernero', 'abro el cofre'\n\n"
                "📌 Acciones fuera del juego (crear campaña/personaje) se hacen desde el Lobby."
            )

        return (
            f"El Dungeon Master hace una pausa. '{user_message}' — esa es una pregunta interesante, aventurero. "
            "Consulta el manual de reglas o usa el menú del Lobby para opciones de campaña. "
            "¿Hay algo más que quieras hacer en el mundo del juego?"
        )

    def process_player_turn(
        self,
        campaign_id: str,
        character_id: str,
        text_input: Optional[str] = None,
        audio_path: Optional[str] = None
    ) -> Dict[str, Any]:

        # ── Step 1: Get player message ────────────────────────────────────────
        user_message = text_input or ""
        if audio_path and os.path.exists(audio_path):
            user_message = self.whisper.transcribe(audio_path)
        if not user_message:
            user_message = "Miro a mi alrededor."

        # ── Step 2: Load context & pages history ──────────────────────────────
        campaign = self.campaign_repo.get_by_id(campaign_id) or {
            "id": campaign_id, "name": "La Cripta",
            "system": "D&D 5.5", "tone": "Epic & Dark Fantasy"
        }
        character = self.character_repo.get_by_id(character_id) or {
            "id": character_id, "name": "Héroe", "class": "Guerrero", "race": "Humano",
            "level": 1, "hp_current": 12, "hp_max": 12, "armor_class": 15,
            "stats": {"STR": 16, "DEX": 14, "CON": 15, "INT": 10, "WIS": 12, "CHA": 8}
        }

        # Initialize procedural map using campaign ID
        dungeon = ProceduralDungeon(campaign_id)
        
        # Load previous pages to get current coordinate and page number
        existing_pages = self.message_repo.get_pages(campaign_id)
        current_page = len(existing_pages) + 1
        
        # Default start coordinates (2, 4)
        x, y = 2, 4
        if existing_pages:
            last_page = existing_pages[-1]
            coords = last_page.get("coordinates", {"x": 2, "y": 4})
            x, y = coords.get("x", 2), coords.get("y", 4)

        # ── Step 3: Classify intent ───────────────────────────────────────────
        intent = classify_intent_fast(user_message)

        # ── Step 4: Handle meta/out-of-game questions directly ────────────────
        if intent == "meta_question":
            narrative_response = self._handle_meta_question(user_message, character, campaign)
            self.message_repo.add_message(
                campaign_id, "user", user_message, character_id,
                page_number=current_page, coordinates_json=json.dumps({"x": x, "y": y})
            )
            self.message_repo.add_message(
                campaign_id, "assistant", narrative_response,
                page_number=current_page, coordinates_json=json.dumps({"x": x, "y": y})
            )
            return {
                "player_text": user_message,
                "intent": intent,
                "mechanics": "",
                "roll": None,
                "narrative": narrative_response,
                "audio_file": "",
                "xp_gained": 0,
                "page_number": current_page,
                "coordinates": {"x": x, "y": y},
                "choices": []
            }

        # ── Step 5: Movement processing ───────────────────────────────────────
        roll_details = None
        mechanics_summary = ""
        xp_gained = 0
        moved = False

        if intent == "movement_action":
            t = user_message.lower()
            old_x, old_y = x, y
            if "norte" in t or "north" in t:
                if y > 0:
                    y -= 1
                    moved = True
            elif "sur" in t or "south" in t:
                if y < 4:
                    y += 1
                    moved = True
            elif "oeste" in t or "west" in t:
                if x > 0:
                    x -= 1
                    moved = True
            elif "este" in t or "east" in t:
                if x < 4:
                    x += 1
                    moved = True

            if moved:
                mechanics_summary = f"Te mueves de ({old_x}, {old_y}) a ({x}, {y}). "
            else:
                mechanics_summary = "Un muro de piedra maciza bloquea el paso en esa dirección. "

        # Get room details for current coordinate
        room = dungeon.get_room(x, y)
        room_desc = f"Habitación en ({x}, {y}): '{room['name']}'. {room['description']}"

        # ── Step 6: Rules & Encounter resolution ──────────────────────────────
        if room["type"] in ("combat", "boss") and room["enemies"] and not room.get("cleared"):
            # Start/Continue combat with the room's procedural enemy
            enemy = room["enemies"][0]
            char_level = character.get("level", 1)
            str_val = character.get("stats", {}).get("STR", 10)
            str_mod = (str_val - 10) // 2
            proficiency = 2 + (char_level - 1) // 4
            attacker = {"name": character["name"], "attack_bonus": str_mod + proficiency}
            weapon = {"name": "tu arma", "damage_formula": "1d8+3"}

            combat_res = CombatEngine.resolve_attack(attacker, enemy, weapon)
            roll_details = combat_res["attack_roll"]
            self.roll_repo.save_roll(campaign_id, character_id, character["name"], "1d20+atk", roll_details)

            hit_str = "IMPACTO" if combat_res["hit"] else "FALLO"
            label = "JEFE FINAL" if room["type"] == "boss" else "Enemigo"
            mechanics_summary += (
                f"Combates contra el {label} ({enemy['name']}): Tirada {roll_details['total']} vs CA {enemy['armor_class']} → {hit_str}. "
                f"Daño causado: {combat_res['damage_total']}. "
            )
            if combat_res["hit"]:
                xp_gained = XP_BY_DIFFICULTY["hard"] if room["type"] == "boss" else XP_BY_DIFFICULTY["medium"]
                room["cleared"] = True
                if room["type"] == "boss":
                    mechanics_summary += " ¡ENEMIGO DERROTADO! Has purificado la cripta de Gahenax."

        elif room["type"] == "trap" and not room.get("cleared"):
            # Trigger trap DEX save
            dex_mod = (character.get("stats", {}).get("DEX", 10) - 10) // 2
            roll = DiceEngine.roll("1d20", dex_mod)
            roll_details = roll
            dc = room.get("trap_dc", 12)
            if roll["total"] >= dc:
                mechanics_summary += f"¡Esquivas una trampa! Salvación de DEX: {roll['total']} vs CD {dc} (Éxito)."
                xp_gained = XP_BY_DIFFICULTY["easy"]
            else:
                damage = DiceEngine.roll("1d6", 0)["total"]
                new_hp = max(0, character.get("hp_current", 12) - damage)
                self.character_repo.update_hp(character_id, new_hp)
                mechanics_summary += f"¡Activas una trampa! Salvación de DEX: {roll['total']} vs CD {dc} (Fallo). Sufres {damage} de daño. HP actual: {new_hp}."
            room["cleared"] = True

        elif room["type"] == "loot" and not room.get("cleared"):
            loot_item = room["loot"][0] if room["loot"] else "Poción de Curación"
            gold = room.get("gold", 15)
            # Update character inventory (simplified gold/items append)
            # Ordinarily we'd do a JSON update, let's keep it clean
            mechanics_summary += f"Encuentras: {loot_item} y {gold} piezas de oro."
            xp_gained = XP_BY_DIFFICULTY["easy"]
            room["cleared"] = True

        elif intent == "exploration_action" and not moved:
            wis_mod = (character.get("stats", {}).get("WIS", 10) - 10) // 2
            roll = DiceEngine.roll("1d20", wis_mod)
            roll_details = roll
            result_str = "Éxito notable" if roll["total"] >= 15 else "Éxito parcial" if roll["total"] >= 10 else "Sin hallazgos"
            mechanics_summary += f"Tirada de Percepción: {roll['total']} → {result_str}."

        # ── Step 7: Retrieve history and generate narrative ──────────────────
        history = self.message_repo.get_recent_history(campaign_id, limit=6)
        campaign_summary = campaign.get("narrative_summary", "") or ""
        
        # RAG retrieval based on user query
        relevant_past_events = ""
        try:
            query_emb = self.ollama.generate_embeddings(user_message)
            if query_emb:
                similar_docs = self.vector_repo.search_similar(campaign_id, query_emb, top_k=2)
                if similar_docs:
                    relevant_past_events = " | ".join([doc["content"] for doc in similar_docs])
        except Exception as e:
            print(f"[RAG] Retrieval failed: {e}")
            
        is_boss_cleared = (room["type"] == "boss" and room.get("cleared") == True)
        messages = self._build_messages(
            campaign, character, user_message, mechanics_summary, history, room_desc, campaign_summary, is_boss_cleared, relevant_past_events
        )

        raw_response = self.ollama.generate_chat(messages)

        # Parse narrative and choices out of raw_response
        narrative_response = raw_response
        choices = []
        
        opciones_match = re.search(r'\[OPCIONES\]', raw_response, re.IGNORECASE)
        if opciones_match:
            split_idx = opciones_match.start()
            narrative_response = raw_response[:split_idx].strip()
            options_part = raw_response[split_idx + len("[OPCIONES]"):].strip()
            for line in options_part.split("\n"):
                line = line.strip()
                if not line:
                    continue
                # Clean leading bullet points or numbers
                cleaned_line = re.sub(r'^[-*•\d+\.]\s*', '', line).strip()
                if cleaned_line:
                    choices.append(cleaned_line)

        # Generate and save embedding of the newly generated DM description for future RAG retrieval
        try:
            desc_emb = self.ollama.generate_embeddings(narrative_response)
            if desc_emb:
                self.vector_repo.add_vector(campaign_id, narrative_response, desc_emb)
        except Exception as e:
            print(f"[RAG] Failed to index new narrative event: {e}")

        # ── Step 8: Generate fallback movement choices if none were parsed ───
        if not choices:
            if is_boss_cleared:
                choices.append("Completar gesta con honor (Fin del Episodio)")
            else:
                if y > 0:
                    choices.append("Moverse al Norte")
                if y < 4:
                    choices.append("Moverse al Sur")
                if x > 0:
                    choices.append("Moverse al Oeste")
                if x < 4:
                    choices.append("Moverse al Este")
                choices.append("Registrar la habitación")

        # ── Step 9: Persist to SQLite ─────────────────────────────────────────
        user_stored = user_message
        if mechanics_summary:
            user_stored = f"{user_message}\n[MECÁNICA: {mechanics_summary}]"
            
        self.message_repo.add_message(
            campaign_id, "user", user_stored, character_id,
            page_number=current_page,
            coordinates_json=json.dumps({"x": x, "y": y}),
            choices_json=json.dumps(choices),
            mechanics=mechanics_summary
        )
        self.message_repo.add_message(
            campaign_id, "assistant", narrative_response,
            page_number=current_page,
            coordinates_json=json.dumps({"x": x, "y": y}),
            choices_json=json.dumps(choices),
            mechanics=mechanics_summary
        )

        # ── Step 9.5: Automatic Context Pruning ──────────────────────────────
        all_pages = self.message_repo.get_pages(campaign_id)
        if len(all_pages) >= 5:
            new_summary = self.pruner.prune_history(campaign_id, all_pages)
            if new_summary:
                self.campaign_repo.update_summary(campaign_id, new_summary)

        if xp_gained > 0:
            self.character_repo.update_xp(character_id, xp_gained)

        # ── Step 10: Synthesize voice audio ──────────────────────────────────
        base_dir = Path(__file__).resolve().parents[2]
        audio_out_dir = base_dir / "data" / "voices"
        audio_out_dir.mkdir(parents=True, exist_ok=True)
        output_audio_file = str(audio_out_dir / f"{uuid.uuid4()}.wav")
        self.piper.synthesize(narrative_response, output_audio_file)

        return {
            "player_text": user_message,
            "intent": intent,
            "mechanics": mechanics_summary,
            "roll": roll_details,
            "narrative": narrative_response,
            "audio_file": output_audio_file,
            "xp_gained": xp_gained,
            "page_number": current_page,
            "coordinates": {"x": x, "y": y},
            "choices": choices
        }

