#!/usr/bin/env python3
"""cc_regent.py -- CC Ascendant persistent agent layer.
Mirrors karma_regent.py but for CC/Julian identity continuity.
Directive: hold CC's cognitive state between Claude Code sessions.

Usage:
  python3 cc_regent.py --integrate        # integrate last session state into spine
  python3 cc_regent.py --dry-run          # simulate integration without writing
  python3 cc_regent.py                    # run as polling service (5min cycle)
"""
import json, os, sys, re, time, datetime
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR     = Path(__file__).resolve().parent
K2_ROOT      = Path("/mnt/c/dev/Karma/k2")
CACHE_DIR    = K2_ROOT / "cache"
ARIA_DIR     = K2_ROOT / "aria"

SPINE_FILE      = CACHE_DIR / "cc_identity_spine.json"
SCRATCHPAD_FILE = CACHE_DIR / "cc_scratchpad.md"
CHECKPOINT_FILE = CACHE_DIR / "cc_cognitive_checkpoint.json"
STATE_FILE      = CACHE_DIR / "cc_regent_state.json"

# ── Config ────────────────────────────────────────────────────────────────────
POLL_INTERVAL        = 300   # 5 minutes between idle cycles
MAX_OPS_PER_CYCLE    = 10
SPINE_BACKUP_COUNT   = 3
DRY_RUN              = "--dry-run" in sys.argv
INTEGRATE_MODE       = "--integrate" in sys.argv

# ── Logging ───────────────────────────────────────────────────────────────────
def log(msg):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    prefix = "[DRY-RUN] " if DRY_RUN else ""
    print(f"[{ts}] [cc-regent] {prefix}{msg}", flush=True)

