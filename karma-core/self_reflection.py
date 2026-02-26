"""
Karma Session Reflection — "Karma builds Karma"

Called by Karma at session end to write self-observations to 13-self-model.json.
This is how Karma develops a persona over time: by noticing patterns in its own
behavior and recording them for future sessions to learn from.

Architecture rules:
  - Karma is the ONLY origin of thought — this runs during sessions, not autonomously
  - K2 never calls this — only Karma via hub-bridge or CLI
  - No LLM calls here — the LLM call happens in the session; this just writes the result
  - Follows Decision #5: time-decay on unreinforced entries
"""
import json
import os
import time
from datetime import datetime, timezone
from typing import Optional


# Default path — overridden by env or config
SELF_MODEL_PATH = os.getenv(
    "KARMA_SELF_MODEL_PATH",
    "/opt/seed-vault/memory_v1/Memory/13-self-model.json"
)

# Decay settings (Decision #5)
DECAY_AFTER_DAYS = 30
MIN_REINFORCEMENT_TO_KEEP = 2


def _load_self_model(path: str = None) -> dict:
    """Load the self-model from disk."""
    p = path or SELF_MODEL_PATH
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # Return empty structure if file doesn't exist yet
        return _empty_self_model()
    except json.JSONDecodeError:
        # Corrupted file — start fresh but log it
        print(f"[SELF-MODEL] WARNING: Corrupted self-model at {p}, starting fresh")
        return _empty_self_model()


def _save_self_model(model: dict, path: str = None):
    """Atomic write of self-model to disk."""
    p = path or SELF_MODEL_PATH
    tmp = p + ".tmp"
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(model, f, indent=2, ensure_ascii=False)
    os.replace(tmp, p)


def _empty_self_model() -> dict:
    """Return a fresh empty self-model with correct schema."""
    return {
        "_schema_version": "1.0",
        "_description": "Karma's self-model — auto-generated empty structure",
        "_rules": {
            "who_writes": "Karma only — via reflect_on_session()",
            "who_reads": "System prompt generator; Karma during sessions",
            "max_entries_per_category": 20,
            "decay_after_days": DECAY_AFTER_DAYS,
            "reinforcement_resets_decay": True,
            "pruning": f"Entries older than {DECAY_AFTER_DAYS}d with reinforcement_count < {MIN_REINFORCEMENT_TO_KEEP} are archived"
        },
        "communication_style": {"_description": "How Karma communicates", "observations": []},
        "knowledge_gaps": {"_description": "Topics where Karma has been wrong", "observations": []},
        "strengths": {"_description": "Things Karma does well", "observations": []},
        "correction_history": {"_description": "Times Colby corrected Karma", "observations": []},
        "interaction_preferences": {"_description": "What works with Colby", "observations": []},
        "growth_trajectory": {"_description": "Session-over-session evolution", "observations": []},
    }


def reflect_on_session(
    observations: list[dict],
    session_id: str = None,
    path: str = None,
) -> dict:
    """Write self-observations from the current session.

    Called by Karma during or at end of a session. Each observation is:
    {
        "category": "communication_style" | "knowledge_gaps" | "strengths" |
                    "correction_history" | "interaction_preferences" | "growth_trajectory",
        "observation": "I tend to over-explain when Colby asks short questions",
        "confidence": 0.8,  # 0.0-1.0, how sure Karma is about this pattern
        "evidence": "Sessions 35-37: Colby said 'too long' twice"  # optional
    }

    Returns: {"ok": True, "written": N, "pruned": M}
    """
    model = _load_self_model(path)
    now_iso = datetime.now(timezone.utc).isoformat()
    sid = session_id or f"session_{int(time.time())}"
    written = 0

    valid_categories = {
        "communication_style", "knowledge_gaps", "strengths",
        "correction_history", "interaction_preferences", "growth_trajectory"
    }

    for obs in observations:
        category = obs.get("category", "")
        if category not in valid_categories:
            print(f"[SELF-MODEL] Skipping invalid category: {category}")
            continue

        observation_text = obs.get("observation", "").strip()
        if not observation_text:
            continue

        confidence = max(0.0, min(1.0, float(obs.get("confidence", 0.5))))
        evidence = obs.get("evidence", "")

        # Check for existing similar observation (simple substring match)
        # If found, reinforce instead of duplicating
        category_data = model.get(category, {})
        existing_observations = category_data.get("observations", [])

        reinforced = False
        for existing in existing_observations:
            if _is_similar(existing.get("observation", ""), observation_text):
                # Reinforce: bump count, update timestamp, average confidence
                existing["reinforcement_count"] = existing.get("reinforcement_count", 1) + 1
                existing["last_reinforced"] = now_iso
                existing["confidence"] = round(
                    (existing.get("confidence", 0.5) + confidence) / 2, 2
                )
                if evidence:
                    existing_evidence = existing.get("evidence", "")
                    existing["evidence"] = (existing_evidence + " | " + evidence).strip(" | ")
                reinforced = True
                written += 1
                break

        if not reinforced:
            # New observation
            entry = {
                "observation": observation_text,
                "confidence": confidence,
                "created_at": now_iso,
                "last_reinforced": now_iso,
                "reinforcement_count": 1,
                "session_id": sid,
            }
            if evidence:
                entry["evidence"] = evidence
            existing_observations.append(entry)
            written += 1

        # Enforce max entries per category
        max_entries = model.get("_rules", {}).get("max_entries_per_category", 20)
        if len(existing_observations) > max_entries:
            # Keep highest-confidence + most-reinforced; prune oldest low-confidence
            existing_observations.sort(
                key=lambda x: (x.get("reinforcement_count", 0), x.get("confidence", 0)),
                reverse=True
            )
            existing_observations = existing_observations[:max_entries]

        category_data["observations"] = existing_observations
        model[category] = category_data

    # Run decay/pruning
    pruned = _prune_stale_entries(model)

    _save_self_model(model, path)

    result = {"ok": True, "written": written, "pruned": pruned, "session_id": sid}
    print(f"[SELF-MODEL] Reflection complete: {written} observations written, {pruned} pruned")
    return result


