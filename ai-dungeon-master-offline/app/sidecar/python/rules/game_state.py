from typing import Dict, Any, Optional

ROOMS = {
    "cripta_entrada": {
        "name": "Entrada de la Cripta",
        "description": "Una cámara de piedra con antorchas apagadas. El olor a podredumbre es intenso.",
        "exits": ["pasillo_norte", "camara_trampa"],
        "enemies_pool": ["goblin"]
    },
    "pasillo_norte": {
        "name": "Pasillo Norte",
        "description": "Un corredor estrecho con marcas de garras en las paredes.",
        "exits": ["cripta_entrada", "camara_huesos"],
        "enemies_pool": ["goblin", "goblin_arquero"]
    },
    "camara_trampa": {
        "name": "Cámara de las Trampas",
        "description": "El suelo de piedra tiene marcas sospechosas. Algo cruje bajo cada paso.",
        "exits": ["cripta_entrada"],
        "enemies_pool": []
    },
    "camara_huesos": {
        "name": "Cámara de los Huesos",
        "description": "Montones de huesos apilados hasta el techo. Algunos aún se mueven.",
        "exits": ["pasillo_norte", "altar_serath"],
        "enemies_pool": ["esqueleto", "esqueleto_guerrero"]
    },
    "altar_serath": {
        "name": "Altar de Serath",
        "description": "Un altar de obsidiana con runas que pulsan con luz roja. El Sello de Valdrath descansa sobre él.",
        "exits": ["camara_huesos"],
        "enemies_pool": ["guardian_no_muerto"]
    }
}

ENEMY_TEMPLATES = {
    "goblin": {
        "name": "Goblin", "hp": 15, "max_hp": 15,
        "ac": 13, "damage": "1d6", "attack_bonus": 2,
        "xp": 50, "description": "una criatura verde y astuta"
    },
    "goblin_arquero": {
        "name": "Goblin Arquero", "hp": 12, "max_hp": 12,
        "ac": 12, "damage": "1d8", "attack_bonus": 3,
        "xp": 75, "description": "un goblin con arco y flechas envenenadas"
    },
    "esqueleto": {
        "name": "Esqueleto", "hp": 20, "max_hp": 20,
        "ac": 14, "damage": "1d8+1", "attack_bonus": 3,
        "xp": 100, "description": "un esqueleto reanimado con armadura oxidada"
    },
    "esqueleto_guerrero": {
        "name": "Esqueleto Guerrero", "hp": 30, "max_hp": 30,
        "ac": 16, "damage": "1d10+2", "attack_bonus": 4,
        "xp": 200, "description": "un guerrero esquelético con espada de dos manos"
    },
    "guardian_no_muerto": {
        "name": "Guardián No-Muerto", "hp": 60, "max_hp": 60,
        "ac": 18, "damage": "2d8+4", "attack_bonus": 6,
        "xp": 1000, "description": "un campeón de Serath reanimado, imponente y letal"
    }
}

class GameStateManager:
    def __init__(self):
        self.current_room_id = "cripta_entrada"
        self.enemies: Dict[str, Dict[str, Any]] = {}
        self.player_xp = 0
        self.turn = 1
        self.items_found: list = []
        self._spawn_room_enemies()

    def _spawn_room_enemies(self):
        self.enemies = {}
        room = ROOMS.get(self.current_room_id, {})
        for i, enemy_type in enumerate(room.get("enemies_pool", [])):
            template = ENEMY_TEMPLATES.get(enemy_type)
            if template:
                key = f"{enemy_type}_{i}"
                self.enemies[key] = dict(template)

    def get_active_enemies(self) -> Dict[str, Dict]:
        return {k: v for k, v in self.enemies.items() if v["hp"] > 0}

    def get_first_active_enemy(self) -> Optional[tuple]:
        active = self.get_active_enemies()
        if active:
            key = next(iter(active))
            return key, active[key]
        return None

    def apply_damage_to_enemy(self, enemy_id: str, damage: int) -> bool:
        if enemy_id in self.enemies:
            self.enemies[enemy_id]["hp"] = max(0, self.enemies[enemy_id]["hp"] - damage)
            if self.enemies[enemy_id]["hp"] == 0:
                self.player_xp += self.enemies[enemy_id].get("xp", 0)
                return True
        return False

    def move_to_room(self, room_id: str) -> bool:
        current = ROOMS.get(self.current_room_id, {})
        if room_id in current.get("exits", []):
            self.current_room_id = room_id
            self._spawn_room_enemies()
            return True
        return False

    def to_prompt_context(self) -> str:
        room = ROOMS.get(self.current_room_id, {})
        active = self.get_active_enemies()
        enemies_str = ", ".join(
            f"{e['name']} (HP:{e['hp']}/{e['max_hp']})"
            for e in active.values()
        ) if active else "ninguno"
        exits_str = ", ".join(room.get("exits", []))
        return (
            f"Sala actual: {room.get('name', '?')} — {room.get('description', '')}\n"
            f"Enemigos presentes: {enemies_str}\n"
            f"Salidas disponibles: {exits_str}\n"
            f"Turno: {self.turn} | XP acumulada: {self.player_xp}"
        )

    def to_api_state(self) -> Dict[str, Any]:
        room = ROOMS.get(self.current_room_id, {})
        return {
            "room": room.get("name"),
            "room_id": self.current_room_id,
            "enemies": self.get_active_enemies(),
            "turn": self.turn,
            "xp": self.player_xp,
            "exits": room.get("exits", [])
        }
