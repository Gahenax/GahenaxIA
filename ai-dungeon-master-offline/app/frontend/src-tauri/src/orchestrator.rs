use std::collections::HashMap;
use std::fs;
use serde_json::Value;
use uuid::Uuid;
use regex::Regex;
use crate::db::{get_connection, find_data_dir};
use crate::repositories::{
    Campaign, Character, CampaignRepository, CharacterRepository, DiceRollRepository, MessageRepository, MemoryVectorRepository
};
use crate::rules::{DiceEngine, CombatEngine, ProceduralDungeon};
use crate::voice::VoiceService;
use crate::ollama::OllamaClient;

pub struct ContextPruner;

impl ContextPruner {
    pub async fn prune_history(ollama: &OllamaClient, pages: &[Value]) -> String {
        if pages.len() <= 5 {
            return String::new();
        }

        let pages_to_summarize = &pages[0..pages.len() - 4];
        let mut summary_input = Vec::new();
        for page in pages_to_summarize {
            let p_num = page["page_number"].as_i64().unwrap_or(0);
            let player = page["player_text"].as_str().unwrap_or("");
            let dm = page["dm_text"].as_str().unwrap_or("");
            summary_input.push(format!("Página {} - Jugador: {}\nDM: {}", p_num, player, dm));
        }

        let raw_history_text = summary_input.join("\n\n");
        let prompt = format!(
            "Eres el cronista del Dungeon Master. Lee los siguientes acontecimientos de una aventura de rol \
             and escribe un resumen de no más de 3 párrafos en español. Destaca únicamente los logros, \
             tesoros obtenidos, trampas activadas, daños significativos y enemigos derrotados. Mantén el tono fantástico \
             pero sé extremadamente conciso.\n\n\
             {}\n\n\
             Resumen de la Crónica:",
            raw_history_text
        );

        let messages = serde_json::json!([
            {"role": "system", "content": "Eres un cronista preciso y literario. Resumes historias de rol en español."},
            {"role": "user", "content": prompt}
        ]);

        let summary = ollama.generate_chat(messages.as_array().unwrap(), None).await;
        if summary.trim().is_empty() {
            "El aventurero exploró varias cámaras de la cripta, resolviendo combates y trampas en el camino.".to_string()
        } else {
            summary.trim().to_string()
        }
    }
}

pub fn classify_intent_fast(text: &str) -> String {
    let t = text.to_lowercase();
    let meta_keywords = [
        "quiero crear", "nueva campaña", "nuevo personaje", "cómo", "como jugar",
        "qué es", "que es", "reglas", "ayuda", "help", "opciones", "comandos",
        "inventario", "ficha", "stats", "habilidades", "nivel", "experiencia",
        "cuánto", "cuanto", "qué hago", "que hago", "explica", "dime",
        "nueva partida", "empezar", "comenzar", "reiniciar"
    ];
    if meta_keywords.iter().any(|&kw| t.contains(kw)) {
        return "meta_question".to_string();
    }

    let movement_keywords = ["norte", "sur", "este", "oeste", "north", "south", "east", "west", "mover", "ir al", "ir hacia"];
    if movement_keywords.iter().any(|&kw| t.contains(kw)) {
        return "movement_action".to_string();
    }

    let combat_keywords = [
        "atac", "golpe", "golpeo", "hiero", "dispar", "lanzo", "lanza",
        "espada", "arco", "hacha", "daga", "magia", "hechiz", "iniciativa",
        "peleo", "pelea", "mato", "matar", "destruyo", "defiend", "bloqueo",
        "fight", "attack", "strike"
    ];
    if combat_keywords.iter().any(|&kw| t.contains(kw)) {
        return "combat_action".to_string();
    }

    let inventory_keywords = [
        "equipo", "equipar", "uso", "usar", "tomo", "tomar", "poción", "pocion",
        "bebo", "beber", "mochila", "bolsa", "oro", "compro", "vendo", "objeto",
        "item", "arma", "armadura", "escudo"
    ];
    if inventory_keywords.iter().any(|&kw| t.contains(kw)) {
        return "inventory_action".to_string();
    }

    let social_keywords = [
        "hablo", "hablar", "pregunto", "preguntar", "digo", "decir", "grito",
        "gritar", "persuado", "engaño", "intimido", "negocio", "mercader",
        "tabernero", "aldeano", "npc", "personaje"
    ];
    if social_keywords.iter().any(|&kw| t.contains(kw)) {
        return "social_action".to_string();
    }

    let exploration_keywords = [
        "miro", "busco", "buscar", "investigo", "exploro", "abro", "abrir",
        "puerta", "cofre", "trampa", "escondite", "registro", "examino",
        "observo", "voy", "camino", "entro", "entrar", "salgo", "salir",
        "sigo", "norte", "sur", "este", "oeste", "arriba", "abajo"
    ];
    if exploration_keywords.iter().any(|&kw| t.contains(kw)) {
        return "exploration_action".to_string();
    }

    "exploration_action".to_string()
}

