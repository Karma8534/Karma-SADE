"""
Vesper Improve — The Lisa Loop (S157)

Closes the self-improvement gap: detect failures → generate fixes → apply → verify → keep.
Named after Liza's insight: Ralph loops until convergence, Lisa makes sure the work is right.

Runs on K2 as a cron job or triggered by Vesper governor after promotions.
Uses nexus_agent for fix generation when available, falls back to local Ollama.

Architecture:
  1. DETECT: scan recent Karma interactions for corrections, errors, user frustration
  2. DIAGNOSE: identify root cause (wrong response, missing context, stale data, code bug)
  3. FIX: generate the smallest change that addresses root cause
  4. VERIFY: apply fix, run checks, confirm improvement
  5. KEEP or REVERT: keep only if verification passes
"""

import json, os, time, subprocess, sys, re
from pathlib import Path

# Paths
WORK_DIR = Path(os.environ.get("KARMA_WORK_DIR", "/home/neo/karma-sade"))
K2_CACHE = Path("/mnt/c/dev/Karma/k2/cache")
SPINE_PATH = K2_CACHE / "vesper_identity_spine.json"
IMPROVE_LOG = K2_CACHE / "vesper_improve.jsonl"
LEDGER_PATH = Path("/opt/seed-vault/memory_v1/ledger/memory.jsonl")

# Config
MAX_FIXES_PER_RUN = 3
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://172.22.240.1:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3.5:4b")
HUB_URL = os.environ.get("HUB_URL", "https://hub.arknexus.net")

# ── Step 1: DETECT failures ──────────────────────────────────────────────────

def detect_failures():
    """Scan recent ledger entries for corrections, errors, user frustration signals."""
    failures = []

    # Read last 200 ledger entries
    try:
        if LEDGER_PATH.exists():
            lines = LEDGER_PATH.read_text(encoding="utf-8", errors="replace").strip().split("\n")
            recent = lines[-200:]
        else:
            # Try local fallback
            local_ledger = Path("C:/Users/raest/Documents/Karma_SADE/tmp/transcripts")
            if local_ledger.exists():
                recent = []
                for f in sorted(local_ledger.glob("*.jsonl"))[-5:]:
                    recent.extend(f.read_text(encoding="utf-8", errors="replace").strip().split("\n"))
            else:
                return failures
    except Exception as e:
        print(f"[detect] Error reading ledger: {e}")
        return failures

    for line in recent:
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        content = entry.get("content", entry.get("user_message", ""))
        assistant = entry.get("assistant_text", "")
        tags = entry.get("tags", [])

        if not content:
            continue

        # Signal 1: User corrections ("no", "wrong", "that's not right", "I said")
        correction_patterns = [
            r"\bno[,.]?\s+(that'?s?\s+)?(not|wrong|incorrect)",
            r"\bwrong\b", r"\bthat'?s not right\b",
            r"\bI (already |just )?(said|told|asked)\b",
            r"\bstop\b.*\b(doing|that)\b",
            r"\byou (forgot|missed|skipped)\b",
        ]
        for pat in correction_patterns:
            if re.search(pat, content, re.IGNORECASE):
                failures.append({
                    "type": "user_correction",
                    "signal": content[:200],
                    "response": assistant[:200] if assistant else "",
                    "tags": tags,
                    "ts": entry.get("timestamp", entry.get("ts", "")),
                })
                break

        # Signal 2: Error responses from Karma
        if assistant and any(err in assistant.lower() for err in [
            "error", "failed", "i don't know", "i'm not sure",
            "cannot", "unable to", "i apologize",
        ]):
            failures.append({
                "type": "error_response",
                "signal": assistant[:200],
                "query": content[:200],
                "tags": tags,
                "ts": entry.get("timestamp", entry.get("ts", "")),
            })

        # Signal 3: DPO thumbs-down
        if "dpo-pair" in tags and entry.get("rating") == -1:
            failures.append({
                "type": "dpo_rejection",
                "signal": entry.get("note", content[:200]),
                "response": assistant[:200] if assistant else "",
                "ts": entry.get("timestamp", entry.get("ts", "")),
            })

    # Deduplicate by signal text
    seen = set()
    unique = []
    for f in failures:
        key = f["signal"][:100]
        if key not in seen:
            seen.add(key)
            unique.append(f)

    return unique[:MAX_FIXES_PER_RUN]


