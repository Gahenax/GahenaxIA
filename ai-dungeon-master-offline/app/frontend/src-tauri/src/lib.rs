pub mod db;
pub mod repositories;
pub mod rules;
pub mod voice;
pub mod ollama;
pub mod orchestrator;

use std::collections::HashMap;
use std::fs;
use std::path::Path;
use serde_json::Value;
use tauri::{Manager, State};
use uuid::Uuid;

use db::{get_connection, init_db, find_data_dir, load_env_file};
use repositories::{
    CampaignRepository, CharacterRepository, MessageRepository
};
use rules::{PersonalityQuiz, StorySimulator, ProceduralDungeon};
use orchestrator::Orchestrator;

// State holder for async orchestrator
struct AppState {
    orchestrator: Orchestrator,
}

#[tauri::command]
async fn get_status(state: State<'_, AppState>) -> Result<Value, String> {
    let ollama_ok = state.orchestrator.ollama.is_available().await;
    let whisper_ok = true; // Subprocess check always returns true because helper fallback exists
    let active_model = state.orchestrator.ollama.default_model.lock().unwrap().clone();
    
    let base_dir = find_data_dir();
    let parent = base_dir.parent().unwrap_or(&base_dir);
    let mut piper_path = parent.join("engines").join("piper").join("piper").to_string_lossy().to_string();
    if cfg!(target_os = "windows") && !piper_path.ends_with(".exe") {
        piper_path.push_str(".exe");
    }
    let piper_exists = Path::new(&piper_path).exists();

    Ok(serde_json::json!({
        "status": "online",
        "ollama_available": ollama_ok,
        "ollama_model": active_model,
        "whisper_available": whisper_ok,
        "piper_binary_exists": piper_exists
    }))
}

#[tauri::command]
async fn get_model_status(state: State<'_, AppState>) -> Result<Value, String> {
    let client = reqwest::Client::builder().no_proxy().build().unwrap_or_default();
    let active_model = state.orchestrator.ollama.default_model.lock().unwrap().clone();
    let provider = state.orchestrator.ollama.provider.clone();
    let mut installed = Vec::new();
    
    if provider == "ollama" {
        let url = format!("{}/api/tags", state.orchestrator.ollama.host);
        if let Ok(res) = client.get(&url).send().await {
            if res.status().is_success() {
                if let Ok(val) = res.json::<Value>().await {
                    if let Some(models) = val["models"].as_array() {
                        for m in models {
                            if let Some(name) = m["name"].as_str() {
                                installed.push(name.to_string());
                            }
                        }
                    }
                }
            }
        }
    } else if provider == "openai" {
        installed.push("gpt-4o-mini".to_string());
        installed.push("gpt-4o".to_string());
        installed.push("gpt-3.5-turbo".to_string());
    } else if provider == "groq" {
        installed.push("llama-3.3-70b-versatile".to_string());
        installed.push("llama-3.1-8b-instant".to_string());
        installed.push("mixtral-8x7b-32768".to_string());
    } else {
        installed.push(active_model.clone());
    }

    Ok(serde_json::json!({
        "provider": provider,
        "active_model": active_model,
        "installed_models": installed,
        "is_qwen25": active_model.starts_with("qwen2.5")
    }))
}

#[tauri::command]
async fn set_active_model(state: State<'_, AppState>, model: String) -> Result<Value, String> {
    if let Ok(mut lock) = state.orchestrator.ollama.default_model.lock() {
        *lock = model.clone();
        Ok(serde_json::json!({
            "status": "success",
            "active_model": model
        }))
    } else {
        Err("No se pudo bloquear la configuración de modelos en Rust".to_string())
    }
}

#[tauri::command]
async fn create_campaign(name: String, system: String, tone: String) -> Result<Value, String> {
    let conn = get_connection().map_err(|e| e.to_string())?;
    let campaign = CampaignRepository::create(&conn, &name, &system, &tone).map_err(|e| e.to_string())?;
    Ok(serde_json::to_value(campaign).map_err(|e| e.to_string())?)
}

#[tauri::command]
async fn list_campaigns() -> Result<Value, String> {
    let conn = get_connection().map_err(|e| e.to_string())?;
    let list = CampaignRepository::list_all(&conn).map_err(|e| e.to_string())?;
    Ok(serde_json::to_value(list).map_err(|e| e.to_string())?)
}

