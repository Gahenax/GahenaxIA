use std::collections::HashMap;
use rusqlite::{params, Connection, Result, Row};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use uuid::Uuid;
use regex::Regex;
use rayon::prelude::*;

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct Campaign {
    pub id: String,
    pub name: String,
    pub system: String,
    pub tone: String,
    pub narrative_summary: Option<String>,
    pub created_at: String,
    pub updated_at: String,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct Character {
    pub id: String,
    pub campaign_id: Option<String>,
    pub name: String,
    pub class: String,
    pub race: String,
    pub background: String,
    pub level: i32,
    pub hp_current: i32,
    pub hp_max: i32,
    pub armor_class: i32,
    pub stats: Value,
    pub inventory: Value,
    pub xp: i32,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct CampaignPage {
    pub page_number: i32,
    pub player_text: String,
    pub dm_text: String,
    pub coordinates: Value,
    pub choices: Value,
    pub mechanics: String,
    pub created_at: String,
}

pub struct CampaignRepository;

impl CampaignRepository {
    pub fn create(conn: &Connection, name: &str, system: &str, tone: &str) -> Result<Campaign> {
        let id = Uuid::new_v4().to_string();
        conn.execute(
            "INSERT INTO campaigns (id, name, system, tone, narrative_summary) VALUES (?, ?, ?, ?, '')",
            params![id, name, system, tone],
        )?;
        Self::get_by_id(conn, &id)
    }

    pub fn get_by_id(conn: &Connection, id: &str) -> Result<Campaign> {
        conn.query_row(
            "SELECT id, name, system, tone, narrative_summary, created_at, updated_at FROM campaigns WHERE id = ?",
            params![id],
            |row| {
                Ok(Campaign {
                    id: row.get(0)?,
                    name: row.get(1)?,
                    system: row.get(2)?,
                    tone: row.get(3)?,
                    narrative_summary: row.get(4)?,
                    created_at: row.get(5)?,
                    updated_at: row.get(6)?,
                })
            },
        )
    }

    pub fn list_all(conn: &Connection) -> Result<Vec<Campaign>> {
        let mut stmt = conn.prepare("SELECT id, name, system, tone, narrative_summary, created_at, updated_at FROM campaigns ORDER BY created_at DESC")?;
        let rows = stmt.query_map([], |row| {
            Ok(Campaign {
                id: row.get(0)?,
                name: row.get(1)?,
                system: row.get(2)?,
                tone: row.get(3)?,
                narrative_summary: row.get(4)?,
                created_at: row.get(5)?,
                updated_at: row.get(6)?,
            })
        })?;
        let mut campaigns = Vec::new();
        for c in rows {
            campaigns.push(c?);
        }
        Ok(campaigns)
    }

    pub fn update_summary(conn: &Connection, id: &str, summary: &str) -> Result<()> {
        conn.execute(
            "UPDATE campaigns SET narrative_summary = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            params![summary, id],
        )?;
        Ok(())
    }
}

pub struct CharacterRepository;

impl CharacterRepository {
    fn map_row(row: &Row) -> Result<Character> {
        let stats_str: String = row.get(10)?;
        let stats: Value = serde_json::from_str(&stats_str).unwrap_or(Value::Null);
        let inv_str: String = row.get(11)?;
        let inventory: Value = serde_json::from_str(&inv_str).unwrap_or(Value::Null);

        Ok(Character {
            id: row.get(0)?,
            campaign_id: row.get(1)?,
            name: row.get(2)?,
            class: row.get(3)?,
            race: row.get(4)?,
            background: row.get(5)?,
            level: row.get(6)?,
            hp_current: row.get(7)?,
            hp_max: row.get(8)?,
            armor_class: row.get(9)?,
            stats,
            inventory,
            xp: row.get(12)?,
        })
    }

    pub fn create(
        conn: &Connection,
        campaign_id: Option<&str>,
        name: &str,
        char_class: &str,
        race: &str,
        background: &str,
        hp_max: i32,
        armor_class: i32,
        stats: &Value,
        inventory: &Value,
    ) -> Result<Character> {
        let id = Uuid::new_v4().to_string();
        let stats_str = stats.to_string();
        let inv_str = inventory.to_string();

        conn.execute(
            "INSERT INTO characters (id, campaign_id, name, class, race, background, level, hp_current, hp_max, armor_class, stats_json, inventory_json, xp)
             VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, 0)",
            params![id, campaign_id, name, char_class, race, background, hp_max, hp_max, armor_class, stats_str, inv_str],
        )?;

        Self::get_by_id(conn, &id)
    }

    pub fn get_by_id(conn: &Connection, id: &str) -> Result<Character> {
        conn.query_row(
            "SELECT id, campaign_id, name, class, race, background, level, hp_current, hp_max, armor_class, stats_json, inventory_json, xp FROM characters WHERE id = ?",
            params![id],
            Self::map_row,
        )
    }

    pub fn get_by_campaign(conn: &Connection, campaign_id: &str) -> Result<Vec<Character>> {
        let mut stmt = conn.prepare(
            "SELECT id, campaign_id, name, class, race, background, level, hp_current, hp_max, armor_class, stats_json, inventory_json, xp FROM characters WHERE campaign_id = ?"
        )?;
        let rows = stmt.query_map(params![campaign_id], Self::map_row)?;
        let mut chars = Vec::new();
        for r in rows {
            chars.push(r?);
        }
        Ok(chars)
    }

    pub fn get_all(conn: &Connection) -> Result<Vec<Character>> {
        let mut stmt = conn.prepare(
            "SELECT id, campaign_id, name, class, race, background, level, hp_current, hp_max, armor_class, stats_json, inventory_json, xp FROM characters"
        )?;
        let rows = stmt.query_map([], Self::map_row)?;
        let mut chars = Vec::new();
        for r in rows {
            chars.push(r?);
        }
        Ok(chars)
    }

    pub fn get_global_characters(conn: &Connection) -> Result<Vec<Character>> {
        let mut stmt = conn.prepare(
            "SELECT id, campaign_id, name, class, race, background, level, hp_current, hp_max, armor_class, stats_json, inventory_json, xp FROM characters WHERE campaign_id IS NULL"
        )?;
        let rows = stmt.query_map([], Self::map_row)?;
        let mut chars = Vec::new();
        for r in rows {
            chars.push(r?);
        }
        Ok(chars)
    }

    pub fn assign_to_campaign(conn: &Connection, char_id: &str, campaign_id: &str) -> Result<bool> {
        let count = conn.execute(
            "UPDATE characters SET campaign_id = ? WHERE id = ?",
            params![campaign_id, char_id],
        )?;
        Ok(count > 0)
    }

    pub fn update_hp(conn: &Connection, char_id: &str, hp: i32) -> Result<bool> {
        let count = conn.execute(
            "UPDATE characters SET hp_current = ? WHERE id = ?",
            params![hp, char_id],
        )?;
        Ok(count > 0)
    }

    pub fn update_xp(conn: &Connection, char_id: &str, xp_gain: i32) -> Result<Value> {
        let char_data = Self::get_by_id(conn, char_id)?;
        let xp_thresholds = [
            0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000, 85000, 100000,
            120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000,
        ];
        let current_xp = char_data.xp + xp_gain;
        let current_level = char_data.level;
        let mut new_level = current_level;
        for (i, &threshold) in xp_thresholds.iter().enumerate() {
            if current_xp >= threshold {
                new_level = (i + 1) as i32;
            }
        }
        conn.execute(
            "UPDATE characters SET xp = ?, level = ? WHERE id = ?",
            params![current_xp, new_level, char_id],
        )?;

        Ok(serde_json::json!({
            "xp": current_xp,
            "level": new_level,
            "leveled_up": new_level > current_level
        }))
    }
}

pub struct DiceRollRepository;

impl DiceRollRepository {
    pub fn save_roll(
        conn: &Connection,
        campaign_id: &str,
        actor_id: &str,
        actor_name: &str,
        formula: &str,
        result: &Value,
    ) -> Result<Value> {
        let roll_id = Uuid::new_v4().to_string();
        let result_str = result.to_string();
        conn.execute(
            "INSERT INTO dice_rolls (id, campaign_id, actor_id, actor_name, formula, result_json) VALUES (?, ?, ?, ?, ?, ?)",
            params![roll_id, campaign_id, actor_id, actor_name, formula, result_str],
        )?;
        Ok(serde_json::json!({
            "id": roll_id,
            "campaign_id": campaign_id,
            "actor_id": actor_id,
            "actor_name": actor_name,
            "formula": formula,
            "result": result
        }))
    }
}

pub struct MessageRepository;

impl MessageRepository {
    pub fn add_message(
        conn: &Connection,
        campaign_id: &str,
        role: &str,
        content: &str,
        character_id: Option<&str>,
        page_number: i32,
        coordinates_json: Option<&str>,
        choices_json: Option<&str>,
        mechanics: Option<&str>,
    ) -> Result<()> {
        let msg_id = Uuid::new_v4().to_string();
        conn.execute(
            "INSERT INTO campaign_messages (id, campaign_id, character_id, role, content, page_number, coordinates_json, choices_json, mechanics, is_active)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)",
            params![
                msg_id,
                campaign_id,
                character_id,
                role,
                content,
                page_number,
                coordinates_json,
                choices_json,
                mechanics
            ],
        )?;
        Ok(())
    }

    pub fn get_recent_history(conn: &Connection, campaign_id: &str, limit: i32) -> Result<Vec<Value>> {
        let mut stmt = conn.prepare(
            "SELECT role, content FROM campaign_messages WHERE campaign_id = ? AND is_active = 1 ORDER BY created_at DESC LIMIT ?"
        )?;
        let rows = stmt.query_map(params![campaign_id, limit], |row| {
            let role: String = row.get(0)?;
            let content: String = row.get(1)?;
            Ok(serde_json::json!({
                "role": role,
                "content": content
            }))
        })?;
        let mut history = Vec::new();
        for r in rows {
            history.push(r?);
        }
        history.reverse();
        Ok(history)
    }

    pub fn get_pages(conn: &Connection, campaign_id: &str) -> Result<Vec<CampaignPage>> {
        let mut stmt = conn.prepare(
            "SELECT role, content, page_number, coordinates_json, choices_json, mechanics, created_at
             FROM campaign_messages WHERE campaign_id = ? AND is_active = 1 ORDER BY page_number ASC, created_at ASC"
        )?;

        let rows = stmt.query_map(params![campaign_id], |row| {
            let role: String = row.get(0)?;
            let content: String = row.get(1)?;
            let page_number: i32 = row.get(2)?;
            let coords_str: Option<String> = row.get(3)?;
            let choices_str: Option<String> = row.get(4)?;
            let mechanics: Option<String> = row.get(5)?;
            let created_at: String = row.get(6)?;

            Ok((role, content, page_number, coords_str, choices_str, mechanics, created_at))
        })?;

        let mut pages_map: HashMap<i32, CampaignPage> = HashMap::new();
        let re_mech = Regex::new(r"\[MECÁNICA:.*?\]").unwrap();

        for r_res in rows {
            let (role, content, page_number, coords_str, choices_str, mechanics_opt, created_at) = r_res?;
            let coords = coords_str
                .and_then(|s| serde_json::from_str(&s).ok())
                .unwrap_or_else(|| serde_json::json!({"x": 2, "y": 4}));
            let choices = choices_str
                .and_then(|s| serde_json::from_str(&s).ok())
                .unwrap_or_else(|| serde_json::json!([]));
            let mechanics = mechanics_opt.unwrap_or_default();

            let entry = pages_map.entry(page_number).or_insert_with(|| CampaignPage {
                page_number,
                player_text: String::new(),
                dm_text: String::new(),
                coordinates: coords.clone(),
                choices: choices.clone(),
                mechanics: mechanics.clone(),
                created_at: created_at.clone(),
            });

            if role == "user" {
                let clean_text = re_mech.replace_all(&content, "").to_string();
                entry.player_text = clean_text.trim().to_string();
            } else {
                entry.dm_text = content;
                if !mechanics.is_empty() {
                    entry.mechanics = mechanics;
                }
                if choices != serde_json::json!([]) {
                    entry.choices = choices;
                }
                if coords != serde_json::json!({"x": 2, "y": 4}) {
                    entry.coordinates = coords;
                }
            }
        }

        let mut pages: Vec<CampaignPage> = pages_map.into_values().collect();
        pages.sort_by_key(|p| p.page_number);
        Ok(pages)
    }

    pub fn rollback_to_page(conn: &Connection, campaign_id: &str, page_number: i32) -> Result<usize> {
        let count = conn.execute(
            "UPDATE campaign_messages SET is_active = 0 WHERE campaign_id = ? AND page_number > ?",
            params![campaign_id, page_number],
        )?;
        Ok(count)
    }
}

pub struct MemoryVectorRepository;

impl MemoryVectorRepository {
    pub fn add_vector(
        conn: &Connection,
        campaign_id: &str,
        content: &str,
        embedding: &[f64],
        source_event_id: Option<&str>,
    ) -> Result<()> {
        let vec_id = Uuid::new_v4().to_string();
        let embedding_val = serde_json::json!(embedding);
        let emb_str = embedding_val.to_string();
        conn.execute(
            "INSERT INTO memory_vectors (id, campaign_id, content, embedding_json, source_event_id) VALUES (?, ?, ?, ?, ?)",
            params![vec_id, campaign_id, content, emb_str, source_event_id],
        )?;
        Ok(())
    }

    pub fn search_similar(
        conn: &Connection,
        campaign_id: &str,
        query_vector: &[f64],
        top_k: usize,
    ) -> Result<Vec<Value>> {
        if query_vector.is_empty() {
            return Ok(Vec::new());
        }

        let mut stmt = conn.prepare(
            "SELECT content, embedding_json FROM memory_vectors WHERE campaign_id = ?"
        )?;
        let rows = stmt.query_map(params![campaign_id], |row| {
            let content: String = row.get(0)?;
            let emb_str: String = row.get(1)?;
            Ok((content, emb_str))
        })?;

        let rows_data: Vec<(String, String)> = rows.filter_map(|r| r.ok()).collect();

        fn cosine_similarity(v1: &[f64], v2: &[f64]) -> f64 {
            let dot: f64 = v1.iter().zip(v2.iter()).map(|(a, b)| a * b).sum();
            let norm1: f64 = v1.iter().map(|x| x * x).sum::<f64>().sqrt();
            let norm2: f64 = v2.iter().map(|x| x * x).sum::<f64>().sqrt();
            if norm1 == 0.0 || norm2 == 0.0 {
                return 0.0;
            }
            dot / (norm1 * norm2)
        }

        let mut scored_results: Vec<Value> = rows_data
            .into_par_iter()
            .filter_map(|(content, emb_str)| {
                if let Ok(Value::Array(arr)) = serde_json::from_str::<Value>(&emb_str) {
                    let db_vector: Vec<f64> = arr.iter().filter_map(|v| v.as_f64()).collect();
                    if db_vector.len() == query_vector.len() {
                        let score = cosine_similarity(query_vector, &db_vector);
                        return Some(serde_json::json!({
                            "content": content,
                            "similarity": score
                        }));
                    }
                }
                None
            })
            .collect();

        // Sort by similarity descending
        scored_results.sort_by(|a, b| {
            let sim_a = a["similarity"].as_f64().unwrap_or(0.0);
            let sim_b = b["similarity"].as_f64().unwrap_or(0.0);
            sim_b.partial_cmp(&sim_a).unwrap_or(std::cmp::Ordering::Equal)
        });

        if scored_results.len() > top_k {
            scored_results.truncate(top_k);
        }

        Ok(scored_results)
    }
}
