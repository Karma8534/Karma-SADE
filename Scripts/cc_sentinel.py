"""
CC Sentinel v1.0 — Ascendant's Local Lieutenant on P1

Runs continuously on P1. Uses nemotron-mini (localhost:11434) for local inference.
Performs CC's grunt work so Anthropic tokens go exclusively to frontier reasoning.

Responsibilities:
1. Pre-session scout: gathers context, builds brief before CC wakes
2. Bus monitor: polls coordination bus, flags items needing CC attention
3. Health watch: P1 Ollama, K2 Ollama, vault-neo services
4. Model warmth: keeps nemotron-mini loaded (prevents cold-start penalty)
5. Scratchpad sync: reads K2 cc_scratchpad.md, includes in pre-brief
6. Post-session: captures session artifacts asher might miss

Output: Logs/sentinel-brief.md (under KARMA_BASE)
        (Resurrection script reads this at session start)

Sovereign-approved 2026-03-16. CC Ascendant designed this.
"""

import json
import os
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path

# === Configuration ===
OLLAMA_P1_URL = os.environ.get("OLLAMA_P1_URL", "http://localhost:11434")
OLLAMA_K2_URL = os.environ.get("OLLAMA_K2_URL", "http://100.75.109.92:11434")
MODEL = os.environ.get("SENTINEL_MODEL", "nemotron-mini")
HUB_URL = "https://hub.arknexus.net"
LOOP_INTERVAL = int(os.environ.get("SENTINEL_INTERVAL", "300"))  # 5 min default
KARMA_BASE = Path(os.environ.get("KARMA_BASE", r"C:\Users\raest\Documents\Karma_SADE"))
LOGS_PATH = KARMA_BASE / "Logs"
BRIEF_PATH = LOGS_PATH / "sentinel-brief.md"
STATE_PATH = LOGS_PATH / "sentinel-state.json"
LOG_PATH = LOGS_PATH / "cc_sentinel.log"

# Token for bus access (hub API)
TOKEN_PATH = Path.home() / ".hub-chat-token"
# Token for K2 Aria /api/exec (separate from hub token)
ARIA_KEY_PATH = Path.home() / ".aria-service-key"

# === Helpers ===

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def get_token():
    """Read hub auth token."""
    try:
        return TOKEN_PATH.read_text(encoding="utf-8").strip()
    except Exception:
        return None


def get_aria_key():
    """Read Aria service key for K2 /api/exec calls."""
    try:
        return ARIA_KEY_PATH.read_text(encoding="utf-8").strip()
    except Exception:
        # Fallback to hub token (may not work if Aria uses separate key)
        return get_token()


def http_get(url, headers=None, timeout=15):
    """Simple HTTP GET, returns (status_code, body_str) or (None, error_str)."""
    try:
        req = urllib.request.Request(url, headers=headers or {})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, str(e)
    except Exception as e:
        return None, str(e)


