import os
import json
import sqlite3
import time
from typing import Dict, Any, List, Optional
from gahenax_hub.utils.uuid_v7 import generate_uuidv7

class JulesBridge:
    """
    Puente de Gahenax hacia el Laboratorio Distribuido JULES.
    Versión persistente (SQLite).
    """
    DB_PATH = "gahenax_hub/sessions/cabal_memory.db"

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or self.DB_PATH
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jules_orders (
                order_id TEXT PRIMARY KEY,
                problem TEXT,
                command TEXT,
                priority INTEGER,
                status TEXT,
                timestamp REAL
            )
        """)
        conn.commit()
        conn.close()

    def create_millennium_order(self, problem: str, block_range: tuple, priority: int = 2) -> str:
        order_id = f"JO-{generate_uuidv7()[:8].upper()}"
        command = f"python labs/{problem.lower()}_sweep.py --range {block_range[0]}-{block_range[1]}"
        
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO jules_orders VALUES (?, ?, ?, ?, ?, ?)",
            (order_id, problem, command, priority, "QUEUED", time.time())
        )
        conn.commit()
        conn.close()
            
        print(f"📦 [JULES] Order {order_id} persisted in DB for {problem}")
        return order_id

    def list_orders(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM jules_orders ORDER BY priority DESC, timestamp ASC")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

# Singleton
jules_bridge = JulesBridge()
