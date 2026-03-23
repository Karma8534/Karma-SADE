#!/usr/bin/env python3
"""
Universal AI Memory - Search Service v0.3.1
Phase 3: Auto-Reindexing with Fixed Incremental Logic

Bug Fix:
- Added debug logging for ID tracking
- Fixed race condition in file reading
- Improved cache ID comparison logic
- Added validation to prevent duplicate embeddings

For private personal use only.
"""

import json
import os
import time
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any, Set
from datetime import datetime
from contextlib import asynccontextmanager

import numpy as np
import faiss
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI
import uvicorn
from watchfiles import awatch


# Configuration
LEDGER_PATH = os.getenv("LEDGER_PATH", "/ledger/memory.jsonl")
EMBEDDINGS_DIR = os.getenv("EMBEDDINGS_DIR", "/embeddings")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIMENSION = 1536
AUTO_REINDEX_INTERVAL = int(os.getenv("AUTO_REINDEX_INTERVAL", "300"))  # 5 minutes
EMBED_MAX_CHARS = int(os.getenv("EMBED_MAX_CHARS", "12000"))

# Global state
index: Optional[faiss.IndexFlatL2] = None
memory_entries: List[Dict[str, Any]] = []
embeddings_cache: Optional[np.ndarray] = None
last_indexed_count = 0
indexed_entry_ids: Set[str] = set()
openai_client = None
file_watcher_task = None


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    limit: int = Field(10, ge=1, le=100)
    filter_platform: Optional[str] = None
    filter_role: Optional[str] = None


class SearchResult(BaseModel):
    entry_id: str
    similarity_score: float
    platform: str
    role: str
    content_preview: str
    timestamp: str
    conversation_id: Optional[str] = None


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_indexed: int
    search_time_ms: float


def initialize_openai():
    global openai_client
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not set")
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    print(f"✅ OpenAI initialized ({EMBEDDING_MODEL})")


def get_platform_from_entry(entry: Dict[str, Any]) -> str:
    content = entry.get("content", {})
    if isinstance(content, dict) and "provider" in content:
        return content["provider"]
    tags = entry.get("tags", [])
    for tag in ["claude", "gemini", "chatgpt"]:
        if tag in tags:
            return tag
    source = entry.get("source", {})
    ref = source.get("ref", "")
    if "claude" in ref:
        return "claude"
    elif "gemini" in ref:
        return "gemini"
    elif "chatgpt" in ref:
        return "chatgpt"
    return "system"


def get_role_from_entry(entry: Dict[str, Any]) -> str:
    content = entry.get("content", {})
    # Prefer assistant role when both sides exist in a single ledger turn.
    if isinstance(content, dict) and content.get("assistant_message"):
        return "assistant"
    elif isinstance(content, dict) and content.get("user_message"):
        return "user"
    return "system"


def extract_text_for_embedding(entry: Dict[str, Any]) -> str:
    content = entry.get("content", "")
    platform = get_platform_from_entry(entry)
    if isinstance(content, dict):
        user_msg = content.get("user_message", "")
        # assistant_text is the field used by hub/chat ledger entries (/v1/chat)
        asst_msg = content.get("assistant_message") or content.get("assistant_text", "")
        # Assistant-first indexing to reduce user-message noise in semantic recall.
        if asst_msg and user_msg:
            return f"[{platform}] Assistant: {asst_msg}\n[Prompt Context] {user_msg}"
        elif asst_msg:
            return f"[{platform}] Assistant: {asst_msg}"
        elif user_msg:
            return f"[{platform}] User: {user_msg}"
        elif "message" in content:
            return f"[{platform}] {content['message']}"
        elif "value" in content:
            # Knowledge entries (docs, notes) stored as {"value": "..."}
            return f"[docs] {content['value']}"
        else:
            return f"[{platform}] {json.dumps(content)}"
    return f"[{platform}] {str(content)}"


