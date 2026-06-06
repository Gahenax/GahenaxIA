use std::fs;
use std::path::PathBuf;
use rusqlite::{Connection, Result};

pub fn find_data_dir() -> PathBuf {
    // Search upwards from current working directory or current exe for "app/data" or "data"
    let mut search_paths = Vec::new();
    if let Ok(cwd) = std::env::current_dir() {
        search_paths.push(cwd);
    }
    if let Ok(exe) = std::env::current_exe() {
        if let Some(parent) = exe.parent() {
            search_paths.push(parent.to_path_buf());
        }
    }

    for mut path in search_paths {
        for _ in 0..10 {
            // Check for app/data
            let app_data = path.join("app").join("data");
            if app_data.is_dir() {
                return app_data;
            }
            // Check for direct data folder
            let direct_data = path.join("data");
            if direct_data.is_dir() {
                return direct_data;
            }
            if !path.pop() {
                break;
            }
        }
    }

    // Default fallback to current dir / data
    let fallback = std::env::current_dir().unwrap_or_default().join("data");
    let _ = fs::create_dir_all(&fallback);
    fallback
}

pub fn get_db_path() -> PathBuf {
    find_data_dir().join("campaigns.db")
}

pub fn get_connection() -> Result<Connection> {
    let db_path = get_db_path();
    let conn = Connection::open(db_path)?;
    // Enable WAL mode and foreign keys
    conn.pragma_update(None, "journal_mode", "WAL")?;
    conn.pragma_update(None, "foreign_keys", "ON")?;
    Ok(conn)
}