#[tauri::command]
async fn create_character(
    campaign_id: Option<String>,
    name: String,
    char_class: String,
    race: String,
    background: String,
    hp_max: i32,
    armor_class: i32,
    stats: Value,
    inventory: Value,
) -> Result<Value, String> {
    let conn = get_connection().map_err(|e| e.to_string())?;
    
    if let Some(ref c_id) = campaign_id {
        let existing = CharacterRepository::get_by_campaign(&conn, c_id).map_err(|e| e.to_string())?;
        if existing.len() >= 6 {
            return Err("La campaña ya tiene el límite máximo de 6 personajes.".to_string());
        }
    }

    let character = CharacterRepository::create(
        &conn,
        campaign_id.as_deref(),
        &name,
        &char_class,
        &race,
        &background,
        hp_max,
        armor_class,
        &stats,
        &inventory,
    ).map_err(|e| e.to_string())?;

    Ok(serde_json::to_value(character).map_err(|e| e.to_string())?)
}

#[tauri::command]
async fn list_all_characters(campaign_id: Option<String>, unassigned_only: bool) -> Result<Value, String> {
    let conn = get_connection().map_err(|e| e.to_string())?;
    let list = if unassigned_only {
        CharacterRepository::get_global_characters(&conn).map_err(|e| e.to_string())?
    } else if let Some(ref c_id) = campaign_id {
        CharacterRepository::get_by_campaign(&conn, c_id).map_err(|e| e.to_string())?
    } else {
        CharacterRepository::get_all(&conn).map_err(|e| e.to_string())?
    };
    Ok(serde_json::to_value(list).map_err(|e| e.to_string())?)
}

#[tauri::command]
async fn assign_character(character_id: String, campaign_id: String) -> Result<Value, String> {
    let conn = get_connection().map_err(|e| e.to_string())?;
    let success = CharacterRepository::assign_to_campaign(&conn, &character_id, &campaign_id).map_err(|e| e.to_string())?;
    if !success {
        return Err("Fallo al asignar personaje a la campaña.".to_string());
    }
    Ok(serde_json::json!({
        "status": "success",
        "character_id": character_id,
        "campaign_id": campaign_id
    }))
}

#[tauri::command]
async fn list_characters(campaign_id: String) -> Result<Value, String> {
    let conn = get_connection().map_err(|e| e.to_string())?;
    let list = CharacterRepository::get_by_campaign(&conn, &campaign_id).map_err(|e| e.to_string())?;
    Ok(serde_json::to_value(list).map_err(|e| e.to_string())?)
}

#[tauri::command]
async fn get_campaign_history(campaign_id: String, limit: i32) -> Result<Value, String> {
    let conn = get_connection().map_err(|e| e.to_string())?;
    let history = MessageRepository::get_recent_history(&conn, &campaign_id, limit).map_err(|e| e.to_string())?;
    Ok(serde_json::to_value(history).map_err(|e| e.to_string())?)
}

#[tauri::command]
async fn get_campaign_pages(
    state: State<'_, AppState>,
    campaign_id: String
) -> Result<Value, String> {
    let conn = get_connection().map_err(|e| e.to_string())?;
    let mut pages = MessageRepository::get_pages(&conn, &campaign_id).map_err(|e| e.to_string())?;
    
    if pages.is_empty() {
        if let Ok(chars) = CharacterRepository::get_by_campaign(&conn, &campaign_id) {
            if !chars.is_empty() {
                let character = &chars[0];
                if let Ok(campaign) = CampaignRepository::get_by_id(&conn, &campaign_id) {
                    let intro = state.orchestrator.generate_introduction(&campaign, character).await;
                    let coords_json = serde_json::json!({"x": 2, "y": 4}).to_string();
                    let choices = vec![
                        "Moverse al Norte".to_string(),
                        "Moverse al Sur".to_string(),
                        "Moverse al Este".to_string(),
                        "Moverse al Oeste".to_string(),
                        "Registrar la habitación".to_string()
                    ];
                    let choices_json = serde_json::json!(choices).to_string();
                    
                    let _ = MessageRepository::add_message(
                        &conn, &campaign_id, "assistant", &intro, Some(&character.id),
                        1, Some(&coords_json), Some(&choices_json), Some("")
                    );
                    
                    if let Ok(updated_pages) = MessageRepository::get_pages(&conn, &campaign_id) {
                        pages = updated_pages;
                    }
                }
            }
        }
    }
    
    Ok(serde_json::to_value(pages).map_err(|e| e.to_string())?)
}

