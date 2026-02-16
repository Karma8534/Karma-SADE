"""
Karma Bootstrap — First Awakening
Reads the JSONL ledger, extracts conversation pairs, and builds
the initial world model in FalkorDB via Graphiti.
Also seeds the PostgreSQL analysis tables with karma facts/preferences.
"""
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values, Json

import config


def log(msg: str):
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


# ─── Phase 1: Read Ledger ─────────────────────────────────────────────

def read_ledger(path: str) -> list[dict]:
    """Read all entries from the JSONL ledger."""
    entries = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError as e:
                log(f"  WARN: Skipping line {i+1}: {e}")
    return entries


def classify_entries(entries: list[dict]) -> dict:
    """Sort entries into categories."""
    classified = {
        "captures": [],      # Extension conversation captures
        "facts": [],         # Karma-extracted facts
        "preferences": [],   # Karma-extracted preferences
        "artifacts": [],     # Documentation artifacts
        "sync_logs": [],     # Sync status logs (skip for analysis)
        "test": [],          # Test entries
        "other": [],
    }

    for entry in entries:
        tags = entry.get("tags", [])
        etype = entry.get("type", "")

        if "capture" in tags:
            classified["captures"].append(entry)
        elif "karma-sade" in tags:
            if etype == "fact":
                classified["facts"].append(entry)
            elif etype == "preference":
                classified["preferences"].append(entry)
            elif etype == "artifact":
                classified["artifacts"].append(entry)
            else:
                classified["sync_logs"].append(entry)
        elif "test" in tags:
            classified["test"].append(entry)
        else:
            classified["other"].append(entry)

    return classified


# ─── Phase 2: Seed PostgreSQL ──────────────────────────────────────────

def get_pg_connection():
    """Connect to PostgreSQL analysis schema."""
    return psycopg2.connect(
        host=config.POSTGRES_HOST,
        port=config.POSTGRES_PORT,
        dbname=config.POSTGRES_DB,
        user=config.POSTGRES_USER,
        password=config.POSTGRES_PASSWORD,
    )


def seed_karma_facts(conn, facts: list[dict]):
    """Import karma facts into user_preferences table."""
    if not facts:
        log("  No karma facts to import")
        return 0

    rows = []
    now = datetime.now(timezone.utc)
    for entry in facts:
        content = entry.get("content", {})
        key = content.get("key", "")
        value = content.get("value", "")
        if not key:
            continue
        rows.append((
            "personal",         # category
            key,                # key
            Json(value),        # value as JSONB
            0.95,               # high confidence (explicit fact)
            1,                  # sample_count
            "karma_fact",       # source
            now,                # first_seen
            now,                # last_updated
        ))

    if not rows:
        return 0

    # Deduplicate by (category, key) — keep last occurrence
    seen = {}
    for row in rows:
        seen[(row[0], row[1])] = row
    deduped = list(seen.values())

    with conn.cursor() as cur:
        execute_values(
            cur,
            """INSERT INTO analysis.user_preferences
               (category, key, value, confidence, sample_count, source, first_seen, last_updated)
               VALUES %s
               ON CONFLICT (category, key)
               DO UPDATE SET
                 value = EXCLUDED.value,
                 confidence = GREATEST(analysis.user_preferences.confidence, EXCLUDED.confidence),
                 sample_count = analysis.user_preferences.sample_count + 1,
                 last_updated = EXCLUDED.last_updated
            """,
            deduped
        )
    conn.commit()
    return len(deduped)


def seed_karma_preferences(conn, prefs: list[dict]):
    """Import karma preferences into user_preferences table."""
    if not prefs:
        log("  No karma preferences to import")
        return 0

    rows = []
    now = datetime.now(timezone.utc)
    for entry in prefs:
        content = entry.get("content", {})
        key = content.get("key", "")
        value = content.get("value", "")
        if not key:
            continue

        # Map known keys to categories
        category = "communication"
        comm_keys = {
            "guidance_style", "explanation_depth", "decision_making",
            "safety_approach", "response_style"
        }
        personal_keys = {
            "favorite_color", "chat_box_color", "background_color",
            "chat_area_background", "chat_bubble_color"
        }
        tool_keys = {
            "browser_control_needed", "sync_frequency", "save_personal_preferences"
        }

        if key in personal_keys:
            category = "personal"
        elif key in tool_keys:
            category = "tools"

        rows.append((
            category,
            key,
            Json(value),
            0.95,               # high confidence (explicit preference)
            1,
            "karma_preference",
            now,
            now,
        ))

    if not rows:
        return 0

    # Deduplicate by (category, key) — keep last occurrence
    seen = {}
    for row in rows:
        seen[(row[0], row[1])] = row
    deduped = list(seen.values())

    with conn.cursor() as cur:
        execute_values(
            cur,
            """INSERT INTO analysis.user_preferences
               (category, key, value, confidence, sample_count, source, first_seen, last_updated)
               VALUES %s
               ON CONFLICT (category, key)
               DO UPDATE SET
                 value = EXCLUDED.value,
                 confidence = GREATEST(analysis.user_preferences.confidence, EXCLUDED.confidence),
                 sample_count = analysis.user_preferences.sample_count + 1,
                 last_updated = EXCLUDED.last_updated
            """,
            deduped
        )
    conn.commit()
    return len(deduped)


# ─── Phase 3: FalkorDB / Graphiti World Model ─────────────────────────

