import hashlib
import random
from typing import Dict, Any, List

class ProceduralDungeon:
    ROOM_NAMES = {
        "combat": [
            "Fosa de las Almas", "Sala de Guardia Profanada", "Cámara de la Tortura",
            "Nido de Arañas Gigantes", "Galería de Estatuas Rotas", "Pasillo Inundado de Sangre"
        ],
        "trap": [
            "Pasadizo de las Cuchillas", "Cámara del Gas Asfixiante", "Vestíbulo de las Baldosas Falsas",
            "Cripta de las Estacas Ocultas", "Galería del Fuego Sagrado"
        ],
        "loot": [
            "Cámara del Tesoro Antiguo", "Laboratorio del Alquimista", "Armería del Héroe Caído",
            "Santuario de la Reliquia Sagrada", "Biblioteca de Pergaminos Prohibidos"
        ],
        "empty": [
            "Pasillo de Piedra Húmeda", "Cámara del Eco Silencioso", "Cripta Vacía",
            "Refugio del Aventurero", "Rotonda de las Columnas Caídas"
        ]
    }

    ENEMIES_POOL = [
        {"name": "Duende Asaltante", "hp": 7, "armor_class": 12},
        {"name": "Esqueleto Guerrero", "hp": 9, "armor_class": 13},
        {"name": "Araña de Cripta", "hp": 11, "armor_class": 11},
        {"name": "Zombi Hambriento", "hp": 15, "armor_class": 8},
        {"name": "Cultista Oscuro", "hp": 12, "armor_class": 12}
    ]

    LOOT_POOL = [
        "Poción de Curación", "Anillo de Oro con Rubí", "Escudo de Hierro",
        "Pergamino de Bola de Fuego", "Daga Rúnica (+1)", "Llave Antigua de Bronce"
    ]

    def __init__(self, campaign_id: str):
        self.campaign_id = campaign_id
        # Derive a numerical seed from campaign_id
        seed_hash = hashlib.md5(campaign_id.encode('utf-8')).hexdigest()
        self.seed = int(seed_hash, 16) % 1000000
        self.rng = random.Random(self.seed)
        self.grid_size = 5
        self.grid = self._generate_grid()

    def _generate_grid(self) -> List[List[Dict[str, Any]]]:
        grid = []
        for x in range(self.grid_size):
            row = []
            for y in range(self.grid_size):
                # Default empty room structure
                room = {
                    "x": x,
                    "y": y,
                    "name": "Pasillo de Piedra",
                    "type": "empty",
                    "description": "Un pasillo silencioso y húmedo.",
                    "cleared": False,
                    "enemies": [],
                    "loot": [],
                    "trap_dc": 0,
                    "visited": False
                }
                row.append(room)
            grid.append(row)

        # Place Start Room at (2, 4) (Bottom Center)
        grid[2][4]["name"] = "Entrada de la Cripta"
        grid[2][4]["type"] = "start"
        grid[2][4]["description"] = "El portal de piedra se cierra a tus espaldas. El aire es denso y frío."
        grid[2][4]["cleared"] = True
        grid[2][4]["visited"] = True

        # Place Boss Room at (2, 0) (Top Center)
        grid[2][0]["name"] = "Cámara del Archimago Esqueleto"
        grid[2][0]["type"] = "boss"
        grid[2][0]["description"] = "Una enorme sala iluminada por fuego verde flotante. En el trono aguarda el soberano de la cripta."
        grid[2][0]["enemies"] = [{"name": "Archimago Esqueleto", "hp": 30, "armor_class": 14}]

        # Populate other rooms procedurally
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                if (x == 2 and y == 4) or (x == 2 and y == 0):
                    continue

                # Determine room type
                roll = self.rng.random()
                if roll < 0.35:
                    r_type = "combat"
                    name = self.rng.choice(self.ROOM_NAMES["combat"])
                    enemies = [self.rng.choice(self.ENEMIES_POOL).copy()]
                    # Scale enemy HP slightly for difficulty
                    enemies[0]["hp"] += self.rng.randint(-2, 3)
                    room_data = {
                        "type": r_type, "name": name, "enemies": enemies,
                        "description": f"Un olor a muerte inunda la sala. {enemies[0]['name']} te corta el paso."
                    }
                elif roll < 0.60:
                    r_type = "trap"
                    name = self.rng.choice(self.ROOM_NAMES["trap"])
                    dc = self.rng.choice([11, 12, 13, 14])
                    room_data = {
                        "type": r_type, "name": name, "trap_dc": dc,
                        "description": f"Tus instintos te alertan. Hay algo sospechoso en la disposición de esta sala."
                    }
                elif roll < 0.80:
                    r_type = "loot"
                    name = self.rng.choice(self.ROOM_NAMES["loot"])
                    items = [self.rng.choice(self.LOOT_POOL)]
                    gold = self.rng.randint(10, 50)
                    room_data = {
                        "type": r_type, "name": name, "loot": items, "gold": gold,
                        "description": "Una rara sensación de seguridad te inunda. Ves restos de un tesoro o alijo."
                    }
                else:
                    r_type = "empty"
                    name = self.rng.choice(self.ROOM_NAMES["empty"])
                    room_data = {
                        "type": r_type, "name": name,
                        "description": "Una sala vacía pero llena de sombras susurrantes."
                    }

                grid[x][y].update(room_data)

        return grid

    def get_room(self, x: int, y: int) -> Dict[str, Any]:
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            return self.grid[x][y]
        return None

    def serialize(self) -> List[Dict[str, Any]]:
        rooms = []
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                rooms.append(self.grid[x][y])
        return rooms