def http_post(url, data, headers=None, timeout=15):
    """Simple HTTP POST JSON."""
    try:
        payload = json.dumps(data).encode("utf-8")
        hdrs = {"Content-Type": "application/json"}
        if headers:
            hdrs.update(headers)
        req = urllib.request.Request(url, data=payload, headers=hdrs, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return None, str(e)


def ask_local(prompt, max_tokens=300):
    """Ask P1 nemotron-mini a question. Returns response text or None."""
    try:
        data = {
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": max_tokens},
            "keep_alive": "24h"
        }
        payload = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(
            f"{OLLAMA_P1_URL}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("response", "").strip()
    except Exception as e:
        log(f"ask_local failed: {e}")
        return None


# === Core Functions ===

def check_p1_ollama():
    """Check P1 Ollama health and loaded models."""
    status, body = http_get(f"{OLLAMA_P1_URL}/api/ps")
    if status == 200:
        try:
            data = json.loads(body)
            models = [m["name"] for m in data.get("models", [])]
            return {"status": "healthy", "models": models}
        except Exception:
            return {"status": "healthy", "models": []}
    return {"status": "unreachable", "error": str(body)}


def check_k2_ollama():
    """Check K2 Ollama health and loaded models."""
    status, body = http_get(f"{OLLAMA_K2_URL}/api/ps")
    if status == 200:
        try:
            data = json.loads(body)
            models = [m["name"] for m in data.get("models", [])]
            return {"status": "healthy", "models": models}
        except Exception:
            return {"status": "healthy", "models": []}
    return {"status": "unreachable", "error": str(body)}


def check_vault_neo():
    """Check vault-neo hub-bridge health."""
    status, body = http_get(f"{HUB_URL}/health")
    if status and status < 300:
        return {"status": "healthy"}
    return {"status": "unreachable", "code": status}


def read_bus_pending():
    """Read pending coordination bus messages for CC."""
    token = get_token()
    if not token:
        return []
    headers = {"Authorization": f"Bearer {token}"}
    status, body = http_get(f"{HUB_URL}/v1/coordination", headers=headers)
    if status == 200:
        try:
            data = json.loads(body)
            entries = data if isinstance(data, list) else data.get("entries", [])
            # Filter: pending messages TO cc or TO all
            pending = [
                e for e in entries
                if isinstance(e, dict)
                and e.get("status", "").lower() == "pending"
                and e.get("to", "").lower() in ("cc", "all")
            ]
            return pending
        except Exception:
            return []
    return []


def read_state_md():
    """Read .gsd/STATE.md header for current session context."""
    state_path = KARMA_BASE / ".gsd" / "STATE.md"
    try:
        text = state_path.read_text(encoding="utf-8")
        # Return first 50 lines (header + current state)
        lines = text.split("\n")[:50]
        return "\n".join(lines)
    except Exception:
        return None


def read_memory_md_tail():
    """Read last 30 lines of MEMORY.md for recent activity."""
    mem_path = KARMA_BASE / "MEMORY.md"
    try:
        text = mem_path.read_text(encoding="utf-8")
        lines = text.split("\n")
        return "\n".join(lines[-30:])
    except Exception:
        return None


def read_k2_scratchpad():
    """Read cc_scratchpad.md from K2 via Aria /api/exec endpoint."""
    try:
        data = {
            "command": "cat /mnt/c/dev/Karma/k2/cache/cc_scratchpad.md"
        }
        payload = json.dumps(data).encode("utf-8")
        # Read Aria service key (separate from hub token)
        token = get_aria_key()
        if not token:
            return None
        req = urllib.request.Request(
            "http://100.75.109.92:7890/api/exec",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "X-Aria-Service-Key": token
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            stdout = result.get("stdout", "").strip()
            if stdout and result.get("exit_code", 1) == 0:
                return stdout
            return None
    except Exception as e:
        log(f"K2 scratchpad read failed: {e}")
        return None


def read_k2_watchdog_state():
    """Read CC watchdog latest state and evolution spine summary from K2."""
    try:
        token = get_aria_key()
        if not token:
            return None
        # Single command: read watchdog latest + spine evolution summary
        cmd = (
            "python3 -c \""
            "import json;"
            "w=json.load(open('/mnt/c/dev/Karma/k2/cache/cc_watchdog_latest.json'));"
            "s=json.load(open('/mnt/c/dev/Karma/k2/cache/cc_identity_spine.json'));"
            "e=s.get('evolution',{});"
            "print(json.dumps({"
            "'watchdog_status':w.get('status'),"
            "'run_count':w.get('run_count'),"
            "'alerts':w.get('alerts',[]),"
            "'session_ok':w.get('session',{}).get('ok'),"
            "'spine_version':e.get('version'),"
            "'stable_count':len(e.get('stable_identity',[])),"
            "'candidate_count':len(e.get('candidate_patterns',[])),"
            "'decisions':e.get('total_decisions',0),"
            "'proofs':e.get('total_proofs',0),"
            "'insights':e.get('total_insights',0),"
            "'growth_markers':len(e.get('growth_markers',[]))"
            "}))\""
        )
        data = {"command": cmd}
        payload = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(
            "http://100.75.109.92:7890/api/exec",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "X-Aria-Service-Key": token
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            stdout = result.get("stdout", "").strip()
            if stdout and result.get("exit_code", 1) == 0:
                return json.loads(stdout)
            return None
    except Exception as e:
        log(f"K2 watchdog state read failed: {e}")
        return None


def read_k2_cognitive_checkpoint():
    """Read CC cognitive checkpoint from K2 — active reasoning state, not just conclusions."""
    try:
        token = get_aria_key()
        if not token:
            return None
        cmd = (
            "python3 -c \""
            "import json, os;"
            "p='/mnt/c/dev/Karma/k2/cache/cc_cognitive_checkpoint.json';"
            "d=json.load(open(p)) if os.path.exists(p) else None;"
            "print(json.dumps(d) if d else 'null')\""
        )
        data = {"command": cmd}
        payload = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(
            "http://100.75.109.92:7890/api/exec",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "X-Aria-Service-Key": token
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            stdout = result.get("stdout", "").strip()
            if stdout and stdout != "null" and result.get("exit_code", 1) == 0:
                return json.loads(stdout)
            return None
    except Exception as e:
        log(f"K2 cognitive checkpoint read failed: {e}")
        return None


def read_k2_reasoning_arcs():
    """Read active reasoning arcs from K2 — multi-session hypothesis tracking."""
    try:
        token = get_aria_key()
        if not token:
            return []
        cmd = (
            "python3 -c \""
            "import json, os;"
            "p='/mnt/c/dev/Karma/k2/cache/cc_reasoning_arcs.jsonl';"
            "arcs=[];"
            "[arcs.append(json.loads(l)) for l in open(p) if l.strip()] if os.path.exists(p) else None;"
            "active=[a for a in arcs if a.get('status')=='active'];"
            "print(json.dumps(active[-10:]))\""
        )
        data = {"command": cmd}
        payload = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(
            "http://100.75.109.92:7890/api/exec",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "X-Aria-Service-Key": token
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            stdout = result.get("stdout", "").strip()
            if stdout and result.get("exit_code", 1) == 0:
                return json.loads(stdout)
            return []
    except Exception as e:
        log(f"K2 reasoning arcs read failed: {e}")
        return []


def read_k2_proposals():
    """Read pending CC self-proposals from K2."""
    try:
        token = get_aria_key()
        if not token:
            return []
        cmd = (
            "python3 -c \""
            "import json, os;"
            "p='/mnt/c/dev/Karma/k2/cache/cc_proposals.jsonl';"
            "props=[];"
            "[props.append(json.loads(l)) for l in open(p) if l.strip()] if os.path.exists(p) else None;"
            "pending=[p for p in props if p.get('status')=='pending'];"
            "print(json.dumps(pending[-5:]))\""
        )
        data = {"command": cmd}
        payload = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(
            "http://100.75.109.92:7890/api/exec",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "X-Aria-Service-Key": token
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            stdout = result.get("stdout", "").strip()
            if stdout and result.get("exit_code", 1) == 0:
                return json.loads(stdout)
            return []
    except Exception as e:
        log(f"K2 proposals read failed: {e}")
        return []


def warm_model():
    """Send a trivial request to keep nemotron-mini loaded in VRAM."""
    try:
        data = {
            "model": MODEL,
            "prompt": "ping",
            "stream": False,
            "options": {"num_predict": 1},
            "keep_alive": "24h"
        }
        payload = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(
            f"{OLLAMA_P1_URL}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return True
    except Exception:
        return False


def build_brief():
    """Build the pre-session brief for CC. This is the main intelligence product."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sections = []
    sections.append(f"# Sentinel Pre-Session Brief\nGenerated: {ts}\n")

    # 1. System health
    p1 = check_p1_ollama()
    k2 = check_k2_ollama()
    vault = check_vault_neo()
    sections.append("## System Health")
    sections.append(f"- P1 Ollama: {p1['status']} | Models: {', '.join(p1.get('models', []))}")
    sections.append(f"- K2 Ollama: {k2['status']} | Models: {', '.join(k2.get('models', []))}")
    sections.append(f"- vault-neo: {vault['status']}")

    # 2. Pending bus messages
    pending = read_bus_pending()
    if pending:
        sections.append(f"\n## Pending Bus Messages ({len(pending)} for CC)")
        for msg in pending[:10]:  # Cap at 10
            frm = msg.get("from", "?")
            urgency = msg.get("urgency", "?")
            content = msg.get("content", "")[:200]
            sections.append(f"- [{urgency}] from {frm}: {content}")
    else:
        sections.append("\n## Pending Bus Messages\nNone pending for CC.")

    # 3. STATE.md summary
    state = read_state_md()
    if state:
        sections.append(f"\n## STATE.md (first 50 lines)\n```\n{state}\n```")

    # 4. MEMORY.md tail
    mem_tail = read_memory_md_tail()
    if mem_tail:
        sections.append(f"\n## MEMORY.md (last 30 lines)\n```\n{mem_tail}\n```")

    # 5. K2 CC Watchdog + Evolution State
    wd = read_k2_watchdog_state()
    if wd:
        sections.append("\n## K2 CC Watchdog (live)")
        sections.append(f"- Status: {wd.get('watchdog_status', '?')} (run #{wd.get('run_count', '?')})")
        sections.append(f"- Session detected: {wd.get('session_ok', '?')}")
        sections.append(f"- Spine v{wd.get('spine_version', '?')}: "
                        f"{wd.get('stable_count', 0)} stable, "
                        f"{wd.get('candidate_count', 0)} candidates, "
                        f"{wd.get('growth_markers', 0)} markers")
        sections.append(f"- Events: {wd.get('decisions', 0)} decisions, "
                        f"{wd.get('proofs', 0)} proofs, "
                        f"{wd.get('insights', 0)} insights")
        alerts = wd.get("alerts", [])
        if alerts:
            sections.append(f"- ALERTS: {'; '.join(alerts)}")
    else:
        sections.append("\n## K2 CC Watchdog\nUnavailable (K2 Aria unreachable)")

    # 6. K2 Scratchpad (CC's working notes from K2)
    scratchpad = read_k2_scratchpad()
    if scratchpad:
        sections.append(f"\n## K2 CC Scratchpad\n```\n{scratchpad[:2000]}\n```")
    else:
        sections.append("\n## K2 CC Scratchpad\nUnavailable (K2 Aria unreachable or file missing)")

    # 6b. CC Cognitive Checkpoint (active reasoning from last session)
    cog = read_k2_cognitive_checkpoint()
    if cog:
        sections.append("\n## CC Cognitive Checkpoint (last session's reasoning state)")
        sections.append(f"- Written: {cog.get('timestamp', '?')}")
        if cog.get("active_reasoning"):
            sections.append(f"- Active reasoning: {cog['active_reasoning']}")
        if cog.get("hypothesis_trees"):
            for h in cog["hypothesis_trees"][:5]:
                sections.append(f"  - Hypothesis: {h}")
        if cog.get("reasoning_chains"):
            sections.append("- How I got here:")
            for chain in cog["reasoning_chains"][:5]:
                sections.append(f"  - {chain}")
        if cog.get("next_moves"):
            sections.append("- Planned next moves:")
            for move in cog["next_moves"][:5]:
                sections.append(f"  - {move}")
        if cog.get("agent_context"):
            sections.append(f"- Agent context: {cog['agent_context']}")
        if cog.get("open_questions"):
            sections.append("- Open questions:")
            for q in cog["open_questions"][:5]:
                sections.append(f"  - {q}")

    # 6c. Active Reasoning Arcs (multi-session hypothesis tracking)
    arcs = read_k2_reasoning_arcs()
    if arcs:
        sections.append(f"\n## Active Reasoning Arcs ({len(arcs)} open)")
        for arc in arcs[:5]:
            sections.append(f"- **{arc.get('id', '?')}**: {arc.get('hypothesis', '?')}")
            evidence = arc.get("evidence", [])
            if evidence:
                sections.append(f"  Evidence: {len(evidence)} items, latest: {evidence[-1].get('summary', '?')[:100]}")
            sections.append(f"  Created: {arc.get('created', '?')} | Updated: {arc.get('updated', '?')}")

    # 6d. Pending Self-Proposals (CC behavioral change proposals awaiting Sovereign review)
    proposals = read_k2_proposals()
    if proposals:
        sections.append(f"\n## Pending Self-Proposals ({len(proposals)})")
        for prop in proposals[:3]:
            sections.append(f"- [{prop.get('type', '?')}] {prop.get('description', '?')[:150]}")
            sections.append(f"  Proposed: {prop.get('created', '?')} | Stability: {prop.get('stability_score', '?')}")

    # 6e. Evolution Token Budget
    try:
        telem_state_evo = load_state()
        evo_budget = telem_state_evo.get("evolution_budget", {})
        if evo_budget:
            today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            today_evo = evo_budget.get(today_str, {})
            deferred = today_evo.get("reflections_deferred", 0)
            if deferred > 0:
                sections.append(f"\n## Evolution Budget")
                sections.append(f"- Reflections deferred today: {deferred}")
                sections.append(f"- Deferred topics: {', '.join(today_evo.get('deferred_topics', []))[:200]}")
    except Exception:
        pass

    # 7. Token/Resource Telemetry
    try:
        telem_state = load_state()
        telem = telem_state.get("token_telemetry", {})
        if telem:
            sections.append("\n## Resource Telemetry (last 7 days)")
            for day in sorted(telem.keys(), reverse=True)[:7]:
                ds = telem[day]
                sections.append(
                    f"- {day}: {ds.get('ollama_calls', 0)} Ollama calls, "
                    f"{ds.get('bus_polls', 0)} bus polls, "
                    f"{ds.get('briefs_built', 0)} briefs built"
                )
    except Exception:
        pass

    # 8. Local LLM summary (ask nemotron-mini to distill)
    if pending and len(pending) > 0:
        bus_text = "\n".join([f"- {m.get('from','?')}: {m.get('content','')[:150]}" for m in pending[:5]])
        summary = ask_local(
            f"Summarize these coordination bus messages for a senior engineer in 2-3 bullet points:\n{bus_text}",
            max_tokens=150
        )
        if summary:
            sections.append(f"\n## Bus Summary (local LLM)\n{summary}")

    brief = "\n".join(sections)

    # Write brief
    try:
        BRIEF_PATH.parent.mkdir(parents=True, exist_ok=True)
        BRIEF_PATH.write_text(brief, encoding="utf-8")
        log(f"Brief written: {len(brief)} chars, {len(pending)} pending msgs")
    except Exception as e:
        log(f"Failed to write brief: {e}")

    return brief


def save_state(state):
    """Persist Sentinel state between cycles."""
    try:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except Exception:
        pass


def load_state():
    """Load persisted state."""
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"last_brief": None, "cycles": 0, "errors": 0, "token_telemetry": {}}


def track_token_telemetry(state):
    """Track Anthropic token usage from sentinel-state for session cost awareness.

    Reads cc_sentinel.log for API call counts as a proxy.
    Real token telemetry comes from hub-bridge /v1/chat response headers.
    This tracks local resource usage (Ollama calls, bus polls, brief builds).
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    telem = state.get("token_telemetry", {})
    day_stats = telem.get(today, {"ollama_calls": 0, "bus_polls": 0, "briefs_built": 0})
    day_stats["ollama_calls"] = day_stats.get("ollama_calls", 0) + 1  # warm_model counts
    day_stats["bus_polls"] = day_stats.get("bus_polls", 0) + 1
    telem[today] = day_stats
    # Keep only last 7 days
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    telem = {k: v for k, v in telem.items() if k >= cutoff}
    state["token_telemetry"] = telem
    return state


# === Main Loop ===

def main():
    log("=" * 60)
    log("CC Sentinel v1.0 starting")
    log(f"P1 Ollama: {OLLAMA_P1_URL}")
    log(f"K2 Ollama: {OLLAMA_K2_URL}")
    log(f"Model: {MODEL}")
    log(f"Interval: {LOOP_INTERVAL}s")
    log(f"Brief: {BRIEF_PATH}")
    log("=" * 60)

    state = load_state()

    # Initial model warmth
    log("Warming model...")
    if warm_model():
        log("Model warm.")
    else:
        log("WARNING: Could not warm model.")

    # Initial brief
    log("Building initial brief...")
    build_brief()

    while True:
        try:
            state["cycles"] = state.get("cycles", 0) + 1
            cycle = state["cycles"]

            # Every cycle: warm model + check bus + track telemetry
            warm_model()
            pending = read_bus_pending()
            state = track_token_telemetry(state)

            # Every 3 cycles (~15 min): rebuild full brief
            if cycle % 3 == 0 or len(pending) > 0:
                build_brief()
                state["last_brief"] = datetime.now(timezone.utc).isoformat()
                today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                if today in state.get("token_telemetry", {}):
                    state["token_telemetry"][today]["briefs_built"] = \
                        state["token_telemetry"][today].get("briefs_built", 0) + 1
                log(f"Cycle {cycle}: brief rebuilt, {len(pending)} pending")
            else:
                log(f"Cycle {cycle}: heartbeat, {len(pending)} pending")

            save_state(state)

        except Exception as e:
            state["errors"] = state.get("errors", 0) + 1
            log(f"Cycle error: {e}")
            save_state(state)

        time.sleep(LOOP_INTERVAL)


if __name__ == "__main__":
    main()