pub struct Orchestrator {
    pub ollama: OllamaClient,
    pub voice: VoiceService,
}

impl Orchestrator {
    pub async fn new() -> Self {
        Orchestrator {
            ollama: OllamaClient::new().await,
            voice: VoiceService::new(),
        }
    }

    pub async fn generate_introduction(
        &self,
        campaign: &Campaign,
        character: &Character,
    ) -> String {
        let tone_map = std::collections::HashMap::from([
            ("Epic & Dark Fantasy", "oscuro y épico"),
            ("High Fantasy Comedy", "humorístico y mágico"),
            ("Grimdark & Gritty", "brutal y realista"),
        ]);
        let tone = tone_map.get(campaign.tone.as_str()).unwrap_or(&"épico");

        let tone_instructions = std::collections::HashMap::from([
            ("Epic & Dark Fantasy", "Adopta un estilo literario y cinematográfico de fantasía oscura y sombría. Usa descripciones sensoriales ricas, metáforas solemnes sobre el destino y detalla el eco de las sombras en las ruinas antiguas."),
            ("High Fantasy Comedy", "Adopta un estilo literario dinámico, mágico y ligeramente satírico. Resalta el absurdo de las situaciones, las descripciones coloridas y los detalles extravagantes o cómicos."),
            ("Grimdark & Gritty", "Adopta un estilo crudo, visceral y sumamente realista. Describe texturas ásperas, el frío húmedo, el olor de la sangre, la herrumbre y el agotamiento físico del personaje. Evita el tono heroico clásico."),
        ]);
        let style_instruction = tone_instructions.get(campaign.tone.as_str()).unwrap_or(&"Usa una prosa descriptiva e inmersiva.");

        let system_prompt = format!(
            "Eres el Dungeon Master de D&D 5e. Tono: {}. {} \
             Campaña: '{}' (Estilo Infinite Book/Novela interactiva). \
             Personaje: {} ({} {}, Nv1, Trasfondo: {}). Escribe exclusivamente en español.",
            tone,
            style_instruction,
            campaign.name,
            character.name,
            character.race,
            character.class,
            character.background
        );

        let user_prompt = "Narra el inicio de la aventura de este héroe. El héroe acaba de entrar a la entrada de la cripta y el pesado portal de piedra se cierra a sus espaldas con un eco ensordecedor. Describe el espacio de forma sumamente vívida, sensorial e inmersiva (el olor a piedra vieja y humedad, la luz vacilante de su antorcha, la textura del aire frío). Deja claro el peso del lugar en el personaje según su clase y trasfondo. \n\nEscribe de 2 a 3 párrafos de prosa rica y atmosférica. NO incluyas opciones numéricas, solo la narración y una pregunta final inmersiva sobre qué desea hacer.";

        let messages = serde_json::json!([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]);

        let raw_response = self.ollama.generate_chat(messages.as_array().unwrap(), None).await;
        if raw_response.trim().is_empty() {
            "El portal de piedra se cierra a tus espaldas con un eco ensordecedor. El aire de la cripta es helado y húmedo. Te encuentras en la entrada, sosteniendo tu antorcha. ¿Qué deseas hacer?".to_string()
        } else {
            raw_response.trim().to_string()
        }
    }

