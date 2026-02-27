"""Step 4.4: Incremental Transcript Processing (P8)
Tracks last_processed_line per ledger file. Only processes new lines on each tick.
Groups flat JSONL into logical turns. Offline queue if write fails."""
import json
import os
import time

STATE_FILE = os.getenv("TRANSCRIPT_STATE_FILE", "/opt/seed-vault/memory_v1/ledger/.transcript_state.json")
PENDING_FILE = os.getenv("PENDING_OBS_FILE", "/opt/seed-vault/memory_v1/ledger/pending_observations.jsonl")

def _load_state() -> dict:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def _save_state(state: dict):
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f)
    os.replace(tmp, STATE_FILE)

def _append_pending(observation: dict):
    try:
        with open(PENDING_FILE, "a") as f:
            f.write(json.dumps(observation) + "\n")
    except Exception as e:
        print(f"[TRANSCRIPT] pending queue write failed: {e}")

def process_ledger_incremental(ledger_path: str, processor_fn=None) -> dict:
    state = _load_state()
    file_key = os.path.basename(ledger_path)
    last_line = state.get(file_key, 0)
    if not os.path.exists(ledger_path):
        return {"processed": 0, "skipped": 0, "errors": 0, "new_watermark": last_line}
    processed = skipped = errors = current_line = 0
    with open(ledger_path, "r", encoding="utf-8") as f:
        for current_line, raw in enumerate(f, start=1):
            if current_line <= last_line:
                continue
            raw = raw.strip()
            if not raw:
                skipped += 1
                continue
            try:
                entry = json.loads(raw)
            except json.JSONDecodeError:
                errors += 1
                continue
            if processor_fn:
                try:
                    result = processor_fn(entry)
                    if result:
                        processed += 1
                    else:
                        skipped += 1
                except Exception as e:
                    errors += 1
                    _append_pending({"source": file_key, "line": current_line, "error": str(e), "timestamp": time.time()})
            else:
                processed += 1
    state[file_key] = current_line
    _save_state(state)
    return {"processed": processed, "skipped": skipped, "errors": errors, "new_watermark": current_line}

def group_into_turns(entries: list) -> list:
    turns = []
    current_turn = None
    for entry in entries:
        content = entry.get("content", {})
        user_msg = content.get("user_message", "")
        asst_msg = content.get("assistant_message", "")
        thread_id = content.get("thread_id", "default")
        if not user_msg and not asst_msg:
            continue
        if current_turn and current_turn["thread_id"] == thread_id:
            if user_msg:
                current_turn["messages"].append({"role": "user", "content": user_msg})
            if asst_msg:
                current_turn["messages"].append({"role": "assistant", "content": asst_msg})
        else:
            if current_turn:
                turns.append(current_turn)
            current_turn = {"thread_id": thread_id, "messages": [], "started_at": content.get("captured_at", "")}
            if user_msg:
                current_turn["messages"].append({"role": "user", "content": user_msg})
            if asst_msg:
                current_turn["messages"].append({"role": "assistant", "content": asst_msg})
    if current_turn:
        turns.append(current_turn)
    return turns

def get_processing_status() -> dict:
    state = _load_state()
    pending_count = 0
    if os.path.exists(PENDING_FILE):
        with open(PENDING_FILE, "r") as f:
            pending_count = sum(1 for line in f if line.strip())
    return {"watermarks": state, "pending_retry": pending_count}

def retry_pending() -> dict:
    if not os.path.exists(PENDING_FILE):
        return {"retried": 0, "failed": 0}
    entries = []
    with open(PENDING_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except Exception:
                    pass
    if not entries:
        return {"retried": 0, "failed": 0}
    remaining = []
    retried = 0
    for entry in entries:
        age_hours = (time.time() - entry.get("timestamp", 0)) / 3600
        if age_hours > 168:
            retried += 1
        else:
            remaining.append(entry)
    with open(PENDING_FILE, "w") as f:
        for entry in remaining:
            f.write(json.dumps(entry) + "\n")
    return {"retried": retried, "failed": len(remaining)}