#[tauri::command]
async fn get_campaign_map(campaign_id: String) -> Result<Value, String> {
    let conn = get_connection().map_err(|e| e.to_string())?;
    let campaign = CampaignRepository::get_by_id(&conn, &campaign_id).map_err(|e| e.to_string())?;
    let dungeon = ProceduralDungeon::new(&campaign_id, &campaign.tone, &campaign.name);
    Ok(serde_json::to_value(dungeon.rooms).map_err(|e| e.to_string())?)
}

#[tauri::command]
async fn rollback_campaign(campaign_id: String, page_number: i32) -> Result<Value, String> {
    let conn = get_connection().map_err(|e| e.to_string())?;
    let count = MessageRepository::rollback_to_page(&conn, &campaign_id, page_number).map_err(|e| e.to_string())?;
    Ok(serde_json::json!({
        "status": "success",
        "deactivated_pages": count,
        "rollback_to": page_number
    }))
}

#[tauri::command]
async fn process_turn(
    state: State<'_, AppState>,
    campaign_id: String,
    character_id: String,
    text_input: Option<String>,
    audio_bytes: Option<Vec<u8>>,
) -> Result<Value, String> {
    state.orchestrator.process_player_turn(&campaign_id, &character_id, text_input, audio_bytes).await
}

#[tauri::command]
async fn get_audio_base64(path: String) -> Result<String, String> {
    use base64::{Engine as _, engine::general_purpose};
    let bytes = fs::read(&path).map_err(|e| e.to_string())?;
    let b64 = general_purpose::STANDARD.encode(bytes);
    Ok(format!("data:audio/wav;base64,{}", b64))
}

#[tauri::command]
async fn synthesize_tts(state: State<'_, AppState>, text: String) -> Result<String, String> {
    let data_dir = find_data_dir();
    let temp_dir = data_dir.join("temp_tts");
    let _ = fs::create_dir_all(&temp_dir);
    let output_wav_path = temp_dir.join(format!("tts_{}.wav", Uuid::new_v4().simple())).to_string_lossy().to_string();
    
    state.orchestrator.voice.synthesize(&text, &output_wav_path).map_err(|e| e.to_string())
}

#[tauri::command]
async fn run_story_simulation(
    num_simulations: usize,
    initial_hp: i32,
    armor_class: i32,
    difficulty: String,
) -> Result<Value, String> {
    Ok(StorySimulator::simulate_campaign_paths(
        num_simulations,
        initial_hp,
        armor_class,
        &difficulty,
    ))
}

#[tauri::command]
async fn get_quiz_questions() -> Result<Value, String> {
    Ok(PersonalityQuiz::get_questions())
}

#[tauri::command]
async fn evaluate_quiz(answers: HashMap<String, usize>) -> Result<Value, String> {
    Ok(PersonalityQuiz::evaluate_answers(answers))
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    // 0. Load environment variables from .env file
    load_env_file();

    // 1. Initialize DB and schema migrations synchronously on startup
    init_db().expect("Failed to initialize offline database schema");

    tauri::Builder::default()
        .setup(|app| {
            // Register app state holding active Orchestrator client
            let app_handle = app.handle().clone();
            tauri::async_runtime::block_on(async move {
                let orchestrator = Orchestrator::new().await;
                app_handle.manage(AppState { orchestrator });
            });
            
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            get_status,
            get_model_status,
            set_active_model,
            create_campaign,
            list_campaigns,
            create_character,
            list_all_characters,
            assign_character,
            list_characters,
            get_campaign_history,
            get_campaign_pages,
            get_campaign_map,
            rollback_campaign,
            process_turn,
            get_audio_base64,
            synthesize_tts,
            run_story_simulation,
            get_quiz_questions,
            evaluate_quiz
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
