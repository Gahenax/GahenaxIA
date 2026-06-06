-- SQLite Database Schema for Cripta Offline

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
    stats_json TEXT NOT NULL, -- JSON string containing ability scores (STR, DEX, etc.)
    inventory_json TEXT NOT NULL, -- JSON string containing items, weapons, gold
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
    status TEXT NOT NULL, -- 'alive', 'dead', 'hostile', 'friendly'
    FOREIGN KEY(campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS locations (
    id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL, -- 'visited', 'unvisited', 'destroyed'
    FOREIGN KEY(campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quests (
    id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL, -- 'active', 'completed', 'failed'
    FOREIGN KEY(campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS world_events (
    id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    summary TEXT NOT NULL,
    consequence TEXT NOT NULL,
    importance TEXT NOT NULL, -- 'low', 'medium', 'high', 'critical'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS combat_encounters (
    id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL,
    status TEXT NOT NULL, -- 'active', 'finished'
    round INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS combatants (
    id TEXT PRIMARY KEY,
    encounter_id TEXT NOT NULL,
    entity_id TEXT NOT NULL, -- refers to characters.id or npc/monster identifier
    entity_type TEXT NOT NULL, -- 'character', 'npc'
    name TEXT NOT NULL,
    initiative INTEGER NOT NULL,
    hp INTEGER NOT NULL,
    status TEXT NOT NULL, -- 'alive', 'unconscious', 'dead'
    FOREIGN KEY(encounter_id) REFERENCES combat_encounters(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS dice_rolls (
    id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    actor_name TEXT NOT NULL,
    formula TEXT NOT NULL,
    result_json TEXT NOT NULL, -- full result details
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS memory_vectors (
    id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding_json TEXT NOT NULL, -- JSON list of floats for vector search
    source_event_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
);

-- Optimization indexes
CREATE INDEX IF NOT EXISTS idx_characters_campaign_id ON characters(campaign_id);
CREATE INDEX IF NOT EXISTS idx_npcs_campaign_id ON npcs(campaign_id);
CREATE INDEX IF NOT EXISTS idx_quests_campaign_id ON quests(campaign_id);
CREATE INDEX IF NOT EXISTS idx_world_events_campaign_id ON world_events(campaign_id);
CREATE INDEX IF NOT EXISTS idx_dice_rolls_campaign_id ON dice_rolls(campaign_id);
CREATE INDEX IF NOT EXISTS idx_memory_vectors_campaign_id ON memory_vectors(campaign_id);
