import json
import uuid
import re
from typing import List, Dict, Any, Optional
from memory.db_manager import DatabaseManager
import datetime

class CampaignRepository:
    def __init__(self, db: DatabaseManager):
        self.db = db
        self._ensure_columns()

    def _ensure_columns(self):
        conn = self.db.get_connection()
        try:
            conn.execute("ALTER TABLE campaigns ADD COLUMN narrative_summary TEXT;")
            conn.commit()
        except Exception:
            pass
        conn.close()

    def create(self, name: str, system: str, tone: str) -> Dict[str, Any]:
        campaign_id = str(uuid.uuid4())
        query = """
            INSERT INTO campaigns (id, name, system, tone, narrative_summary)
            VALUES (?, ?, ?, ?, '')
        """
        self.db.execute(query, (campaign_id, name, system, tone))
        return self.get_by_id(campaign_id)

    def get_by_id(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM campaigns WHERE id = ?"
        return self.db.fetch_one(query, (campaign_id,))

    def list_all(self) -> List[Dict[str, Any]]:
        query = "SELECT * FROM campaigns ORDER BY created_at DESC"
        return self.db.fetch_all(query)

    def update_summary(self, campaign_id: str, summary: str):
        query = "UPDATE campaigns SET narrative_summary = ? WHERE id = ?"
        self.db.execute(query, (summary, campaign_id))


class CharacterRepository:
    def __init__(self, db: DatabaseManager):
        self.db = db
        self._ensure_nullable_campaign()

    def _ensure_nullable_campaign(self):
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(characters);")
            columns = cursor.fetchall()
            campaign_id_col = next((c for c in columns if c["name"] == "campaign_id"), None)
            
            if campaign_id_col and campaign_id_col["notnull"] == 1:
                print("[Migration] Recreating characters table to make campaign_id nullable...")
                conn.execute("PRAGMA foreign_keys=OFF;")
                conn.execute("BEGIN TRANSACTION;")
                conn.execute("ALTER TABLE characters RENAME TO characters_old;")
                conn.execute("""
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
                        FOREIGN KEY(campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
                    );
                """)
                # Copy existing data
                xp_select = "xp" if any(c["name"] == "xp" for c in columns) else "0"
                conn.execute(f"""
                    INSERT INTO characters (id, campaign_id, name, class, race, background, level, hp_current, hp_max, armor_class, stats_json, inventory_json, xp)
                    SELECT id, campaign_id, name, class, race, background, level, hp_current, hp_max, armor_class, stats_json, inventory_json, {xp_select} FROM characters_old;
                """)
                conn.execute("DROP TABLE characters_old;")
                conn.execute("COMMIT;")
                conn.execute("PRAGMA foreign_keys=ON;")
                print("[Migration] Recreated characters table successfully.")
        except Exception as e:
            print(f"[Migration] Failed to migrate characters table: {e}")
            try:
                conn.execute("ROLLBACK;")
            except Exception:
                pass
        finally:
            conn.close()

    def create(self, campaign_id: Optional[str], name: str, char_class: str, race: str, background: str, hp_max: int, armor_class: int, stats: dict, inventory: dict) -> Dict[str, Any]:
        char_id = str(uuid.uuid4())
        query = """
            INSERT INTO characters (id, campaign_id, name, class, race, background, hp_current, hp_max, armor_class, stats_json, inventory_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.db.execute(query, (
            char_id, campaign_id, name, char_class, race, background, hp_max, hp_max, armor_class,
            json.dumps(stats), json.dumps(inventory)
        ))
        return self.get_by_id(char_id)

    def get_by_id(self, char_id: str) -> Optional[Dict[str, Any]]:
        char = self.db.fetch_one("SELECT * FROM characters WHERE id = ?", (char_id,))
        if char:
            char = dict(char)
            char["stats"] = json.loads(char["stats_json"])
            char["inventory"] = json.loads(char["inventory_json"])
        return char

    def get_by_campaign(self, campaign_id: str) -> List[Dict[str, Any]]:
        chars = self.db.fetch_all("SELECT * FROM characters WHERE campaign_id = ?", (campaign_id,))
        result = []
        for char in chars:
            c = dict(char)
            c["stats"] = json.loads(c["stats_json"])
            c["inventory"] = json.loads(c["inventory_json"])
            result.append(c)
        return result

    def get_all_characters(self) -> List[Dict[str, Any]]:
        chars = self.db.fetch_all("SELECT * FROM characters")
        result = []
        for char in chars:
            c = dict(char)
            c["stats"] = json.loads(c["stats_json"])
            c["inventory"] = json.loads(c["inventory_json"])
            result.append(c)
        return result

    def get_global_characters(self) -> List[Dict[str, Any]]:
        chars = self.db.fetch_all("SELECT * FROM characters WHERE campaign_id IS NULL")
        result = []
        for char in chars:
            c = dict(char)
            c["stats"] = json.loads(c["stats_json"])
            c["inventory"] = json.loads(c["inventory_json"])
            result.append(c)
        return result

    def assign_to_campaign(self, char_id: str, campaign_id: str) -> bool:
        query = "UPDATE characters SET campaign_id = ? WHERE id = ?"
        return self.db.execute(query, (campaign_id, char_id)) > 0

    def update_hp(self, char_id: str, hp: int) -> bool:
        query = "UPDATE characters SET hp_current = ? WHERE id = ?"
        return self.db.execute(query, (hp, char_id)) > 0

    def update_xp(self, char_id: str, xp_gain: int) -> Dict[str, Any]:
        """Increases XP and handles level up (simplified D&D 5e thresholds)."""
        char = self.get_by_id(char_id)
        if not char:
            return {}
        xp_thresholds = [0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000, 85000, 100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000]
        current_xp = char.get("xp", 0) + xp_gain
        current_level = char.get("level", 1)
        new_level = current_level
        for i, threshold in enumerate(xp_thresholds):
            if current_xp >= threshold:
                new_level = i + 1
        query = "UPDATE characters SET xp = ?, level = ? WHERE id = ?"
        self.db.execute(query, (current_xp, new_level, char_id))
        return {"xp": current_xp, "level": new_level, "leveled_up": new_level > current_level}


class DiceRollRepository:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def save_roll(self, campaign_id: str, actor_id: str, actor_name: str, formula: str, result: dict) -> Dict[str, Any]:
        roll_id = str(uuid.uuid4())
        query = """
            INSERT INTO dice_rolls (id, campaign_id, actor_id, actor_name, formula, result_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        self.db.execute(query, (roll_id, campaign_id, actor_id, actor_name, formula, json.dumps(result)))
        return {"id": roll_id, "campaign_id": campaign_id, "actor_id": actor_id, "actor_name": actor_name, "formula": formula, "result": result}


class MessageRepository:
    """Persists campaign message history for LLM context window with book page details."""

    def __init__(self, db: DatabaseManager):
        self.db = db
        self._ensure_table()

    def _ensure_table(self):
        conn = self.db.get_connection()
        conn.execute("""
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
        """)
        # Alter table to add columns if they don't exist (compatibility layer)
        columns = [
            ("page_number", "INTEGER DEFAULT 1"),
            ("coordinates_json", "TEXT"),
            ("choices_json", "TEXT"),
            ("mechanics", "TEXT"),
            ("is_active", "INTEGER DEFAULT 1")
        ]
        for col_name, col_type in columns:
            try:
                conn.execute(f"ALTER TABLE campaign_messages ADD COLUMN {col_name} {col_type};")
            except Exception:
                pass # Column already exists
        try:
            conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_campaign ON campaign_messages (campaign_id, is_active, page_number);")
        except Exception:
            pass
        conn.commit()
        conn.close()

    def add_message(self, campaign_id: str, role: str, content: str, character_id: Optional[str] = None, page_number: int = 1, coordinates_json: Optional[str] = None, choices_json: Optional[str] = None, mechanics: Optional[str] = None) -> None:
        msg_id = str(uuid.uuid4())
        self.db.execute(
            """INSERT INTO campaign_messages (id, campaign_id, character_id, role, content, page_number, coordinates_json, choices_json, mechanics, is_active)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)""",
            (msg_id, campaign_id, character_id, role, content, page_number, coordinates_json, choices_json, mechanics)
        )

    def get_recent_history(self, campaign_id: str, limit: int = 10) -> List[Dict[str, str]]:
        """Returns recent messages formatted for Ollama chat API."""
        rows = self.db.fetch_all(
            "SELECT role, content FROM campaign_messages WHERE campaign_id = ? AND is_active = 1 ORDER BY created_at DESC LIMIT ?",
            (campaign_id, limit)
        )
        # Reverse so oldest first (chronological for LLM context)
        return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]

    def get_pages(self, campaign_id: str) -> List[Dict[str, Any]]:
        """Aggregates player and DM turns into structured pages for Infinite Book layout."""
        rows = self.db.fetch_all(
            "SELECT role, content, page_number, coordinates_json, choices_json, mechanics, created_at FROM campaign_messages WHERE campaign_id = ? AND is_active = 1 ORDER BY page_number ASC, created_at ASC",
            (campaign_id,)
        )
        
        pages = {}
        for r in rows:
            p_num = r["page_number"]
            if p_num not in pages:
                pages[p_num] = {
                    "page_number": p_num,
                    "player_text": "",
                    "dm_text": "",
                    "coordinates": json.loads(r["coordinates_json"]) if r["coordinates_json"] else {"x": 2, "y": 4},
                    "choices": json.loads(r["choices_json"]) if r["choices_json"] else [],
                    "mechanics": r["mechanics"] or "",
                    "created_at": r["created_at"]
                }
            if r["role"] == "user":
                clean_text = re.sub(r'\[MECÁNICA:.*?\]', '', r["content"]).strip()
                pages[p_num]["player_text"] = clean_text
            else:
                pages[p_num]["dm_text"] = r["content"]
                if r["mechanics"]:
                    pages[p_num]["mechanics"] = r["mechanics"]
                if r["choices_json"]:
                    pages[p_num]["choices"] = json.loads(r["choices_json"])
                if r["coordinates_json"]:
                    pages[p_num]["coordinates"] = json.loads(r["coordinates_json"])
                    
        return sorted(list(pages.values()), key=lambda x: x["page_number"])

    def rollback_to_page(self, campaign_id: str, page_number: int) -> int:
        """Deactivates all pages after the specified page number, effectively branching/rolling back."""
        query = "UPDATE campaign_messages SET is_active = 0 WHERE campaign_id = ? AND page_number > ?"
        return self.db.execute(query, (campaign_id, page_number))


class MemoryVectorRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def add_vector(self, campaign_id: str, content: str, embedding: List[float], source_event_id: Optional[str] = None) -> None:
        import uuid
        vec_id = str(uuid.uuid4())
        self.db.execute(
            """INSERT INTO memory_vectors (id, campaign_id, content, embedding_json, source_event_id)
               VALUES (?, ?, ?, ?, ?)""",
            (vec_id, campaign_id, content, json.dumps(embedding), source_event_id)
        )

    def search_similar(self, campaign_id: str, query_vector: List[float], top_k: int = 3) -> List[Dict[str, Any]]:
        if not query_vector:
            return []
            
        def cosine_similarity(v1, v2):
            import math
            dot = sum(a*b for a, b in zip(v1, v2))
            norm1 = math.sqrt(sum(a*a for a in v1))
            norm2 = math.sqrt(sum(a*a for a in v2))
            if norm1 == 0 or norm2 == 0:
                return 0.0
            return dot / (norm1 * norm2)

        rows = self.db.fetch_all(
            "SELECT content, embedding_json FROM memory_vectors WHERE campaign_id = ?",
            (campaign_id,)
        )
        
        scored_results = []
        for r in rows:
            try:
                emb = json.loads(r["embedding_json"])
                sim = cosine_similarity(query_vector, emb)
                scored_results.append({"content": r["content"], "similarity": sim})
            except Exception:
                continue
                
        scored_results.sort(key=lambda x: x["similarity"], reverse=True)
        return scored_results[:top_k]

