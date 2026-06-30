# -*- coding: utf-8 -*-
"""ASTRA Persistence Layer — SQLite v1.0
FPF-structured persistence for autonomous operation.

Tables:
  - chat_history: all conversations (survives restart)
  - session_state: active vault, mode, settings (survives restart)
  - event_log: everything ASTRA does (FPF-structured, timestamped, evidenced)
  - model_registry: AutoModel metrics (survives restart)
  - colony_state: evolution state (survives restart)
  - proposals: FPF Autonomous Loop proposals (survives restart)
  - growth_state: capability levels and evidence (survives restart)
  - system_metrics: CPU/RAM/GPU samples (time series)
  - memory_vector: semantic memory (ChromaDB fallback)

All entries are FPF-structured:
  - R-M-W: role, method, work (A.15)
  - L/A/D/E: classification (A.6.B)
  - F-G-R: formality, scope, reliability (C.2)
  - timestamp, evidence, provenance
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from astra_core.config import PROJECT_ROOT


class ASTRAPersistence:
    """
    FPF-structured SQLite persistence for ASTRA autonomous operation.
    
    A.1: This is a holon — has own boundaries (DB file), 
         participates in ASTRA kernel (reads/writes), 
         and is part of larger system (system state monitoring).
    
    A.15: Role = PersistenceHolon, Method = SQLite CRUD, Work = records saved/retrieved.
    """
    
    DB_PATH = Path(PROJECT_ROOT) / "astra_state.db"
    
    def __init__(self, db_path: Path = None):
        self.db_path = db_path or self.DB_PATH
        self._init_db()
    
    def _init_db(self):
        """Initialize all tables with FPF-structured schema."""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            
            # Chat history — every message survives restart
            c.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    vault TEXT DEFAULT '',
                    mode TEXT DEFAULT 'chat',
                    source_model TEXT DEFAULT '',
                    metadata TEXT DEFAULT '{}'
                )
            """)
            
            # Session state
            c.execute("""
                CREATE TABLE IF NOT EXISTS session_state (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Event log — FPF-structured E-category log
            c.execute("""
                CREATE TABLE IF NOT EXISTS event_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    role TEXT NOT NULL,
                    method TEXT NOT NULL,
                    work_description TEXT NOT NULL,
                    performer TEXT DEFAULT 'ASTRA',
                    formality INTEGER DEFAULT 2,
                    scope TEXT DEFAULT 'G1',
                    assurance TEXT DEFAULT 'LA',
                    lade_class TEXT DEFAULT 'E',
                    holon_affected TEXT DEFAULT '',
                    data_json TEXT DEFAULT '{}',
                    evidence_json TEXT DEFAULT '[]'
                )
            """)
            
            # Model registry
            c.execute("""
                CREATE TABLE IF NOT EXISTS model_registry (
                    model_id TEXT PRIMARY KEY,
                    provider TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    avg_latency_ms REAL DEFAULT 0,
                    success_rate REAL DEFAULT 1,
                    last_tested TEXT,
                    quality_score REAL DEFAULT 0,
                    quality_tasks_json TEXT DEFAULT '{}',
                    input_cost REAL DEFAULT 0,
                    output_cost REAL DEFAULT 0,
                    supports_code INTEGER DEFAULT 0,
                    supports_reasoning INTEGER DEFAULT 0,
                    supports_creative INTEGER DEFAULT 0,
                    supports_long_context INTEGER DEFAULT 0,
                    supports_vision INTEGER DEFAULT 0,
                    supports_russian INTEGER DEFAULT 1,
                    available INTEGER DEFAULT 1,
                    errors_24h INTEGER DEFAULT 0,
                    weight_latency REAL DEFAULT 0.25,
                    weight_quality REAL DEFAULT 0.40,
                    weight_cost REAL DEFAULT 0.20,
                    weight_reliability REAL DEFAULT 0.15,
                    overall_score REAL DEFAULT 0,
                    updated_at TEXT
                )
            """)
            
            # Colony state
            c.execute("""
                CREATE TABLE IF NOT EXISTS colony_state (
                    key TEXT PRIMARY KEY,
                    value_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Proposals
            c.execute("""
                CREATE TABLE IF NOT EXISTS proposals (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    lade_class TEXT NOT NULL,
                    lade_scores_json TEXT DEFAULT '{}',
                    lade_explanation TEXT DEFAULT '',
                    formality_level INTEGER DEFAULT 2,
                    formality_reason TEXT DEFAULT '',
                    claim_scope TEXT DEFAULT 'G1',
                    scope_details_json TEXT DEFAULT '[]',
                    reliability_json TEXT DEFAULT '{}',
                    role TEXT NOT NULL,
                    method TEXT NOT NULL,
                    work_description TEXT NOT NULL,
                    work_evidence TEXT DEFAULT '',
                    target_file TEXT NOT NULL,
                    target_holon TEXT NOT NULL,
                    change_type TEXT NOT NULL,
                    constitution_passed INTEGER DEFAULT 0,
                    constitution_reason TEXT DEFAULT '',
                    fitness_score REAL DEFAULT 0,
                    fitness_dimensions_json TEXT DEFAULT '{}',
                    status TEXT DEFAULT 'proposed',
                    applied_at TEXT,
                    verified_at TEXT,
                    rollback_at TEXT
                )
            """)
            
            # Growth state
            c.execute("""
                CREATE TABLE IF NOT EXISTS growth_state (
                    capability_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    current_level INTEGER DEFAULT 0,
                    potential_level INTEGER DEFAULT 10,
                    current_evidence TEXT DEFAULT '',
                    growth_path TEXT DEFAULT '',
                    required_for_autonomy INTEGER DEFAULT 0,
                    next_action TEXT DEFAULT '',
                    last_improved TEXT DEFAULT '',
                    improvement_evidence_json TEXT DEFAULT '[]',
                    formality INTEGER DEFAULT 0,
                    scope TEXT DEFAULT 'G1',
                    assurance TEXT DEFAULT 'LA',
                    depends_on_json TEXT DEFAULT '[]',
                    blocks_json TEXT DEFAULT '[]',
                    updated_at TEXT
                )
            """)
            
            # System metrics
            c.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    cpu_percent REAL,
                    ram_percent REAL,
                    ram_used_mb REAL,
                    ram_total_mb REAL,
                    gpu_load REAL,
                    gpu_temp REAL,
                    vram_used_mb REAL,
                    vram_total_mb REAL,
                    disk_percent REAL,
                    disk_used_gb REAL,
                    disk_total_gb REAL,
                    network_sent_mb REAL,
                    network_recv_mb REAL,
                    process_count INTEGER
                )
            """)
            
            # Memory vector (ChromaDB fallback)
            c.execute("""
                CREATE TABLE IF NOT EXISTS memory_vector (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    content TEXT,
                    metadata TEXT,
                    embedding TEXT,
                    created_at TEXT
                )
            """)
            
            conn.commit()
            print(f"[PERSISTENCE] DB initialized: {self.db_path}")
    
    # ── Chat History ──
    
    def add_chat_message(self, role: str, content: str, vault: str = "", 
                       mode: str = "chat", source_model: str = "", 
                       metadata: Optional[Dict] = None) -> int:
        """Add a chat message. Returns row id."""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO chat_history (timestamp, role, content, vault, mode, source_model, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (datetime.now().isoformat(), role, content, vault, mode, source_model, 
                  json.dumps(metadata or {})))
            conn.commit()
            return c.lastrowid
    
    def get_chat_history(self, vault: str = "", limit: int = 100) -> List[Dict]:
        """Get recent chat history."""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            if vault:
                c.execute("""
                    SELECT timestamp, role, content, vault, mode, source_model, metadata
                    FROM chat_history WHERE vault = ? ORDER BY timestamp DESC LIMIT ?
                """, (vault, limit))
            else:
                c.execute("""
                    SELECT timestamp, role, content, vault, mode, source_model, metadata
                    FROM chat_history ORDER BY timestamp DESC LIMIT ?
                """, (limit,))
            rows = c.fetchall()
        return [
            {
                "timestamp": r[0], "role": r[1], "content": r[2], "vault": r[3],
                "mode": r[4], "source_model": r[5], "metadata": json.loads(r[6] or "{}")
            }
            for r in rows
        ]
    
    def clear_chat_history(self, vault: str = "") -> int:
        """Clear chat history. Returns count deleted."""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            if vault:
                c.execute("DELETE FROM chat_history WHERE vault = ?", (vault,))
            else:
                c.execute("DELETE FROM chat_history")
            conn.commit()
            return c.rowcount
    
    # ── Session State ──
    
    def set_state(self, key: str, value: str):
        """Set a session state key."""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""
                INSERT OR REPLACE INTO session_state (key, value, updated_at)
                VALUES (?, ?, ?)
            """, (key, value, datetime.now().isoformat()))
            conn.commit()
    
    def get_state(self, key: str, default: str = "") -> str:
        """Get a session state key."""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT value FROM session_state WHERE key = ?", (key,))
            row = c.fetchone()
            return row[0] if row else default
    
    # ── Event Log ──
    
    def log_event(self, event_type: str, role: str, method: str, 
                  work_description: str, performer: str = "ASTRA",
                  formality: int = 2, scope: str = "G1", assurance: str = "LA",
                  lade_class: str = "E", holon_affected: str = "",
                  data: Optional[Dict] = None, evidence: Optional[List] = None) -> int:
        """Log an FPF-structured event. Returns row id."""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO event_log (timestamp, event_type, role, method, work_description,
                    performer, formality, scope, assurance, lade_class, holon_affected,
                    data_json, evidence_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (datetime.now().isoformat(), event_type, role, method, work_description,
                  performer, formality, scope, assurance, lade_class, holon_affected,
                  json.dumps(data or {}), json.dumps(evidence or [])))
            conn.commit()
            return c.lastrowid
    
    def get_events(self, limit: int = 50, event_type: str = None) -> List[Dict]:
        """Get recent events."""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            if event_type:
                c.execute("""
                    SELECT timestamp, event_type, role, method, work_description,
                           performer, formality, scope, assurance, lade_class
                    FROM event_log WHERE event_type = ? ORDER BY timestamp DESC LIMIT ?
                """, (event_type, limit))
            else:
                c.execute("""
                    SELECT timestamp, event_type, role, method, work_description,
                           performer, formality, scope, assurance, lade_class
                    FROM event_log ORDER BY timestamp DESC LIMIT ?
                """, (limit,))
            rows = c.fetchall()
        return [
            {
                "timestamp": r[0], "event_type": r[1], "role": r[2], "method": r[3],
                "work_description": r[4], "performer": r[5], "formality": r[6],
                "scope": r[7], "assurance": r[8], "lade_class": r[9]
            }
            for r in rows
        ]
    
    # ── Stats ──
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            tables = ["chat_history", "event_log", "model_registry", "proposals", "growth_state", "system_metrics"]
            stats = {}
            for t in tables:
                c.execute(f"SELECT COUNT(*) FROM {t}")
                stats[t] = c.fetchone()[0]
            return stats


# ═══════════════════════════════════════════════════════════
# Singleton
# ═══════════════════════════════════════════════════════════

_PERSISTENCE: Optional[ASTRAPersistence] = None


def get_persistence() -> ASTRAPersistence:
    """Get singleton persistence instance."""
    global _PERSISTENCE
    if _PERSISTENCE is None:
        _PERSISTENCE = ASTRAPersistence()
    return _PERSISTENCE


if __name__ == "__main__":
    p = ASTRAPersistence()
    print("DB Stats:", p.get_stats())
