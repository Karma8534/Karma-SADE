"""
Step 3.5: Client-Managed Context + Compaction (P1)
When context exceeds threshold, compress via extractive summarization.
Store opaque blob in sessions.compaction_blob.

Phase 3: Pure extractive (no LLM cost).
Phase 4+: GLM-4.7-Flash generative compaction (free tier).
"""

import json
import sqlite3
import os
from datetime import datetime, timezone

DB_PATH = os.getenv("MEMORY_DB_PATH", "/opt/seed-vault/memory_v1/memory.db")

# Compaction triggers
TOKEN_THRESHOLD = int(os.getenv("COMPACTION_TOKEN_THRESHOLD", "50000"))
# Rough approximation: 1 token ≈ 4 chars
CHAR_THRESHOLD = TOKEN_THRESHOLD * 4


def estimate_tokens(text: str) -> int:
    """Rough token estimation: ~4 chars per token for English."""
    return len(text) // 4


def needs_compaction(messages: list) -> bool:
    """Check if the message history exceeds the compaction threshold."""
    total_chars = sum(len(m.get("content", "")) for m in messages)
    return total_chars > CHAR_THRESHOLD


def compact_context(messages: list, session_id: str = "") -> dict:
    """
    P1: Extractive compaction when context exceeds threshold.
    
    Strategy:
    - Keep system messages intact (identity, tools)
    - Keep last 10 exchanges intact (recent context)
    - Compress older exchanges to structured summary
    - Store blob in sessions.compaction_blob
    
    Returns: {
        compacted_messages: list,  # Reduced message list
        summary: dict,             # Structured summary of compressed content
        tokens_saved: int,
        blob_stored: bool,
    }
    """
    if not needs_compaction(messages):
        return {
            "compacted_messages": messages,
            "summary": None,
            "tokens_saved": 0,
            "blob_stored": False,
        }
    
    # Separate system messages from conversation
    system_msgs = [m for m in messages if m.get("role") == "system"]
    conversation = [m for m in messages if m.get("role") != "system"]
    
    # Keep last 10 exchanges (20 messages: user+assistant pairs)
    keep_recent = 20
    if len(conversation) <= keep_recent:
        return {
            "compacted_messages": messages,
            "summary": None,
            "tokens_saved": 0,
            "blob_stored": False,
        }
    
    old_messages = conversation[:-keep_recent]
    recent_messages = conversation[-keep_recent:]
    
    # Extractive summary of old messages
    summary = _extract_summary(old_messages)
    
    # Create compaction message
    compaction_msg = {
        "role": "system",
        "content": _format_summary(summary),
    }
    
    compacted = system_msgs + [compaction_msg] + recent_messages
    
    old_chars = sum(len(m.get("content", "")) for m in old_messages)
    new_chars = len(compaction_msg["content"])
    tokens_saved = (old_chars - new_chars) // 4
    
    # Store blob in sessions table
    blob_stored = False
    if session_id:
        try:
            blob = json.dumps(summary).encode("utf-8")
            db = sqlite3.connect(DB_PATH)
            db.execute("""
                UPDATE sessions SET compaction_blob=?, token_count=?
                WHERE session_id=?
            """, (blob, estimate_tokens(
                "".join(m.get("content", "") for m in compacted)
            ), session_id))
            db.commit()
            db.close()
            blob_stored = True
        except Exception as e:
            print(f"[COMPACT] blob store failed: {e}")
    
    return {
        "compacted_messages": compacted,
        "summary": summary,
        "tokens_saved": tokens_saved,
        "blob_stored": blob_stored,
    }


def _extract_summary(messages: list) -> dict:
    """
    Extract key information from a list of messages.
    Pure extractive — no LLM call.
    """
    decisions = []
    questions = []
    action_items = []
    key_facts = []
    
    decision_markers = ["decided", "decision", "agreed", "confirmed", "locked",
                        "chose", "settled", "ruling", "final"]
    question_markers = ["?", "should we", "what about", "how do", "can we",
                        "need to figure", "open question"]
    action_markers = ["todo", "action item", "next step", "need to",
                      "will do", "going to", "plan to", "must"]
    
    for msg in messages:
        content = msg.get("content", "")
        role = msg.get("role", "")
        
        sentences = content.replace("\n", ". ").split(". ")
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or len(sentence) < 10:
                continue
            
            lower = sentence.lower()
            
            if any(m in lower for m in decision_markers):
                decisions.append(sentence[:200])
            elif any(m in lower for m in question_markers):
                questions.append(sentence[:200])
            elif any(m in lower for m in action_markers):
                action_items.append(sentence[:200])
            elif len(sentence) > 30 and role == "assistant":
                # Key facts from assistant responses
                key_facts.append(sentence[:200])
    
    # Deduplicate and limit
    return {
        "decisions": list(dict.fromkeys(decisions))[:10],
        "questions": list(dict.fromkeys(questions))[:5],
        "action_items": list(dict.fromkeys(action_items))[:10],
        "key_facts": list(dict.fromkeys(key_facts))[:15],
        "messages_compressed": len(messages),
        "compressed_at": datetime.now(timezone.utc).isoformat(),
    }


def _format_summary(summary: dict) -> str:
    """Format the extractive summary as a system message."""
    parts = ["=== COMPACTED CONTEXT (earlier conversation) ==="]
    
    if summary.get("decisions"):
        parts.append("\nDecisions made:")
        for d in summary["decisions"]:
            parts.append(f"  - {d}")
    
    if summary.get("action_items"):
        parts.append("\nAction items:")
        for a in summary["action_items"]:
            parts.append(f"  - {a}")
    
    if summary.get("questions"):
        parts.append("\nOpen questions:")
        for q in summary["questions"]:
            parts.append(f"  - {q}")
    
    if summary.get("key_facts"):
        parts.append("\nKey facts:")
        for f in summary["key_facts"]:
            parts.append(f"  - {f}")
    
    parts.append(f"\n({summary.get('messages_compressed', 0)} earlier messages compressed)")
    parts.append("=== END COMPACTED CONTEXT ===")
    
    return "\n".join(parts)
