use std::collections::HashMap;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use rand::{Rng, SeedableRng};
use rand::rngs::StdRng;
use regex::Regex;
use crate::db::find_data_dir;

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct RollResult {
    pub formula: String,
    pub rolls: Vec<i32>,
    pub selected_raw: i32,
    pub modifier: i32,
    pub total: i32,
    pub sides: i32,
    pub num_dice: i32,
    pub advantage_mode: String,
    pub reason: String,
    pub is_critical_hit: bool,
    pub is_critical_fail: bool,
}

pub struct DiceEngine;

impl DiceEngine {
    pub fn roll(formula: &str, advantage_mode: &str) -> RollResult {
        let mut rng = rand::thread_rng();
        let formula_clean: String = formula.replace(' ', "").to_lowercase();
        
        let re = Regex::new(r"^(?P<num>\d+)?d(?P<sides>\d+)(?:(?P<mod_sign>[+-])(?P<mod_val>\d+))?$").unwrap();
        
        let (num, sides, mod_sign, mod_val) = if let Some(caps) = re.captures(&formula_clean) {
            let num = caps.name("num").map_or(1, |m| m.as_str().parse::<i32>().unwrap_or(1));
            let sides = caps.name("sides").map_or(20, |m| m.as_str().parse::<i32>().unwrap_or(20));
            let mod_sign = caps.name("mod_sign").map_or("+", |m| m.as_str());
            let mod_val = caps.name("mod_val").map_or(0, |m| m.as_str().parse::<i32>().unwrap_or(0));
            (num, sides, mod_sign, mod_val)
        } else {
            (1, 20, "+", 0)
        };

        let mut dice_rolls = Vec::new();
        let selected_result;
        let reason;

        if sides == 20 && num == 1 && (advantage_mode == "advantage" || advantage_mode == "disadvantage") {
            let roll1 = rng.gen_range(1..=20);
            let roll2 = rng.gen_range(1..=20);
            dice_rolls.push(roll1);
            dice_rolls.push(roll2);
            if advantage_mode == "advantage" {
                selected_result = std::cmp::max(roll1, roll2);
                reason = format!("Advantage (max of {} and {})", roll1, roll2);
            } else {
                selected_result = std::cmp::min(roll1, roll2);
                reason = format!("Disadvantage (min of {} and {})", roll1, roll2);
            }
        } else {
            for _ in 0..num {
                dice_rolls.push(rng.gen_range(1..=sides));
            }
            selected_result = dice_rolls.iter().sum();
            reason = "Standard roll".to_string();
        }

        let modifier = if mod_sign == "+" { mod_val } else { -mod_val };
        let total = selected_result + modifier;

        RollResult {
            formula: formula.to_string(),
            rolls: dice_rolls,
            selected_raw: selected_result,
            modifier,
            total,
            sides,
            num_dice: num,
            advantage_mode: advantage_mode.to_string(),
            reason,
            is_critical_hit: sides == 20 && selected_result == 20,
            is_critical_fail: sides == 20 && selected_result == 1,
        }
    }
}

pub struct CombatEngine;

impl CombatEngine {
    pub fn roll_initiative(combatants: &[Value]) -> Vec<Value> {
        let mut active = Vec::new();
        for c in combatants {
            let id = c["id"].as_str().unwrap_or("").to_string();
            let name = c["name"].as_str().unwrap_or("").to_string();
            let entity_type = c["entity_type"].as_str().unwrap_or("character").to_string();
            let dex_mod = c["dex_mod"].as_i64().unwrap_or(0) as i32;
            let hp = c["hp_current"].as_i64().or_else(|| c["hp"].as_i64()).unwrap_or(10) as i32;
            let hp_max = c["hp_max"].as_i64().unwrap_or(10) as i32;
            
            let roll = DiceEngine::roll("1d20", "normal");
            let total = roll.selected_raw + dex_mod;

            active.push(serde_json::json!({
                "entity_id": id,
                "entity_type": entity_type,
                "name": name,
                "initiative": total,
                "hp": hp,
                "hp_max": hp_max,
                "status": "alive"
            }));
        }

        active.sort_by(|a, b| b["initiative"].as_i64().unwrap_or(0).cmp(&a["initiative"].as_i64().unwrap_or(0)));
        active
    }

    pub fn resolve_attack(
        attacker: &Value,
        defender: &Value,
        weapon: &Value,
        advantage_mode: &str,
    ) -> Value {
        let attack_bonus = attacker["attack_bonus"].as_i64().unwrap_or(0) as i32;
        let sign = if attack_bonus >= 0 { "+" } else { "-" };
        let formula = format!("1d20{}{}", sign, attack_bonus.abs());

        let attack_roll = DiceEngine::roll(&formula, advantage_mode);
        let roll_total = attack_roll.total;
        let is_crit = attack_roll.is_critical_hit;
        let is_fail = attack_roll.is_critical_fail;

        let ac = defender["armor_class"].as_i64().or_else(|| defender["ac"].as_i64()).unwrap_or(10) as i32;

        let mut hit = false;
        let mut damage_total = 0;
        let mut damage_roll_val = Value::Null;

        if !is_fail && (is_crit || roll_total >= ac) {
            hit = true;
            let mut damage_formula = weapon["damage_formula"].as_str().unwrap_or("1d6").to_string();
            
            if is_crit {
                damage_formula = Self::double_damage_dice(&damage_formula);
            }

            let damage_roll = DiceEngine::roll(&damage_formula, "normal");
            damage_total = std::cmp::max(1, damage_roll.total);
            damage_roll_val = serde_json::to_value(damage_roll).unwrap_or(Value::Null);
        }

        let defender_prev_hp = defender["hp"].as_i64().unwrap_or(10) as i32;
        let new_hp = std::cmp::max(0, defender_prev_hp - damage_total);
        let status = if new_hp <= 0 {
            if defender["entity_type"].as_str().unwrap_or("") == "npc" { "dead" } else { "unconscious" }
        } else {
            "alive"
        };

        serde_json::json!({
            "attacker": attacker["name"].as_str().unwrap_or(""),
            "defender": defender["name"].as_str().unwrap_or(""),
            "hit": hit,
            "is_critical": is_crit,
            "attack_roll": attack_roll,
            "damage_total": damage_total,
            "damage_roll": damage_roll_val,
            "defender_prev_hp": defender_prev_hp,
            "defender_new_hp": new_hp,
            "defender_status": status,
            "narrative_hint": if is_crit { "Critical hit!" } else if hit { "Hit" } else { "Miss" }
        })
    }

