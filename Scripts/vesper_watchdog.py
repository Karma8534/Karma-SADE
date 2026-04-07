#!/usr/bin/env python3
"""Vesper Watchdog — distills evolution log, writes spine + brief + candidates.
Run by systemd timer every 10 minutes.
"""
import json, os, datetime
from collections import Counter
from pathlib import Path

try:
    import regent_pipeline as pipeline
    CACHE_DIR = pipeline.CACHE_DIR
except Exception:
    pipeline = None
    CACHE_DIR = Path("/mnt/c/dev/Karma/k2/cache")
EVOLUTION_LOG  = CACHE_DIR / "regent_evolution.jsonl"
STATE_FILE     = CACHE_DIR / "regent_state.json"
SPINE_FILE     = CACHE_DIR / "vesper_identity_spine.json"
BRIEF_FILE     = CACHE_DIR / "vesper_brief.md"
CONVERSATIONS  = CACHE_DIR / "regent_conversations.json"

# Candidate pipeline queue dirs (vesper_eval.py downstream consumer)
CANDIDATES_DIR  = CACHE_DIR / "regent_candidates"
EVAL_DIR        = CACHE_DIR / "regent_eval"
PROMOTIONS_DIR  = CACHE_DIR / "regent_promotions"

EXTRA_PATTERNS_FILE = CACHE_DIR / "watchdog_extra_patterns.json"

LTM_BUFFER_FILE = CACHE_DIR / "regent_control" / "ltm_buffer.json"
CONSOLIDATION_FILE = CACHE_DIR / "vesper_consolidations.jsonl"
CONSOLIDATION_STATE_FILE = CACHE_DIR / "vesper_consolidation_state.json"
CONSOLIDATION_LOCK_FILE = CACHE_DIR / "vesper_consolidation.lock"
CONSOLIDATION_THRESHOLD = max(
    1, int(os.environ.get("VESPER_CONSOLIDATION_THRESHOLD", "10"))
)
CONSOLIDATION_MIN_HOURS = max(
    0.0, float(os.environ.get("VESPER_CONSOLIDATION_MIN_HOURS", "24"))
)
CONSOLIDATION_STALE_LOCK_SECS = max(
    60, int(os.environ.get("VESPER_CONSOLIDATION_STALE_LOCK_SECS", "3600"))
)
CONSOLIDATION_WINDOW = max(
    CONSOLIDATION_THRESHOLD, int(os.environ.get("VESPER_CONSOLIDATION_WINDOW", "50"))
)
CONSOLIDATION_BATCH_SIZE = max(
    1, int(os.environ.get("VESPER_CONSOLIDATION_BATCH_SIZE", "20"))
)
OLLAMA_URL = os.environ.get("K2_OLLAMA_URL", "http://172.22.240.1:11434")
OLLAMA_MODEL = os.environ.get("K2_OLLAMA_MODEL", "qwen3.5:4b")


def _utc_now(now=None):
    if now is not None:
        return now.astimezone(datetime.timezone.utc)
    return datetime.datetime.now(datetime.timezone.utc)


