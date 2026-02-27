"""
Karma Memory Tools — The Memory Behind the Mind
Handles admission, retrieval, update, deletion, and session context.
All operations go through SQLite (memory.db) with FTS5 + embedding search.

Implements: P4 (salience+novelty), P5 (session context), P6 (memory-before-prompt),
            P9 (RRF hybrid search), Decision #5 (time-decay), Decision #6 (newer wins).
"""

import json
import hashlib
import sqlite3
import os
import numpy as np
from datetime import datetime, timezone
from sentence_transformers import SentenceTransformer

# ─── Configuration ────────────────────────────────────────────────────────
DB_PATH = os.getenv("MEMORY_DB_PATH", "/opt/seed-vault/memory_v1/memory.db")
LEDGER_DIR = os.getenv("LEDGER_DIR", "/opt/seed-vault/memory_v1/ledger")
CANDIDATES_JSONL = os.path.join(LEDGER_DIR, "candidates.jsonl")
DECISION_LOG_JSONL = os.path.join(LEDGER_DIR, "decision_log.jsonl")

# Load embedding model once at import (~250MB RAM, cached after first load)
EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

CATEGORIES = [
    "identity", "decision", "failure", "learning",
    "relationship", "technical", "preference"
]

# Gate thresholds (Decision #4: admission threshold 0.5)
SALIENCE_THRESHOLD = 0.35
NOVELTY_THRESHOLD = 0.82
MERGE_THRESHOLD = 0.85   # Auto-merge (newer wins, Decision #6)
AMBIGUOUS_THRESHOLD = 0.70  # Queue for Colby review


# ─── Embedding Helpers ────────────────────────────────────────────────────

def _embed(text: str) -> bytes:
    """Compute 384d L2-normalized embedding, return as bytes for SQLite BLOB."""
    vec = EMBED_MODEL.encode(text, normalize_embeddings=True)
    return vec.astype(np.float32).tobytes()


def _cosine_sim(blob_a: bytes, blob_b: bytes) -> float:
    """Cosine similarity between two embedding blobs (already L2-normalized → dot product)."""
    a = np.frombuffer(blob_a, dtype=np.float32)
    b = np.frombuffer(blob_b, dtype=np.float32)
    return float(np.dot(a, b))


# ─── Scoring Helpers ──────────────────────────────────────────────────────

def _compute_salience(content: str, cell_type: str, pinned: bool,
                      confidence: float = 0.5) -> float:
    """P4 salience formula: length + specificity + type boost + confidence + pinned."""
    words = content.split()
    if not words:
        return 0.0
    # Use a softer length curve: short but specific content still scores
    length_norm = min(len(words) / 30.0, 1.0)
    has_numbers = 1.0 if any(c.isdigit() for c in content) else 0.0
    has_capitalized = 1.0 if any(w[0].isupper() for w in words if w) else 0.0
    kind_boost = 0.15 if cell_type in ("decision", "failure", "risk") else 0.0
    pinned_boost = 0.5 if pinned else 0.0
    # High-confidence sources (Colby-confirmed=1.0) get a boost
    confidence_boost = 0.15 * confidence
    generic_penalty = 0.2 if len(words) < 3 else 0.0

    return min(1.0, 0.30 * length_norm + 0.15 * has_numbers
               + 0.15 * has_capitalized + kind_boost + pinned_boost
               + confidence_boost - generic_penalty)


def _compute_novelty(embedding: bytes, db: sqlite3.Connection) -> float:
    """P4 novelty: 1.0 - max_similarity to any existing non-archived cell."""
    rows = db.execute(
        "SELECT embedding FROM mem_cells WHERE archived=0"
    ).fetchall()
    if not rows:
        return 1.0  # First entry is maximally novel
    max_sim = max(_cosine_sim(embedding, row[0]) for row in rows)
    return 1.0 - max_sim


def _infer_scene(content: str) -> str:
    """Simple keyword-based scene inference. Phase 2 will add LLM fallback."""
    lower = content.lower()
    scene_keywords = {
        "identity": ["i am", "my name", "karma is", "who i am", "my purpose"],
        "architecture": ["docker", "falkordb", "sqlite", "droplet", "container", "server"],
        "preferences": ["prefer", "like", "dislike", "want", "don't want", "style"],
        "relationships": ["colby", "ollie", "family", "friend", "pet"],
        "decisions": ["decided", "decision", "chose", "locked", "confirmed"],
        "failures": ["failed", "broke", "error", "bug", "crash", "wrong"],
        "learnings": ["learned", "realized", "discovered", "found that", "insight"],
    }
    for scene, keywords in scene_keywords.items():
        if any(kw in lower for kw in keywords):
            return scene
    return "general"