    fn double_damage_dice(formula: &str) -> String {
        let re = Regex::new(r"^\s*(\d+)?(d\d+.*)$").unwrap();
        if let Some(caps) = re.captures(formula) {
            let num = caps.get(1).map_or(1, |m| m.as_str().parse::<i32>().unwrap_or(1));
            let rest = caps.get(2).map_or("", |m| m.as_str());
            return format!("{}{}", num * 2, rest);
        }
        formula.to_string()
    }
}

pub struct StorySimulator;

impl StorySimulator {
    pub fn simulate_campaign_paths(
        num_simulations: usize,
        initial_hp: i32,
        armor_class: i32,
        difficulty: &str,
    ) -> Value {
        let mut rng = rand::thread_rng();
        let mut survival_count = 0;
        let mut death_count = 0;
        let mut total_combat = 0;
        let mut total_traps = 0;
        let mut total_rests = 0;
        let mut hp_remaining_survivors = Vec::new();

        let combat_damage_multiplier = match difficulty {
            "hard" => 1.5,
            "easy" => 0.7,
            _ => 1.0,
        };

        for _ in 0..num_simulations {
            let mut hp = initial_hp;
            let mut is_alive = true;
            let mut combats = 0;
            let mut traps = 0;
            let mut rests = 0;

            for _ in 0..5 {
                if !is_alive {
                    break;
                }

                let roll: f64 = rng.gen();
                if roll < 0.30 {
                    traps += 1;
                    let dex_save = rng.gen_range(1..=20) + 2;
                    if dex_save < 12 {
                        let damage = rng.gen_range(1..=6);
                        hp -= damage;
                        if hp <= 0 {
                            is_alive = false;
                        }
                    }
                } else if roll < 0.70 {
                    combats += 1;
                    let goblin_hit = rng.gen_range(1..=20) + 4;
                    if goblin_hit >= armor_class {
                        let damage = ((rng.gen_range(1..=6) + 2) as f64 * combat_damage_multiplier) as i32;
                        hp -= damage;
                        if hp <= 0 {
                            is_alive = false;
                        }
                    }
                } else {
                    rests += 1;
                    let heal = rng.gen_range(1..=4);
                    hp = std::cmp::min(initial_hp, hp + heal);
                }
            }

            if is_alive {
                survival_count += 1;
                hp_remaining_survivors.push(hp);
            } else {
                death_count += 1;
            }

            total_combat += combats;
            total_traps += traps;
            total_rests += rests;
        }

        let avg_hp_remaining = if !hp_remaining_survivors.is_empty() {
            hp_remaining_survivors.iter().sum::<i32>() as f64 / hp_remaining_survivors.len() as f64
        } else {
            0.0
        };

        serde_json::json!({
            "total_simulations": num_simulations,
            "survival_rate": survival_count as f64 / num_simulations as f64,
            "death_rate": death_count as f64 / num_simulations as f64,
            "avg_combats_per_run": total_combat as f64 / num_simulations as f64,
            "avg_traps_per_run": total_traps as f64 / num_simulations as f64,
            "avg_rests_per_run": total_rests as f64 / num_simulations as f64,
            "avg_hp_remaining_survivors": avg_hp_remaining,
            "difficulty_level": difficulty
        })
    }
}

pub struct PersonalityQuiz;