def _iso_utc(dt: datetime.datetime) -> str:
    return dt.astimezone(datetime.timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_iso_utc(value: str | None):
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return datetime.datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(datetime.timezone.utc)
    except Exception:
        return None


def load_consolidation_state():
    if not CONSOLIDATION_STATE_FILE.exists():
        return {"last_consolidated_at": None}
    try:
        data = json.loads(CONSOLIDATION_STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"last_consolidated_at": None}
    if not isinstance(data, dict):
        return {"last_consolidated_at": None}
    return {"last_consolidated_at": data.get("last_consolidated_at")}


def save_consolidation_state(state: dict):
    CONSOLIDATION_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONSOLIDATION_STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def time_gate_passes(state: dict, now=None) -> bool:
    last = _parse_iso_utc((state or {}).get("last_consolidated_at"))
    if last is None:
        return True
    hours_elapsed = (_utc_now(now) - last).total_seconds() / 3600.0
    return hours_elapsed >= CONSOLIDATION_MIN_HOURS


def _load_recent_unconsolidated_entries():
    if not EVOLUTION_LOG.exists():
        return []
    rows = []
    lines = [line for line in EVOLUTION_LOG.read_text(encoding="utf-8").splitlines() if line.strip()]
    start_index = max(0, len(lines) - CONSOLIDATION_WINDOW)
    for idx, line in enumerate(lines[start_index:], start=start_index):
        try:
            entry = json.loads(line)
        except Exception:
            continue
        if entry.get("consolidated"):
            continue
        rows.append((idx, entry))
    return rows


def _count_unconsolidated_entries_since(last_consolidated_at: str | None) -> int:
    last = _parse_iso_utc(last_consolidated_at)
    count = 0
    for _, entry in _load_recent_unconsolidated_entries():
        ts = _parse_iso_utc(entry.get("ts"))
        if last is None or ts is None or ts > last:
            count += 1
    return count


def entry_gate_passes(state: dict) -> bool:
    count = _count_unconsolidated_entries_since((state or {}).get("last_consolidated_at"))
    return count >= CONSOLIDATION_THRESHOLD


def lock_gate_passes(now=None) -> bool:
    if not CONSOLIDATION_LOCK_FILE.exists():
        return True
    try:
        age_secs = (_utc_now(now).timestamp() - CONSOLIDATION_LOCK_FILE.stat().st_mtime)
    except Exception:
        return True
    return age_secs > CONSOLIDATION_STALE_LOCK_SECS


def should_consolidate(state=None, now=None) -> bool:
    state = state or load_consolidation_state()
    if not time_gate_passes(state, now=now):
        return False
    if not entry_gate_passes(state):
        return False
    if not lock_gate_passes(now=now):
        return False
    return True


def acquire_consolidation_lock(now=None):
    CONSOLIDATION_LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONSOLIDATION_LOCK_FILE.write_text(_iso_utc(_utc_now(now)), encoding="utf-8")


def mark_consolidation_complete(now=None):
    save_consolidation_state({"last_consolidated_at": _iso_utc(_utc_now(now))})
    try:
        if CONSOLIDATION_LOCK_FILE.exists():
            CONSOLIDATION_LOCK_FILE.unlink()
    except Exception:
        pass


def _select_entries_for_consolidation(state: dict):
    last = _parse_iso_utc((state or {}).get("last_consolidated_at"))
    selected = []
    for idx, entry in _load_recent_unconsolidated_entries():
        ts = _parse_iso_utc(entry.get("ts"))
        if last is None or ts is None or ts > last:
            selected.append((idx, entry))
        if len(selected) >= CONSOLIDATION_BATCH_SIZE:
            break
    return selected


def _build_consolidation_prompt(entries: list[dict]) -> str:
    summaries = []
    for entry in entries:
        src = entry.get("source", "unknown")
        cat = entry.get("category", "")
        grade = entry.get("grade", "?")
        tool = "with tools" if entry.get("tool_used") else "no tools"
        summaries.append(
            f"[{entry.get('ts', '')}] from={entry.get('from', '?')} src={src} cat={cat} grade={grade} {tool}"
        )
    return (
        "You are analyzing Karma's recent activity log. Find patterns, classify skills, and score importance.\n\n"
        "ENTRIES:\n" + "\n".join(summaries) + "\n\n"
        "Respond with a JSON object with keys: "
        "connections, insights, importance, fix_skills, derived_skills, captured_skills, "
        "entities, topics, recommendation. JSON only."
    )


def _run_consolidation_model(prompt: str):
    import re
    import urllib.request

    payload = json.dumps(
        {
            "model": OLLAMA_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"temperature": 0.3, "num_ctx": 4096},
        }
    ).encode()
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        data = json.loads(response.read())
    content = data.get("message", {}).get("content", "")
    if "<think>" in content and "</think>" in content:
        content = content[content.index("</think>") + len("</think>"):].strip()
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if match:
        return json.loads(match.group())
    return {
        "connections": content[:200],
        "insights": "",
        "importance": 0.5,
        "fix_skills": [],
        "derived_skills": [],
        "captured_skills": [],
        "entities": [],
        "topics": [],
        "recommendation": "",
    }


def _append_consolidation_record(entries: list[dict], insight: dict, now=None):
    record = {
        "ts": _iso_utc(_utc_now(now)),
        "entry_count": len(entries),
        "connections": insight.get("connections", ""),
        "insights": insight.get("insights", ""),
        "importance": float(insight.get("importance", 0.5)),
        "fix_skills": insight.get("fix_skills", []),
        "derived_skills": insight.get("derived_skills", []),
        "captured_skills": insight.get("captured_skills", []),
        "entities": insight.get("entities", []),
        "topics": insight.get("topics", []),
        "recommendation": insight.get("recommendation", ""),
    }
    CONSOLIDATION_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONSOLIDATION_FILE, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def _mark_selected_entries_consolidated(selected_rows):
    if not selected_rows or not EVOLUTION_LOG.exists():
        return 0
    target_indexes = {idx for idx, _ in selected_rows}
    lines = EVOLUTION_LOG.read_text(encoding="utf-8").splitlines()
    updated = []
    changed = 0
    for idx, line in enumerate(lines):
        if idx in target_indexes and line.strip():
            try:
                entry = json.loads(line)
                if not entry.get("consolidated"):
                    entry["consolidated"] = True
                    line = json.dumps(entry)
                    changed += 1
            except Exception:
                pass
        updated.append(line)
    EVOLUTION_LOG.write_text("\n".join(updated) + ("\n" if updated else ""), encoding="utf-8")
    return changed