# ─── Ledger Helpers ───────────────────────────────────────────────────────

def _log_decision(action: str, details: dict) -> None:
    """Append to decision_log.jsonl — audit trail for all memory mutations."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        **details
    }
    try:
        os.makedirs(os.path.dirname(DECISION_LOG_JSONL), exist_ok=True)
        with open(DECISION_LOG_JSONL, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"[MEMORY] decision_log write failed: {e}")


def _append_candidate(content: str, category: str, source: str,
                      confidence: float, similar_id: str, similarity: float) -> None:
    """Queue ambiguous entries in candidates.jsonl for Colby review."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "content": content,
        "category": category,
        "source": source,
        "confidence": confidence,
        "similar_to": similar_id,
        "similarity": round(similarity, 4),
        "status": "pending_review"
    }
    try:
        os.makedirs(os.path.dirname(CANDIDATES_JSONL), exist_ok=True)
        with open(CANDIDATES_JSONL, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"[MEMORY] candidates.jsonl write failed: {e}")


# ─── Step 1.1: admit_memory() ────────────────────────────────────────────

def admit_memory(content: str, category: str, source: str,
                 confidence: float, pinned: bool = False) -> dict:
    """
    Admit a new memory through the quality gate.
    Gate: salience >= 0.35 AND novelty >= 0.82 (or pinned=True bypasses).

    Returns: {action: "added"|"updated"|"queued"|"rejected", ...}
    """
    if category not in CATEGORIES:
        return {"action": "rejected", "reason": f"Invalid category: {category}"}
    if not 0.0 <= confidence <= 1.0:
        return {"action": "rejected", "reason": f"Invalid confidence: {confidence}"}
    if not content or not content.strip():
        return {"action": "rejected", "reason": "Empty content"}

    embedding = _embed(content)
    timestamp = datetime.now(timezone.utc).timestamp()

    db = sqlite3.connect(DB_PATH)
    try:
        salience = _compute_salience(content, category, pinned, confidence)
        novelty = _compute_novelty(embedding, db)

        if not pinned and (salience < SALIENCE_THRESHOLD or novelty < NOVELTY_THRESHOLD):
            if novelty < NOVELTY_THRESHOLD:
                # Near-duplicate — find closest and consider merge or queue
                rows = db.execute(
                    "SELECT id, content, embedding FROM mem_cells WHERE archived=0"
                ).fetchall()
                if rows:
                    best_id, best_content, best_sim = None, None, 0.0
                    for row in rows:
                        sim = _cosine_sim(embedding, row[2])
                        if sim > best_sim:
                            best_sim, best_id, best_content = sim, row[0], row[1]

                    if best_sim > MERGE_THRESHOLD:
                        # Decision #6: Newer wins + archive old
                        result = update_memory(
                            best_id, content,
                            f"Auto-merge: newer content wins (sim={best_sim:.3f})"
                        )
                        return {"action": "updated",
                                "reason": f"Merged with {best_id} (sim={best_sim:.3f})",
                                "merge_result": result}
                    elif best_sim > AMBIGUOUS_THRESHOLD:
                        # Queue for Colby review
                        _append_candidate(content, category, source,
                                          confidence, best_id, best_sim)
                        return {"action": "queued",
                                "reason": f"Ambiguous similarity ({best_sim:.3f}), queued for review"}

            return {"action": "rejected",
                    "reason": f"Below gate: salience={salience:.3f}, novelty={novelty:.3f}"}

        # Passed gate — admit as new entry
        entry_id = f"mem_{hashlib.sha256(content.encode()).hexdigest()[:12]}"

        db.execute("""
            INSERT OR IGNORE INTO mem_cells
            (id, scene, cell_type, salience, novelty, content, embedding,
             confidence, source, pinned, created_at, last_accessed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (entry_id, _infer_scene(content), category, salience, novelty,
              content, embedding, confidence, source,
              1 if pinned else 0, timestamp, timestamp))

        if db.total_changes > 0:
            # Get the rowid for FTS index
            rowid = db.execute(
                "SELECT rowid FROM mem_cells WHERE id=?", (entry_id,)
            ).fetchone()[0]
            db.execute("""
                INSERT INTO mem_cells_fts(rowid, content, scene, cell_type)
                VALUES (?, ?, ?, ?)
            """, (rowid, content, _infer_scene(content), category))

        db.commit()

        _log_decision("admit_memory", {
            "id": entry_id, "category": category, "source": source,
            "salience": round(salience, 3), "novelty": round(novelty, 3),
            "pinned": pinned
        })

        return {"action": "added", "id": entry_id,
                "salience": round(salience, 3), "novelty": round(novelty, 3)}
    finally:
        db.close()


# ─── Step 1.2: retrieve_memory() ─────────────────────────────────────────

def retrieve_memory(query: str, top_k: int = 5,
                    category_filter: str = None) -> list:
    """
    Hybrid retrieval: FTS5 + embedding similarity + RRF fusion (P9).
    Memory-before-prompt: call this BEFORE constructing the LLM prompt (P6).

    Returns: list of {id, content, cell_type, scene, salience, confidence, score}
    """
    query_embedding = _embed(query)
    db = sqlite3.connect(DB_PATH)
    now = datetime.now(timezone.utc).timestamp()

    try:
        # ── Layer 1: FTS5 keyword search ──
        fts_params = [query]
        fts_sql = "SELECT rowid, rank FROM mem_cells_fts WHERE mem_cells_fts MATCH ?"
        if category_filter:
            fts_sql += " AND cell_type = ?"
            fts_params.append(category_filter)
        try:
            fts_results = db.execute(fts_sql, fts_params).fetchall()
        except sqlite3.OperationalError:
            # FTS query syntax error (e.g., special chars) — fall back to empty
            fts_results = []
        fts_ranks = {row[0]: i + 1 for i, row in enumerate(fts_results)}

        # ── Layer 2: Embedding similarity search ──
        where_clause = "WHERE archived=0"
        params = []
        if category_filter:
            where_clause += " AND cell_type=?"
            params.append(category_filter)
        rows = db.execute(
            f"SELECT rowid, id, content, embedding, salience, usage, "
            f"confidence, last_accessed, cell_type, scene "
            f"FROM mem_cells {where_clause}",
            params
        ).fetchall()

        vec_scored = []
        for row in rows:
            sim = _cosine_sim(query_embedding, row[3])
            if sim < 0.4:
                continue
            vec_scored.append((row, sim))
        vec_scored.sort(key=lambda x: x[1], reverse=True)
        vec_ranks = {item[0][0]: i + 1 for i, item in enumerate(vec_scored)}

        # ── RRF fusion (P9): score = Σ 1/(60 + rank_i) ──
        all_rowids = set(fts_ranks.keys()) | set(vec_ranks.keys())
        rrf_scored = []
        for rowid in all_rowids:
            rrf = 0.0
            if rowid in fts_ranks:
                rrf += 1.0 / (60 + fts_ranks[rowid])
            if rowid in vec_ranks:
                rrf += 1.0 / (60 + vec_ranks[rowid])
            rrf_scored.append((rowid, rrf))

        rrf_scored.sort(key=lambda x: x[1], reverse=True)

        # ── Apply recency decay (Decision #5) + salience weighting ──
        row_lookup = {r[0]: r for r in rows}
        results = []
        for rowid, rrf in rrf_scored[:top_k * 2]:
            row_data = row_lookup.get(rowid)
            if not row_data:
                continue
            days_old = (now - row_data[7]) / 86400
            recency = 0.99 ** days_old
            salience_weight = 0.55 + 0.45 * row_data[4]
            usage_decay = 1.0 / (1.0 + 0.15 * row_data[5])
            final_score = rrf * salience_weight * recency * usage_decay

            results.append({
                "id": row_data[1],
                "content": row_data[2],
                "cell_type": row_data[8],
                "scene": row_data[9],
                "salience": row_data[4],
                "confidence": row_data[6],
                "score": round(final_score, 6)
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        top = results[:top_k]

        # Update last_accessed (keeps useful memories from going stale)
        for entry in top:
            db.execute(
                "UPDATE mem_cells SET last_accessed=?, usage=usage+1 WHERE id=?",
                (now, entry["id"])
            )
        db.commit()

        return top

    finally:
        db.close()


# ─── Step 1.3: update_memory(), delete_memory() ──────────────────────────

def update_memory(memory_id: str, new_content: str, reason: str) -> dict:
    """
    Decision #6: Newer wins + archive old content.
    Updates content + embedding, logs the change.
    """
    db = sqlite3.connect(DB_PATH)
    try:
        old = db.execute(
            "SELECT content, rowid FROM mem_cells WHERE id=?", (memory_id,)
        ).fetchone()
        if not old:
            return {"action": "not_found", "reason": f"No entry: {memory_id}"}

        old_content, rowid = old[0], old[1]
        old_hash = hashlib.sha256(old_content.encode()).hexdigest()[:12]
        new_hash = hashlib.sha256(new_content.encode()).hexdigest()[:12]
        new_embedding = _embed(new_content)
        now = datetime.now(timezone.utc).timestamp()
        new_scene = _infer_scene(new_content)

        # Update the cell
        db.execute("""
            UPDATE mem_cells
            SET content=?, embedding=?, last_accessed=?, scene=?
            WHERE id=?
        """, (new_content, new_embedding, now, new_scene, memory_id))

        # Update FTS index (delete old + insert new)
        db.execute("DELETE FROM mem_cells_fts WHERE rowid=?", (rowid,))
        cell_type = db.execute(
            "SELECT cell_type FROM mem_cells WHERE id=?", (memory_id,)
        ).fetchone()[0]
        db.execute("""
            INSERT INTO mem_cells_fts(rowid, content, scene, cell_type)
            VALUES (?, ?, ?, ?)
        """, (rowid, new_content, new_scene, cell_type))

        db.commit()

        _log_decision("update_memory", {
            "memory_id": memory_id, "reason": reason,
            "old_hash": old_hash, "new_hash": new_hash
        })

        return {"action": "updated", "old_hash": old_hash, "new_hash": new_hash}
    finally:
        db.close()


def delete_memory(memory_id: str, reason: str) -> dict:
    """Soft delete: set archived=1, log to decision_log."""
    db = sqlite3.connect(DB_PATH)
    try:
        exists = db.execute(
            "SELECT id FROM mem_cells WHERE id=?", (memory_id,)
        ).fetchone()
        if not exists:
            return {"action": "not_found", "reason": f"No entry: {memory_id}"}

        now = datetime.now(timezone.utc).timestamp()
        db.execute("UPDATE mem_cells SET archived=1 WHERE id=?", (memory_id,))
        db.commit()

        _log_decision("delete_memory", {
            "memory_id": memory_id, "reason": reason,
            "archived_at": datetime.now(timezone.utc).isoformat()
        })

        return {"action": "archived", "id": memory_id, "reason": reason}
    finally:
        db.close()


# ─── Step 1.4: Session Context (P5, P1) ──────────────────────────────────

def save_session_context(session_id: str, task: str = "", goal: str = "",
                         approaches: str = "", decisions: str = "",
                         state: str = "", compaction_blob: bytes = None,
                         token_count: int = 0) -> dict:
    """
    Write 5-field session context (P5) + optional compaction blob (P1).
    Called at session end or when compaction threshold hit.
    """
    db = sqlite3.connect(DB_PATH)
    try:
        now = datetime.now(timezone.utc).timestamp()
        db.execute("""
            INSERT OR REPLACE INTO sessions
            (session_id, task, goal, approaches, decisions, state,
             compaction_blob, token_count, created_at, ended_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (session_id, task, goal, approaches, decisions, state,
              compaction_blob, token_count, now, now))
        db.commit()
        return {"action": "saved", "session_id": session_id}
    finally:
        db.close()


def load_last_session() -> dict:
    """Load most recent session context for resume (P5)."""
    db = sqlite3.connect(DB_PATH)
    try:
        row = db.execute("""
            SELECT session_id, task, goal, approaches, decisions, state
            FROM sessions ORDER BY ended_at DESC LIMIT 1
        """).fetchone()
        if not row:
            return None
        return {
            "session_id": row[0], "task": row[1], "goal": row[2],
            "approaches": row[3], "decisions": row[4], "state": row[5]
        }
    finally:
        db.close()


# ─── Pending Observations (for session-start briefing) ───────────────────

def load_pending_observations(since_session_id: str = None,
                              limit: int = 50) -> list:
    """Load recent observations from the consciousness loop for context injection."""
    db = sqlite3.connect(DB_PATH)
    try:
        if since_session_id:
            # Get the timestamp of the last session end
            row = db.execute(
                "SELECT ended_at FROM sessions WHERE session_id=?",
                (since_session_id,)
            ).fetchone()
            if row:
                obs = db.execute(
                    "SELECT observed_at, event_type, description, outcome "
                    "FROM observations WHERE observed_at > ? "
                    "ORDER BY observed_at DESC LIMIT ?",
                    (row[0], limit)
                ).fetchall()
                return [{"observed_at": r[0], "event_type": r[1],
                         "description": r[2], "outcome": r[3]} for r in obs]

        # Default: last N observations
        rows = db.execute(
            "SELECT observed_at, event_type, description, outcome "
            "FROM observations ORDER BY observed_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
        return [{"observed_at": r[0], "event_type": r[1],
                 "description": r[2], "outcome": r[3]}
                for r in rows]
    finally:
        db.close()