impl PersonalityQuiz {
    pub fn get_questions() -> Value {
        // Question list matching the original Spanish set
        let raw = r#"[
            {
                "id": 1,
                "question": "¿Qué impulsa a tu personaje?",
                "options": [
                    {"text": "Gloria"},
                    {"text": "Venganza"},
                    {"text": "Conocimiento"},
                    {"text": "Poder"},
                    {"text": "Justicia"},
                    {"text": "Libertad"},
                    {"text": "Riqueza"},
                    {"text": "Proteger a alguien"},
                    {"text": "Supervivencia"}
                ]
            },
            {
                "id": 2,
                "question": "¿Qué teme perder más que su propia vida?",
                "options": [
                    {"text": "Familia"},
                    {"text": "Honor"},
                    {"text": "Libertad"},
                    {"text": "Poder"},
                    {"text": "Identidad"},
                    {"text": "Fe"},
                    {"text": "Conocimiento"},
                    {"text": "Nada"}
                ]
            },
            {
                "id": 3,
                "question": "Si solo pudieras salvar una cosa de un incendio...",
                "options": [
                    {"text": "Un ser querido"},
                    {"text": "Un libro"},
                    {"text": "Un arma"},
                    {"text": "Dinero"},
                    {"text": "Un símbolo importante"},
                    {"text": "A ti mismo"}
                ]
            },
            {
                "id": 4,
                "question": "Encuentras una bolsa con 10.000 monedas. ¿Qué haces?",
                "options": [
                    {"text": "La devuelvo"},
                    {"text": "Busco al dueño y cobro recompensa"},
                    {"text": "Me quedo una parte"},
                    {"text": "Me la quedo toda"}
                ]
            },
            {
                "id": 5,
                "question": "Un enemigo derrotado pide clemencia.",
                "options": [
                    {"text": "Lo perdono"},
                    {"text": "Lo encarcelo"},
                    {"text": "Lo utilizo"},
                    {"text": "Lo ejecuto"}
                ]
            },
            {
                "id": 6,
                "question": "¿Qué pesa más?",
                "options": [
                    {"text": "La ley"},
                    {"text": "La justicia"},
                    {"text": "La lealtad"},
                    {"text": "El resultado"}
                ]
            },
            {
                "id": 7,
                "question": "Un dragón bloquea el camino. ¿Qué haces primero?",
                "options": [
                    {"text": "Hablar"},
                    {"text": "Analizar"},
                    {"text": "Esconderme"},
                    {"text": "Atarcar"}
                ]
            },
            {
                "id": 8,
                "question": "¿Qué rol te gusta cumplir?",
                "options": [
                    {"text": "Protector"},
                    {"text": "Estratega"},
                    {"text": "Explorador"},
                    {"text": "Líder"},
                    {"text": "Asesino"},
                    {"text": "Mago"},
                    {"text": "Soporte"}
                ]
            },
            {
                "id": 9,
                "question": "¿Qué te parece más divertido?",
                "options": [
                    {"text": "Hacer daño"},
                    {"text": "Resolver problemas"},
                    {"text": "Descubrir secretos"},
                    {"text": "Negociar"},
                    {"text": "Liderar"}
                ]
            },
            {
                "id": 10,
                "question": "¿Dónde creciste?",
                "options": [
                    {"text": "Ciudad"},
                    {"text": "Aldea"},
                    {"text": "Bosque"},
                    {"text": "Desierto"},
                    {"text": "Montañas"},
                    {"text": "Academia"},
                    {"text": "Templo"},
                    {"text": "Calles"}
                ]
            },
            {
                "id": 11,
                "question": "¿Qué marcó tu infancia?",
                "options": [
                    {"text": "Guerra"},
                    {"text": "Pobreza"},
                    {"text": "Traición"},
                    {"text": "Muerte"},
                    {"text": "Educación estricta"},
                    {"text": "Aventura"},
                    {"text": "Nada especial"}
                ]
            },
            {
                "id": 12,
                "question": "¿Quién fue tu mayor influencia?",
                "options": [
                    {"text": "Padre"},
                    {"text": "Madre"},
                    {"text": "Maestro"},
                    {"text": "Amigo"},
                    {"text": "Rival"},
                    {"text": "Nadie"}
                ]
            },
            {
                "id": 13,
                "question": "¿Cuál describe mejor a tu personaje?",
                "options": [
                    {"text": "Valiente"},
                    {"text": "Astuto"},
                    {"text": "Curioso"},
                    {"text": "Compasivo"},
                    {"text": "Ambicioso"},
                    {"text": "Disciplinado"},
                    {"text": "Rebelde"}
                ]
            },
            {
                "id": 14,
                "question": "¿Cómo reaccionas bajo presión?",
                "options": [
                    {"text": "Peleo"},
                    {"text": "Pienso"},
                    {"text": "Improviso"},
                    {"text": "Lidero"},
                    {"text": "Escapo"}
                ]
            },
            {
                "id": 15,
                "question": "¿Qué defecto define a tu personaje?",
                "options": [
                    {"text": "Orgullo"},
                    {"text": "Ira"},
                    {"text": "Codicia"},
                    {"text": "Miedo"},
                    {"text": "Impulsividad"},
                    {"text": "Obsesión"},
                    {"text": "Desconfianza"}
                ]
            }
        ]"#;
        serde_json::from_str(raw).unwrap_or(Value::Null)
    }

    pub fn evaluate_answers(answers: HashMap<String, usize>) -> Value {
        let mut stats = HashMap::from([
            ("STR".to_string(), 10),
            ("DEX".to_string(), 10),
            ("CON".to_string(), 10),
            ("INT".to_string(), 10),
            ("WIS".to_string(), 10),
            ("CHA".to_string(), 10),
        ]);

        let mut class_weights = HashMap::from([
            ("barbarian", 0), ("bard", 0), ("cleric", 0), ("druid", 0),
            ("fighter", 0), ("monk", 0), ("paladin", 0), ("ranger", 0),
            ("rogue", 0), ("sorcerer", 0), ("warlock", 0), ("wizard", 0),
        ]);

        let mut align_law = 0;
        let mut align_chaos = 0;
        let mut align_good = 0;
        let mut align_evil = 0;

        let mut motivation = "Supervivencia".to_string();
        let mut fear = "Perder la vida".to_string();
        let mut virtue = "Curioso".to_string();
        let mut flaw = "Desconfianza".to_string();
        let mut origin = "Aldea".to_string();
        let mut childhood_event = "normal".to_string();
        let mut influence = "Nadie".to_string();

        for (q_id_str, opt_idx) in answers {
            let q_id = q_id_str.parse::<i32>().unwrap_or(0);
            
            // Match indices and points manually to mirror Python rules engine perfectly
            match q_id {
                1 => match opt_idx {
                    0 => { motivation = "Gloria".to_string(); *stats.get_mut("CHA").unwrap() += 2; *class_weights.get_mut("fighter").unwrap() += 2; *class_weights.get_mut("bard").unwrap() += 1; },
                    1 => { motivation = "Venganza".to_string(); *stats.get_mut("STR").unwrap() += 2; *class_weights.get_mut("barbarian").unwrap() += 2; *class_weights.get_mut("warlock").unwrap() += 1; },
                    2 => { motivation = "Conocimiento".to_string(); *stats.get_mut("INT").unwrap() += 2; *class_weights.get_mut("wizard").unwrap() += 2; *class_weights.get_mut("druid").unwrap() += 1; },
                    3 => { motivation = "Poder".to_string(); *stats.get_mut("CHA").unwrap() += 1; *stats.get_mut("INT").unwrap() += 1; *class_weights.get_mut("sorcerer").unwrap() += 2; *class_weights.get_mut("warlock").unwrap() += 2; },
                    4 => { motivation = "Justicia".to_string(); *stats.get_mut("WIS").unwrap() += 2; *class_weights.get_mut("paladin").unwrap() += 3; *class_weights.get_mut("cleric").unwrap() += 1; },
                    5 => { motivation = "Libertad".to_string(); *stats.get_mut("DEX").unwrap() += 2; *class_weights.get_mut("ranger").unwrap() += 2; *class_weights.get_mut("rogue").unwrap() += 1; },
                    6 => { motivation = "Riqueza".to_string(); *stats.get_mut("DEX").unwrap() += 1; *stats.get_mut("CHA").unwrap() += 1; *class_weights.get_mut("rogue").unwrap() += 2; *class_weights.get_mut("bard").unwrap() += 1; },
                    7 => { motivation = "Proteger a alguien".to_string(); *stats.get_mut("CON").unwrap() += 2; *class_weights.get_mut("cleric").unwrap() += 2; *class_weights.get_mut("paladin").unwrap() += 2; },
                    8 => { motivation = "Supervivencia".to_string(); *stats.get_mut("CON").unwrap() += 1; *stats.get_mut("WIS").unwrap() += 1; *class_weights.get_mut("barbarian").unwrap() += 1; *class_weights.get_mut("monk").unwrap() += 2; },
                    _ => {}
                },
                2 => match opt_idx {
                    0 => { fear = "Perder a su familia".to_string(); *stats.get_mut("CON").unwrap() += 1; *stats.get_mut("WIS").unwrap() += 1; *class_weights.get_mut("cleric").unwrap() += 1; },
                    1 => { fear = "Perder su honor".to_string(); *stats.get_mut("STR").unwrap() += 1; *class_weights.get_mut("paladin").unwrap() += 2; *class_weights.get_mut("fighter").unwrap() += 1; },
                    2 => { fear = "Perder su libertad".to_string(); *stats.get_mut("DEX").unwrap() += 1; *class_weights.get_mut("ranger").unwrap() += 1; *class_weights.get_mut("rogue").unwrap() += 1; },
                    3 => { fear = "Perder su poder".to_string(); *stats.get_mut("CHA").unwrap() += 1; *class_weights.get_mut("sorcerer").unwrap() += 1; *class_weights.get_mut("warlock").unwrap() += 1; },
                    4 => { fear = "Perder su identidad".to_string(); *stats.get_mut("INT").unwrap() += 1; *class_weights.get_mut("wizard").unwrap() += 1; *class_weights.get_mut("monk").unwrap() += 1; },
                    5 => { fear = "Perder su fe".to_string(); *stats.get_mut("WIS").unwrap() += 2; *class_weights.get_mut("cleric").unwrap() += 2; },
                    6 => { fear = "Perder el conocimiento acumulado".to_string(); *stats.get_mut("INT").unwrap() += 2; *class_weights.get_mut("wizard").unwrap() += 2; },
                    7 => { fear = "No temer a nada".to_string(); *stats.get_mut("STR").unwrap() += 1; *class_weights.get_mut("barbarian").unwrap() += 2; },
                    _ => {}
                },
                3 => match opt_idx {
                    0 => { *stats.get_mut("CON").unwrap() += 2; *class_weights.get_mut("cleric").unwrap() += 1; *class_weights.get_mut("paladin").unwrap() += 1; },
                    1 => { *stats.get_mut("INT").unwrap() += 2; *class_weights.get_mut("wizard").unwrap() += 2; },
                    2 => { *stats.get_mut("STR").unwrap() += 2; *class_weights.get_mut("fighter").unwrap() += 2; *class_weights.get_mut("barbarian").unwrap() += 1; },
                    3 => { *stats.get_mut("CHA").unwrap() += 2; *class_weights.get_mut("rogue").unwrap() += 2; },
                    4 => { *stats.get_mut("WIS").unwrap() += 2; *class_weights.get_mut("cleric").unwrap() += 2; *class_weights.get_mut("monk").unwrap() += 1; },
                    5 => { *stats.get_mut("DEX").unwrap() += 2; *class_weights.get_mut("ranger").unwrap() += 1; *class_weights.get_mut("warlock").unwrap() += 1; },
                    _ => {}
                },
                4 => match opt_idx {
                    0 => { *stats.get_mut("WIS").unwrap() += 1; align_law += 2; align_good += 2; },
                    1 => { *stats.get_mut("CHA").unwrap() += 1; align_law += 1; align_good += 1; },
                    2 => { *stats.get_mut("DEX").unwrap() += 1; },
                    3 => { align_chaos += 2; align_evil += 2; },
                    _ => {}
                },
                5 => match opt_idx {
                    0 => { *stats.get_mut("WIS").unwrap() += 2; align_good += 2; },
                    1 => { align_law += 2; },
                    2 => { *stats.get_mut("INT").unwrap() += 1; align_chaos += 1; align_evil += 1; },
                    3 => { *stats.get_mut("STR").unwrap() += 1; align_chaos += 1; align_evil += 2; },
                    _ => {}
                },
                6 => match opt_idx {
                    0 => { align_law += 3; },
                    1 => { align_good += 2; },
                    2 => { align_law += 1; align_good += 1; },
                    3 => { align_chaos += 2; },
                    _ => {}
                },
                7 => match opt_idx {
                    0 => { *stats.get_mut("CHA").unwrap() += 2; *class_weights.get_mut("bard").unwrap() += 3; *class_weights.get_mut("sorcerer").unwrap() += 1; },
                    1 => { *stats.get_mut("INT").unwrap() += 2; *class_weights.get_mut("wizard").unwrap() += 3; *class_weights.get_mut("monk").unwrap() += 1; },
                    2 => { *stats.get_mut("DEX").unwrap() += 2; *class_weights.get_mut("rogue").unwrap() += 3; *class_weights.get_mut("ranger").unwrap() += 1; },
                    3 => { *stats.get_mut("STR").unwrap() += 2; *class_weights.get_mut("fighter").unwrap() += 2; *class_weights.get_mut("barbarian").unwrap() += 3; },
                    _ => {}
                },
                8 => match opt_idx {
                    0 => { *stats.get_mut("CON").unwrap() += 2; *class_weights.get_mut("fighter").unwrap() += 2; *class_weights.get_mut("paladin").unwrap() += 3; },
                    1 => { *stats.get_mut("INT").unwrap() += 2; *class_weights.get_mut("wizard").unwrap() += 2; *class_weights.get_mut("monk").unwrap() += 1; },
                    2 => { *stats.get_mut("DEX").unwrap() += 2; *class_weights.get_mut("ranger").unwrap() += 3; },
                    3 => { *stats.get_mut("CHA").unwrap() += 2; *class_weights.get_mut("bard").unwrap() += 1; *class_weights.get_mut("paladin").unwrap() += 2; },
                    4 => { *stats.get_mut("DEX").unwrap() += 2; *class_weights.get_mut("rogue").unwrap() += 3; },
                    5 => { *stats.get_mut("INT").unwrap() += 2; *class_weights.get_mut("wizard").unwrap() += 3; },
                    6 => { *stats.get_mut("WIS").unwrap() += 2; *class_weights.get_mut("cleric").unwrap() += 3; *class_weights.get_mut("druid").unwrap() += 2; },
                    _ => {}
                },
                9 => match opt_idx {
                    0 => { *stats.get_mut("STR").unwrap() += 2; *class_weights.get_mut("barbarian").unwrap() += 2; *class_weights.get_mut("fighter").unwrap() += 1; },
                    1 => { *stats.get_mut("INT").unwrap() += 2; *class_weights.get_mut("wizard").unwrap() += 2; *class_weights.get_mut("monk").unwrap() += 1; },
                    2 => { *stats.get_mut("WIS").unwrap() += 2; *class_weights.get_mut("ranger").unwrap() += 1; *class_weights.get_mut("warlock").unwrap() += 2; },
                    3 => { *stats.get_mut("CHA").unwrap() += 2; *class_weights.get_mut("bard").unwrap() += 2; },
                    4 => { *stats.get_mut("CHA").unwrap() += 2; *class_weights.get_mut("paladin").unwrap() += 2; },
                    _ => {}
                },
                10 => match opt_idx {
                    0 => { origin = "ciudad".to_string(); *stats.get_mut("CHA").unwrap() += 1; },
                    1 => { origin = "aldea".to_string(); *stats.get_mut("CON").unwrap() += 1; },
                    2 => { origin = "bosque".to_string(); *stats.get_mut("WIS").unwrap() += 1; *class_weights.get_mut("druid").unwrap() += 1; *class_weights.get_mut("ranger").unwrap() += 1; },
                    3 => { origin = "desierto".to_string(); *stats.get_mut("CON").unwrap() += 1; },
                    4 => { origin = "montañas".to_string(); *stats.get_mut("STR").unwrap() += 1; },
                    5 => { origin = "academia".to_string(); *stats.get_mut("INT").unwrap() += 2; *class_weights.get_mut("wizard").unwrap() += 1; },
                    6 => { origin = "templo".to_string(); *stats.get_mut("WIS").unwrap() += 2; *class_weights.get_mut("cleric").unwrap() += 1; },
                    7 => { origin = "calles".to_string(); *stats.get_mut("DEX").unwrap() += 2; *class_weights.get_mut("rogue").unwrap() += 1; },
                    _ => {}
                },
                11 => match opt_idx {
                    0 => { childhood_event = "guerra".to_string(); *stats.get_mut("STR").unwrap() += 1; *class_weights.get_mut("fighter").unwrap() += 1; },
                    1 => { childhood_event = "pobreza".to_string(); *stats.get_mut("DEX").unwrap() += 1; *class_weights.get_mut("rogue").unwrap() += 1; },
                    2 => { childhood_event = "traición".to_string(); *stats.get_mut("CHA").unwrap() += 1; *class_weights.get_mut("warlock").unwrap() += 1; },
                    3 => { childhood_event = "muerte".to_string(); *stats.get_mut("WIS").unwrap() += 1; },
                    4 => { childhood_event = "educacion".to_string(); *stats.get_mut("INT").unwrap() += 1; *class_weights.get_mut("monk").unwrap() += 1; },
                    5 => { childhood_event = "aventura".to_string(); *stats.get_mut("DEX").unwrap() += 1; },
                    6 => { childhood_event = "normal".to_string(); *stats.get_mut("CON").unwrap() += 1; },
                    _ => {}
                },
                12 => match opt_idx {
                    0 => { influence = "padre".to_string(); *stats.get_mut("STR").unwrap() += 1; },
                    1 => { influence = "madre".to_string(); *stats.get_mut("CON").unwrap() += 1; },
                    2 => { influence = "maestro".to_string(); *stats.get_mut("INT").unwrap() += 1; *class_weights.get_mut("wizard").unwrap() += 1; },
                    3 => { influence = "amigo".to_string(); *stats.get_mut("CHA").unwrap() += 1; },
                    4 => { influence = "rival".to_string(); *stats.get_mut("DEX").unwrap() += 1; },
                    5 => { influence = "nadie".to_string(); *stats.get_mut("WIS").unwrap() += 1; },
                    _ => {}
                },
                13 => match opt_idx {
                    0 => { virtue = "Valiente".to_string(); *stats.get_mut("STR").unwrap() += 1; *class_weights.get_mut("fighter").unwrap() += 1; *class_weights.get_mut("paladin").unwrap() += 1; },
                    1 => { virtue = "Astuto".to_string(); *stats.get_mut("DEX").unwrap() += 1; *class_weights.get_mut("rogue").unwrap() += 1; },
                    2 => { virtue = "Curioso".to_string(); *stats.get_mut("INT").unwrap() += 1; *class_weights.get_mut("wizard").unwrap() += 1; },
                    3 => { virtue = "Compasivo".to_string(); *stats.get_mut("WIS").unwrap() += 1; *class_weights.get_mut("cleric").unwrap() += 1; },
                    4 => { virtue = "Ambicioso".to_string(); *stats.get_mut("CHA").unwrap() += 1; *class_weights.get_mut("warlock").unwrap() += 1; },
                    5 => { virtue = "Disciplinado".to_string(); *stats.get_mut("CON").unwrap() += 1; *class_weights.get_mut("monk").unwrap() += 1; },
                    6 => { virtue = "Rebelde".to_string(); *stats.get_mut("DEX").unwrap() += 1; *class_weights.get_mut("barbarian").unwrap() += 1; },
                    _ => {}
                },
                14 => match opt_idx {
                    0 => { *stats.get_mut("STR").unwrap() += 1; *class_weights.get_mut("barbarian").unwrap() += 1; *class_weights.get_mut("fighter").unwrap() += 1; },
                    1 => { *stats.get_mut("INT").unwrap() += 1; *class_weights.get_mut("wizard").unwrap() += 1; },
                    2 => { *stats.get_mut("DEX").unwrap() += 1; *class_weights.get_mut("rogue").unwrap() += 1; },
                    3 => { *stats.get_mut("CHA").unwrap() += 1; *class_weights.get_mut("paladin").unwrap() += 1; },
                    4 => { *stats.get_mut("DEX").unwrap() += 1; *class_weights.get_mut("ranger").unwrap() += 1; },
                    _ => {}
                },
                15 => match opt_idx {
                    0 => { flaw = "Orgullo desmedido".to_string(); *stats.get_mut("CHA").unwrap() += 1; },
                    1 => { flaw = "Ira incontrolable".to_string(); *stats.get_mut("STR").unwrap() += 1; },
                    2 => { flaw = "Codicia insaciable".to_string(); *stats.get_mut("DEX").unwrap() += 1; },
                    3 => { flaw = "Miedo al fracaso".to_string(); *stats.get_mut("WIS").unwrap() += 1; },
                    4 => { flaw = "Impulsividad imprudente".to_string(); *stats.get_mut("DEX").unwrap() += 1; },
                    5 => { flaw = "Obsesión por cumplir promesas".to_string(); *stats.get_mut("INT").unwrap() += 1; },
                    6 => { flaw = "Desconfianza paranoica".to_string(); *stats.get_mut("WIS").unwrap() += 1; },
                    _ => {}
                },
                _ => {}
            }
        }

        // Determine class based on highest weight
        let mut assigned_cls_key = "fighter";
        let mut max_weight = -1;
        for (k, &w) in &class_weights {
            if w > max_weight {
                max_weight = w;
                assigned_cls_key = k;
            }
        }

        // Class details mappings:
        // (Class, Background, Race, hp_start, ac_start, primary_stat, sec_stat, class_es, race_es)
        let (assigned_class, assigned_bg, assigned_race, hp_start, ac_start, primary_stat, sec_stat, class_es, race_es) = match assigned_cls_key {
            "barbarian" => ("Barbarian", "Farmer", "Orc", 12, 14, "STR", "CON", "Bárbaro", "Orco"),
            "bard" => ("Bard", "Entertainer", "Elf", 8, 13, "CHA", "DEX", "Bardo", "Elfo"),
            "cleric" => ("Cleric", "Acolyte", "Human", 8, 16, "WIS", "CON", "Clérigo", "Humano"),
            "druid" => ("Druid", "Guide", "Elf", 8, 12, "WIS", "DEX", "Druida", "Elfo"),
            "fighter" => ("Fighter", "Soldier", "Dwarf", 10, 16, "STR", "CON", "Guerrero", "Enano"),
            "monk" => ("Monk", "Hermit", "Human", 8, 15, "DEX", "WIS", "Monje", "Humano"),
            "paladin" => ("Paladin", "Guard", "Goliath", 10, 16, "STR", "CHA", "Paladín", "Goliac"),
            "ranger" => ("Ranger", "Guide", "Elf", 10, 14, "DEX", "WIS", "Explorador", "Elfo"),
            "rogue" => ("Rogue", "Criminal", "Halfling", 8, 14, "DEX", "INT", "Pícaro", "Mediano"),
            "sorcerer" => ("Sorcerer", "Charlatan", "Tiefling", 6, 12, "CHA", "CON", "Hechicero", "Tiflin"),
            "warlock" => ("Warlock", "Merchant", "Tiefling", 8, 13, "CHA", "CON", "Brujo", "Tiflin"),
            "wizard" | _ => ("Wizard", "Sage", "Gnome", 6, 12, "INT", "DEX", "Mago", "Gnomo"),
        };

        // Stats ASI additions (+2, +1)
        *stats.get_mut(primary_stat).unwrap() += 2;
        *stats.get_mut(sec_stat).unwrap() += 1;

        for (_, v) in stats.iter_mut() {
            *v = std::cmp::max(8, std::cmp::min(18, *v));
        }

        // Calculate HP
        let con_val = *stats.get("CON").unwrap();
        let con_mod = (con_val - 10) / 2;
        let hp_max = hp_start + con_mod;

        // Determine Alignment
        let law_chaos = align_law - align_chaos;
        let good_evil = align_good - align_evil;

        let align_lc = if law_chaos > 1 { "Legal" } else if law_chaos < -1 { "Caótico" } else { "Neutral" };
        let align_ge = if good_evil > 1 { "Bueno" } else if good_evil < -1 { "Malvado" } else { "Neutral" };

        let alignment = if align_lc != "Neutral" || align_ge != "Neutral" {
            format!("{} {}", align_lc, align_ge)
        } else {
            "Neutral Auténtico".to_string()
        };

        // Map backgrounds to Spanish
        let bg_es = match assigned_bg {
            "Acolyte" => "Acólito",
            "Artisan" => "Artesano",
            "Charlatan" => "Charlatán",
            "Criminal" => "Criminal",
            "Entertainer" => "Artista",
            "Farmer" => "Granjero / Campesino",
            "Guard" => "Guardia",
            "Guide" => "Guía",
            "Hermit" => "Ermitaño",
            "Merchant" => "Comerciante",
            "Noble" => "Noble",
            "Sage" => "Sabio",
            "Sailor" => "Marinero",
            "Scribe" => "Escriba",
            "Soldier" => "Soldado",
            "Wayfarer" | _ => "Vagabundo",
        };

        let origin_text = match origin.as_str() {
            "ciudad" => "en el bullicio de una gran metrópolis",
            "aldea" => "en una humilde aldea de frontera",
            "bosque" => "en el susurro cobijante de los bosques primigenios",
            "desierto" => "en la implacable inmensidad de las dunas del desierto",
            "montañas" => "bajo los picos helados y las rocas de las montañas",
            "academia" => "entre los pasillos llenos de polvo de una gran academia",
            "templo" => "bajo los cánticos de fe en un templo sagrado",
            "calles" | _ => "sobre los adoquines fríos de los callejones más bajos",
        };

        let event_text = match childhood_event.as_str() {
            "guerra" => "donde la guerra arrasó con todo lo que conocía, forjando su temple a fuego",
            "pobreza" => "marcado por la pobreza extrema y la necesidad constante de buscar comida",
            "traición" => "con el dolor de una gran traición de alguien en quien confiaba plenamente",
            "muerte" => "a la sombra de una muerte trágica que cambió su perspectiva de la vida",
            "educacion" => "bajo la tutela de una educación severa e inamovible",
            "aventura" => "viviendo aventuras desde niño que avivaron su ansia de conocer el mundo",
            "normal" | _ => "viviendo una vida sencilla hasta que el llamado del destino tocó su puerta",
        };

        let influence_text = match influence.as_str() {
            "padre" => "siguiendo los pasos rígidos de su padre",
            "madre" => "inspirado por la bondad y fortaleza de su madre",
            "maestro" => "guiado por las sabias y misteriosas enseñanzas de su maestro",
            "amigo" => "en honor a un gran amigo de la infancia que ya no está",
            "rival" => "impulsado por la necesidad constante de superar a su gran rival",
            "nadie" | _ => "forjando su propio camino sin la guía de nadie",
        };

        let description = format!(
            "Criado {}, {}. Decidió emprender su viaje {}. Hoy en día, su espíritu se define como {} pero carga con la sombra de un(a) {}.",
            origin_text, event_text, influence_text, virtue.to_lowercase(), flaw.to_lowercase()
        );

        // Run Monte Carlo balance simulation
        let simulation = StorySimulator::simulate_campaign_paths(5000, hp_max, ac_start, "medium");
        let recommended_diff = if simulation["survival_rate"].as_f64().unwrap_or(0.5) < 0.40 {
            "easy"
        } else if simulation["survival_rate"].as_f64().unwrap_or(0.5) > 0.85 {
            "hard"
        } else {
            "medium"
        };

        serde_json::json!({
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
        })
    }
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct ProceduralDungeon {
    pub campaign_id: String,
    pub seed: u64,
    pub grid_size: usize,
    pub rooms: Vec<Value>,
}