async def build_world_model(captures: list[dict], limit: int):
    """
    Feed conversation captures into Graphiti to build the knowledge graph.
    Graphiti extracts entities, relationships, and temporal context automatically.
    """
    try:
        from graphiti_core import Graphiti
        from graphiti_core.llm_client import OpenAIClient
        from graphiti_core.llm_client.config import LLMConfig
        from graphiti_core.driver.falkordb_driver import FalkorDriver
    except ImportError as e:
        log(f"  ERROR: graphiti-core not available: {e}")
        log("  Skipping world model build — install graphiti-core[falkordb]")
        return 0

    log(f"  Connecting to FalkorDB at {config.FALKORDB_HOST}:{config.FALKORDB_PORT}...")

    llm_config = LLMConfig(
        api_key=config.OPENAI_API_KEY,
        model=config.ANALYSIS_MODEL,
    )
    llm_client = OpenAIClient(config=llm_config)

    falkor_driver = FalkorDriver(
        host=config.FALKORDB_HOST,
        port=config.FALKORDB_PORT,
    )

    graphiti = Graphiti(
        graph_driver=falkor_driver,
        llm_client=llm_client,
    )

    try:
        await graphiti.build_indices_and_constraints()
        log("  FalkorDB indices ready")
    except Exception as e:
        log(f"  WARN: Index creation: {e}")

    # Sort by captured_at for temporal ordering
    sorted_captures = sorted(
        captures,
        key=lambda x: x.get("content", {}).get("captured_at", ""),
    )

    # Limit for bootstrap
    to_process = sorted_captures[:limit]
    log(f"  Processing {len(to_process)} of {len(sorted_captures)} captures...")

    processed = 0
    errors = 0

    for i, entry in enumerate(to_process):
        content = entry.get("content", {})
        user_msg = content.get("user_message", "")
        assistant_msg = content.get("assistant_message", "")
        provider = content.get("provider", "unknown")
        captured_at = content.get("captured_at", "")
        thread_id = content.get("thread_id", "")

        if not user_msg and not assistant_msg:
            continue

        # Build episode content for Graphiti
        episode_body = f"[{provider}] User: {user_msg[:500]}\nAssistant: {assistant_msg[:500]}"

        try:
            ref_time = datetime.fromisoformat(captured_at.replace("Z", "+00:00")) if captured_at else datetime.now(timezone.utc)

            await graphiti.add_episode(
                name=f"conversation_{thread_id}_{i}",
                episode_body=episode_body,
                source_description=f"Conversation on {provider}",
                reference_time=ref_time,
                group_id=config.GRAPHITI_GROUP_ID,
            )
            processed += 1

            if (i + 1) % 10 == 0:
                log(f"  Progress: {i+1}/{len(to_process)} episodes added")

        except Exception as e:
            errors += 1
            if errors <= 5:
                log(f"  ERROR on entry {i}: {e}")
            elif errors == 6:
                log("  (suppressing further errors...)")

    log(f"  World model: {processed} episodes added, {errors} errors")

    await graphiti.close()
    return processed


# ─── Main Bootstrap ────────────────────────────────────────────────────

def main():
    log("=" * 60)
    log("KARMA BOOTSTRAP — First Awakening")
    log("=" * 60)

    # Phase 1: Read and classify ledger
    log("")
    log("Phase 1: Reading ledger...")
    ledger_path = config.LEDGER_PATH
    if not Path(ledger_path).exists():
        log(f"  ERROR: Ledger not found at {ledger_path}")
        sys.exit(1)

    entries = read_ledger(ledger_path)
    classified = classify_entries(entries)

    log(f"  Total entries: {len(entries)}")
    log(f"  Captures:      {len(classified['captures'])}")
    log(f"  Facts:         {len(classified['facts'])}")
    log(f"  Preferences:   {len(classified['preferences'])}")
    log(f"  Artifacts:     {len(classified['artifacts'])}")
    log(f"  Sync logs:     {len(classified['sync_logs'])} (skipped)")
    log(f"  Test:          {len(classified['test'])} (skipped)")

    # Phase 2: Seed PostgreSQL with known facts
    log("")
    log("Phase 2: Seeding PostgreSQL with karma facts + preferences...")
    try:
        conn = get_pg_connection()
        facts_imported = seed_karma_facts(conn, classified["facts"])
        log(f"  Imported {facts_imported} facts")
        prefs_imported = seed_karma_preferences(conn, classified["preferences"])
        log(f"  Imported {prefs_imported} preferences")
        conn.close()
        log("  PostgreSQL seeded successfully")
    except Exception as e:
        log(f"  ERROR connecting to PostgreSQL: {e}")
        log("  Continuing without PostgreSQL seeding...")

    # Phase 3: Build world model in FalkorDB
    log("")
    log("Phase 3: Building world model in FalkorDB...")
    log(f"  Bootstrap limit: {config.BOOTSTRAP_LIMIT} conversations")

    import asyncio
    try:
        processed = asyncio.run(
            build_world_model(classified["captures"], config.BOOTSTRAP_LIMIT)
        )
        log(f"  World model bootstrap complete: {processed} episodes")
    except Exception as e:
        log(f"  ERROR building world model: {e}")
        log("  World model will be built incrementally on next run")

    # Summary
    log("")
    log("=" * 60)
    log("BOOTSTRAP COMPLETE")
    log(f"  Facts in PostgreSQL: {facts_imported if 'facts_imported' in dir() else '?'}")
    log(f"  Preferences in PostgreSQL: {prefs_imported if 'prefs_imported' in dir() else '?'}")
    log(f"  Episodes in FalkorDB: {processed if 'processed' in dir() else '?'}")
    log("=" * 60)


if __name__ == "__main__":
    main()