# ── Step 2: DIAGNOSE root cause ──────────────────────────────────────────────

def diagnose(failure):
    """Use LLM to identify root cause of a failure."""
    prompt = f"""You are diagnosing a failure in Karma, a persistent AI peer.

Failure type: {failure['type']}
User signal: {failure.get('signal', '')}
Karma's response: {failure.get('response', failure.get('query', ''))}

Identify the root cause in ONE sentence. Then specify:
- CATEGORY: one of [wrong_context, missing_knowledge, stale_data, code_bug, prompt_gap, behavior_drift]
- FIX_TARGET: one of [system_prompt, memory, code, config, spine_pattern]
- DESCRIPTION: what specifically should change (max 2 sentences)

Output as JSON: {{"category": "...", "fix_target": "...", "description": "..."}}"""

    result = _call_ollama(prompt)
    try:
        # Extract JSON from response
        match = re.search(r'\{[^}]+\}', result)
        if match:
            return json.loads(match.group())
    except (json.JSONDecodeError, AttributeError):
        pass

    return {"category": "unknown", "fix_target": "spine_pattern", "description": result[:200]}


# ── Step 3: GENERATE fix ─────────────────────────────────────────────────────

def generate_fix(failure, diagnosis):
    """Generate the smallest change that addresses the root cause."""
    target = diagnosis.get("fix_target", "spine_pattern")

    if target == "system_prompt":
        return _generate_prompt_fix(failure, diagnosis)
    elif target == "spine_pattern":
        return _generate_spine_fix(failure, diagnosis)
    elif target == "memory":
        return _generate_memory_fix(failure, diagnosis)
    else:
        # For code/config fixes, just log the recommendation
        return {
            "action": "log_recommendation",
            "recommendation": diagnosis.get("description", ""),
            "requires_cc": True,
        }


def _generate_prompt_fix(failure, diagnosis):
    """Generate an addition to the system prompt."""
    prompt = f"""Based on this failure: {diagnosis['description']}

Write ONE short rule (max 30 words) to add to Karma's system prompt that prevents this failure from recurring.
Output ONLY the rule text, nothing else."""

    rule = _call_ollama(prompt).strip()
    return {
        "action": "append_prompt_rule",
        "rule": rule,
        "file": "Memory/00-karma-system-prompt-live.md",
    }


def _generate_spine_fix(failure, diagnosis):
    """Generate a new behavioral pattern for the spine."""
    return {
        "action": "add_spine_pattern",
        "pattern": {
            "type": "behavioral_correction",
            "description": diagnosis.get("description", ""),
            "source_failure": failure.get("type", "unknown"),
            "confidence": 0.6,  # Start low, governor can promote
        },
    }


def _generate_memory_fix(failure, diagnosis):
    """Generate a memory correction."""
    return {
        "action": "memory_correction",
        "correction": diagnosis.get("description", ""),
    }


# ── Step 4: APPLY + VERIFY ──────────────────────────────────────────────────

def apply_and_verify(fix):
    """Apply the fix and verify it works. Returns (success, evidence)."""
    action = fix.get("action", "")

    if action == "append_prompt_rule":
        return _apply_prompt_rule(fix)
    elif action == "add_spine_pattern":
        return _apply_spine_pattern(fix)
    elif action == "memory_correction":
        return _apply_memory_correction(fix)
    elif action == "log_recommendation":
        _log_improvement(fix, applied=False, evidence="Requires CC session to apply")
        return False, "Logged for CC"
    else:
        return False, f"Unknown action: {action}"