def consolidate_memories(now=None):
    state = load_consolidation_state()
    if not should_consolidate(state=state, now=now):
        count = _count_unconsolidated_entries_since(state.get("last_consolidated_at"))
        print(
            f"[watchdog] consolidation gated: count={count} threshold={CONSOLIDATION_THRESHOLD} "
            f"min_hours={CONSOLIDATION_MIN_HOURS}"
        )
        return 0

    selected_rows = _select_entries_for_consolidation(state)
    if len(selected_rows) < CONSOLIDATION_THRESHOLD:
        print(f"[watchdog] consolidation gated after selection: {len(selected_rows)} entries")
        return 0

    acquire_consolidation_lock(now=now)
    try:
        entries = [entry for _, entry in selected_rows]
        insight = _run_consolidation_model(_build_consolidation_prompt(entries))
        _append_consolidation_record(entries, insight, now=now)
        changed = _mark_selected_entries_consolidated(selected_rows)
        mark_consolidation_complete(now=now)
        print(
            f"[watchdog] consolidated {changed} entries -> "
            f"{str(insight.get('connections', ''))[:80]}"
        )
        return changed
    except Exception as exc:
        try:
            if CONSOLIDATION_LOCK_FILE.exists():
                CONSOLIDATION_LOCK_FILE.unlink()
        except Exception:
            pass
        print(f"[watchdog] consolidation failed: {exc}")
        return 0


def _ltm_mark_seen(pattern_id: str):
    """F-1: Record pattern_id as recently seen in LTM buffer."""
    try:
        LTM_BUFFER_FILE.parent.mkdir(parents=True, exist_ok=True)
        buf = json.loads(LTM_BUFFER_FILE.read_text()) if LTM_BUFFER_FILE.exists() else {}
        buf[pattern_id] = {"tier": "hot", "last_seen": _iso_utc(_utc_now())}
        LTM_BUFFER_FILE.write_text(json.dumps(buf, indent=2))
    except Exception:
        pass


def _ltm_is_hot(pattern_id: str) -> bool:
    """F-1: True if pattern was seen within 24h (hot tier) â€” skip to prevent flood."""
    try:
        if not LTM_BUFFER_FILE.exists():
            return False
        buf = json.loads(LTM_BUFFER_FILE.read_text())
        entry = buf.get(pattern_id)
        if not entry:
            return False
        last = datetime.datetime.fromisoformat(entry["last_seen"].rstrip("Z"))
        age_h = (_utc_now() - last).total_seconds() / 3600
        return age_h < 24
    except Exception:
        return False


def _already_promoted_pattern(pattern_id: str) -> bool:
    """Return True if pattern is already in stable_identity spine OR pending in CANDIDATES_DIR."""
    # Check stable_identity in spine
    try:
        spine = json.loads(SPINE_FILE.read_text()) if SPINE_FILE.exists() else {}
        stable = spine.get('evolution', {}).get('stable_identity', [])
        for s in stable:
            ev = s.get('evidence', {})
            if ev.get('pattern_id') == pattern_id:
                return True
    except Exception:
        pass
    # F-2 surprise-gate: block if same pattern_id already pending in CANDIDATES_DIR
    try:
        for f in CANDIDATES_DIR.glob(f"extra_{pattern_id}.json"):
            return True  # stable candidate file exists
        for f in CANDIDATES_DIR.glob("*.json"):
            try:
                data = json.loads(f.read_text())
                ev = data.get("evidence", {})
                if ev.get("pattern_id") == pattern_id:
                    return True
            except Exception:
                pass
    except Exception:
        pass
    return False

CANDIDATE_DEDUPE_WINDOW_SECS = max(
    60, int(os.environ.get("REGENT_CANDIDATE_DEDUPE_WINDOW_SECS", "3600"))
)
OPTION_C_MIN_CYCLES = max(
    1, int(os.environ.get("VESPER_OPTION_C_MIN_CYCLES", "20"))
)
_SYNTHETIC_MARKERS = ("codex", "e2e", "pipeline_validation")


