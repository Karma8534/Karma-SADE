"""
Karma Batch Ingest — Parallel processor for remaining ledger conversations.

Runs concurrent Graphiti add_episode calls with semaphore-limited parallelism.
FalkorDB has a low concurrent query limit, so concurrency is capped at 3.
Each episode that hits "Max pending queries" is retried with backoff.

Usage:
  docker exec -d karma-server sh -c 'python3 batch_ingest.py > /tmp/batch.log 2>&1'
  docker exec karma-server tail -f /tmp/batch.log

Skips:
  - Entries without user_message + assistant content
  - karma-terminal entries (already ingested live via chat server)
  - Entries already processed by bootstrap + previous batch runs

Hub/chat support (2026-03-03):
  - hub/chat/default tagged entries use assistant_text (not assistant_message)
  - Treated as provider "hub-chat", source_description "Karma hub-chat"
  - Retroactively ingests all 1543 existing Colby<->Karma conversations
"""
import argparse
import asyncio
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import config

# ─── Globals ────────────────────────────────────────────────────────────
_progress = {"done": 0, "errors": 0, "total": 0, "start": 0.0}


def log(msg: str):
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


# ─── Ledger Reading ─────────────────────────────────────────────────────

def read_conversation_pairs(ledger_path: str) -> list[dict]:
    pairs = []
    with open(ledger_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                content = entry.get("content", {})
                assistant = content.get("assistant_message") or content.get("assistant_text", "")
                if content.get("user_message") and assistant:
                    pairs.append(entry)
            except json.JSONDecodeError:
                pass
    return pairs


def get_already_ingested_count() -> dict:
    import redis
    try:
        r = redis.Redis(host=config.FALKORDB_HOST, port=config.FALKORDB_PORT, decode_responses=True)
        result = r.execute_command(
            "GRAPH.QUERY", config.GRAPHITI_GROUP_ID,
            "MATCH (e:Episodic) RETURN e.source_description AS src, count(e) AS cnt"
        )
        sources = {}
        if len(result) >= 2 and result[1]:
            for row in result[1]:
                sources[row[0]] = row[1]
        return sources
    except Exception as e:
        log(f"  WARN: Could not query existing episodes: {e}")
        return {}


def filter_unprocessed(pairs: list[dict], already: dict) -> list[dict]:
    done_counts = {}
    for src, cnt in already.items():
        if "Conversation on" in src:
            provider = src.replace("Conversation on ", "")
            done_counts[provider] = done_counts.get(provider, 0) + cnt
        elif "Batch ingest from" in src:
            provider = src.replace("Batch ingest from ", "")
            done_counts[provider] = done_counts.get(provider, 0) + cnt
        elif "Karma hub-chat" in src:
            done_counts["hub-chat"] = done_counts.get("hub-chat", 0) + cnt

    by_provider = {}
    for entry in pairs:
        tags = entry.get("tags", [])
        if "hub" in tags and "chat" in tags:
            provider = "hub-chat"
        else:
            provider = entry.get("content", {}).get("provider", "unknown")
        if provider not in by_provider:
            by_provider[provider] = []
        by_provider[provider].append(entry)

    remaining = []
    for provider, entries in by_provider.items():
        if provider == "karma-terminal":
            log(f"  Skip {len(entries)} karma-terminal (live)")
            continue
        already_done = done_counts.get(provider, 0)
        to_add = entries[already_done:]
        log(f"  {provider}: {len(entries)} total, {already_done} done, {len(to_add)} remaining")
        remaining.extend(to_add)

    remaining.sort(key=lambda x: x.get("content", {}).get("captured_at", "") or x.get("created_at", ""))
    return remaining


# ─── Graphiti Setup ─────────────────────────────────────────────────────

async def create_graphiti():
    from graphiti_core import Graphiti
    from graphiti_core.llm_client import OpenAIClient
    from graphiti_core.llm_client.config import LLMConfig
    from graphiti_core.driver.falkordb_driver import FalkorDriver

    llm_client = OpenAIClient(config=LLMConfig(
        api_key=config.OPENAI_API_KEY,
        model=config.ANALYSIS_MODEL,
    ))
    falkor_driver = FalkorDriver(
        host=config.FALKORDB_HOST,
        port=config.FALKORDB_PORT,
    )
    graphiti = Graphiti(graph_driver=falkor_driver, llm_client=llm_client)
    try:
        await graphiti.build_indices_and_constraints()
    except Exception:
        pass
    return graphiti


# ─── Single Episode Ingestion with Retry ─────────────────────────────────

async def ingest_one(graphiti, sem: asyncio.Semaphore, entry: dict, idx: int, max_retries: int = 3):
    content = entry.get("content", {})
    user_msg = content.get("user_message", "")
    assistant_msg = content.get("assistant_message", "") or content.get("assistant_text", "")
    tags = entry.get("tags", [])
    if "hub" in tags and "chat" in tags:
        provider = "hub-chat"
        source_desc = "Karma hub-chat"
        episode_body = "[karma-chat] User: " + user_msg[:500] + "\nKarma: " + assistant_msg[:500]
    else:
        provider = content.get("provider", "unknown")
        source_desc = "Batch ingest from " + provider
        episode_body = "[" + provider + "] User: " + user_msg[:500] + "\nAssistant: " + assistant_msg[:500]
    captured_at = content.get("captured_at", "") or entry.get("created_at", "")
    thread_id = content.get("thread_id", "karma-hub") if provider == "hub-chat" else content.get("thread_id", "unknown")

    async with sem:
        for attempt in range(max_retries):
            try:
                ref_time = (
                    datetime.fromisoformat(captured_at.replace("Z", "+00:00"))
                    if captured_at
                    else datetime.now(timezone.utc)
                )
                await graphiti.add_episode(
                    name=f"p_{provider[:3]}_{thread_id[:16]}_{idx}",
                    episode_body=episode_body,
                    source_description=source_desc,
                    reference_time=ref_time,
                    group_id=config.GRAPHITI_GROUP_ID,
                )
                _progress["done"] += 1
                break  # Success

            except Exception as e:
                err_str = str(e)
                if "Max pending queries" in err_str and attempt < max_retries - 1:
                    # FalkorDB overloaded — backoff and retry
                    wait = 2 ** attempt
                    await asyncio.sleep(wait)
                    continue
                else:
                    _progress["errors"] += 1
                    if _progress["errors"] <= 10:
                        log(f"    ERR #{idx} [{provider}] (attempt {attempt+1}): {err_str[:80]}")
                    break

    # Log every 10
    done = _progress["done"] + _progress["errors"]
    if done > 0 and done % 10 == 0:
        elapsed = time.monotonic() - _progress["start"]
        rate = _progress["done"] / elapsed if elapsed > 0 else 0
        pct = done / _progress["total"] * 100
        eta_s = ((_progress["total"] - done) / rate) if rate > 0 else 0
        log(f"  [{done}/{_progress['total']}] {pct:.0f}% | {rate:.2f} eps/s | "
            f"ETA {eta_s/60:.1f}m | ok:{_progress['done']} err:{_progress['errors']}")


# ─── Main ────────────────────────────────────────────────────────────────

async def run(args):
    log("=" * 60)
    log("KARMA BATCH INGEST — Parallel (FalkorDB-safe)")
    log(f"  Concurrency: {args.concurrency}  |  Retry: 3x with backoff")
    log("=" * 60)

    ledger_path = config.LEDGER_PATH
    if not Path(ledger_path).exists():
        log(f"  ERROR: Ledger not found at {ledger_path}")
        sys.exit(1)

    all_pairs = read_conversation_pairs(ledger_path)
    log(f"  Conversation pairs in ledger: {len(all_pairs)}")

    already = get_already_ingested_count()
    total_ingested = sum(already.values())
    log(f"  Already ingested: {total_ingested} episodes")

    remaining = filter_unprocessed(all_pairs, already)
    log(f"  TO PROCESS: {len(remaining)}")

    if not remaining:
        log("  All caught up!")
        return

    if args.dry_run:
        log(f"  DRY RUN — would process {len(remaining)} entries")
        return

    log(f"\n  Starting ingestion...")
    graphiti = await create_graphiti()
    sem = asyncio.Semaphore(args.concurrency)

    _progress["total"] = len(remaining)
    _progress["done"] = 0
    _progress["errors"] = 0
    _progress["start"] = time.monotonic()

    # Process in waves of 30 (small enough to avoid task pile-up)
    wave_size = 30
    total_waves = -(-len(remaining) // wave_size)
    for wave_start in range(0, len(remaining), wave_size):
        wave = remaining[wave_start:wave_start + wave_size]
        wave_num = wave_start // wave_size + 1
        log(f"  Wave {wave_num}/{total_waves} ({len(wave)} eps)...")

        tasks = [
            ingest_one(graphiti, sem, entry, wave_start + i)
            for i, entry in enumerate(wave)
        ]
        await asyncio.gather(*tasks)

    elapsed = time.monotonic() - _progress["start"]
    await graphiti.close()

    log("")
    log("=" * 60)
    log("COMPLETE")
    log(f"  OK:     {_progress['done']}")
    log(f"  Errors: {_progress['errors']}")
    log(f"  Time:   {elapsed:.0f}s ({elapsed/60:.1f}min)")
    if _progress["done"] > 0:
        log(f"  Rate:   {_progress['done']/elapsed:.2f} eps/s")

    import redis
    try:
        r = redis.Redis(host=config.FALKORDB_HOST, port=config.FALKORDB_PORT, decode_responses=True)
        ep = r.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, "MATCH (n:Episodic) RETURN count(n)")
        ent = r.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, "MATCH (n:Entity) RETURN count(n)")
        rel = r.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, "MATCH ()-[r]->() RETURN count(r)")
        log(f"  Graph: {ent[1][0][0]} entities | {ep[1][0][0]} episodes | {rel[1][0][0]} relationships")
    except Exception:
        pass
    log("=" * 60)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--concurrency", type=int, default=3,
                        help="Concurrent episodes (default: 3, FalkorDB safe)")
    asyncio.run(run(parser.parse_args()))


if __name__ == "__main__":
    main()
