import hashlib
import random
import os
import json
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

        # Path declarations relative to this file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, "..", "..", "data")
        
        # Determine theme file based on campaign tone/name
        scenario_filename = "crypt.json"
        try:
            from memory.db_manager import DatabaseManager
            db = DatabaseManager()
            campaign = db.fetch_one("SELECT * FROM campaigns WHERE id = ?", (campaign_id,))
            if campaign:
                tone = campaign.get("tone", "").lower()
                name = campaign.get("name", "").lower()
                if "convergencia" in name or "convergencia" in tone or "dietrix" in name or "dietrix" in tone:
                    scenario_filename = "eon_de_convergencia.json"
                elif "forest" in name or "forest" in tone or "bosque" in name or "bosque" in tone:
                    scenario_filename = "forest.json"
        except Exception as e:
            print(f"[MapGen] Failed to query campaign info for theme selection: {e}")

        # Load custom theme (scenario) if available
        self.room_names = self.ROOM_NAMES
        scenario_file = os.path.join(data_dir, "scenarios", scenario_filename)
        if os.path.exists(scenario_file):
            try:
                with open(scenario_file, 'r', encoding='utf-8') as f:
                    scen_data = json.load(f)
                    self.room_names = {
                        "combat": scen_data.get("combat", self.ROOM_NAMES["combat"]),
                        "trap": scen_data.get("trap", self.ROOM_NAMES["trap"]),
                        "loot": scen_data.get("loot", self.ROOM_NAMES["loot"]),
                        "empty": scen_data.get("empty", self.ROOM_NAMES["empty"])
                    }
            except Exception as e:
                print(f"[MapGen] Error loading scenarios: {e}")
                
        # Load bestiary (monsters) if available
        self.enemies_pool = self.ENEMIES_POOL
        monsters_file = os.path.join(data_dir, "bestiary", "monsters.json")
        if os.path.exists(monsters_file):
            try:
                with open(monsters_file, 'r', encoding='utf-8') as f:
                    m_data = json.load(f)
                    self.enemies_pool = [{"name": m["name"], "hp": m["hp"], "armor_class": m["armor_class"]} for m in m_data]
            except Exception as e:
                print(f"[MapGen] Error loading bestiary: {e}")
                
        # Load loot if available
        self.loot_pool = self.LOOT_POOL
        loot_file = os.path.join(data_dir, "loot", "loot.json")
        if os.path.exists(loot_file):
            try:
                with open(loot_file, 'r', encoding='utf-8') as f:
                    l_data = json.load(f)
                    self.loot_pool = [l["name"] for l in l_data]
            except Exception as e:
                print(f"[MapGen] Error loading loot: {e}")

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
        
        # Pull boss from custom bestiary if possible, otherwise use fallback
        boss_name = "Archimago Esqueleto"
        if len(self.enemies_pool) > 0:
            # Look for a boss or use the toughest one
            boss_candidate = next((e for e in self.enemies_pool if "Mímico" in e["name"] or "Bugbear" in e["name"]), self.enemies_pool[-1])
            boss_name = boss_candidate["name"]
        
        grid[2][0]["enemies"] = [{"name": boss_name, "hp": 30, "armor_class": 14}]

    def _build_procedural_description(self, r_type: str, details: Dict[str, Any]) -> str:
        # Atmosphere definitions
        atmospheres = {
            "combat": [
                "El aire está impregnado de un hedor metálico a sangre fresca.",
                "Un frío antinatural te cala hasta los huesos al cruzar el umbral.",
                "El sonido de cadenas arrastrándose resuena desde las esquinas oscuras.",
                "Un murmullo de rezos blasfemos parece flotar en el aire estancado.",
                "La visibilidad es casi nula debido a una neblina densa y húmeda."
            ],
            "trap": [
                "Un silencio tenso e inquietante gobierna cada rincón de la estancia.",
                "Una corriente de aire helado sopla de forma intermitente desde el techo.",
                "El goteo constante de agua ácida corroe lentamente las losas del suelo.",
                "Una extraña quietud te eriza la piel, alertando tus sentidos de explorador.",
                "El ambiente se siente cargado, como si el propio aire contuviera la respiración."
            ],
            "loot": [
                "Una tenue luminiscencia dorada se filtra a través de las grietas de la mampostería.",
                "Un reconfortante aroma a sándalo y cera antigua perfuma el ambiente.",
                "El eco del silencio se siente diferente aquí, casi pacífico.",
                "Un rayo de luz espectral ilumina el centro de la cámara, disipando las sombras.",
                "El polvo aquí está removido, revelando marcas de antiguos viajeros mercenarios."
            ],
            "empty": [
                "Las sombras parecen estirarse y bailar al ritmo de la llama de tu antorcha.",
                "El polvo acumulado de décadas cubre las baldosas agrietadas.",
                "El viento susurra lamentos incomprensibles a través de las rendijas de los muros.",
                "Una bóveda de columnas rotas y telarañas gruesas se extiende sobre ti.",
                "El eco de tus propios pasos es el único sonido que llena este vacío sepulcral."
            ]
        }
        
        # Structure definitions
        structures = [
            "Los muros de sillería muestran inscripciones rúnicas desgastadas por el tiempo.",
            "Columnas de mármol negro fracturadas sostienen un techo abovedado a punto de colapsar.",
            "Un canal poco profundo de agua estancada cruza la sala de lado a lado.",
            "El suelo está cubierto de escombros de antiguas estatuas de guerreros decapitados.",
            "Grandes rejas de hierro oxidado cuelgan de las paredes laterales.",
            "Las paredes están cubiertas de una densa capa de líquenes fosforescentes de color azul pálido.",
            "La estancia presenta un relieve tallado en el techo que representa una constelación olvidada."
        ]
        
        # Danger/Details
        threats = {
            "combat": [
                f"Frente a ti, {details.get('enemy_name', 'una criatura')} emerge de la penumbra listo para atacar.",
                f"Sientes unos ojos hambrientos observándote; {details.get('enemy_name', 'un enemigo')} te corta el paso.",
                f"El descanso eterno de {details.get('enemy_name', 'un ser oscuro')} ha sido interrumpido por tu presencia y ruge furioso.",
                f"Una figura hostil identificada como {details.get('enemy_name', 'un guardián')} custodia el centro de la sala alzando sus armas."
            ],
            "trap": [
                "Percibes una ligera inclinación en las baldosas bajo tus pies y marcas sospechosas en la pared.",
                "Finísimos hilos de alambre casi invisibles cruzan a la altura de tus tobillos.",
                "Agujeros diminutos en las paredes sugieren un mecanismo de disparo listo para activarse.",
                "El suelo en el centro de la sala vibra ligeramente al menor peso."
            ],
            "loot": [
                f"Entre las ruinas, descansa {details.get('loot_item', 'un cofre antiguo')} junto a un saco de monedas.",
                "Un cofre con el escudo de Valdrath se encuentra medio enterrado bajo los escombros.",
                f"Un pedestal de piedra sostiene {details.get('loot_item', 'un objeto valioso')} que brilla bajo la penumbra.",
                "En una hornacina en la pared, localizas un alijo con provisiones y un cofre de madera."
            ],
            "empty": [
                "A pesar de registrar cada rincón, no encuentras más que ruinas vacías y ecos del pasado.",
                "No parece haber amenazas inmediatas aquí, solo el peso del olvido.",
                "Una búsqueda rápida confirma que esta cámara fue saqueada hace mucho tiempo.",
                "Es un lugar desolado, ideal para recuperar el aliento si el peligro no acechara afuera."
            ]
        }
        
        atm = self.rng.choice(atmospheres.get(r_type, atmospheres["empty"]))
        struc = self.rng.choice(structures)
        thr = self.rng.choice(threats.get(r_type, threats["empty"]))
        
        return f"{atm} {struc} {thr}"

    def _generate_grid(self) -> List[List[Dict[str, Any]]]:
        grid = []
        for x in range(self.grid_size):
            row = []
            for y in range(self.grid_size):
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
        
        boss_name = "Archimago Esqueleto"
        if len(self.enemies_pool) > 0:
            boss_candidate = next((e for e in self.enemies_pool if "Mímico" in e["name"] or "Bugbear" in e["name"]), self.enemies_pool[-1])
            boss_name = boss_candidate["name"]
        
        grid[2][0]["enemies"] = [{"name": boss_name, "hp": 30, "armor_class": 14}]

        # Populate other rooms procedurally
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                if (x == 2 and y == 4) or (x == 2 and y == 0):
                    continue

                roll = self.rng.random()
                if roll < 0.35:
                    r_type = "combat"
                    name = self.rng.choice(self.room_names["combat"])
                    enemies = [self.rng.choice(self.enemies_pool).copy()]
                    enemies[0]["hp"] += self.rng.randint(-2, 3)
                    desc = self._build_procedural_description(r_type, {"enemy_name": enemies[0]["name"]})
                    room_data = {
                        "type": r_type, "name": name, "enemies": enemies,
                        "description": desc
                    }
                elif roll < 0.60:
                    r_type = "trap"
                    name = self.rng.choice(self.room_names["trap"])
                    dc = self.rng.choice([11, 12, 13, 14])
                    desc = self._build_procedural_description(r_type, {"trap_dc": dc})
                    room_data = {
                        "type": r_type, "name": name, "trap_dc": dc,
                        "description": desc
                    }
                elif roll < 0.80:
                    r_type = "loot"
                    name = self.rng.choice(self.room_names["loot"])
                    items = [self.rng.choice(self.loot_pool)]
                    gold = self.rng.randint(10, 50)
                    desc = self._build_procedural_description(r_type, {"loot_item": items[0]})
                    room_data = {
                        "type": r_type, "name": name, "loot": items, "gold": gold,
                        "description": desc
                    }
                else:
                    r_type = "empty"
                    name = self.rng.choice(self.room_names["empty"])
                    desc = self._build_procedural_description(r_type, {})
                    room_data = {
                        "type": r_type, "name": name,
                        "description": desc
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