impl ProceduralDungeon {
    fn build_procedural_description(
        r_type: &str,
        enemy_name: &str,
        loot_item: &str,
        rng: &mut StdRng,
    ) -> String {
        let atmospheres_combat = vec![
            "El aire está impregnado de un hedor metálico a sangre fresca.",
            "Un frío antinatural te cala hasta los huesos al cruzar el umbral.",
            "El sonido de cadenas arrastrándose resuena desde las esquinas oscuras.",
            "Un murmullo de rezos blasfemos parece flotar en el aire estancado.",
            "La visibilidad es casi nula debido a una neblina densa y húmeda."
        ];
        let atmospheres_trap = vec![
            "Un silencio tenso e inquietante gobierna cada rincón de la estancia.",
            "Una corriente de aire helado sopla de forma intermitente desde el techo.",
            "El goteo constante de agua ácida corroe lentamente las losas del suelo.",
            "Una extraña quietud te eriza la piel, alertando tus sentidos de explorador.",
            "El ambiente se siente cargado, como si el propio aire contuviera la respiración."
        ];
        let atmospheres_loot = vec![
            "Una tenue luminiscencia dorada se filtra a través de las grietas de la mampostería.",
            "Un reconfortante aroma a sándalo y cera antigua perfuma el ambiente.",
            "El eco del silencio se siente diferente aquí, casi pacífico.",
            "Un rayo de luz espectral ilumina el centro de la cámara, disipando las sombras.",
            "El polvo aquí está removido, revelando marcas de antiguos viajeros mercenarios."
        ];
        let atmospheres_empty = vec![
            "Las sombras parecen estirarse y bailar al ritmo de la llama de tu antorcha.",
            "El polvo acumulado de décadas cubre las baldosas agrietadas.",
            "El viento susurra lamentos incomprensibles a través de las rendijas de los muros.",
            "Una bóveda de columnas rotas y telarañas gruesas se extiende sobre ti.",
            "El eco de tus propios pasos es el único sonido que llena este vacío sepulcral."
        ];

        let structures = vec![
            "Los muros de sillería muestran inscripciones rúnicas desgastadas por el tiempo.",
            "Columnas de mármol negro fracturadas sostienen un techo abovedado a punto de colapsar.",
            "Un canal poco profundo de agua estancada cruza la sala de lado a lado.",
            "El suelo está cubierto de escombros de antiguas estatuas de guerreros decapitados.",
            "Grandes rejas de hierro oxidado cuelgan de las paredes laterales.",
            "Las paredes están cubiertas de una densa capa de líquenes fosforescentes de color azul pálido.",
            "La estancia presenta un relieve tallado en el techo que representa una constelación olvidada."
        ];

        let atmospheres = match r_type {
            "combat" => &atmospheres_combat,
            "trap" => &atmospheres_trap,
            "loot" => &atmospheres_loot,
            _ => &atmospheres_empty,
        };

        let threats = match r_type {
            "combat" => vec![
                format!("Frente a ti, {} emerge de la penumbra listo para atacar.", enemy_name),
                format!("Sientes unos ojos hambrientos observándote; {} te corta el paso.", enemy_name),
                format!("El descanso eterno de {} ha sido interrumpido por tu presencia y ruge furioso.", enemy_name),
                format!("Una figura hostil identificada como {} custodia el centro de la sala alzando sus armas.", enemy_name)
            ],
            "trap" => vec![
                "Percibes una ligera inclinación en las baldosas bajo tus pies y marcas sospechosas en la pared.".to_string(),
                "Finísimos hilos de alambre casi invisibles cruzan a la altura de tus tobillos.".to_string(),
                "Agujeros diminutos en las paredes sugieren un mecanismo de disparo listo para activarse.".to_string(),
                "El suelo en el centro de la sala vibra ligeramente al menor peso.".to_string()
            ],
            "loot" => vec![
                format!("Entre las ruinas, descansa {} junto a un saco de monedas.", loot_item),
                "Un cofre con el escudo de Valdrath se encuentra medio enterrado bajo los escombros.".to_string(),
                format!("Un pedestal de piedra sostiene {} que brilla bajo la penumbra.", loot_item),
                "En una hornacina en la pared, localizas un alijo con provisiones y un cofre de madera.".to_string()
            ],
            _ => vec![
                "A pesar de registrar cada rincón, no encuentras más que ruinas vacías y ecos del pasado.".to_string(),
                "No parece haber amenazas inmediatas aquí, solo el peso del olvido.".to_string(),
                "Una búsqueda rápida confirma que esta cámara fue saqueada hace mucho tiempo.".to_string(),
                "Es un lugar desolado, ideal para recuperar el aliento si el peligro no acechara afuera.".to_string()
            ],
        };

        let atm = atmospheres[rng.gen_range(0..atmospheres.len())];
        let struc = structures[rng.gen_range(0..structures.len())];
        let thr = &threats[rng.gen_range(0..threats.len())];

        format!("{} {} {}", atm, struc, thr)
    }

