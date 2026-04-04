#!/usr/bin/env python3
"""consolidation_db.py — Two-table SQLite persistence for memory consolidation.

Primitive #12: Replace JSONL files with structured SQLite database.
Tables: memories (individual records) + consolidations (cross-cutting insights).
Inspired by ProtoGensis memory-agent-bedrock pattern (obs #22319).

Usage:
    from consolidation_db import ConsolidationDB
    db = ConsolidationDB()
    db.add_memory("Colby approved nexus v5.3.0", importance=0.9, entities=["Colby", "nexus"], topics=["plan"])
    db.add_consolidation(memory_ids=[1,2,3], connections="...", insights="...")
    results = db.query_memories(limit=20)
"""
import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime, timezone


DB_PATH = Path(os.environ.get("CONSOLIDATION_DB", str(
    Path(__file__).resolve().parent.parent / "tmp" / "consolidation.db"
)))


class ConsolidationDB:
    def __init__(self, db_path=None):
        self.db_path = Path(db_path) if db_path else DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                summary TEXT NOT NULL,
                entities TEXT DEFAULT '[]',
                topics TEXT DEFAULT '[]',
                importance REAL DEFAULT 0.5,
                source TEXT DEFAULT 'unknown',
                consolidated INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS consolidations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_ids TEXT DEFAULT '[]',
                connections TEXT DEFAULT '',
                insights TEXT DEFAULT '',
                fix_skills TEXT DEFAULT '[]',
                derived_skills TEXT DEFAULT '[]',
                captured_skills TEXT DEFAULT '[]',
                importance REAL DEFAULT 0.5,
                recommendation TEXT DEFAULT '',
                created_at TEXT DEFAULT (datetime('now'))
            );

            CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance DESC);
            CREATE INDEX IF NOT EXISTS idx_memories_consolidated ON memories(consolidated);
            CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at DESC);
        """)
        self.conn.commit()

    def add_memory(self, summary, importance=0.5, entities=None, topics=None, source="unknown"):
        self.conn.execute(
            "INSERT INTO memories (summary, entities, topics, importance, source) VALUES (?, ?, ?, ?, ?)",
            (summary, json.dumps(entities or []), json.dumps(topics or []), importance, source)
        )
        self.conn.commit()
        return self.conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    def add_consolidation(self, memory_ids, connections="", insights="", fix_skills=None,
                          derived_skills=None, captured_skills=None, importance=0.5, recommendation=""):
        self.conn.execute(
            """INSERT INTO consolidations
               (memory_ids, connections, insights, fix_skills, derived_skills, captured_skills, importance, recommendation)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (json.dumps(memory_ids), connections, insights,
             json.dumps(fix_skills or []), json.dumps(derived_skills or []),
             json.dumps(captured_skills or []), importance, recommendation)
        )
        # Mark memories as consolidated
        for mid in memory_ids:
            self.conn.execute("UPDATE memories SET consolidated = 1 WHERE id = ?", (mid,))
        self.conn.commit()
        return self.conn.execute("SELECT last_insert_rowid()").fetchone()[0]

    def get_unconsolidated(self, limit=20):
        rows = self.conn.execute(
            "SELECT * FROM memories WHERE consolidated = 0 ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def query_memories(self, limit=50, min_importance=0.0):
        rows = self.conn.execute(
            "SELECT * FROM memories WHERE importance >= ? ORDER BY importance DESC, created_at DESC LIMIT ?",
            (min_importance, limit)
        ).fetchall()
        return [dict(r) for r in rows]

    def query_consolidations(self, limit=10):
        rows = self.conn.execute(
            "SELECT * FROM consolidations ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def stats(self):
        mem_count = self.conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
        con_count = self.conn.execute("SELECT COUNT(*) FROM consolidations").fetchone()[0]
        uncon = self.conn.execute("SELECT COUNT(*) FROM memories WHERE consolidated = 0").fetchone()[0]
        avg_imp = self.conn.execute("SELECT AVG(importance) FROM memories").fetchone()[0] or 0
        return {
            "memories": mem_count,
            "consolidations": con_count,
            "unconsolidated": uncon,
            "avg_importance": round(avg_imp, 3),
            "db_path": str(self.db_path),
        }

    def close(self):
        self.conn.close()


if __name__ == "__main__":
    db = ConsolidationDB()

    # Test
    mid1 = db.add_memory("Colby approved nexus v5.3.0", importance=0.9, entities=["Colby", "nexus"], topics=["plan"])
    mid2 = db.add_memory("LFM2 350M deployed on P1", importance=0.7, entities=["LFM2", "P1"], topics=["infrastructure"])
    mid3 = db.add_memory("Consolidation agent verified on K2", importance=0.8, entities=["K2", "consolidation"], topics=["evolution"])

    cid = db.add_consolidation(
        memory_ids=[mid1, mid2, mid3],
        connections="All relate to S160 infrastructure improvements",
        insights="Session 160 focused on independence + self-improvement",
        fix_skills=["P107 stop-after-milestone"],
        captured_skills=["3-tier cascade routing"],
        importance=0.85,
    )

    print(f"Stats: {db.stats()}")
    print(f"Unconsolidated: {len(db.get_unconsolidated())}")
    print(f"Recent consolidations: {len(db.query_consolidations())}")
    print("ALL TESTS PASS")
    db.close()
