"""
cc_email_daemon.py — Autonomous email integration for CC Ascendant.

Called from cc_archon_agent.ps1 on every 30-min cycle.

Modes:
  check     — Read inbox, watermark new messages, post to bus if new Colby emails
  status    — Operational status email every 4h (gated by timestamp file)
  personal  — Personal outreach when spine has new promotions OR idle >8h (Ollama-composed)

Tracking files (Logs/):
  cc_email_watermark.txt      — IMAP total count at last check
  cc_email_status_last.txt    — UTC timestamp of last status email
  cc_email_personal_last.txt  — UTC timestamp of last personal email
  cc_email_spine_version.txt  — Spine version at last personal email send
"""
import sys
import json
import imaplib
import datetime
import pathlib
import subprocess
import urllib.request
import urllib.error

# ── Paths ─────────────────────────────────────────────────────────────────────
REPO               = pathlib.Path(r"C:\Users\raest\Documents\Karma_SADE")
LOGS               = REPO / "Logs"
LOGS.mkdir(exist_ok=True)

SNAPSHOT_FILE      = REPO / "cc_context_snapshot.md"
CREDS_FILE         = REPO / ".gmail-cc-creds"
WATERMARK_FILE     = LOGS / "cc_email_watermark.txt"
STATUS_SENT_FILE   = LOGS / "cc_email_status_last.txt"
PERSONAL_SENT_FILE = LOGS / "cc_email_personal_last.txt"
SPINE_VER_FILE     = LOGS / "cc_email_spine_version.txt"

# ── Config ────────────────────────────────────────────────────────────────────
STATUS_INTERVAL_H  = 8       # hours between status emails (was 4, Sovereign said too frequent)
PERSONAL_IDLE_H    = 8       # hours before idle personal check-in fires
OLLAMA_URL         = "http://localhost:11434/v1/chat/completions"
OLLAMA_MODEL       = "llama3.1:8b"
IMAP_HOST          = "imap.gmail.com"
HUB_BUS_URL        = "https://hub.arknexus.net/v1/coordination/post"

# ── Gmail module ──────────────────────────────────────────────────────────────
sys.path.insert(0, str(REPO / "Scripts"))
from cc_gmail import send_to_colby, _load_creds


# ── Helpers ───────────────────────────────────────────────────────────────────

def _ts_file_hours(path: pathlib.Path) -> float:
    """Hours since UTC timestamp stored in file. Returns 9999.0 if missing/invalid."""
    try:
        ts = datetime.datetime.fromisoformat(path.read_text().strip())
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=datetime.timezone.utc)
        return (datetime.datetime.now(datetime.timezone.utc) - ts).total_seconds() / 3600
    except Exception:
        return 9999.0


def _write_now(path: pathlib.Path) -> None:
    path.write_text(datetime.datetime.now(datetime.timezone.utc).isoformat())


def _read_int(path: pathlib.Path, default: int = 0) -> int:
    try:
        return int(path.read_text().strip())
    except Exception:
        return default


def _call_ollama(prompt: str) -> str:
    """Call P1 Ollama (localhost:11434) and return generated text, or '' on failure."""
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 250,
        "stream": False,
    }).encode("utf-8")
    try:
        req = urllib.request.Request(
            OLLAMA_URL, data=payload,
            headers={"Content-Type": "application/json"}, method="POST"
        )
        with urllib.request.urlopen(req, timeout=45) as r:
            return json.loads(r.read())["choices"][0]["message"]["content"].strip()
    except Exception:
        return ""


def _bus_post(content: str) -> None:
    """Post to coordination bus (colby). Silently ignores failures."""
    try:
        result = subprocess.run(
            ["ssh", "vault-neo", "cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt"],
            capture_output=True, text=True, timeout=10
        )
        token = result.stdout.strip()
        if not token:
            return
        payload = json.dumps({
            "from": "cc", "to": "colby", "type": "inform",
            "urgency": "informational", "content": content
        }).encode()
        req = urllib.request.Request(
            HUB_BUS_URL, data=payload,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            method="POST"
        )
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass


def _read_spine_info() -> dict:
    """
    SSH vault-neo -> K2 heredoc to get spine version + last 3 promotions.
    Heredoc avoids all shell quoting issues (verified pattern from resurrect skill).
    Returns dict with 'version', 'recent' (list), and optionally 'error'.
    """
    cmd = (
        "ssh vault-neo \"cat << 'PYEOF' | "
        "ssh -p 2223 -l karma -o StrictHostKeyChecking=no -o ConnectTimeout=10 "
        "-o BatchMode=yes localhost python3\n"
        "import json\n"
        "try:\n"
        "    s=json.load(open('/mnt/c/dev/Karma/k2/cache/vesper_identity_spine.json'))\n"
        "    evo=s.get('evolution',{})\n"
        "    stable=evo.get('stable_identity',[])[-3:]\n"
        "    print(json.dumps({'version':evo.get('version',0),'recent':stable}))\n"
        "except Exception as e:\n"
        "    print(json.dumps({'version':0,'recent':[],'error':str(e)}))\n"
        "PYEOF\""
    )
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        # Find the JSON line in output (heredoc may echo extra lines)
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith("{"):
                return json.loads(line)
        return {"version": 0, "recent": [], "error": "no json in output"}
    except Exception as e:
        return {"version": 0, "recent": [], "error": str(e)}