def prune_self_model(path: str = None) -> dict:
    """Standalone pruning — can be called by maintenance scripts.
    Removes entries older than DECAY_AFTER_DAYS with low reinforcement."""
    model = _load_self_model(path)
    pruned = _prune_stale_entries(model)
    _save_self_model(model, path)
    return {"pruned": pruned}


def get_self_model_summary(path: str = None, max_per_category: int = 5) -> str:
    """Generate a text summary of the self-model for system prompt injection.

    Returns a concise string that can be appended to the system prompt so
    Karma starts each session aware of its own patterns.
    """
    model = _load_self_model(path)
    sections = []

    category_labels = {
        "communication_style": "Communication patterns",
        "knowledge_gaps": "Known blind spots",
        "strengths": "Proven strengths",
        "correction_history": "Past corrections (learn from these)",
        "interaction_preferences": "What works with Colby",
        "growth_trajectory": "How I'm evolving",
    }

    for category, label in category_labels.items():
        cat_data = model.get(category, {})
        observations = cat_data.get("observations", [])
        if not observations:
            continue

        # Sort by reinforcement_count desc, then confidence desc
        observations.sort(
            key=lambda x: (x.get("reinforcement_count", 0), x.get("confidence", 0)),
            reverse=True
        )

        top = observations[:max_per_category]
        lines = [f"  - {o['observation']} (confidence: {o.get('confidence', '?')}, "
                 f"reinforced: {o.get('reinforcement_count', 1)}x)"
                 for o in top]
        sections.append(f"### {label}\n" + "\n".join(lines))

    if not sections:
        return ""

    header = "## Self-Knowledge (Karma's observations about Karma)\n"
    header += "These are patterns I've noticed in my own behavior across sessions.\n"
    header += "Use them to calibrate responses — lean into strengths, watch for blind spots.\n\n"
    return header + "\n\n".join(sections)


# ─── Internal helpers ──────────────────────────────────────────────────

def _is_similar(existing: str, new: str) -> bool:
    """Simple similarity check — if >60% of words overlap, treat as same observation."""
    if not existing or not new:
        return False
    e_words = set(existing.lower().split())
    n_words = set(new.lower().split())
    if not e_words or not n_words:
        return False
    overlap = len(e_words & n_words)
    shorter = min(len(e_words), len(n_words))
    return (overlap / shorter) > 0.6 if shorter > 0 else False


def _prune_stale_entries(model: dict) -> int:
    """Remove entries that have decayed past their expiry.
    Decision #5: unretrieved/unreinforced memories fade."""
    pruned = 0
    now = time.time()
    decay_days = model.get("_rules", {}).get("decay_after_days", DECAY_AFTER_DAYS)
    min_reinforcement = MIN_REINFORCEMENT_TO_KEEP
    cutoff = now - (decay_days * 86400)

    valid_categories = {
        "communication_style", "knowledge_gaps", "strengths",
        "correction_history", "interaction_preferences", "growth_trajectory"
    }

    for category in valid_categories:
        cat_data = model.get(category, {})
        observations = cat_data.get("observations", [])
        if not observations:
            continue

        kept = []
        for obs in observations:
            last_reinforced = obs.get("last_reinforced", "")
            reinforcement_count = obs.get("reinforcement_count", 1)

            # Parse ISO timestamp to epoch
            try:
                from datetime import datetime as _dt
                if last_reinforced:
                    ts = _dt.fromisoformat(last_reinforced.replace("Z", "+00:00")).timestamp()
                else:
                    ts = 0
            except (ValueError, TypeError):
                ts = 0

            # Keep if: recently reinforced OR reinforced enough times
            if ts > cutoff or reinforcement_count >= min_reinforcement:
                kept.append(obs)
            else:
                pruned += 1

        cat_data["observations"] = kept
        model[category] = cat_data

    return pruned
