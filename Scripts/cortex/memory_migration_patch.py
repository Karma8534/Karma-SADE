#!/usr/bin/env python3
"""
Sprint 6 Task 7: Memory Migration/Fusion — Patch for vesper_watchdog.py
Adds extract_migration_candidates() function and wires it into __main__.

Apply: scp to K2, then append to vesper_watchdog.py before the `if __name__` block.
"""

MIGRATION_FUNCTION = '''

# ── Sprint 6 Task 7: Memory Migration/Fusion (S155) ─────────────────────────

def extract_migration_candidates():
    """Emit memory migration candidates based on pattern repetition in evolution log.

    Migration rules (from nexus.md Phase 7B):
    - raw event seen 3+ times → memory_distillation candidate
    - repeated fact in 5+ episodes → memory_promotion candidate
    - repeated workflow in 10+ episodes → memory_policy candidate
    - contradictory observations → memory_conflict candidate
    """
    if not EVOLUTION_LOG.exists():
        return 0

    for d in (CANDIDATES_DIR,):
        d.mkdir(parents=True, exist_ok=True)

    lines = [l for l in EVOLUTION_LOG.read_text(encoding="utf-8").splitlines() if l.strip()]

    # Count topic/pattern occurrences across recent entries
    topic_counts = {}  # topic -> [entries]
    for l in lines[-200:]:  # scan last 200 entries
        try:
            e = json.loads(l)
            # Extract topic from category or insight or source
            topic = e.get("category", e.get("insight", e.get("source", "")))
            if not topic or len(str(topic)) < 3:
                continue
            topic_key = str(topic).lower().strip()[:80]
            if topic_key not in topic_counts:
                topic_counts[topic_key] = []
            topic_counts[topic_key].append(e)
        except Exception:
            pass

    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    written = 0

    for topic, entries in topic_counts.items():
        count = len(entries)
        # Skip if candidate already exists for this topic recently
        if _recent_candidate_exists(f"migration_{topic[:20]}", window_secs=86400):
            continue

        cand_type = None
        confidence = 0.7

        if count >= 10:
            cand_type = "memory_policy"
            confidence = 0.92
            description = f"Pattern '{topic}' seen {count} times — promote to policy/invariant"
        elif count >= 5:
            cand_type = "memory_promotion"
            confidence = 0.85
            description = f"Pattern '{topic}' seen {count} times — promote to stable preference"
        elif count >= 3:
            cand_type = "memory_distillation"
            confidence = 0.78
            description = f"Pattern '{topic}' seen {count} times — distill to extracted fact"
        else:
            continue

        candidate_id = f"migration_{ts}_{topic[:20].replace(' ', '_')}"
        fname = CANDIDATES_DIR / f"cand_{ts}_{cand_type}.json"
        if fname.exists():
            continue

        payload = {
            "candidate_id": candidate_id,
            "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
            "source": "vesper_watchdog",
            "type": cand_type,
            "excerpt": description,
            "evidence": {
                "topic": topic,
                "occurrence_count": count,
                "sample_entries": [str(e.get("ts", ""))[:20] for e in entries[:3]],
            },
            "proposed_change": {
                "target": "memory_tier",
                "description": description,
                "memcube": {
                    "version": 1,
                    "tier": "stable" if count >= 5 else "distilled",
                    "promotion_state": "candidate",
                    "decay_policy": "persistent" if count >= 10 else "default",
                },
            },
            "confidence": confidence,
            "requires_eval": True,
            "status": "pending",
        }
        fname.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        written += 1

    # Conflict detection: look for contradictory entries (same topic, different values)
    # Simple heuristic: if a topic has both positive and negative sentiment markers
    for topic, entries in topic_counts.items():
        if len(entries) < 2:
            continue
        insights = [str(e.get("insight", "")) for e in entries if e.get("insight")]
        if not insights:
            continue
        # Check for contradiction markers
        has_positive = any(w in " ".join(insights).lower() for w in ["fixed", "resolved", "working", "passed", "success"])
        has_negative = any(w in " ".join(insights).lower() for w in ["broken", "failed", "error", "crash", "timeout", "drift"])
        if has_positive and has_negative:
            cand_type = "memory_conflict"
            candidate_id = f"conflict_{ts}_{topic[:20].replace(' ', '_')}"
            fname = CANDIDATES_DIR / f"cand_{ts}_{cand_type}.json"
            if fname.exists() or _recent_candidate_exists("memory_conflict", window_secs=86400):
                continue
            payload = {
                "candidate_id": candidate_id,
                "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
                "source": "vesper_watchdog",
                "type": cand_type,
                "excerpt": f"Contradictory signals for '{topic}' — both success and failure markers",
                "evidence": {
                    "topic": topic,
                    "positive_signals": [i[:50] for i in insights if any(w in i.lower() for w in ["fixed", "resolved", "working"])],
                    "negative_signals": [i[:50] for i in insights if any(w in i.lower() for w in ["broken", "failed", "error"])],
                },
                "proposed_change": {
                    "target": "conflict_resolution",
                    "description": f"Resolve contradiction for '{topic}'",
                    "memcube": {"version": 1, "tier": "raw", "promotion_state": "conflict", "decay_policy": "review"},
                },
                "confidence": 0.65,
                "requires_eval": True,
                "status": "pending",
            }
            fname.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            written += 1

    if written:
        print(f"[watchdog] migration: {written} memory migration candidates emitted")
    return written
'''

MAIN_PATCH = '''    extract_migration_candidates()'''

if __name__ == "__main__":
    print("This is a patch definition file. Apply to vesper_watchdog.py on K2.")
    print(f"Function length: {len(MIGRATION_FUNCTION)} chars")
    print(f"Main patch: {MAIN_PATCH.strip()}")