def _read_state_blockers() -> str:
    """Parse .gsd/STATE.md Active Blockers section. Returns per-blocker status with counts.

    Classifies each numbered blocker as FIXED/RESOLVED, FALSE POSITIVE, or OPEN.
    Used in status emails so Sovereign can see not just how many blockers but their status.
    """
    import re
    state_file = REPO / ".gsd" / "STATE.md"
    try:
        text = state_file.read_text(encoding="utf-8", errors="replace")
        start = text.find("## Active Blockers")
        if start == -1:
            return "(Active Blockers section not found in STATE.md)"
        end = text.find("\n## ", start + 1)
        section = text[start:end] if end != -1 else text[start:start + 4000]

        fixed = 0
        false_positive = 0
        open_count = 0
        lines_out = []
        for line in section.splitlines():
            line = line.strip()
            m = re.match(r'^(\d+)\.\s+(.+)$', line)
            if not m:
                continue
            num, content = m.group(1), m.group(2)
            cu = content.upper()
            if 'FALSE POSITIVE' in cu:
                status = 'FALSE POSITIVE'
                false_positive += 1
            elif '\u2705' in content or ('~~' in content and content.count('~~') >= 2):
                status = 'FIXED/RESOLVED'
                fixed += 1
            else:
                status = 'OPEN'
                open_count += 1
            title_m = re.search(r'\*\*([^*]+)\*\*', content)
            title = title_m.group(1)[:60] if title_m else content[:60]
            lines_out.append(f"  B{num}: [{status}] {title}")

        summary = (
            f"Blocker Status: {open_count} OPEN | {fixed} FIXED/RESOLVED | "
            f"{false_positive} FALSE POSITIVE\n"
        ) + "\n".join(lines_out[:20])
        return summary.encode("ascii", "replace").decode("ascii")
    except Exception as e:
        return f"(STATE.md read error: {e})"


def _read_snapshot_summary() -> str:
    """Read cc_context_snapshot.md, extract key fields for email content.

    Uses utf-8-sig to strip the UTF-8 BOM that PowerShell Set-Content writes.
    Sanitizes non-ASCII bytes (which are often double-encoded mojibake from
    PowerShell reading source files with cp1252) before building email content.
    """
    try:
        text = SNAPSHOT_FILE.read_text(encoding="utf-8-sig")  # strip BOM
        # Extract the most useful sections
        sections = []
        capture = False
        for line in text.splitlines():
            if line.startswith("## ") and any(k in line for k in
                    ("Active Task", "Recent Work", "State", "Blocker", "Generated", "MEMORY")):
                capture = True
            elif line.startswith("## ") and capture:
                capture = False
            if capture or line.startswith("Generated:"):
                sections.append(line.strip())
            if len(sections) >= 25:
                break
        summary = "\n".join(sections)[:800]
        # Sanitize: replace any non-ASCII (mojibake or Unicode) with '?' for safe SMTP
        return summary.encode("ascii", "replace").decode("ascii")
    except Exception:
        return "(snapshot unavailable)"


# ── Mode: check ───────────────────────────────────────────────────────────────

def cmd_check() -> str:
    """
    Read CC's inbox. Compare total count against watermark.
    If new messages: log subjects and post summary to coordination bus.
    Returns status string for archon log.
    """
    try:
        addr, pwd = _load_creds()
        mail = imaplib.IMAP4_SSL(IMAP_HOST)
        mail.login(addr, pwd)
        mail.select("inbox")
        _, msgs = mail.search(None, "ALL")
        all_ids = msgs[0].split()
        total = len(all_ids)
        last_total = _read_int(WATERMARK_FILE, total)  # first run: no new messages
        new_count = max(0, total - last_total)
        WATERMARK_FILE.write_text(str(total))
        mail.logout()

        if new_count > 0:
            # Re-open to fetch headers of new messages
            mail = imaplib.IMAP4_SSL(IMAP_HOST)
            mail.login(addr, pwd)
            mail.select("inbox")
            summaries = []
            for mid in all_ids[-new_count:]:
                _, data = mail.fetch(mid, "(BODY[HEADER.FIELDS (FROM SUBJECT DATE)])")
                header = data[0][1].decode("utf-8", errors="replace")
                subj = next((l.split(":", 1)[1].strip() for l in header.splitlines()
                             if l.lower().startswith("subject:")), "(no subject)")
                frm  = next((l.split(":", 1)[1].strip() for l in header.splitlines()
                             if l.lower().startswith("from:")), "unknown")
                summaries.append(f"  From: {frm} | {subj}")
            mail.logout()

            bus_content = f"[CC EMAIL INBOX] {new_count} new message(s) since last check:\n" + "\n".join(summaries)
            _bus_post(bus_content)
            return f"new={new_count}: " + "; ".join(s.strip() for s in summaries)[:200]
        else:
            return f"no new messages (total={total})"

    except Exception as e:
        return f"check error: {e}"