def extract_content_preview(entry: Dict[str, Any], max_length: int = 200) -> str:
    content = entry.get("content", "")
    if isinstance(content, dict):
        # Assistant-first preview keeps returned context synthesis-rich.
        # assistant_text is the field used by hub/chat ledger entries (/v1/chat)
        asst = content.get("assistant_message") or content.get("assistant_text", "")
        if asst:
            text = asst
        elif content.get("user_message"):
            text = content["user_message"]
        elif "message" in content:
            text = content["message"]
        elif "value" in content:
            text = content["value"]
        else:
            text = json.dumps(content, indent=2)
    else:
        text = str(content)
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text


def should_index_entry(entry: Dict[str, Any]) -> bool:
    content = entry.get("content", "")
    if not isinstance(content, dict):
        return True
    if content.get("assistant_message"):
        return True
    if content.get("message"):
        return True
    # Index knowledge entries (docs, notes) stored as {"value": "..."}
    if content.get("value"):
        return True
    # Skip user-only records to reduce semantic noise.
    if content.get("user_message") and not content.get("assistant_message"):
        return False
    return False


def load_memory_ledger() -> List[Dict[str, Any]]:
    entries = []
    raw_count = 0
    if not os.path.exists(LEDGER_PATH):
        print(f"⚠️  Ledger not found: {LEDGER_PATH}")
        return entries

    # Ensure file is fully written by waiting briefly
    time.sleep(0.5)

    with open(LEDGER_PATH, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                raw_count += 1
                if should_index_entry(entry):
                    entries.append(entry)
            except json.JSONDecodeError as e:
                print(f"⚠️  Line {line_num}: {e}")

    print(f"📚 Loaded {len(entries)} indexable entries from {raw_count} ledger rows")
    return entries


def sanitize_text_for_embedding(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)
    # Replace invalid unicode/surrogate sequences that can break request encoding.
    text = text.encode("utf-8", errors="replace").decode("utf-8")
    text = text.replace("\x00", " ").strip()
    if len(text) > EMBED_MAX_CHARS:
        text = text[:EMBED_MAX_CHARS]
    return text or "[empty]"


def generate_embeddings_batch(texts: List[str], batch_size: int = 100) -> np.ndarray:
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = [sanitize_text_for_embedding(t) for t in texts[i:i + batch_size]]
        try:
            response = openai_client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=batch
            )
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)
            print(f"  Embedded {min(i+batch_size, len(texts))}/{len(texts)}")
        except Exception as e:
            print(f"❌ Batch {i} failed: {e}")
            print(f"  ↪ Falling back to per-item embedding for batch {i}")
            for item in batch:
                try:
                    response = openai_client.embeddings.create(
                        model=EMBEDDING_MODEL,
                        input=[item]
                    )
                    all_embeddings.append(response.data[0].embedding)
                except Exception as single_e:
                    # Last resort: retry with tighter truncation.
                    tighter = item[: max(1000, EMBED_MAX_CHARS // 2)]
                    try:
                        response = openai_client.embeddings.create(
                            model=EMBEDDING_MODEL,
                            input=[tighter]
                        )
                        all_embeddings.append(response.data[0].embedding)
                    except Exception as final_e:
                        print(f"  ⚠️  Per-item fallback failed: {single_e} / {final_e}")
                        all_embeddings.append([0.0] * EMBEDDING_DIMENSION)
    return np.array(all_embeddings, dtype=np.float32)


def build_faiss_index(embeddings: np.ndarray) -> faiss.IndexFlatL2:
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    print(f"🔍 FAISS index: {index.ntotal} vectors")
    return index


def save_cache(embeddings: np.ndarray, entries: List[Dict[str, Any]]):
    Path(EMBEDDINGS_DIR).mkdir(parents=True, exist_ok=True)

    # Create ordered list of entry IDs matching embedding order
    entry_ids = [e.get("id", "") for e in entries]

    np.save(Path(EMBEDDINGS_DIR) / "embeddings.npy", embeddings)
    with open(Path(EMBEDDINGS_DIR) / "metadata.json", 'w') as f:
        json.dump({
            "entry_count": len(entries),
            "dimension": EMBEDDING_DIMENSION,
            "model": EMBEDDING_MODEL,
            "updated": datetime.utcnow().isoformat(),
            "entry_ids": entry_ids
        }, f, indent=2)
    print(f"💾 Saved cache: {len(embeddings)} vectors, {len(entry_ids)} IDs")


def load_cache() -> Optional[tuple]:
    emb_path = Path(EMBEDDINGS_DIR) / "embeddings.npy"
    meta_path = Path(EMBEDDINGS_DIR) / "metadata.json"
    if not emb_path.exists() or not meta_path.exists():
        return None
    try:
        embeddings = np.load(emb_path)
        with open(meta_path, 'r') as f:
            metadata = json.load(f)
        print(f"📦 Loaded cache: {len(embeddings)} vectors, {len(metadata.get('entry_ids', []))} IDs")
        return embeddings, metadata
    except Exception as e:
        print(f"⚠️  Cache load failed: {e}")
        return None


def incremental_reindex():
    """
    Incremental reindex: Only embed new entries that aren't cached
    """
    global index, memory_entries, embeddings_cache, last_indexed_count, indexed_entry_ids

    print("\n🔄 Incremental reindex...")

    # Load current entries from ledger
    memory_entries = load_memory_ledger()

    if not memory_entries:
        print("⚠️  No entries")
        return

    # Build set of current entry IDs
    current_ids = {e.get("id", "") for e in memory_entries}
    current_ids.discard("")  # Remove empty IDs

    print(f"📊 Current ledger: {len(memory_entries)} entries, {len(current_ids)} unique IDs")

    # Load existing cache
    cache = load_cache()

    if cache:
        cached_emb, meta = cache
        cached_ids = set(meta.get("entry_ids", []))
        cached_ids.discard("")  # Remove empty IDs

        print(f"📦 Cached: {len(cached_emb)} vectors, {len(cached_ids)} unique IDs")

        # Find new entries
        new_ids = current_ids - cached_ids

        # DEBUG: Show ID comparison
        print(f"🔍 ID Comparison:")
        print(f"   Current IDs: {len(current_ids)}")
        print(f"   Cached IDs: {len(cached_ids)}")
        print(f"   New IDs: {len(new_ids)}")
        if new_ids:
            print(f"   Sample new IDs: {list(new_ids)[:3]}")

        if not new_ids:
            print(f"✅ No new entries - using cache")
            embeddings_cache = cached_emb
            index = build_faiss_index(embeddings_cache)
            last_indexed_count = len(memory_entries)
            indexed_entry_ids = cached_ids
            return

        print(f"🆕 Found {len(new_ids)} new entries")

        # Extract new entries ONLY
        new_entries = [e for e in memory_entries if e.get("id", "") in new_ids]

        # Verify we got the right count
        if len(new_entries) != len(new_ids):
            print(f"⚠️  Warning: Expected {len(new_ids)} new entries, got {len(new_entries)}")

        # Generate embeddings for new entries only
        print(f"🤖 Generating embeddings for {len(new_entries)} new entries...")
        new_texts = [extract_text_for_embedding(e) for e in new_entries]
        new_embeddings = generate_embeddings_batch(new_texts)

        # Combine with cached embeddings
        print(f"🔗 Combining: {len(cached_emb)} cached + {len(new_embeddings)} new")
        embeddings_cache = np.vstack([cached_emb, new_embeddings])
        print(f"✅ Combined: {len(embeddings_cache)} total vectors")

    else:
        # No cache, full reindex
        print(f"🤖 Full reindex: Generating embeddings for {len(memory_entries)} entries...")
        texts = [extract_text_for_embedding(e) for e in memory_entries]
        embeddings_cache = generate_embeddings_batch(texts)

    # Build index
    index = build_faiss_index(embeddings_cache)

    # Verify vector count matches entry count
    if len(embeddings_cache) != len(memory_entries):
        print(f"⚠️  WARNING: Vector count mismatch!")
        print(f"   Entries: {len(memory_entries)}")
        print(f"   Vectors: {len(embeddings_cache)}")

    # Save cache
    save_cache(embeddings_cache, memory_entries)

    last_indexed_count = len(memory_entries)
    indexed_entry_ids = current_ids
    print(f"✅ Indexed {last_indexed_count} entries")


async def watch_ledger_file():
    """Watch memory.jsonl for changes and trigger reindex"""
    print(f"👁️  Watching {LEDGER_PATH} for changes...")

    async for changes in awatch(LEDGER_PATH):
        print(f"\n📝 Detected changes: {len(changes)} events")
        await asyncio.sleep(3)  # Increased debounce: wait for file writes to complete

        try:
            incremental_reindex()
        except Exception as e:
            print(f"❌ Auto-reindex failed: {e}")
            import traceback
            traceback.print_exc()


async def periodic_reindex():
    """Fallback: Periodic reindex every N minutes"""
    while True:
        await asyncio.sleep(AUTO_REINDEX_INTERVAL)
        print(f"\n⏰ Periodic reindex (every {AUTO_REINDEX_INTERVAL}s)")
        try:
            incremental_reindex()
        except Exception as e:
            print(f"❌ Periodic reindex failed: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    # Startup
    print("\n" + "="*60)
    print("🚀 Universal AI Memory - Search Service v0.3.1")
    print("="*60)

    initialize_openai()
    incremental_reindex()

    # Start file watcher in background
    global file_watcher_task
    file_watcher_task = asyncio.create_task(watch_ledger_file())

    # Start periodic reindex in background
    periodic_task = asyncio.create_task(periodic_reindex())

    print(f"\n✅ Auto-reindex enabled:")
    print(f"  - File watcher: {LEDGER_PATH}")
    print(f"  - Periodic check: every {AUTO_REINDEX_INTERVAL}s")
    print("="*60 + "\n")

    yield

    # Shutdown
    if file_watcher_task:
        file_watcher_task.cancel()
    periodic_task.cancel()


# Initialize FastAPI with lifespan
app = FastAPI(
    title="Universal AI Memory - Search Service",
    description="Semantic search with auto-reindexing (v0.3.1 - Fixed)",
    version="0.3.1",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://claude.ai",
        "https://chatgpt.com",
        "https://gemini.google.com",
    ],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/healthz")
async def healthz():
    return {
        "status": "healthy",
        "indexed_entries": last_indexed_count,
        "index_ready": index is not None,
        "auto_reindex": True,
        "version": "0.3.1"
    }


@app.post("/v1/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    start = time.time()
    if index is None:
        raise HTTPException(503, "Index not ready")
    try:
        resp = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=request.query
        )
        q_emb = np.array([resp.data[0].embedding], dtype=np.float32)
        distances, indices = index.search(q_emb, min(request.limit * 2, len(memory_entries)))
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx >= len(memory_entries):
                continue
            entry = memory_entries[idx]
            platform = get_platform_from_entry(entry)
            role = get_role_from_entry(entry)
            if request.filter_platform and platform != request.filter_platform:
                continue
            if request.filter_role and role != request.filter_role:
                continue
            similarity = 1.0 / (1.0 + float(dist))
            results.append(SearchResult(
                entry_id=entry.get("id", ""),
                similarity_score=round(similarity, 4),
                platform=platform,
                role=role,
                content_preview=extract_content_preview(entry),
                timestamp=entry.get("created_at", ""),
                conversation_id=entry.get("content", {}).get("thread_id") if isinstance(entry.get("content"), dict) else None
            ))
            if len(results) >= request.limit:
                break
        return SearchResponse(
            query=request.query,
            results=results,
            total_indexed=last_indexed_count,
            search_time_ms=round((time.time() - start) * 1000, 2)
        )
    except Exception as e:
        raise HTTPException(500, f"Search failed: {e}")


@app.post("/v1/reindex")
async def reindex():
    try:
        incremental_reindex()
        return {
            "status": "success",
            "indexed": last_indexed_count,
            "auto_reindex": True,
            "version": "0.3.1"
        }
    except Exception as e:
        raise HTTPException(500, f"Reindex failed: {e}")


if __name__ == "__main__":
    uvicorn.run("search_service:app", host="0.0.0.0", port=8081)