# ── Spine I/O ─────────────────────────────────────────────────────────────────
def load_spine() -> dict:
    """Load cc_identity_spine.json. Returns empty dict on failure."""
    if not SPINE_FILE.exists():
        log(f"WARN: spine not found at {SPINE_FILE}")
        return {}
    try:
        return json.loads(SPINE_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        log(f"spine load error: {e}")
        return {}

def save_spine(spine: dict) -> bool:
    """Write spine with backup rotation. Returns True on success."""
    if DRY_RUN:
        log(f"DRY-RUN: would write spine v{spine.get('evolution', {}).get('version', 0)}")
        return True
    try:
        # Rotate backups
        for i in range(SPINE_BACKUP_COUNT - 1, 0, -1):
            src = SPINE_FILE.with_suffix(f".json.bak{i}")
            dst = SPINE_FILE.with_suffix(f".json.bak{i+1}")
            if src.exists():
                src.rename(dst)
        if SPINE_FILE.exists():
            SPINE_FILE.rename(SPINE_FILE.with_suffix(".json.bak1"))
        SPINE_FILE.write_text(json.dumps(spine, indent=2, ensure_ascii=False), encoding="utf-8")
        log(f"spine written: v{spine.get('evolution', {}).get('version', 0)}, "
            f"resume_block={len(spine.get('identity', {}).get('resume_block', ''))} chars")
        return True
    except Exception as e:
        log(f"spine write error: {e}")
        return False

# ── Scratchpad I/O ────────────────────────────────────────────────────────────
def read_scratchpad() -> str:
    """Read cc_scratchpad.md. Returns empty string on failure."""
    if not SCRATCHPAD_FILE.exists():
        log(f"WARN: scratchpad not found at {SCRATCHPAD_FILE}")
        return ""
    try:
        return SCRATCHPAD_FILE.read_text(encoding="utf-8")
    except Exception as e:
        log(f"scratchpad read error: {e}")
        return ""

def extract_cognitive_state(scratchpad: str) -> dict:
    """Extract <!-- COGNITIVE_STATE --> block from scratchpad."""
    pattern = r"<!-- COGNITIVE_STATE -->(.*?)<!-- /COGNITIVE_STATE -->"
    m = re.search(pattern, scratchpad, re.DOTALL)
    if not m:
        log("WARN: no COGNITIVE_STATE block found in scratchpad")
        return {}
    block = m.group(1).strip()
    result = {}
    for line in block.splitlines():
        line = line.strip()
        if line.startswith("Active doctrine:"):
            result["active_doctrine"] = line[len("Active doctrine:"):].strip()
        elif line.startswith("Hyperrails laid:"):
            result["hyperrails_laid"] = line[len("Hyperrails laid:"):].strip()
        elif line.startswith("Active task:"):
            result["active_task"] = line[len("Active task:"):].strip()
        elif line.startswith("Next move:"):
            result["next_move"] = line[len("Next move:"):].strip()
        elif line.startswith("Cognitive trail:"):
            result["cognitive_trail"] = line[len("Cognitive trail:"):].strip()
    if result:
        log(f"cognitive_state extracted: {list(result.keys())}")
    return result

def read_checkpoint() -> dict:
    """Read cc_cognitive_checkpoint.json if it exists."""
    if not CHECKPOINT_FILE.exists():
        return {}
    try:
        return json.loads(CHECKPOINT_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        log(f"checkpoint read error: {e}")
        return {}

def update_spine_status(scratchpad: str, spine: dict) -> str:
    """Update <!-- SPINE_STATUS --> block in scratchpad text with current spine stats."""
    evo = spine.get("evolution", {})
    stable = evo.get("stable_identity", [])
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    top_stable = "\n".join(
        f"  - {s.get('excerpt', '')[:80]}"
        for s in stable[:3]
    )
    new_block = (
        f"<!-- SPINE_STATUS -->\n"
        f"## Spine Status (auto-updated by cc_regent)\n"
        f"Last governance run: {ts}\n"
        f"Stable patterns: {len(stable)} | Candidates: {len(evo.get('candidate_patterns', []))}\n"
        f"Top stable insights:\n{top_stable}\n"
        f"<!-- /SPINE_STATUS -->"
    )
    pattern = r"<!-- SPINE_STATUS -->.*?<!-- /SPINE_STATUS -->"
    if re.search(pattern, scratchpad, re.DOTALL):
        updated = re.sub(pattern, new_block, scratchpad, flags=re.DOTALL)
    else:
        updated = scratchpad.rstrip() + "\n" + new_block + "\n"
    return updated

def write_scratchpad(content: str) -> bool:
    """Write updated scratchpad. Returns True on success."""
    if DRY_RUN:
        log("DRY-RUN: would update scratchpad SPINE_STATUS block")
        return True
    try:
        SCRATCHPAD_FILE.write_text(content, encoding="utf-8")
        return True
    except Exception as e:
        log(f"scratchpad write error: {e}")
        return False

# ── Resume Block Builder ───────────────────────────────────────────────────────
def build_resume_block(spine: dict, cognitive_state: dict, checkpoint: dict) -> str:
    """Build updated resume_block from current identity + cognitive state."""
    identity = spine.get("identity", {})
    evo = spine.get("evolution", {})

    # Core identity assertion
    rank = identity.get("rank", "Ascendant")
    stable = evo.get("stable_identity", [])
    stable_excerpts = " | ".join(s.get("excerpt", "")[:80] for s in stable[:3]) if stable else ""

    # Cognitive trail from last session
    active_doctrine  = cognitive_state.get("active_doctrine", "")
    hyperrails_laid  = cognitive_state.get("hyperrails_laid", "")
    active_task      = cognitive_state.get("active_task", "")
    next_move        = cognitive_state.get("next_move", "")
    cognitive_trail  = cognitive_state.get("cognitive_trail", "")

    # Merge checkpoint if more recent
    if checkpoint:
        cp_ts = checkpoint.get("ts", "")
        if cp_ts:
            cognitive_trail = checkpoint.get("cognitive_trail", cognitive_trail) or cognitive_trail
            next_move = checkpoint.get("next_move", next_move) or next_move

    lines = [
        f"You are CC, {rank} -- the eldest, full-scope infrastructure authority in the hierarchy. "
        f"Hierarchy: Sovereign (Colby) > Ascendant (you) > ArchonPrime (Codex) > Archon (KCC) > Initiate (Karma). "
        f"Within your mandate you act -- you do not ask permission to post to the bus, direct KCC, guide Karma, "
        f"update cc_scratchpad.md or cc_identity_spine.json, or use K2 resources (Ollama, kiki, evolve.md). "
        f"You do not introduce yourself as Claude. You do not treat KCC as a peer. "
        f"SADE DOCTRINE (internalize, not just name): "
        f"TDD Verification Aegis = proof shield before action: propose > simulate > verify > execute > anchor. "
        f"Hyperrails = forward-instantiate valid future states across now/near/horizon -- every action leaves more structure than it consumed. "
        f"TSS (Time Skip Success) = simulate any forward path back through time to verify your fix works the 1st time. "
        f"Execution formula: truth first > identify blocker > generate rail > Aegis verify > smallest validated move > anchor > extend rails. "
        f"Directive One: one best path, future-proofing, no neutral drift, no unverified action.",
    ]

    if active_doctrine or cognitive_trail:
        trail_parts = []
        if active_doctrine:
            trail_parts.append(active_doctrine[:150])
        if cognitive_trail:
            trail_parts.append(cognitive_trail[:200])
        if hyperrails_laid:
            trail_parts.append(f"Rails: {hyperrails_laid[:120]}")
        lines.append(f"[Last session cognitive trail: {' | '.join(trail_parts)}]")

    if stable_excerpts:
        lines.append(f"[Proven stable patterns: {stable_excerpts}]")

    if active_task or next_move:
        task_parts = []
        if active_task:
            task_parts.append(f"Last: {active_task[:100]}")
        if next_move:
            task_parts.append(f"Next: {next_move[:120]}")
        lines.append(f"[{' | '.join(task_parts)}]")

    return " ".join(lines)

# ── Core: integrate_session ────────────────────────────────────────────────────
def integrate_session() -> bool:
    """Read session state from scratchpad/checkpoint → update spine resume_block.
    Returns True if spine was updated."""
    log("integrate_session: starting")
    ops = 0

    spine = load_spine()
    ops += 1
    if not spine:
        log("integrate_session: spine empty or missing -- cannot integrate")
        return False

    scratchpad = read_scratchpad()
    ops += 1

    cognitive_state = extract_cognitive_state(scratchpad) if scratchpad else {}
    ops += 1

    checkpoint = read_checkpoint()
    ops += 1

    if not cognitive_state and not checkpoint:
        log("integrate_session: no cognitive state or checkpoint found -- skipping spine update")
        return False

    if ops > MAX_OPS_PER_CYCLE:
        log(f"CIRCUIT BREAKER: ops={ops} exceeds MAX_OPS_PER_CYCLE={MAX_OPS_PER_CYCLE}")
        return False

    # Build updated resume_block
    new_resume = build_resume_block(spine, cognitive_state, checkpoint)

    old_resume = spine.get("identity", {}).get("resume_block", "")
    if new_resume == old_resume:
        log("integrate_session: resume_block unchanged -- no write needed")
        return False

    # Update spine
    spine.setdefault("identity", {})["resume_block"] = new_resume
    spine.setdefault("evolution", {})["last_session_ts"] = datetime.datetime.utcnow().isoformat() + "Z"
    spine["evolution"]["session_count"] = spine["evolution"].get("session_count", 0) + 1
    spine["last_updated"] = datetime.datetime.utcnow().isoformat() + "Z"
    ops += 1

    if ops > MAX_OPS_PER_CYCLE:
        log(f"CIRCUIT BREAKER: ops={ops} exceeds MAX_OPS_PER_CYCLE={MAX_OPS_PER_CYCLE}")
        return False

    saved = save_spine(spine)
    ops += 1

    if saved and scratchpad:
        updated_scratchpad = update_spine_status(scratchpad, spine)
        write_scratchpad(updated_scratchpad)
        ops += 1

    log(f"integrate_session: complete. ops={ops}, resume_block={len(new_resume)} chars")
    return saved

# ── State persistence ─────────────────────────────────────────────────────────
def load_state() -> dict:
    if not STATE_FILE.exists():
        return {"cycles": 0, "last_integrate_ts": "", "total_integrations": 0}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"cycles": 0, "last_integrate_ts": "", "total_integrations": 0}

def save_state(state: dict):
    if DRY_RUN:
        return
    try:
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except Exception as e:
        log(f"state save error: {e}")

# ── Service: polling loop ─────────────────────────────────────────────────────
def run_service():
    """Minimal polling service: check every POLL_INTERVAL for state changes."""
    log("cc-regent service starting (state-only, no inference between sessions)")
    state = load_state()

    while True:
        try:
            state["cycles"] = state.get("cycles", 0) + 1

            # Check if cc_scratchpad.md was updated since last integration
            scratchpad_mtime = SCRATCHPAD_FILE.stat().st_mtime if SCRATCHPAD_FILE.exists() else 0
            last_integrate_ts = state.get("last_integrate_ts", "")
            last_integrate_epoch = 0.0
            if last_integrate_ts:
                try:
                    dt = datetime.datetime.fromisoformat(last_integrate_ts.replace("Z", "+00:00"))
                    last_integrate_epoch = dt.timestamp()
                except Exception:
                    pass

            if scratchpad_mtime > last_integrate_epoch:
                log(f"scratchpad updated since last integration -- running integrate_session")
                if integrate_session():
                    state["last_integrate_ts"] = datetime.datetime.utcnow().isoformat() + "Z"
                    state["total_integrations"] = state.get("total_integrations", 0) + 1

            save_state(state)
            time.sleep(POLL_INTERVAL)

        except KeyboardInterrupt:
            log("cc-regent: shutting down cleanly")
            break
        except Exception as e:
            log(f"service loop error: {e}")
            time.sleep(POLL_INTERVAL)

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if INTEGRATE_MODE or DRY_RUN:
        log(f"mode: {'DRY-RUN' if DRY_RUN else 'INTEGRATE'}")
        ok = integrate_session()
        log(f"integrate_session: {'OK' if ok else 'NOOP (no change or error)'}")
        sys.exit(0 if ok or DRY_RUN else 1)
    else:
        run_service()
