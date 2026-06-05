from typing import Dict, Any, List
from rules.story_simulator import StorySimulator

class PersonalityQuiz:
    """
    Evaluates player answers to a rich 5-phase personality quiz
    to generate a complete narrative identity and stats sheet.
    """

    QUESTIONS = [
        # PHASE I: EL NÚCLEO DEL HÉROE
        {
            "id": 1,
            "question": "¿Qué impulsa a tu personaje?",
            "options": [
                {"text": "Gloria", "ideal": "Gloria", "points": {"CHA": 2, "class_fighter": 2, "class_bard": 1}},
                {"text": "Venganza", "ideal": "Venganza", "points": {"STR": 2, "class_barbarian": 2, "class_warlock": 1}},
                {"text": "Conocimiento", "ideal": "Conocimiento", "points": {"INT": 2, "class_wizard": 2, "class_druid": 1}},
                {"text": "Poder", "ideal": "Poder", "points": {"CHA": 1, "INT": 1, "class_sorcerer": 2, "class_warlock": 2}},
                {"text": "Justicia", "ideal": "Justicia", "points": {"WIS": 2, "class_paladin": 3, "class_cleric": 1}},
                {"text": "Libertad", "ideal": "Libertad", "points": {"DEX": 2, "class_ranger": 2, "class_rogue": 1}},
                {"text": "Riqueza", "ideal": "Riqueza", "points": {"DEX": 1, "CHA": 1, "class_rogue": 2, "class_bard": 1}},
                {"text": "Proteger a alguien", "ideal": "Proteger a alguien", "points": {"CON": 2, "class_cleric": 2, "class_paladin": 2}},
                {"text": "Supervivencia", "ideal": "Supervivencia", "points": {"CON": 1, "WIS": 1, "class_barbarian": 1, "class_monk": 2}}
            ]
        },
        {
            "id": 2,
            "question": "¿Qué teme perder más que su propia vida?",
            "options": [
                {"text": "Familia", "fear": "Perder a su familia", "points": {"CON": 1, "WIS": 1, "class_cleric": 1}},
                {"text": "Honor", "fear": "Perder su honor", "points": {"STR": 1, "class_paladin": 2, "class_fighter": 1}},
                {"text": "Libertad", "fear": "Perder su libertad", "points": {"DEX": 1, "class_ranger": 1, "class_rogue": 1}},
                {"text": "Poder", "fear": "Perder su poder", "points": {"CHA": 1, "class_sorcerer": 1, "class_warlock": 1}},
                {"text": "Identidad", "fear": "Perder su identidad", "points": {"INT": 1, "class_wizard": 1, "class_monk": 1}},
                {"text": "Fe", "fear": "Perder su fe", "points": {"WIS": 2, "class_cleric": 2}},
                {"text": "Conocimiento", "fear": "Perder el conocimiento acumulado", "points": {"INT": 2, "class_wizard": 2}},
                {"text": "Nada", "fear": "No temer a nada", "points": {"STR": 1, "class_barbarian": 2}}
            ]
        },
        {
            "id": 3,
            "question": "Si solo pudieras salvar una cosa de un incendio...",
            "options": [
                {"text": "Un ser querido", "save": "Un ser querido", "points": {"CON": 2, "class_cleric": 1, "class_paladin": 1}},
                {"text": "Un libro", "save": "Un libro", "points": {"INT": 2, "class_wizard": 2}},
                {"text": "Un arma", "save": "Un arma", "points": {"STR": 2, "class_fighter": 2, "class_barbarian": 1}},
                {"text": "Dinero", "save": "Dinero", "points": {"CHA": 2, "class_rogue": 2}},
                {"text": "Un símbolo importante", "save": "Un símbolo sagrado", "points": {"WIS": 2, "class_cleric": 2, "class_monk": 1}},
                {"text": "A ti mismo", "save": "A sí mismo", "points": {"DEX": 2, "class_ranger": 1, "class_warlock": 1}}
            ]
        },
        # PHASE II: MORALIDAD
        {
            "id": 4,
            "question": "Encuentras una bolsa con 10.000 monedas. ¿Qué haces?",
            "options": [
                {"text": "La devuelvo", "moral": "lawful_good", "points": {"WIS": 1, "alignment_law": 2, "alignment_good": 2}},
                {"text": "Busco al dueño y cobro recompensa", "moral": "neutral_good", "points": {"CHA": 1, "alignment_law": 1, "alignment_good": 1}},
                {"text": "Me quedo una parte", "moral": "neutral", "points": {"DEX": 1}},
                {"text": "Me la quedo toda", "moral": "chaotic_evil", "points": {"alignment_chaos": 2, "alignment_evil": 2}}
            ]
        },
        {
            "id": 5,
            "question": "Un enemigo derrotado pide clemencia.",
            "options": [
                {"text": "Lo perdono", "clemency": "perdonar", "points": {"WIS": 2, "alignment_good": 2}},
                {"text": "Lo encarcelo", "clemency": "encarcelar", "points": {"alignment_law": 2}},
                {"text": "Lo utilizo", "clemency": "utilizar", "points": {"INT": 1, "alignment_chaos": 1, "alignment_evil": 1}},
                {"text": "Lo ejecuto", "clemency": "ejecutar", "points": {"STR": 1, "alignment_chaos": 1, "alignment_evil": 2}}
            ]
        },
        {
            "id": 6,
            "question": "¿Qué pesa más?",
            "options": [
                {"text": "La ley", "weight": "la_ley", "points": {"alignment_law": 3}},
                {"text": "La justicia", "weight": "la_justicia", "points": {"alignment_good": 2}},
                {"text": "La lealtad", "weight": "la_lealtad", "points": {"alignment_law": 1, "alignment_good": 1}},
                {"text": "El resultado", "weight": "el_resultado", "points": {"alignment_chaos": 2}}
            ]
        },
        # PHASE III: ESTILO DE JUEGO
        {
            "id": 7,
            "question": "Un dragón bloquea el camino. ¿Qué haces primero?",
            "options": [
                {"text": "Hablar", "action": "parley", "points": {"CHA": 2, "class_bard": 3, "class_sorcerer": 1}},
                {"text": "Analizar", "action": "analyze", "points": {"INT": 2, "class_wizard": 3, "class_monk": 1}},
                {"text": "Esconderme", "action": "hide", "points": {"DEX": 2, "class_rogue": 3, "class_ranger": 1}},
                {"text": "Atarcar", "action": "attack", "points": {"STR": 2, "class_fighter": 2, "class_barbarian": 3}}
            ]
        },
        {
            "id": 8,
            "question": "¿Qué rol te gusta cumplir?",
            "options": [
                {"text": "Protector", "role": "protector", "points": {"CON": 2, "class_fighter": 2, "class_paladin": 3}},
                {"text": "Estratega", "role": "estratega", "points": {"INT": 2, "class_wizard": 2, "class_monk": 1}},
                {"text": "Explorador", "role": "explorador", "points": {"DEX": 2, "class_ranger": 3}},
                {"text": "Líder", "role": "lider", "points": {"CHA": 2, "class_bard": 1, "class_paladin": 2}},
                {"text": "Asesino", "role": "asesino", "points": {"DEX": 2, "class_rogue": 3}},
                {"text": "Mago", "role": "mago", "points": {"INT": 2, "class_wizard": 3}},
                {"text": "Soporte", "role": "soporte", "points": {"WIS": 2, "class_cleric": 3, "class_druid": 2}}
            ]
        },
        {
            "id": 9,
            "question": "¿Qué te parece más divertido?",
            "options": [
                {"text": "Hacer daño", "fun": "combat", "points": {"STR": 2, "class_barbarian": 2, "class_fighter": 1}},
                {"text": "Resolver problemas", "fun": "puzzle", "points": {"INT": 2, "class_wizard": 2, "class_monk": 1}},
                {"text": "Descubrir secretos", "fun": "secrets", "points": {"WIS": 2, "class_ranger": 1, "class_warlock": 2}},
                {"text": "Negociar", "fun": "diplomacy", "points": {"CHA": 2, "class_bard": 2}},
                {"text": "Liderar", "fun": "lead", "points": {"CHA": 2, "class_paladin": 2}}
            ]
        },
        # PHASE IV: PASADO
        {
            "id": 10,
            "question": "¿Dónde creciste?",
            "options": [
                {"text": "Ciudad", "origin": "ciudad", "points": {"CHA": 1}},
                {"text": "Aldea", "origin": "aldea", "points": {"CON": 1}},
                {"text": "Bosque", "origin": "bosque", "points": {"WIS": 1, "class_druid": 1, "class_ranger": 1}},
                {"text": "Desierto", "origin": "desierto", "points": {"CON": 1}},
                {"text": "Montañas", "origin": "montañas", "points": {"STR": 1}},
                {"text": "Academia", "origin": "academia", "points": {"INT": 2, "class_wizard": 1}},
                {"text": "Templo", "origin": "templo", "points": {"WIS": 2, "class_cleric": 1}},
                {"text": "Calles", "origin": "calles", "points": {"DEX": 2, "class_rogue": 1}}
            ]
        },
        {
            "id": 11,
            "question": "¿Qué marcó tu infancia?",
            "options": [
                {"text": "Guerra", "event": "guerra", "points": {"STR": 1, "class_fighter": 1}},
                {"text": "Pobreza", "event": "pobreza", "points": {"DEX": 1, "class_rogue": 1}},
                {"text": "Traición", "event": "traición", "points": {"CHA": 1, "class_warlock": 1}},
                {"text": "Muerte", "event": "muerte", "points": {"WIS": 1}},
                {"text": "Educación estricta", "event": "educacion", "points": {"INT": 1, "class_monk": 1}},
                {"text": "Aventura", "event": "aventura", "points": {"DEX": 1}},
                {"text": "Nada especial", "event": "normal", "points": {"CON": 1}}
            ]
        },
        {
            "id": 12,
            "question": "¿Quién fue tu mayor influencia?",
            "options": [
                {"text": "Padre", "influence": "padre", "points": {"STR": 1}},
                {"text": "Madre", "influence": "madre", "points": {"CON": 1}},
                {"text": "Maestro", "influence": "maestro", "points": {"INT": 1, "class_wizard": 1}},
                {"text": "Amigo", "influence": "amigo", "points": {"CHA": 1}},
                {"text": "Rival", "influence": "rival", "points": {"DEX": 1}},
                {"text": "Nadie", "influence": "nadie", "points": {"WIS": 1}}
            ]
        },
        # PHASE V: PERSONALIDAD
        {
            "id": 13,
            "question": "¿Cuál describe mejor a tu personaje?",
            "options": [
                {"text": "Valiente", "trait": "Valiente", "points": {"STR": 1, "class_fighter": 1, "class_paladin": 1}},
                {"text": "Astuto", "trait": "Astuto", "points": {"DEX": 1, "class_rogue": 1}},
                {"text": "Curioso", "trait": "Curioso", "points": {"INT": 1, "class_wizard": 1}},
                {"text": "Compasivo", "trait": "Compasivo", "points": {"WIS": 1, "class_cleric": 1}},
                {"text": "Ambicioso", "trait": "Ambicioso", "points": {"CHA": 1, "class_warlock": 1}},
                {"text": "Disciplinado", "trait": "Disciplinado", "points": {"CON": 1, "class_monk": 1}},
                {"text": "Rebelde", "trait": "Rebelde", "points": {"DEX": 1, "class_barbarian": 1}}
            ]
        },
        {
            "id": 14,
            "question": "¿Cómo reaccionas bajo presión?",
            "options": [
                {"text": "Peleo", "pressure": "luchas con coraje", "points": {"STR": 1, "class_barbarian": 1, "class_fighter": 1}},
                {"text": "Pienso", "pressure": "analizas fríamente", "points": {"INT": 1, "class_wizard": 1}},
                {"text": "Improviso", "pressure": "improvisas rápidamente", "points": {"DEX": 1, "class_rogue": 1}},
                {"text": "Lidero", "pressure": "tomas el mando", "points": {"CHA": 1, "class_paladin": 1}},
                {"text": "Escapo", "pressure": "te retiras tácticamente", "points": {"DEX": 1, "class_ranger": 1}}
            ]
        },
        {
            "id": 15,
            "question": "¿Qué defecto define a tu personaje?",
            "options": [
                {"text": "Orgullo", "flaw": "Orgullo desmedido", "points": {"CHA": 1}},
                {"text": "Ira", "flaw": "Ira incontrolable", "points": {"STR": 1}},
                {"text": "Codicia", "flaw": "Codicia insaciable", "points": {"DEX": 1}},
                {"text": "Miedo", "flaw": "Miedo al fracaso", "points": {"WIS": 1}},
                {"text": "Impulsividad", "flaw": "Impulsividad imprudente", "points": {"DEX": 1}},
                {"text": "Obsesión", "flaw": "Obsesión por cumplir promesas", "points": {"INT": 1}},
                {"text": "Desconfianza", "flaw": "Desconfianza paranoica", "points": {"WIS": 1}}
            ]
        }
    ]

    @staticmethod
    def evaluate_answers(answers: Dict[int, int]) -> Dict[str, Any]:
        """
        Evaluates answers (map of question_id -> option_index) and returns:
        - Narrative Identity (Raza, Clase, Trasfondo, Alineamiento, Motivación, Miedo, Virtud, Defecto, Descripción)
        - Ability scores (STR, DEX, CON, INT, WIS, CHA) starting from base 10.
        - Auto-calibrated recommended game difficulty and balance metrics.
        """
        stats = {"STR": 10, "DEX": 10, "CON": 10, "INT": 10, "WIS": 10, "CHA": 10}
        
        class_weights = {
            "barbarian": 0, "bard": 0, "cleric": 0, "druid": 0,
            "fighter": 0, "monk": 0, "paladin": 0, "ranger": 0,
            "rogue": 0, "sorcerer": 0, "warlock": 0, "wizard": 0
        }

        alignment_matrix = {"law": 0, "chaos": 0, "good": 0, "evil": 0}
        
        # Narrative variables
        motivation = "Supervivencia"
        fear = "Perder la vida"
        virtue = "Curioso"
        flaw = "Desconfianza"
        
        origin = "Aldea"
        childhood_event = "normal"
        influence = "Nadie"

        # Aggregate points
        for q_id, opt_idx in answers.items():
            question = next((q for q in PersonalityQuiz.QUESTIONS if q["id"] == int(q_id)), None)
            if not question or opt_idx >= len(question["options"]):
                continue
                
            opt = question["options"][opt_idx]
            points = opt.get("points", {})
            
            # Save narrative parameters
            if "ideal" in opt: motivation = opt["ideal"]
            if "fear" in opt: fear = opt["fear"]
            if "trait" in opt: virtue = opt["trait"]
            if "flaw" in opt: flaw = opt["flaw"]
            if "origin" in opt: origin = opt["origin"]
            if "event" in opt: childhood_event = opt["event"]
            if "influence" in opt: influence = opt["influence"]
            
            # Sum up alignment
            for align_k in ["law", "chaos", "good", "evil"]:
                alignment_matrix[align_k] += points.get(f"alignment_{align_k}", 0)

            # Sum up classes and stats
            for key, val in points.items():
                if key.startswith("class_"):
                    cls_name = key.replace("class_", "")
                    if cls_name in class_weights:
                        class_weights[cls_name] += val
                elif key in stats:
                    stats[key] += val

        # Determine class based on highest weight
        assigned_cls_key = max(class_weights, key=class_weights.get)
        
        # Class details mappings
        class_mapping = {
            "barbarian": ("Barbarian", "Farmer", "Orc", 12, 14, "STR", "CON", "Bárbaro", "Orco"),
            "bard": ("Bard", "Entertainer", "Elf", 8, 13, "CHA", "DEX", "Bardo", "Elfo"),
            "cleric": ("Cleric", "Acolyte", "Human", 8, 16, "WIS", "CON", "Clérigo", "Humano"),
            "druid": ("Druid", "Guide", "Elf", 8, 12, "WIS", "DEX", "Druida", "Elfo"),
            "fighter": ("Fighter", "Soldier", "Dwarf", 10, 16, "STR", "CON", "Guerrero", "Enano"),
            "monk": ("Monk", "Hermit", "Human", 8, 15, "DEX", "WIS", "Monje", "Humano"),
            "paladin": ("Paladin", "Guard", "Goliath", 10, 16, "STR", "CHA", "Paladín", "Goliac"),
            "ranger": ("Ranger", "Guide", "Elf", 10, 14, "DEX", "WIS", "Explorador", "Elfo"),
            "rogue": ("Rogue", "Criminal", "Halfling", 8, 14, "DEX", "INT", "Pícaro", "Mediano"),
            "sorcerer": ("Sorcerer", "Charlatan", "Tiefling", 6, 12, "CHA", "CON", "Hechicero", "Tiflin"),
            "warlock": ("Warlock", "Merchant", "Tiefling", 8, 13, "CHA", "CON", "Brujo", "Tiflin"),
            "wizard": ("Wizard", "Sage", "Gnome", 6, 12, "INT", "DEX", "Mago", "Gnomo")
        }

        assigned_class, assigned_bg, assigned_race, hp_start, ac_start, primary_stat, sec_stat, class_es, race_es = class_mapping[assigned_cls_key]

        # Stats ASI additions (+2, +1)
        stats[primary_stat] += 2
        stats[sec_stat] += 1
        
        for k in stats:
            stats[k] = max(8, min(18, stats[k]))

        # Calculate HP
        con_mod = (stats["CON"] - 10) // 2
        hp_max = hp_start + con_mod

        # Determine Alignment
        law_chaos = alignment_matrix["law"] - alignment_matrix["chaos"]
        good_evil = alignment_matrix["good"] - alignment_matrix["evil"]
        
        align_lc = "Neutral"
        if law_chaos > 1: align_lc = "Legal"
        elif law_chaos < -1: align_lc = "Caótico"
        
        align_ge = "Neutral"
        if good_evil > 1: align_ge = "Bueno"
        elif good_evil < -1: align_ge = "Malvado"
        
        alignment = f"{align_lc} {align_ge}" if align_lc != "Neutral" or align_ge != "Neutral" else "Neutral Auténtico"

        # Map backgrounds to Spanish
        bg_mapping_es = {
            "Acolyte": "Acólito",
            "Artisan": "Artesano",
            "Charlatan": "Charlatán",
            "Criminal": "Criminal",
            "Entertainer": "Artista",
            "Farmer": "Granjero / Campesino",
            "Guard": "Guardia",
            "Guide": "Guía",
            "Hermit": "Ermitaño",
            "Merchant": "Comerciante",
            "Noble": "Noble",
            "Sage": "Sabio",
            "Sailor": "Marinero",
            "Scribe": "Escriba",
            "Soldier": "Soldado",
            "Wayfarer": "Vagabundo"
        }
        bg_es = bg_mapping_es.get(assigned_bg, assigned_bg)

        # Procedural Description matching Pokémon Mystery Dungeon + Cripta style
        origin_text = {
            "ciudad": "en el bullicio de una gran metrópolis",
            "aldea": "en una humilde aldea de frontera",
            "bosque": "en el susurro cobijante de los bosques primigenios",
            "desierto": "en la implacable inmensidad de las dunas del desierto",
            "montañas": "bajo los picos helados y las rocas de las montañas",
            "academia": "entre los pasillos llenos de polvo de una gran academia",
            "templo": "bajo los cánticos de fe en un templo sagrado",
            "calles": "sobre los adoquines fríos de los callejones más bajos"
        }.get(origin, "en un lugar lejano")

        event_text = {
            "guerra": "donde la guerra arrasó con todo lo que conocía, forjando su temple a fuego",
            "pobreza": "marcado por la pobreza extrema y la necesidad constante de buscar comida",
            "traición": "con el dolor de una gran traición de alguien en quien confiaba plenamente",
            "muerte": "a la sombra de una muerte trágica que cambió su perspectiva de la vida",
            "educacion": "bajo la tutela de una educación severa e inamovible",
            "aventura": "viviendo aventuras desde niño que avivaron su ansia de conocer el mundo",
            "normal": "viviendo una vida sencilla hasta que el llamado del destino tocó su puerta"
        }.get(childhood_event, "teniendo una infancia tranquila")

        influence_text = {
            "padre": "siguiendo los pasos rígidos de su padre",
            "madre": "inspirado por la bondad y fortaleza de su madre",
            "maestro": "guiado por las sabias y misteriosas enseñanzas de su maestro",
            "amigo": "en honor a un gran amigo de la infancia que ya no está",
            "rival": "impulsado por la necesidad constante de superar a su gran rival",
            "nadie": "forjando su propio camino sin la guía de nadie"
        }.get(influence, "siguiendo su propio instinto")

        description = (
            f"Criado {origin_text}, {event_text}. "
            f"Decidió emprender su viaje {influence_text}. Hoy en día, su espíritu se define como "
            f"{virtue.lower()} pero carga con la sombra de un(a) {flaw.lower()}."
        )

        # Run Monte Carlo balance simulation
        simulation = StorySimulator.simulate_campaign_paths(
            num_simulations=5000,
            initial_hp=hp_max,
            armor_class=ac_start,
            difficulty="medium"
        )
        recommended_diff = "medium"
        if simulation["survival_rate"] < 0.40:
            recommended_diff = "easy"
        elif simulation["survival_rate"] > 0.85:
            recommended_diff = "hard"

        return {
            "class": assigned_class,
            "class_es": class_es,
            "race": assigned_race,
            "race_es": race_es,
            "background": assigned_bg,
            "background_es": bg_es,
            "alignment": alignment,
            "ideal": motivation,
            "fear": fear,
            "virtue": virtue,
            "flaw": flaw,
            "description": description,
            "hp_max": hp_max,
            "armor_class": ac_start,
            "stats": stats,
            "simulation_analysis": {
                "survival_rate": simulation["survival_rate"],
                "recommended_difficulty": recommended_diff,
                "avg_combats": simulation["avg_combats_per_run"]
            }
        }