    pub fn handle_meta_question(&self, user_message: &str, character: &Value, _campaign: &Value) -> String {
        let t = user_message.to_lowercase();

        if t.contains("crear campaña") || t.contains("nueva campaña") || t.contains("nueva partida") {
            return "⚙️ Para crear una nueva campaña, vuelve al Lobby usando el botón 'Volver al Lobby' \
                    en la esquina superior derecha. Desde ahí puedes crear una nueva gesta con su propio nombre y tono narrativo.".to_string();
        }

        if t.contains("nuevo personaje") || t.contains("crear personaje") || t.contains("crear héroe") {
            return "⚙️ Para crear un nuevo personaje, selecciona una campaña desde el Lobby. \
                    En el panel derecho aparecerá la opción de 'Iniciar Entrevista' (estilo Pokémon Mystery Dungeon) \
                    o crear una ficha manualmente.".to_string();
        }

        if t.contains("inventario") || t.contains("ficha") || t.contains("stats") || t.contains("habilidades") {
            let stats_val = &character["stats"];
            let mut stat_parts = Vec::new();
            if let Some(obj) = stats_val.as_object() {
                for (k, v) in obj {
                    stat_parts.push(format!("{}: {}", k, v));
                }
            }
            let stat_str = if stat_parts.is_empty() { "N/A".to_string() } else { stat_parts.join(" | ") };
            
            return format!(
                "📋 **Ficha de {}**\n\
                 Raza/Clase: {} {} Nv.{}\n\
                 HP: {}/{} | CA: {}\n\
                 Stats: {}\n\
                 Trasfondo: {}",
                character["name"].as_str().unwrap_or("Héroe"),
                character["race"].as_str().unwrap_or("?"),
                character["class"].as_str().unwrap_or("?"),
                character["level"].as_i64().unwrap_or(1),
                character["hp_current"].as_i64().unwrap_or(0),
                character["hp_max"].as_i64().unwrap_or(0),
                character["armor_class"].as_i64().unwrap_or(0),
                stat_str,
                character["background"].as_str().unwrap_or("?")
            );
        }

        if t.contains("cómo") || t.contains("como") || t.contains("ayuda") || t.contains("help") || t.contains("reglas") || t.contains("qué puedo") || t.contains("que puedo") {
            return "🎲 **Comandos disponibles en juego:**\n\
                    • Escribe tu acción en el campo de texto (ej: 'Ataco al orco con mi espada')\n\
                    • Usa el botón 🎙️ para hablar directamente\n\
                    • Los dados se tiran automáticamente según tu acción\n\
                    • Puedes pedir: 'miro alrededor', 'hablo con el tabernero', 'abro el cofre'\n\n\
                    📌 Acciones fuera del juego (crear campaña/personaje) se hacen desde el Lobby.".to_string();
        }

        format!(
            "El Dungeon Master hace una pausa. '{}' — esa es una pregunta interesante, aventurero. \
             Consulta el manual de reglas o usa el menú del Lobby para opciones de campaña. \
             ¿Hay algo más que quieras hacer en el mundo del juego?",
            user_message
        )
    }