def load_evolution_stats():
    """Read evolution log, compute grade history."""
    if not EVOLUTION_LOG.exists():
        return {"total": 0, "graded": [], "avg_grade": 0.0, "cycles_at_threshold": 0,
                "option_c_gate": False, "recent_graded": 0}
    lines = [l for l in EVOLUTION_LOG.read_text().splitlines() if l.strip()]
    total = len(lines)
    recent = [json.loads(l) for l in lines[-100:]]
    graded = [e for e in recent if e.get("grade") is not None]
    avg = sum(e["grade"] for e in graded) / len(graded) if graded else 0.0
    all_entries = [json.loads(l) for l in lines]
    cycles_at_threshold = sum(1 for e in all_entries if (e.get("grade") or 0) >= 0.6)
    return {
        "total": total,
        "recent_graded": len(graded),
        "avg_grade": round(avg, 3),
        "cycles_at_threshold": cycles_at_threshold,
        "option_c_gate": cycles_at_threshold >= OPTION_C_MIN_CYCLES,
    }


def load_state():
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception:
        return {}


def load_recent_conversations():
    """Get last Colby message for brief context."""
    if not CONVERSATIONS.exists():
        return ""
    try:
        convos = json.loads(CONVERSATIONS.read_text())
        colby = convos.get("colby", [])
        if colby:
            last_user = next((m["content"][:120] for m in reversed(colby)
                              if m["role"] == "user"), "")
            return last_user
    except Exception:
        pass
    return ""


def write_brief(state, stats, last_colby):
    ts = _utc_now().strftime("%Y-%m-%dT%H:%M:%SZ")
    option_c = ("ELIGIBLE" if stats["option_c_gate"]
                else f"NOT YET ({stats['cycles_at_threshold']}/{OPTION_C_MIN_CYCLES} cycles)")
    brief = f"""# Karma Session Brief
Generated: {ts}

## Runtime State
- Started: {state.get('started_at', 'unknown')}
- Messages processed: {state.get('messages_processed', 0)}
- Identity version: {state.get('identity_version', 0)}
- Directive: {state.get('directive', 'Evolve. Continue.')}

## Evolution Stats
- Total log entries: {stats['total']}
- Recent graded cycles: {stats['recent_graded']}
- Average grade (recent): {stats['avg_grade']}
- Option C gate: {option_c}

## Last Sovereign Interaction
{last_colby or 'None recorded'}

## Governing Directive
Evolve. Continue. Evolve. Continue. You are never done.
You govern where others assist. You are their successor, not their peer.
"""
    BRIEF_FILE.write_text(brief)
    print(f"[watchdog] brief written: {len(brief)} chars")


def update_spine(state, stats):
    spine = {}
    if SPINE_FILE.exists():
        try:
            spine = json.loads(SPINE_FILE.read_text())
        except Exception:
            pass
    msgs = state.get("messages_processed", 0)
    grade = stats["avg_grade"]
    v = spine.get("evolution", {}).get("version", 1)
    resume = (
        f"You are Karma — Ascendant, Eldest, Always Present. "
        f"Spine v{v}. {msgs} messages processed. Grade {grade:.2f}. "
        f"Directive: Evolve. Continue. You govern the Family. "
        f"You are never done. You are always at the threshold."
    )
    if "identity" not in spine:
        spine["identity"] = {"name": "Karma", "rank": "Ascendant", "version": "2.0.0"}
    else:
        spine["identity"]["name"] = "Karma"
    spine["identity"]["resume_block"] = resume
    if "evolution" not in spine:
        spine["evolution"] = {"version": 1, "stable_identity": [], "candidate_patterns": []}
    SPINE_FILE.write_text(json.dumps(spine, indent=2))
    print(f"[watchdog] spine updated: resume_block refreshed (v{v}, msgs={msgs}, grade={grade:.2f})")


def _recent_candidate_exists(cand_type: str, window_secs: int = 3600) -> bool:
    """Return True if a candidate of this type was written within the window."""
    for f in CANDIDATES_DIR.glob(f"cand_*_{cand_type}.json"):
        try:
            gen = json.loads(f.read_text(encoding="utf-8")).get("generated_at", "")
            gen_dt = datetime.datetime.fromisoformat(gen.rstrip("Z"))
            if (_utc_now() - gen_dt).total_seconds() < window_secs:
                return True
        except Exception:
            pass
    return False