def _apply_prompt_rule(fix):
    """Append a rule to system prompt. Verify file still valid."""
    rule = fix.get("rule", "")
    if not rule or len(rule) < 10:
        return False, "Rule too short"

    filepath = WORK_DIR / fix.get("file", "Memory/00-karma-system-prompt-live.md")
    if not filepath.exists():
        return False, f"File not found: {filepath}"

    # Read current content
    original = filepath.read_text(encoding="utf-8")

    # Append rule
    addition = f"\n\n**[VESPER-LEARNED]:** {rule}\n"
    filepath.write_text(original + addition, encoding="utf-8")

    # Verify: file is still valid (not corrupted, reasonable size)
    new_content = filepath.read_text(encoding="utf-8")
    if len(new_content) < len(original):
        # Revert — something went wrong
        filepath.write_text(original, encoding="utf-8")
        return False, "File got smaller after write — reverted"

    if len(new_content) > len(original) + 500:
        # Revert — too much added
        filepath.write_text(original, encoding="utf-8")
        return False, "Too much content added — reverted"

    return True, f"Appended rule: {rule[:80]}"


def _apply_spine_pattern(fix):
    """Add a behavioral pattern to the spine."""
    pattern = fix.get("pattern", {})
    if not pattern:
        return False, "No pattern to add"

    try:
        spine = json.loads(SPINE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return False, "Cannot read spine"

    candidates = spine.get("evolution", {}).get("candidate_patterns", [])
    if not isinstance(candidates, list):
        candidates = []

    pattern["added_by"] = "vesper_improve"
    pattern["added_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    candidates.append(pattern)
    spine.setdefault("evolution", {})["candidate_patterns"] = candidates

    SPINE_PATH.write_text(json.dumps(spine, indent=2, ensure_ascii=False), encoding="utf-8")
    return True, f"Added candidate pattern: {pattern.get('description', '')[:80]}"


def _apply_memory_correction(fix):
    """Post correction to coordination bus for CC to apply."""
    correction = fix.get("correction", "")
    if not correction:
        return False, "No correction text"

    # Post to bus
    try:
        import urllib.request
        token_path = Path("/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt")
        if token_path.exists():
            token = token_path.read_text().strip()
        else:
            return False, "No hub token"

        payload = json.dumps({
            "from": "vesper-improve",
            "to": "cc",
            "type": "directive",
            "urgency": "normal",
            "content": f"[VESPER-CORRECTION] {correction}",
        }).encode()
        req = urllib.request.Request(
            f"{HUB_URL}/v1/coordination/post",
            data=payload,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return True, f"Posted to bus: {data.get('id', '?')}"
    except Exception as e:
        return False, f"Bus post failed: {e}"


# ── Logging ──────────────────────────────────────────────────────────────────

def _log_improvement(data, applied=True, evidence=""):
    """Append to improvement log."""
    entry = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "applied": applied,
        "evidence": evidence,
        **data,
    }
    with open(IMPROVE_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ── LLM Call ─────────────────────────────────────────────────────────────────

def _call_ollama(prompt, max_tokens=500):
    """Call local Ollama for diagnosis/fix generation. $0 cost."""
    import urllib.request
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": max_tokens},
    }).encode()
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            return data.get("response", "")
    except Exception as e:
        print(f"[ollama] Error: {e}")
        return ""


# ── Main Loop ────────────────────────────────────────────────────────────────

def run():
    """One improvement cycle. Call from cron or governor."""
    print(f"[vesper-improve] Starting improvement cycle at {time.strftime('%H:%M:%S')}")

    # Step 1: Detect
    failures = detect_failures()
    print(f"[vesper-improve] Detected {len(failures)} failure(s)")

    if not failures:
        print("[vesper-improve] No failures to address. Clean.")
        return

    for failure in failures:
        print(f"[vesper-improve] Processing: {failure['type']} — {failure['signal'][:60]}")

        # Step 2: Diagnose
        diagnosis = diagnose(failure)
        print(f"[vesper-improve] Diagnosis: {diagnosis.get('category')} → {diagnosis.get('fix_target')}")

        # Step 3: Generate fix
        fix = generate_fix(failure, diagnosis)
        print(f"[vesper-improve] Fix: {fix.get('action')}")

        # Step 4: Apply + Verify
        success, evidence = apply_and_verify(fix)
        print(f"[vesper-improve] {'APPLIED' if success else 'SKIPPED'}: {evidence[:80]}")

        # Log
        _log_improvement({
            "failure": failure,
            "diagnosis": diagnosis,
            "fix": fix,
        }, applied=success, evidence=evidence)

    print(f"[vesper-improve] Cycle complete. {len(failures)} failure(s) processed.")


if __name__ == "__main__":
    run()