    pub async fn process_player_turn(
        &self,
        campaign_id: &str,
        character_id: &str,
        text_input: Option<String>,
        audio_bytes: Option<Vec<u8>>,
    ) -> Result<Value, String> {
        let conn = get_connection().map_err(|e| e.to_string())?;

        // 1. Get player message
        let mut user_message = text_input.unwrap_or_default();
        if let Some(bytes) = audio_bytes {
            let temp_wav = find_data_dir().join(format!("temp_input_{}.wav", Uuid::new_v4()));
            if let Ok(mut f) = fs::File::create(&temp_wav) {
                use std::io::Write;
                let _ = f.write_all(&bytes);
                user_message = self.voice.transcribe(&temp_wav.to_string_lossy());
                let _ = fs::remove_file(temp_wav);
            }
        }
        if user_message.trim().is_empty() {
            user_message = "Miro a mi alrededor.".to_string();
        }

        // 2. Load context
        let campaign = CampaignRepository::get_by_id(&conn, campaign_id).unwrap_or_else(|_| {
            crate::repositories::Campaign {
                id: campaign_id.to_string(),
                name: "La Cripta".to_string(),
                system: "D&D 5.5".to_string(),
                tone: "Epic & Dark Fantasy".to_string(),
                narrative_summary: Some(String::new()),
                created_at: String::new(),
                updated_at: String::new(),
            }
        });
        let campaign_val = serde_json::to_value(&campaign).unwrap();

        let character = CharacterRepository::get_by_id(&conn, character_id).unwrap_or_else(|_| {
            crate::repositories::Character {
                id: character_id.to_string(),
                campaign_id: Some(campaign_id.to_string()),
                name: "Héroe".to_string(),
                class: "Guerrero".to_string(),
                race: "Humano".to_string(),
                background: "Soldado".to_string(),
                level: 1,
                hp_current: 12,
                hp_max: 12,
                armor_class: 15,
                stats: serde_json::json!({"STR": 16, "DEX": 14, "CON": 15, "INT": 10, "WIS": 12, "CHA": 8}),
                inventory: serde_json::json!({}),
                xp: 0,
            }
        });
        let mut character_val = serde_json::to_value(&character).unwrap();

        // Load procedural dungeon
        let dungeon = ProceduralDungeon::new(campaign_id, &campaign.tone, &campaign.name);

        // Load previous pages
        let existing_pages = MessageRepository::get_pages(&conn, campaign_id).unwrap_or_default();
        let current_page = (existing_pages.len() + 1) as i32;

        let mut x = 2;
        let mut y = 4;
        if !existing_pages.is_empty() {
            let last_page = &existing_pages[existing_pages.len() - 1];
            if let Some(coords) = last_page.coordinates.as_object() {
                x = coords.get("x").and_then(|v| v.as_i64()).unwrap_or(2) as usize;
                y = coords.get("y").and_then(|v| v.as_i64()).unwrap_or(4) as usize;
            }
        }

        // 3. Classify intent
        let intent = classify_intent_fast(&user_message);

        // 4. Handle meta questions directly
        if intent == "meta_question" {
            let narrative_response = self.handle_meta_question(&user_message, &character_val, &campaign_val);
            let coords_json = serde_json::json!({"x": x, "y": y}).to_string();
            let _ = MessageRepository::add_message(
                &conn, campaign_id, "user", &user_message, Some(character_id),
                current_page, Some(&coords_json), None, None
            );
            let _ = MessageRepository::add_message(
                &conn, campaign_id, "assistant", &narrative_response, Some(character_id),
                current_page, Some(&coords_json), None, None
            );

            return Ok(serde_json::json!({
                "player_text": user_message,
                "intent": intent,
                "mechanics": "",
                "roll": Value::Null,
                "narrative": narrative_response,
                "audio_file": "",
                "xp_gained": 0,
                "page_number": current_page,
                "coordinates": {"x": x, "y": y},
                "choices": []
            }));
        }

        // 5. Movement processing
        let mut roll_details = Value::Null;
        let mut mechanics_summary = String::new();
        let mut xp_gained = 0;
        let mut moved = false;

        if intent == "movement_action" {
            let t = user_message.to_lowercase();
            let old_x = x;
            let old_y = y;

            if t.contains("norte") || t.contains("north") {
                if y > 0 { y -= 1; moved = true; }
            } else if t.contains("sur") || t.contains("south") {
                if y < 4 { y += 1; moved = true; }
            } else if t.contains("oeste") || t.contains("west") {
                if x > 0 { x -= 1; moved = true; }
            } else if t.contains("este") || t.contains("east") {
                if x < 4 { x += 1; moved = true; }
            }

            if moved {
                mechanics_summary = format!("Te mueves de ({}, {}) a ({}, {}). ", old_x, old_y, x, y);
            } else {
                mechanics_summary = "Un muro de piedra maciza bloquea el paso en esa dirección. ".to_string();
            }
        }

        // Get room details
        let grid_size = 5;
        let mut room = dungeon.rooms[x * grid_size + y].clone();
        let room_desc = format!("Habitación en ({}, {}): '{}'. {}", x, y, room["name"].as_str().unwrap_or(""), room["description"].as_str().unwrap_or(""));

        // 6. Rules & Encounter resolution
        let is_cleared = room["cleared"].as_bool().unwrap_or(false);
        let room_type = room["type"].as_str().unwrap_or("").to_string();

        if (room_type == "combat" || room_type == "boss") && !room["enemies"].as_array().unwrap_or(&vec![]).is_empty() && !is_cleared {
            let enemy = &room["enemies"][0];
            let char_level = character.level;
            let str_val = character.stats["STR"].as_i64().unwrap_or(10) as i32;
            let str_mod = (str_val - 10) / 2;
            let proficiency = 2 + (char_level - 1) / 4;

            let attacker = serde_json::json!({
                "name": character.name,
                "attack_bonus": str_mod + proficiency
            });
            let weapon = serde_json::json!({
                "name": "tu arma",
                "damage_formula": "1d8+3"
            });

            let combat_res = CombatEngine::resolve_attack(&attacker, enemy, &weapon, "normal");
            let roll = &combat_res["attack_roll"];
            roll_details = roll.clone();

            let _ = DiceRollRepository::save_roll(&conn, campaign_id, character_id, &character.name, "1d20+atk", roll);

            let hit_str = if combat_res["hit"].as_bool().unwrap_or(false) { "IMPACTO" } else { "FALLO" };
            let label = if room_type == "boss" { "JEFE FINAL" } else { "Enemigo" };
            
            mechanics_summary.push_str(&format!(
                "Combates contra el {} ({}): Tirada {} vs CA {} → {}. Daño causado: {}. ",
                label,
                enemy["name"].as_str().unwrap_or(""),
                roll["total"].as_i64().unwrap_or(0),
                enemy["armor_class"].as_i64().unwrap_or(10),
                hit_str,
                combat_res["damage_total"].as_i64().unwrap_or(0)
            ));

            if combat_res["hit"].as_bool().unwrap_or(false) {
                xp_gained = if room_type == "boss" { 100 } else { 50 };
                room["cleared"] = Value::Bool(true);
                if room_type == "boss" {
                    mechanics_summary.push_str(" ¡ENEMIGO DERROTADO! Has purificado la cripta de Gahenax.");
                }
            }
        } else if room_type == "trap" && !is_cleared {
            let dex_val = character.stats["DEX"].as_i64().unwrap_or(10) as i32;
            let dex_mod = (dex_val - 10) / 2;
            let roll = DiceEngine::roll("1d20", &format!("{:+}", dex_mod));
            let roll_total = roll.total;
            roll_details = serde_json::to_value(&roll).unwrap_or(Value::Null);

            let dc = room["trap_dc"].as_i64().unwrap_or(12) as i32;
            if roll_total >= dc {
                mechanics_summary.push_str(&format!("¡Esquivas una trampa! Salvación de DEX: {} vs CD {} (Éxito).", roll_total, dc));
                xp_gained = 25;
            } else {
                let damage = DiceEngine::roll("1d6", "normal").total;
                let new_hp = std::cmp::max(0, character.hp_current - damage);
                let _ = CharacterRepository::update_hp(&conn, character_id, new_hp);
                character_val["hp_current"] = Value::Number(new_hp.into());
                mechanics_summary.push_str(&format!("¡Activas una trampa! Salvación de DEX: {} vs CD {} (Fallo). Sufres {} de daño. HP actual: {}.", roll_total, dc, damage, new_hp));
            }
            room["cleared"] = Value::Bool(true);
        } else if room_type == "loot" && !is_cleared {
            let loot_item = room["loot"][0].as_str().unwrap_or("Poción de Curación");
            let gold = room["gold"].as_i64().unwrap_or(15);
            mechanics_summary.push_str(&format!("Encuentras: {} y {} piezas de oro.", loot_item, gold));
            xp_gained = 25;
            room["cleared"] = Value::Bool(true);
        } else if intent == "exploration_action" && !moved {
            let wis_val = character.stats["WIS"].as_i64().unwrap_or(10) as i32;
            let wis_mod = (wis_val - 10) / 2;
            let roll = DiceEngine::roll("1d20", &format!("{:+}", wis_mod));
            roll_details = serde_json::to_value(&roll).unwrap_or(Value::Null);
            let result_str = if roll.total >= 15 { "Éxito notable" } else if roll.total >= 10 { "Éxito parcial" } else { "Sin hallazgos" };
            mechanics_summary.push_str(&format!("Tirada de Percepción: {} → {}.", roll.total, result_str));
        }

        // 7. Retrieve RAG and generate narrative
        let mut history_list = Vec::new();
        for p in &existing_pages {
            history_list.push(serde_json::json!({"role": "user", "content": p.player_text.clone()}));
            history_list.push(serde_json::json!({"role": "assistant", "content": p.dm_text.clone()}));
        }

        let mut relevant_past_events = String::new();
        let query_emb = self.ollama.generate_embeddings(&user_message).await;
        if !query_emb.is_empty() {
            if let Ok(similar_docs) = MemoryVectorRepository::search_similar(&conn, campaign_id, &query_emb, 2) {
                let doc_texts: Vec<&str> = similar_docs.iter().filter_map(|d| d["content"].as_str()).collect();
                relevant_past_events = doc_texts.join(" | ");
            }
        }

        let tone_map = HashMap::from([
            ("Epic & Dark Fantasy", "oscuro y épico"),
            ("High Fantasy Comedy", "humorístico y mágico"),
            ("Grimdark & Gritty", "brutal y realista"),
        ]);
        let tone = tone_map.get(campaign.tone.as_str()).unwrap_or(&"épico");

        let tone_instructions = HashMap::from([
            ("Epic & Dark Fantasy", "Adopta un estilo literario y cinematográfico de fantasía oscura y sombría. Usa descripciones sensoriales ricas, metáforas solemnes sobre el destino y detalla el eco de las sombras en las ruinas antiguas."),
            ("High Fantasy Comedy", "Adopta un estilo literario dinámico, mágico y ligeramente satírico. Resalta el absurdo de las situaciones, las descripciones coloridas y los detalles extravagantes o cómicos de los enemigos."),
            ("Grimdark & Gritty", "Adopta un estilo crudo, visceral y sumamente realista. Describe textures ásperas, el frío húmedo, el olor de la sangre, la herrumbre y el agotamiento físico del personaje. Evita el tono heroico clásico."),
        ]);
        let style_instruction = tone_instructions.get(campaign.tone.as_str()).unwrap_or(&"Usa una prosa descriptiva e inmersiva.");

        let is_boss_cleared = room_type == "boss" && room["cleared"].as_bool().unwrap_or(false);
        let boss_instruction = if is_boss_cleared { " ¡EL ARCHIMAGO ESQUELETO (JEFE FINAL) HA SIDO DERROTADO! Narra la gran victoria del héroe en tono triunfal y dale un cierre autoconclusivo y definitivo a esta aventura en la cripta." } else { "" };

        let campaign_summary = campaign.narrative_summary.clone().unwrap_or_default();
        let summary_block = if !campaign_summary.is_empty() { format!(" RESUMEN ANTERIOR: {}.", campaign_summary) } else { String::new() };
        let rag_block = if !relevant_past_events.is_empty() { format!(" ACONTECIMIENTOS PASADOS RELEVANTES: {}.", relevant_past_events) } else { String::new() };

        let system_prompt = format!(
            "Eres el Dungeon Master de D&D 5e. Tono: {}. {} \
             Campaña: '{}' (Estilo Infinite Book/Novela interactiva).{}{} \
             Personaje: {} ({} {}, Nv{}, HP {}/{}, CA {}). \
             LUGAR ACTUAL: {}. {}",
            tone,
            style_instruction,
            campaign.name,
            summary_block,
            rag_block,
            character.name,
            character.race,
            character.class,
            character.level,
            character_val["hp_current"].as_i64().unwrap_or(12),
            character.hp_max,
            character.armor_class,
            room_desc,
            boss_instruction
        );

        let mut messages = vec![serde_json::json!({"role": "system", "content": system_prompt})];
        // Add limited history
        let recent_history = if history_list.len() > 6 { &history_list[history_list.len() - 6..] } else { &history_list[..] };
        messages.extend_from_slice(recent_history);

        let user_turn = if !mechanics_summary.is_empty() {
            format!("{}\n\n[RESULTADO MECÁNICO: {}]", user_message, mechanics_summary)
        } else {
            user_message.clone()
        };
        messages.push(serde_json::json!({"role": "user", "content": user_turn}));

        let raw_response = self.ollama.generate_chat(&messages, None).await;

        let mut narrative_response = raw_response.clone();
        let mut choices = Vec::new();

        let re_options = Regex::new(r"(?i)\[OPCIONES\]").unwrap();
        if let Some(m) = re_options.find(&raw_response) {
            let split_idx = m.start();
            narrative_response = raw_response[..split_idx].trim().to_string();
            let options_part = raw_response[split_idx + m.as_str().len()..].trim();
            let re_clean = Regex::new(r"^[-*•\d+\.]\s*").unwrap();
            for line in options_part.split('\n') {
                let clean_line = re_clean.replace(line.trim(), "").to_string();
                if !clean_line.is_empty() {
                    choices.push(clean_line);
                }
            }
        }

        // Add embeddings for RAG indexing
        let desc_emb = self.ollama.generate_embeddings(&narrative_response).await;
        if !desc_emb.is_empty() {
            let _ = MemoryVectorRepository::add_vector(&conn, campaign_id, &narrative_response, &desc_emb, None);
        }

        // Fallback choices
        if choices.is_empty() {
            if is_boss_cleared {
                choices.push("Completar gesta con honor (Fin del Episodio)".to_string());
            } else {
                if y > 0 { choices.push("Moverse al Norte".to_string()); }
                if y < 4 { choices.push("Moverse al Sur".to_string()); }
                if x > 0 { choices.push("Moverse al Oeste".to_string()); }
                if x < 4 { choices.push("Moverse al Este".to_string()); }
                choices.push("Registrar la habitación".to_string());
            }
        }

        // 8. Persist turn to SQLite
        let user_stored = if !mechanics_summary.is_empty() {
            format!("{}\n[MECÁNICA: {}]", user_message, mechanics_summary)
        } else {
            user_message.clone()
        };

        let coords_json = serde_json::json!({"x": x, "y": y}).to_string();
        let choices_json = serde_json::json!(choices).to_string();
        let _ = MessageRepository::add_message(
            &conn, campaign_id, "user", &user_stored, Some(character_id),
            current_page, Some(&coords_json), Some(&choices_json), Some(&mechanics_summary)
        );
        let _ = MessageRepository::add_message(
            &conn, campaign_id, "assistant", &narrative_response, Some(character_id),
            current_page, Some(&coords_json), Some(&choices_json), Some(&mechanics_summary)
        );

        // 9. Pruning history summary
        let all_pages_new = MessageRepository::get_pages(&conn, campaign_id).unwrap_or_default();
        let all_pages_val = serde_json::to_value(&all_pages_new).unwrap_or(Value::Null);
        if let Value::Array(ref arr) = all_pages_val {
            if arr.len() >= 5 {
                let new_summary = ContextPruner::prune_history(&self.ollama, arr).await;
                if !new_summary.is_empty() {
                    let _ = CampaignRepository::update_summary(&conn, campaign_id, &new_summary);
                }
            }
        }

        if xp_gained > 0 {
            let _ = CharacterRepository::update_xp(&conn, character_id, xp_gained);
        }

        // 10. Synthesize voice TTS output
        let data_dir = find_data_dir();
        let voices_dir = data_dir.join("voices");
        let _ = fs::create_dir_all(&voices_dir);
        let output_audio_file = voices_dir.join(format!("{}.wav", Uuid::new_v4())).to_string_lossy().to_string();
        let _ = self.voice.synthesize(&narrative_response, &output_audio_file);

        Ok(serde_json::json!({
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
        }))
    }
}
