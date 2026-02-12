"""
Karma Memory System
Provides persistent memory across sessions using SQLite + ChromaDB

Features:
- Stores all conversations permanently
- Semantic search for relevant context
- Tool call history tracking
- Auto-generates knowledge summaries
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import hashlib

# Try to import ChromaDB (optional for now)
try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("⚠️  ChromaDB not installed. Semantic search disabled.")
    print("   Install with: pip install chromadb")


class KarmaMemory:
    """Persistent memory system for Karma"""

    def __init__(self, base_path: Optional[Path] = None):
        """Initialize memory system"""
        if base_path is None:
            base_path = Path.home() / "karma"

        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        # SQLite for structured storage
        self.db_path = self.base_path / "memory.db"
        self.conn = sqlite3.connect(str(self.db_path))
        self._init_db()

        # ChromaDB for semantic search
        if CHROMADB_AVAILABLE:
            embeddings_path = self.base_path / "embeddings"
            self.chroma_client = chromadb.PersistentClient(path=str(embeddings_path))
            self.memory_collection = self.chroma_client.get_or_create_collection("karma_memory")
        else:
            self.chroma_client = None
            self.memory_collection = None

        # Tool history
        self.tool_log = self.base_path / "tool_history.jsonl"

    def _init_db(self):
        """Create database schema"""
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                timestamp DATETIME,
                role TEXT,
                content TEXT,
                metadata TEXT,
                embedding_id TEXT
            )
        ''')

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                started_at DATETIME,
                ended_at DATETIME,
                summary TEXT,
                message_count INTEGER
            )
        ''')

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS knowledge (
                topic TEXT PRIMARY KEY,
                content TEXT,
                last_updated DATETIME,
                source TEXT
            )
        ''')

        self.conn.commit()

    def store_message(self, role: str, content: str, session_id: str, metadata: Optional[Dict] = None):
        """Store a conversation message"""
        msg_id = hashlib.md5(f"{session_id}{datetime.now().isoformat()}{content}".encode()).hexdigest()

        metadata_json = json.dumps(metadata or {})

        # Store in SQLite
        self.conn.execute('''
            INSERT INTO conversations (id, session_id, timestamp, role, content, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (msg_id, session_id, datetime.now(), role, content, metadata_json))
        self.conn.commit()

        # Store in ChromaDB for semantic search
        if self.memory_collection:
            try:
                self.memory_collection.add(
                    documents=[content],
                    metadatas=[{"role": role, "session_id": session_id, "timestamp": datetime.now().isoformat()}],
                    ids=[msg_id]
                )
            except Exception as e:
                print(f"⚠️  ChromaDB storage failed: {e}")

        return msg_id

    def search_memory(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search memory semantically"""
        if not self.memory_collection:
            # Fallback to keyword search in SQLite
            cursor = self.conn.execute('''
                SELECT role, content, timestamp, metadata
                FROM conversations
                WHERE content LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (f'%{query}%', n_results))

            results = []
            for row in cursor.fetchall():
                results.append({
                    "role": row[0],
                    "content": row[1],
                    "timestamp": row[2],
                    "metadata": json.loads(row[3] or "{}")
                })
            return results

        # Semantic search with ChromaDB
        try:
            results = self.memory_collection.query(
                query_texts=[query],
                n_results=n_results
            )

            formatted = []
            for i, doc in enumerate(results['documents'][0]):
                formatted.append({
                    "content": doc,
                    "metadata": results['metadatas'][0][i]
                })
            return formatted
        except Exception as e:
            print(f"⚠️  Semantic search failed: {e}")
            return []

    def get_conversation(self, session_id: str) -> List[Dict]:
        """Get all messages from a session"""
        cursor = self.conn.execute('''
            SELECT role, content, timestamp, metadata
            FROM conversations
            WHERE session_id = ?
            ORDER BY timestamp ASC
        ''', (session_id,))

        messages = []
        for row in cursor.fetchall():
            messages.append({
                "role": row[0],
                "content": row[1],
                "timestamp": row[2],
                "metadata": json.loads(row[3] or "{}")
            })
        return messages

    def log_tool_call(self, tool_name: str, args: Dict, result: str):
        """Log a tool execution"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "args": args,
            "result": result
        }

        with open(self.tool_log, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def store_knowledge(self, topic: str, content: str, source: str = "conversation"):
        """Store a piece of knowledge"""
        self.conn.execute('''
            INSERT OR REPLACE INTO knowledge (topic, content, last_updated, source)
            VALUES (?, ?, ?, ?)
        ''', (topic, content, datetime.now(), source))
        self.conn.commit()

    def get_knowledge(self, topic: str) -> Optional[str]:
        """Retrieve knowledge on a topic"""
        cursor = self.conn.execute('''
            SELECT content FROM knowledge WHERE topic = ?
        ''', (topic,))

        row = cursor.fetchone()
        return row[0] if row else None

    def generate_summary(self, session_id: str) -> str:
        """Generate a summary of a session"""
        messages = self.get_conversation(session_id)

        if not messages:
            return "No messages in this session."

        summary_parts = []
        summary_parts.append(f"Session {session_id}")
        summary_parts.append(f"Messages: {len(messages)}")
        summary_parts.append(f"Started: {messages[0]['timestamp']}")
        summary_parts.append(f"Ended: {messages[-1]['timestamp']}")

        # Extract key topics (simple word frequency)
        all_text = " ".join(m['content'] for m in messages)
        words = all_text.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 5:  # Only count longer words
                word_freq[word] = word_freq.get(word, 0) + 1

        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        summary_parts.append(f"Key topics: {', '.join(w[0] for w in top_words)}")

        return "\n".join(summary_parts)

    def close(self):
        """Close database connections"""
        self.conn.close()


# Example usage
if __name__ == "__main__":
    # Initialize memory
    memory = KarmaMemory()

    # Store a test conversation
    session_id = "test_session_1"
    memory.store_message("user", "How do I fix the dashboard?", session_id)
    memory.store_message("assistant", "Add /dashboard to _PUBLIC_ROUTES in karma_cockpit_service.py", session_id)

    # Search memory
    results = memory.search_memory("dashboard")
    print("\n🔍 Search Results:")
    for r in results:
        print(f"  • {r.get('content', 'N/A')[:80]}...")

    # Store knowledge
    memory.store_knowledge("dashboard_auth_fix", "Add routes to _PUBLIC_ROUTES set")

    print("\n✅ Memory system initialized!")
    print(f"📁 Database: {memory.db_path}")
    print(f"📁 Tool log: {memory.tool_log}")

    memory.close()