pub fn init_db() -> Result<()> {
    let conn = get_connection()?;

    // Migration: make campaign_id nullable in characters table if it is currently NOT NULL
    if let Ok(mut stmt) = conn.prepare("PRAGMA table_info(characters)") {
        let mut needs_migration = false;
        if let Ok(mut rows) = stmt.query([]) {
            while let Ok(Some(row)) = rows.next() {
                let name: String = row.get(1)?;
                let notnull: i32 = row.get(3)?;
                if name == "campaign_id" && notnull == 1 {
                    needs_migration = true;
                    break;
                }
            }
        }
        if needs_migration {
            println!("[Database] Migrating characters table to make campaign_id nullable...");
            let migration_sql = r#"
                PRAGMA foreign_keys=OFF;
                CREATE TABLE characters_new (
                    id TEXT PRIMARY KEY,
                    campaign_id TEXT,
                    name TEXT NOT NULL,
                    class TEXT NOT NULL,
                    race TEXT NOT NULL,
                    background TEXT NOT NULL,
                    level INTEGER NOT NULL DEFAULT 1,
                    hp_current INTEGER NOT NULL,
                    hp_max INTEGER NOT NULL,
                    armor_class INTEGER NOT NULL,
                    stats_json TEXT NOT NULL,
                    inventory_json TEXT NOT NULL,
                    xp INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY(campaign_id) REFERENCES campaigns(id) ON DELETE SET NULL
                );
                INSERT INTO characters_new (id, campaign_id, name, class, race, background, level, hp_current, hp_max, armor_class, stats_json, inventory_json, xp)
                SELECT id, campaign_id, name, class, race, background, level, hp_current, hp_max, armor_class, stats_json, inventory_json, COALESCE(xp, 0) FROM characters;
                DROP TABLE characters;
                ALTER TABLE characters_new RENAME TO characters;
                PRAGMA foreign_keys=ON;
            "#;
            let _ = conn.execute_batch(migration_sql);
        }
    }
    
    // Check if schema.sql exists in the resolved data directory
    let schema_file = find_data_dir().join("schema.sql");
    if schema_file.exists() {
        if let Ok(schema_sql) = fs::read_to_string(schema_file) {
            let _ = conn.execute_batch(&schema_sql);
            return Ok(());
        }
    }

    // Fallback embedded schema if schema.sql isn't found
    let fallback_schema = r#"
    CREATE TABLE IF NOT EXISTS campaigns (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        system TEXT NOT NULL,
        tone TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS characters (
        id TEXT PRIMARY KEY,
        campaign_id TEXT,
        name TEXT NOT NULL,
        class TEXT NOT NULL,
        race TEXT NOT NULL,
        background TEXT NOT NULL,
        level INTEGER NOT NULL DEFAULT 1,
        hp_current INTEGER NOT NULL,
        hp_max INTEGER NOT NULL,
        armor_class INTEGER NOT NULL,
        stats_json TEXT NOT NULL,
        inventory_json TEXT NOT NULL,
        xp INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY(campaign_id) REFERENCES campaigns(id) ON DELETE SET NULL
    );
    CREATE TABLE IF NOT EXISTS npcs (
        id TEXT PRIMARY KEY,
        campaign_id TEXT NOT NULL,
        name TEXT NOT NULL,
        role TEXT NOT NULL,
        personality TEXT NOT NULL,
        goal TEXT NOT NULL,
        relationship_score INTEGER DEFAULT 0,
        status TEXT NOT NULL,
        FOREIGN KEY(campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS locations (
        id TEXT PRIMARY KEY,
        campaign_id TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY(campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS quests (
        id TEXT PRIMARY KEY,
        campaign_id TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY(campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS world_events (
        id TEXT PRIMARY KEY,
        campaign_id TEXT NOT NULL,
        session_id TEXT NOT NULL,
        summary TEXT NOT NULL,
        consequence TEXT NOT NULL,
        importance TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS combat_encounters (
        id TEXT PRIMARY KEY,
        campaign_id TEXT NOT NULL,
        status TEXT NOT NULL,
        round INTEGER NOT NULL DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS combatants (
        id TEXT PRIMARY KEY,
        encounter_id TEXT NOT NULL,
        entity_id TEXT NOT NULL,
        entity_type TEXT NOT NULL,
        name TEXT NOT NULL,
        initiative INTEGER NOT NULL,
        hp INTEGER NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY(encounter_id) REFERENCES combat_encounters(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS dice_rolls (
        id TEXT PRIMARY KEY,
        campaign_id TEXT NOT NULL,
        actor_id TEXT NOT NULL,
        actor_name TEXT NOT NULL,
        formula TEXT NOT NULL,
        result_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS memory_vectors (
        id TEXT PRIMARY KEY,
        campaign_id TEXT NOT NULL,
        content TEXT NOT NULL,
        embedding_json TEXT NOT NULL,
        source_event_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS campaign_messages (
        id TEXT PRIMARY KEY,
        campaign_id TEXT NOT NULL,
        character_id TEXT,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        page_number INTEGER DEFAULT 1,
        coordinates_json TEXT,
        choices_json TEXT,
        mechanics TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_characters_campaign_id ON characters(campaign_id);
    CREATE INDEX IF NOT EXISTS idx_npcs_campaign_id ON npcs(campaign_id);
    CREATE INDEX IF NOT EXISTS idx_quests_campaign_id ON quests(campaign_id);
    CREATE INDEX IF NOT EXISTS idx_world_events_campaign_id ON world_events(campaign_id);
    CREATE INDEX IF NOT EXISTS idx_dice_rolls_campaign_id ON dice_rolls(campaign_id);
    CREATE INDEX IF NOT EXISTS idx_memory_vectors_campaign_id ON memory_vectors(campaign_id);
    CREATE INDEX IF NOT EXISTS idx_messages_campaign ON campaign_messages (campaign_id, is_active, page_number);
    "#;

    conn.execute_batch(fallback_schema)?;
    
    // Optional migration to add columns dynamically if needed (similar to repositories._ensure_columns and repositories._ensure_table)
    let _ = conn.execute("ALTER TABLE campaigns ADD COLUMN narrative_summary TEXT;", []);
    let _ = conn.execute("ALTER TABLE characters ADD COLUMN xp INTEGER NOT NULL DEFAULT 0;", []);
    
    Ok(())
}

pub fn load_env_file() {
    let mut search_paths = Vec::new();
    if let Ok(cwd) = std::env::current_dir() {
        search_paths.push(cwd);
    }
    if let Ok(exe) = std::env::current_exe() {
        if let Some(parent) = exe.parent() {
            search_paths.push(parent.to_path_buf());
        }
    }

    let mut env_path = None;
    for mut path in search_paths {
        for _ in 0..10 {
            let p1 = path.join("app").join("sidecar").join("python").join(".env");
            if p1.is_file() {
                env_path = Some(p1);
                break;
            }
            let p2 = path.join("sidecar").join("python").join(".env");
            if p2.is_file() {
                env_path = Some(p2);
                break;
            }
            let p3 = path.join(".env");
            if p3.is_file() {
                env_path = Some(p3);
                break;
            }
            if !path.pop() {
                break;
            }
        }
        if env_path.is_some() {
            break;
        }
    }

    if let Some(path) = env_path {
        println!("[Tauri] Loading .env file from: {:?}", path);
        if let Ok(content) = fs::read_to_string(path) {
            for line in content.lines() {
                let line_trimmed = line.trim();
                if line_trimmed.is_empty() || line_trimmed.starts_with('#') {
                    continue;
                }
                if let Some(idx) = line_trimmed.find('=') {
                    let key = line_trimmed[..idx].trim();
                    let val = line_trimmed[idx + 1..].trim();
                    if !key.is_empty() {
                        std::env::set_var(key, val);
                    }
                }
            }
        }
    } else {
        println!("[Tauri] No .env file found in search paths.");
    }
}