    pub fn new(campaign_id: &str, tone: &str, name: &str) -> Self {
        // Derive numerical seed from MD5 of campaign_id
        let digest = md5::compute(campaign_id.as_bytes());
        let mut seed_bytes = [0u8; 8];
        seed_bytes.copy_from_slice(&digest.0[0..8]);
        let seed = u64::from_le_bytes(seed_bytes) % 1000000;
        
        let mut rng = StdRng::seed_from_u64(seed);
        let grid_size = 5;

        // Default Room Lists
        let mut combat_names = vec![
            "Fosa de las Almas".to_string(), "Sala de Guardia Profanada".to_string(), "Cámara de la Tortura".to_string(),
            "Nido de Arañas Gigantes".to_string(), "Galería de Estatuas Rotas".to_string(), "Pasillo Inundado de Sangre".to_string()
        ];
        let mut trap_names = vec![
            "Pasadizo de las Cuchillas".to_string(), "Cámara del Gas Asfixiante".to_string(), "Vestíbulo de las Baldosas Falsas".to_string(),
            "Cripta de las Estacas Ocultas".to_string(), "Galería del Fuego Sagrado".to_string()
        ];
        let mut loot_names = vec![
            "Cámara del Tesoro Antiguo".to_string(), "Laboratorio del Alquimista".to_string(), "Armería del Héroe Caído".to_string(),
            "Santuario de la Reliquia Sagrada".to_string(), "Biblioteca de Pergaminos Prohibidos".to_string()
        ];
        let mut empty_names = vec![
            "Pasillo de Piedra Húmeda".to_string(), "Cámara del Eco Silencioso".to_string(), "Cripta Vacía".to_string(),
            "Refugio del Aventurero".to_string(), "Rotonda de las Columnas Caídas".to_string()
        ];

        let mut enemies_pool = vec![
            serde_json::json!({"name": "Duende Asaltante", "hp": 7, "armor_class": 12}),
            serde_json::json!({"name": "Esqueleto Guerrero", "hp": 9, "armor_class": 13}),
            serde_json::json!({"name": "Araña de Cripta", "hp": 11, "armor_class": 11}),
            serde_json::json!({"name": "Zombi Hambriento", "hp": 15, "armor_class": 8}),
            serde_json::json!({"name": "Cultista Oscuro", "hp": 12, "armor_class": 12})
        ];

        let mut loot_pool = vec![
            "Poción de Curación".to_string(), "Anillo de Oro con Rubí".to_string(), "Escudo de Hierro".to_string(),
            "Pergamino de Bola de Fuego".to_string(), "Daga Rúnica (+1)".to_string(), "Llave Antigua de Bronce".to_string()
        ];

        // Scenario file name check matching Python sidecar
        let mut scenario_filename = "crypt.json";
        let tone_lc = tone.to_lowercase();
        let name_lc = name.to_lowercase();
        if name_lc.contains("convergencia") || tone_lc.contains("convergencia") || name_lc.contains("dietrix") || tone_lc.contains("dietrix") {
            scenario_filename = "eon_de_convergencia.json";
        } else if name_lc.contains("forest") || tone_lc.contains("forest") || name_lc.contains("bosque") || tone_lc.contains("bosque") {
            scenario_filename = "forest.json";
        }

        let data_dir = find_data_dir();
        
        // Read custom theme JSON
        let scenario_path = data_dir.join("scenarios").join(scenario_filename);
        if scenario_path.exists() {
            if let Ok(content) = std::fs::read_to_string(scenario_path) {
                if let Ok(val) = serde_json::from_str::<Value>(&content) {
                    if let Some(arr) = val["combat"].as_array() {
                        combat_names = arr.iter().filter_map(|v| v.as_str()).map(|s| s.to_string()).collect();
                    }
                    if let Some(arr) = val["trap"].as_array() {
                        trap_names = arr.iter().filter_map(|v| v.as_str()).map(|s| s.to_string()).collect();
                    }
                    if let Some(arr) = val["loot"].as_array() {
                        loot_names = arr.iter().filter_map(|v| v.as_str()).map(|s| s.to_string()).collect();
                    }
                    if let Some(arr) = val["empty"].as_array() {
                        empty_names = arr.iter().filter_map(|v| v.as_str()).map(|s| s.to_string()).collect();
                    }
                }
            }
        }

        // Read monsters JSON
        let monsters_path = data_dir.join("bestiary").join("monsters.json");
        if monsters_path.exists() {
            if let Ok(content) = std::fs::read_to_string(monsters_path) {
                if let Ok(Value::Array(arr)) = serde_json::from_str::<Value>(&content) {
                    let mut custom_monsters = Vec::new();
                    for item in arr {
                        if let (Some(m_name), Some(hp), Some(ac)) = (item["name"].as_str(), item["hp"].as_i64(), item["armor_class"].as_i64()) {
                            custom_monsters.push(serde_json::json!({
                                "name": m_name,
                                "hp": hp,
                                "armor_class": ac
                            }));
                        }
                    }
                    if !custom_monsters.is_empty() {
                        enemies_pool = custom_monsters;
                    }
                }
            }
        }

        // Read loot JSON
        let loot_path = data_dir.join("loot").join("loot.json");
        if loot_path.exists() {
            if let Ok(content) = std::fs::read_to_string(loot_path) {
                if let Ok(Value::Array(arr)) = serde_json::from_str::<Value>(&content) {
                    let custom_loot: Vec<String> = arr.iter().filter_map(|v| v["name"].as_str()).map(|s| s.to_string()).collect();
                    if !custom_loot.is_empty() {
                        loot_pool = custom_loot;
                    }
                }
            }
        }

        // Generate Grid
        let mut rooms = Vec::new();
        for x in 0..grid_size {
            for y in 0..grid_size {
                let mut room = serde_json::json!({
                    "x": x,
                    "y": y,
                    "name": "Pasillo de Piedra",
                    "type": "empty",
                    "description": "Un pasillo silencioso y húmedo.",
                    "cleared": false,
                    "enemies": [],
                    "loot": [],
                    "trap_dc": 0,
                    "visited": false
                });

                if x == 2 && y == 4 {
                    // Start
                    room["name"] = Value::String("Entrada de la Cripta".to_string());
                    room["type"] = Value::String("start".to_string());
                    room["description"] = Value::String("El portal de piedra se cierra a tus espaldas. El aire es denso y frío.".to_string());
                    room["cleared"] = Value::Bool(true);
                    room["visited"] = Value::Bool(true);
                } else if x == 2 && y == 0 {
                    // Boss
                    room["name"] = Value::String("Cámara del Archimago Esqueleto".to_string());
                    room["type"] = Value::String("boss".to_string());
                    room["description"] = Value::String("Una enorme sala iluminada por fuego verde flotante. En el trono aguarda el soberano de la cripta.".to_string());
                    
                    let mut boss_name = "Archimago Esqueleto".to_string();
                    if !enemies_pool.is_empty() {
                        // Attempt to pick matching boss or toughest monster
                        let found_boss = enemies_pool.iter().find(|e| e["name"].as_str().unwrap_or("").contains("Mímico") || e["name"].as_str().unwrap_or("").contains("Bugbear"));
                        if let Some(b) = found_boss {
                            boss_name = b["name"].as_str().unwrap_or("Archimago Esqueleto").to_string();
                        } else {
                            boss_name = enemies_pool.last().unwrap()["name"].as_str().unwrap_or("Archimago Esqueleto").to_string();
                        }
                    }
                    room["enemies"] = serde_json::json!([{"name": boss_name, "hp": 30, "armor_class": 14}]);
                } else {
                    // Procedural
                    let roll: f64 = rng.gen();
                    if roll < 0.35 {
                        let c_idx = rng.gen_range(0..combat_names.len());
                        let name_str = combat_names[c_idx].clone();
                        let e_idx = rng.gen_range(0..enemies_pool.len());
                        let mut enemy = enemies_pool[e_idx].clone();
                        let hp_mod = rng.gen_range(-2..=3);
                        let current_hp = enemy["hp"].as_i64().unwrap_or(10) as i32;
                        enemy["hp"] = serde_json::json!(std::cmp::max(1, current_hp + hp_mod));
                        
                        room["type"] = Value::String("combat".to_string());
                        room["name"] = Value::String(name_str.to_string());
                        room["enemies"] = serde_json::json!([enemy]);
                        let desc = Self::build_procedural_description("combat", enemy["name"].as_str().unwrap_or(""), "", &mut rng);
                        room["description"] = Value::String(desc);
                    } else if roll < 0.60 {
                        let t_idx = rng.gen_range(0..trap_names.len());
                        let name_str = trap_names[t_idx].clone();
                        let dc = match rng.gen_range(0..4) {
                            0 => 11,
                            1 => 12,
                            2 => 13,
                            _ => 14
                        };
                        room["type"] = Value::String("trap".to_string());
                        room["name"] = Value::String(name_str.to_string());
                        room["trap_dc"] = Value::Number(dc.into());
                        let desc = Self::build_procedural_description("trap", "", "", &mut rng);
                        room["description"] = Value::String(desc);
                    } else if roll < 0.80 {
                        let l_idx = rng.gen_range(0..loot_names.len());
                        let name_str = loot_names[l_idx].clone();
                        let p_idx = rng.gen_range(0..loot_pool.len());
                        let item = loot_pool[p_idx].clone();
                        let gold = rng.gen_range(10..50);
                        
                        room["type"] = Value::String("loot".to_string());
                        room["name"] = Value::String(name_str.to_string());
                        room["loot"] = serde_json::json!([item]);
                        room["gold"] = Value::Number(gold.into());
                        let desc = Self::build_procedural_description("loot", "", &item, &mut rng);
                        room["description"] = Value::String(desc);
                    } else {
                        let e_idx = rng.gen_range(0..empty_names.len());
                        let name_str = empty_names[e_idx].clone();
                        room["type"] = Value::String("empty".to_string());
                        room["name"] = Value::String(name_str.to_string());
                        let desc = Self::build_procedural_description("empty", "", "", &mut rng);
                        room["description"] = Value::String(desc);
                    }
                }

                rooms.push(room);
            }
        }

        ProceduralDungeon {
            campaign_id: campaign_id.to_string(),
            seed,
            grid_size,
            rooms,
        }
    }
}
