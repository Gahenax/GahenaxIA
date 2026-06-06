import os
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional

DB_FILE_NAME = "campaigns.db"

class DatabaseManager:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Default directory structure: /app/data/campaigns.db relative to sidecar/python/
            base_dir = Path(__file__).resolve().parents[3] # go up: memory -> python -> sidecar -> app
            data_dir = base_dir / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = str(data_dir / DB_FILE_NAME)
            self.schema_path = str(data_dir / "schema.sql")
        else:
            self.db_path = db_path
            self.schema_path = str(Path(db_path).parent / "schema.sql")
            
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        # Enable WAL mode for concurrency and foreign key enforcement
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def init_db(self):
        """Initializes database schema if tables do not exist."""
        conn = self.get_connection()
        try:
            # Try to read schema from the schema.sql file
            if os.path.exists(self.schema_path):
                with open(self.schema_path, "r", encoding="utf-8") as f:
                    schema_sql = f.read()
                conn.executescript(schema_sql)
                conn.commit()
            else:
                # Embedded fallback schema in case file is missing
                fallback_schema = """
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
                    campaign_id TEXT NOT NULL,
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
                    FOREIGN KEY(campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
                );
                """
                conn.executescript(fallback_schema)
                conn.commit()
        finally:
            conn.close()

    def execute(self, query: str, params: tuple = ()) -> int:
        """Executes a write query and returns the number of affected rows."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()

    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Executes a select query and returns all rows as dicts."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Executes a select query and returns a single row as a dict."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_recent_context(self, campaign_id: str, limit: int = 8) -> list:
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT role, content FROM campaign_messages 
                WHERE campaign_id = ? AND is_active = 1
                ORDER BY created_at DESC LIMIT ?
            ''', (campaign_id, limit))
            rows = cursor.fetchall()
            return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]
        finally:
            conn.close()

    def log_action(self, campaign_id: str, action_data: dict):
        role = action_data.get("character_id", "user")
        content = action_data.get("description", "")
        import uuid
        msg_id = str(uuid.uuid4())
        conn = self.get_connection()
        try:
            conn.execute('''
                INSERT INTO campaign_messages (id, campaign_id, role, content, is_active)
                VALUES (?, ?, ?, ?, 1)
            ''', (msg_id, campaign_id, role, content))
            conn.commit()
        finally:
            conn.close()