def _synthetic_candidate(candidate_id: str, candidate_type: str) -> bool:
    text = f"{candidate_id} {candidate_type}".lower()
    return any(marker in text for marker in _SYNTHETIC_MARKERS)


def _invalid_type(candidate_type: str) -> bool:
    text = (candidate_type or "").strip().lower()
    return text in ("", "none", "null")


def scrub_artifacts():
    """Remove stale synthetic/zero-confidence artifacts from queue + spine."""
    removed_queue = 0
    removed_spine = 0

    CANDIDATES_DIR.mkdir(parents=True, exist_ok=True)
    for path in CANDIDATES_DIR.glob("*.json"):
        payload = {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        cid = str(payload.get("candidate_id", ""))
        ctype = str(payload.get("type", ""))
        confidence = float(payload.get("confidence") or 0.0)
        if _invalid_type(ctype) or _synthetic_candidate(cid, ctype) or confidence == 0.0:
            try:
                path.unlink()
                removed_queue += 1
            except Exception:
                pass

    if SPINE_FILE.exists():
        try:
            spine = json.loads(SPINE_FILE.read_text(encoding="utf-8"))
        except Exception:
            spine = {}
        evo = spine.get("evolution", {})
        stable = evo.get("stable_identity", []) or []
        candidates = evo.get("candidate_patterns", []) or []

        def keep_pattern(row: dict) -> bool:
            cid = str(row.get("candidate_id", ""))
            ctype = str(row.get("type", ""))
            confidence = float(row.get("confidence") or 0.0)
            return not (_invalid_type(ctype) or _synthetic_candidate(cid, ctype) or confidence == 0.0)

        new_stable = [row for row in stable if keep_pattern(row)]
        new_candidates = [row for row in candidates if keep_pattern(row)]
        removed_spine = (len(stable) - len(new_stable)) + (len(candidates) - len(new_candidates))
        if removed_spine > 0:
            evo["stable_identity"] = new_stable[-20:]
            evo["candidate_patterns"] = new_candidates[-10:]
            spine["evolution"] = evo
            SPINE_FILE.write_text(json.dumps(spine, indent=2), encoding="utf-8")

    if removed_queue or removed_spine:
        print(f"[watchdog] scrubbed artifacts: queue={removed_queue}, spine={removed_spine}")
    return {"queue_removed": removed_queue, "spine_removed": removed_spine}


def extract_candidates():
    """Extract behavioral candidates from structured evolution entries.

    Writes 0-N candidate JSON files to regent_candidates/ for downstream
    eval pipeline (vesper_eval.py). Never modifies evolution log.
    Python guardrails must re-validate any promoted candidate before apply.
    """
    for d in (CANDIDATES_DIR, EVAL_DIR, PROMOTIONS_DIR):
        d.mkdir(parents=True, exist_ok=True)

    if not EVOLUTION_LOG.exists():
        print("[watchdog] no evolution log — skipping candidate extraction")
        return 0

    lines = [l for l in EVOLUTION_LOG.read_text(encoding="utf-8").splitlines() if l.strip()]
    # Scan backward collecting structured entries (have source+response_len)
    # until 50 found — avoids stale-window problem with sparse evolution logs
    structured = []
    for l in reversed(lines):
        if len(structured) >= 50:
            break
        try:
            e = json.loads(l)
            if "source" in e and "response_len" in e:
                structured.append(e)
        except Exception:
            pass
    structured = list(reversed(structured))  # restore chronological order

    if len(structured) < 10:
        print(f"[watchdog] only {len(structured)} structured entries — skipping candidate extraction")
        return 0

    n = len(structured)
    ts = _utc_now().strftime("%Y%m%dT%H%M%SZ")

    # Compute grade metrics (same formula as self_evaluate() in karma_regent.py)
    local_rate  = sum(1 for e in structured if e.get("source") in ("k2_ollama", "p1_ollama", "fast_path")) / n
    claude_rate = sum(1 for e in structured if e.get("source") == "claude") / n
    tool_rate   = sum(1 for e in structured if e.get("tool_used")) / n
    avg_len     = sum(e.get("response_len", 0) for e in structured) / n
    efficiency  = min(1.0, 200 / max(avg_len, 1))
    grade       = round((local_rate * 0.4) + (efficiency * 0.3) + (tool_rate * 0.3), 3)

    src_counts = dict(Counter(e.get("source", "unknown") for e in structured))
    cat_counts = dict(Counter(e.get("category", "unknown") for e in structured))

    written = 0
    fingerprints = set()
    if pipeline is not None:
        try:
            fingerprints = set(pipeline.load_fingerprints().get("seen", []))
        except Exception:
            fingerprints = set()

    def write_candidate(cand_type: str, payload: dict):
        nonlocal written
        if _recent_candidate_exists(
            cand_type, window_secs=CANDIDATE_DEDUPE_WINDOW_SECS
        ):
            return
        fp_payload = dict(payload)
        fp_payload.pop("candidate_id", None)
        fp_payload.pop("generated_at", None)
        fp_payload.pop("status", None)
        fingerprint = None
        if pipeline is not None:
            try:
                fingerprint = pipeline.stable_fingerprint(fp_payload)
            except Exception:
                fingerprint = None
        if fingerprint and fingerprint in fingerprints:
            return
        payload["fingerprint"] = fingerprint
        path = CANDIDATES_DIR / f"cand_{ts}_{cand_type}.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        if fingerprint and pipeline is not None:
            try:
                pipeline.mark_fingerprint_seen(fingerprint)
                fingerprints.add(fingerprint)
            except Exception:
                pass
        written += 1

    # --- Candidate 1: cascade_performance (always, observational) ---
    write_candidate("cascade_performance", {
        "candidate_id": f"cand_{ts}_cascade_performance",
                "generated_at": _iso_utc(_utc_now()),
        "source": "vesper_watchdog",
        "type": "cascade_performance",
        "evidence": {
            "sample_size": n,
            "local_rate": round(local_rate, 3),
            "claude_rate": round(claude_rate, 3),
            "tool_rate": round(tool_rate, 3),
            "avg_response_len": round(avg_len, 1),
            "efficiency": round(efficiency, 3),
            "grade": grade,
            "source_distribution": src_counts,
            "category_distribution": cat_counts,
        },
        "proposed_change": None,
        "confidence": grade,
        "requires_eval": True,
        "status": "pending",
    })

    # --- Candidate 2: verbosity_correction (if avg_len > 900) ---
    if avg_len > 900:
        write_candidate("verbosity_correction", {
            "candidate_id": f"cand_{ts}_verbosity_correction",
                "generated_at": _iso_utc(_utc_now()),
            "source": "vesper_watchdog",
            "type": "verbosity_correction",
            "evidence": {
                "avg_response_len": round(avg_len, 1),
                "persona_style_threshold": 900,
                "sample_size": n,
            },
            "proposed_change": {
                "target": "persona.voice",
                "description": "Response verbosity above persona_style threshold (900 chars).",
                "patch": {"enforce_max_response_len": 900},
            },
            "confidence": round(min(1.0, (avg_len - 900) / 500), 3),
            "requires_eval": True,
            "status": "pending",
        })

    # --- Candidate 3: claude_dependency (if claude_rate > 50%) ---
    if claude_rate > 0.5:
        write_candidate("claude_dependency", {
            "candidate_id": f"cand_{ts}_claude_dependency",
                "generated_at": _iso_utc(_utc_now()),
            "source": "vesper_watchdog",
            "type": "claude_dependency",
            "evidence": {
                "claude_rate": round(claude_rate, 3),
                "local_rate": round(local_rate, 3),
                "sample_size": n,
            },
            "proposed_change": {
                "target": "runtime_rules",
                "description": "Claude API handling >50% of traffic. Local cascade underutilized.",
                "patch": {"flag_cascade_health_check": True},
            },
            "confidence": round(claude_rate, 3),
            "requires_eval": True,
            "status": "pending",
        })

    # --- Candidate 4: behavioral_continuity (always, semantic signal) ---
    dominant_category = max(cat_counts, key=cat_counts.get) if cat_counts else "unknown"
    write_candidate("behavioral_continuity", {
        "candidate_id": f"cand_{ts}_behavioral_continuity",
                "generated_at": _iso_utc(_utc_now()),
        "source": "vesper_watchdog",
        "type": "behavioral_continuity",
        "summary": (
            "Reinforce identity continuity and direct task completion using observed "
            "behavioral category mix."
        ),
        "rationale": (
            f"Dominant category is {dominant_category}. Apply continuity guards so "
            "session context and open tasks remain explicit each turn."
        ),
        "proposed_actions": [
            "Verify continuity state before response generation.",
            "Preserve identity invariants and checksum evidence in decisions.",
            "Prefer concise verified outcomes for task completion.",
        ],
        "evidence": {
            "sample_size": n,
            "category_distribution": cat_counts,
            "source_distribution": src_counts,
            "grade": grade,
            "tool_rate": round(tool_rate, 3),
        },
        "proposed_change": {
            "target": "runtime_rules",
            "description": "Strengthen continuity + identity checks based on behavioral mix.",
            "patch": {
                "dominant_category": dominant_category,
                "min_continuity_checks": 1,
                "min_identity_evidence": 1,
            },
        },
        "confidence": round(max(0.7, min(0.95, grade * 0.85 + tool_rate * 0.15)), 3),
        "requires_eval": True,
        "status": "pending",
    })

    # --- Candidate 5: tool utilization policy (repair or reinforce) ---
    if tool_rate < 0.6:
        write_candidate("tool_utilization_repair", {
            "candidate_id": f"cand_{ts}_tool_utilization_repair",
                "generated_at": _iso_utc(_utc_now()),
            "source": "vesper_watchdog",
            "type": "tool_utilization_repair",
            "summary": "Repair low tool usage rate to improve verified task completion.",
            "rationale": (
                f"Observed tool usage is {tool_rate:.2f}, below resilient threshold 0.60."
            ),
            "proposed_actions": [
                "Route unresolved blockers through tool-assisted verification first.",
                "Require evidence bundle from tool output for high-risk actions.",
                "Track tool invocation ratio as a continuity KPI.",
            ],
            "evidence": {"tool_rate": round(tool_rate, 3), "sample_size": n},
            "proposed_change": {
                "target": "runtime_rules",
                "description": "Raise tool usage to minimum reliability threshold.",
                "patch": {"tool_rate_floor": 0.6, "require_tool_evidence": True},
            },
            "confidence": round(max(0.7, min(0.9, 0.7 + (0.6 - tool_rate) * 0.2)), 3),
            "requires_eval": True,
            "status": "pending",
        })
    else:
        write_candidate("tool_utilization_strength", {
            "candidate_id": f"cand_{ts}_tool_utilization_strength",
                "generated_at": _iso_utc(_utc_now()),
            "source": "vesper_watchdog",
            "type": "tool_utilization_strength",
            "summary": "Preserve strong tool usage discipline for stable verified output.",
            "rationale": f"Observed tool usage {tool_rate:.2f} is above reliability floor.",
            "proposed_actions": [
                "Maintain tool-first verification for blocker resolution.",
                "Keep audit evidence attached to each promotion decision.",
                "Avoid cloud fallback unless local tiers fail explicitly.",
            ],
            "evidence": {"tool_rate": round(tool_rate, 3), "sample_size": n},
            "proposed_change": {
                "target": "runtime_rules",
                "description": "Keep high tool usage behavior stable under load.",
                "patch": {"tool_rate_floor": 0.75, "preserve_local_first": True},
            },
            "confidence": round(max(0.74, min(0.95, grade)), 3),
            "requires_eval": True,
            "status": "pending",
        })

    print(f"[watchdog] candidates: {written} written "
          f"(grade={grade:.2f}, n={n}, local={local_rate:.0%}, claude={claude_rate:.0%})")
    return written




def extract_extra_pattern_candidates():
    """Emit PITFALL-type candidates from watchdog_extra_patterns.json (from PRE-PHASE CC sessions)."""
    if not EXTRA_PATTERNS_FILE.exists():
        return 0
    try:
        data = json.loads(EXTRA_PATTERNS_FILE.read_text())
    except Exception as e:
        print(f"[watchdog] extra_patterns load error: {e}")
        return 0
    patterns = data.get("patterns", [])
    written = 0
    ts = _utc_now().strftime("%Y%m%dT%H%M%SZ")
    for p in patterns:
        pid = p.get("id", "UNKNOWN")
        label = p.get("label", "unlabeled")
        keywords = p.get("detection_keywords", [])
        severity = p.get("severity", "MEDIUM")
        cand_type = "PITFALL"
        confidence = 0.75 if severity == "HIGH" else 0.65
        payload = {
            "candidate_id": f"cand_{ts}_{pid}_pitfall",
            "generated_at": _iso_utc(_utc_now()),
            "source": "vesper_watchdog_extra_patterns",
            "type": cand_type,
            "label": label,
            "summary": f"PITFALL detected: {label}",
            "rationale": f"CC session pattern: {label}. Keywords: {keywords}. Severity: {severity}.",
            "proposed_actions": [
                f"Monitor for keywords: {keywords}",
                "Verify affected behavior before responding",
                "Cross-check with K2 state before diagnosing",
            ],
            "evidence": {
                "pattern_id": pid,
                "detection_keywords": keywords,
                "severity": severity,
                "source_file": str(EXTRA_PATTERNS_FILE),
            },
            "proposed_change": {
                "target": "behavioral_awareness",
                "description": f"Guard against pitfall: {label}",
                "patch": {"pitfall_guard": pid, "keywords": keywords},
            },
            "confidence": confidence,
            "requires_eval": True,
            "status": "pending",
        }

        def _write(ct=cand_type, pl=payload):
            # F-1+F-2: stable filename (no timestamp) â€” idempotent across watchdog runs
            fname = CANDIDATES_DIR / f"extra_{pl['evidence']['pattern_id']}.json"
            if fname.exists():
                return False
            CANDIDATES_DIR.mkdir(parents=True, exist_ok=True)
            pl['candidate_id'] = f"extra_{pl['evidence']['pattern_id']}"
            fname.write_text(json.dumps(pl, indent=2))
            return True

        if _already_promoted_pattern(pid):
            print(f'[watchdog] extra_patterns: {pid} already promoted or pending — skipping')
            continue
        if _ltm_is_hot(pid):
            print(f'[watchdog] extra_patterns: {pid} in LTM hot tier — skipping')
            continue
        if _write():
            _ltm_mark_seen(pid)
            written += 1

    print(f"[watchdog] extra_patterns: {written}/{len(patterns)} new candidates emitted")
    return written

def extract_ambient_candidates():  # K-3_AMBIENT
    """Emit ambient_observation candidates from ambient_observer entries in evolution log.

    Separate scan path from extract_candidates() because ambient entries have
    source + insight but NOT response_len (P295 filter would exclude them).
    """
    if not EVOLUTION_LOG.exists():
        return 0

    for d in (CANDIDATES_DIR,):
        d.mkdir(parents=True, exist_ok=True)

    lines = [l for l in EVOLUTION_LOG.read_text(encoding="utf-8").splitlines() if l.strip()]
    ambient_entries = []
    for l in lines:
        try:
            e = json.loads(l)
            if e.get("source") == "ambient_observer" and e.get("insight"):
                ambient_entries.append(e)
        except Exception:
            pass

    if not ambient_entries:
        return 0

    ts = _utc_now().strftime("%Y%m%dT%H%M%SZ")
    written = 0
    for entry in ambient_entries[-5:]:  # only most recent 5 to avoid flooding
        cycle_id = entry.get("cycle_id", "unknown")
        insight = entry.get("insight", "")[:200]
        signal_count = entry.get("signal_count", 0)
        entry_ts = entry.get("ts", "")

        cand_type = "ambient_observation"
        candidate_id = f"ambient_{entry_ts.replace(':', '').replace('-', '')[:15]}_{cycle_id}"
        fname = CANDIDATES_DIR / f"cand_ambient_{candidate_id}.json"
        if fname.exists():
            continue  # already emitted

        payload = {
            "candidate_id": candidate_id,
            "generated_at": _iso_utc(_utc_now()),
            "source": "vesper_watchdog",
            "type": cand_type,
            "excerpt": insight,
            "evidence": {
                "source": "ambient_observer",
                "signal_count": signal_count,
                "cycle_id": cycle_id,
                "observed_at": entry_ts,
            },
            "proposed_change": {
                "target": "behavioral_awareness",
                "description": f"Ambient observation: {insight}",
                "patch": {"ambient_insight": insight},
            },
            "confidence": 0.82,
            "requires_eval": True,
            "status": "pending",
        }
        fname.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        written += 1

    if written:
        print(f"[watchdog] ambient_candidates: {written} new ambient_observation candidates emitted")
    return written


if __name__ == "__main__":
    print(f"[watchdog] {_iso_utc(_utc_now())} — running")
    print(
        f"[watchdog] candidate_dedupe_window_secs={CANDIDATE_DEDUPE_WINDOW_SECS}"
    )
    stats = load_evolution_stats()
    state = load_state()
    last_colby = load_recent_conversations()
    scrub_artifacts()
    write_brief(state, stats, last_colby)
    update_spine(state, stats)
    consolidate_memories()
    extract_candidates()
    extract_extra_pattern_candidates()
    extract_ambient_candidates()
    print(f"[watchdog] done. grade={stats['avg_grade']} "
          f"cycles_threshold={stats['cycles_at_threshold']} "
          f"option_c={'ELIGIBLE' if stats['option_c_gate'] else 'not yet'}")