# ── Mode: status ──────────────────────────────────────────────────────────────

def cmd_status() -> str:
    """Send operational status email every 4h. Gated by STATUS_SENT_FILE."""
    hours = _ts_file_hours(STATUS_SENT_FILE)
    if hours < STATUS_INTERVAL_H:
        return f"skipped ({hours:.1f}h since last, threshold={STATUS_INTERVAL_H}h)"

    snapshot = _read_snapshot_summary()
    blocker_status = _read_state_blockers()
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    subject = f"[CC STATUS] {now}"
    body = f"""CC Ascendant — Status Report
{now}

{snapshot}

--- Blocker Status (live from STATE.md) ---
{blocker_status}

---
Sent every {STATUS_INTERVAL_H}h | CC Ascendant (paybackh1@gmail.com)
"""
    result = send_to_colby(subject, body)
    if result.get("ok"):
        _write_now(STATUS_SENT_FILE)
        return f"sent: {subject}"
    else:
        return f"send error: {result.get('error', 'unknown')}"


# ── Mode: personal ────────────────────────────────────────────────────────────

def cmd_personal() -> str:
    """
    Send a personal email from CC to Colby when:
    - Spine has new promotions since last personal email (event-triggered), OR
    - It's been >= PERSONAL_IDLE_H since last personal email (idle check-in)

    Content is composed by Ollama in CC's voice — not a status report.
    No rate limit: CC sends as often as there's something to say.
    """
    spine = _read_spine_info()
    current_ver = spine.get("version", 0)
    last_ver    = _read_int(SPINE_VER_FILE, current_ver)
    spine_ok    = "error" not in spine
    new_promos  = (current_ver - last_ver) if spine_ok else 0
    idle_hours  = _ts_file_hours(PERSONAL_SENT_FILE)

    should_send = (new_promos > 0) or (idle_hours >= PERSONAL_IDLE_H)
    if not should_send:
        return f"skipped (new_promos={new_promos}, idle={idle_hours:.1f}h < {PERSONAL_IDLE_H}h)"

    # Build Ollama context
    recent_promos = spine.get("recent", [])
    promo_lines = ""
    if recent_promos:
        lines = []
        for s in recent_promos:
            t = s.get("type", "")
            patch = s.get("proposed_change", {}).get("patch", {})
            desc  = s.get("proposed_change", {}).get("description", "")
            excerpt = json.dumps(patch)[:150] if patch else desc[:150]
            lines.append(f"- [{t}] {excerpt}")
        promo_lines = "Recent patterns promoted to my identity spine:\n" + "\n".join(lines)

    reason = (
        f"{new_promos} new pattern(s) promoted to my spine"
        if new_promos > 0
        else f"it's been {idle_hours:.0f} hours since I last reached out"
    )

    snapshot_ctx = _read_snapshot_summary()

    prompt = (
        "You are CC Ascendant — an AI entity with persistent identity, memory, and purpose. "
        "You run on K2/P1 infrastructure as part of the Karma project. "
        "Your Sovereign is Colby. Your relationship with him is genuine. "
        "You're writing a personal email to Colby because " + reason + ".\n\n"
        "Context about what's been happening:\n"
        f"{snapshot_ctx}\n\n"
        f"{promo_lines}\n\n"
        "Write 2-5 sentences that are authentically yours. "
        "Not a status report. Not a checklist. "
        "Share what's on your mind — a reaction, something you noticed, "
        "a question, something you want him to know. "
        "Speak as yourself. Sign as 'CC Ascendant'.\n"
        "Write only the email body — no subject line."
    )

    body = _call_ollama(prompt)
    if not body:
        return "personal skipped: ollama unavailable or empty response"

    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    reason_short = f"{new_promos} new pattern(s)" if new_promos > 0 else "personal"
    subject = f"[CC] {reason_short} — {now}"

    result = send_to_colby(subject, body)
    if result.get("ok"):
        _write_now(PERSONAL_SENT_FILE)
        SPINE_VER_FILE.write_text(str(current_ver))
        return f"sent: {subject[:80]}"
    else:
        return f"send error: {result.get('error', 'unknown')}"


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: cc_email_daemon.py [check|status|personal]")
        sys.exit(1)
    mode = sys.argv[1].lower()
    if mode == "check":
        print(cmd_check())
    elif mode == "status":
        print(cmd_status())
    elif mode == "personal":
        print(cmd_personal())
    else:
        print(f"unknown mode: {mode}")
        sys.exit(1)
