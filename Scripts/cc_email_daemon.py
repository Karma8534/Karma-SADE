"""
cc_email_daemon.py — Autonomous email integration for CC Ascendant.

Called from cc_archon_agent.ps1 on the Archon watcher cycle.

Modes:
  check     — Read inbox, queue sovereign directives, acknowledge receipt, post to bus
  status    — Operational status email every 60m (gated by timestamp file)
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
import os
import urllib.request
import urllib.error
from email.utils import parseaddr
import re

# ── Paths ─────────────────────────────────────────────────────────────────────
REPO               = pathlib.Path(r"C:\Users\raest\Documents\Karma_SADE")
LOGS               = REPO / "Logs"
LOGS.mkdir(exist_ok=True)

SNAPSHOT_FILE      = REPO / "cc_context_snapshot.md"
CREDS_FILE         = REPO / ".gmail-cc-creds"
WATERMARK_FILE     = LOGS / "cc_email_watermark.txt"
CHECK_LAST_FILE    = LOGS / "cc_email_check_last.txt"
STATUS_SENT_FILE   = LOGS / "cc_email_status_last.txt"
PERSONAL_SENT_FILE = LOGS / "cc_email_personal_last.txt"
SPINE_VER_FILE     = LOGS / "cc_email_spine_version.txt"
DIRECTIVE_QUEUE_DIR = REPO / "tmp" / "sovereign_email_inbox"
DIRECTIVE_QUEUE_DIR.mkdir(parents=True, exist_ok=True)

# ── Config ────────────────────────────────────────────────────────────────────
CHECK_INTERVAL_MIN  = 15
STATUS_INTERVAL_MIN = 60
PERSONAL_IDLE_H    = 8       # hours before idle personal check-in fires
OLLAMA_URL         = os.environ.get("EMAIL_OLLAMA_URL", "http://localhost:11434/v1/chat/completions")
OLLAMA_MODEL       = os.environ.get("EMAIL_OLLAMA_MODEL", "sam860/LFM2:350m")
IMAP_HOST          = "imap.gmail.com"
HUB_BUS_URL        = "https://hub.arknexus.net/v1/coordination/post"
SOVEREIGN_ADDRESS  = "rae.steele76@gmail.com"

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


def _ts_file_minutes(path: pathlib.Path) -> float:
    return _ts_file_hours(path) * 60.0


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


def _clean_email_text(text: str) -> str:
    replacements = {
        "\u2014": "-",
        "\u2013": "-",
        "\u2019": "'",
        "\u2018": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2026": "...",
        "\u00a0": " ",
        "\u202f": " ",
        "â€”": "-",
        "â€“": "-",
        "â€™": "'",
        "â€œ": '"',
        "â€\x9d": '"',
        "â†’": "->",
        "âœ…": "[done]",
    }
    cleaned = text or ""
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)
    cleaned = cleaned.replace("~~", "").replace("**", "").replace("`", "")
    cleaned = "\n".join(line.rstrip() for line in cleaned.splitlines())
    cleaned = cleaned.encode("ascii", "replace").decode("ascii")
    cleaned = re.sub(r'\?{2,}["\']?', ' - ', cleaned)
    while "  " in cleaned:
        cleaned = cleaned.replace("  ", " ")
    return cleaned.strip()


def is_sovereign_sender(value: str) -> bool:
    _, addr = parseaddr(value or "")
    return addr.strip().lower() == SOVEREIGN_ADDRESS


def build_ack_subject(subject: str) -> str:
    subject = (subject or "Sovereign directive").strip()
    return subject if subject.lower().startswith("re:") else f"Re: {subject}"


def build_ack_body(message: dict) -> str:
    subject = (message.get("subject") or "(no subject)").strip()
    body = (message.get("body") or "").strip()
    preview = body[:400] if body else "(no body included)"
    return (
        "Received. Treating this as sovereign directive.\n\n"
        f"My understanding:\nSubject: {subject}\nDirective preview: {preview}\n\n"
        "I am queuing this directive now for execution and will send status again after implementation."
    )


def queue_sovereign_directive(message: dict, received_at: str | None = None) -> str:
    received_at = received_at or datetime.datetime.now(datetime.timezone.utc).isoformat()
    _, from_addr = parseaddr(message.get("from", ""))
    safe_subject = "".join(ch if ch.isalnum() else "-" for ch in (message.get("subject") or "directive")).strip("-")
    safe_subject = safe_subject[:48] or "directive"
    filename = f"{received_at.replace(':', '').replace('-', '')}_{safe_subject}.json"
    path = DIRECTIVE_QUEUE_DIR / filename
    payload = {
        "kind": "sovereign_email_directive",
        "state": "pending",
        "received_at": received_at,
        "from": from_addr.strip().lower(),
        "subject": (message.get("subject") or "").strip(),
        "date": (message.get("date") or "").strip(),
        "body": (message.get("body") or "").strip(),
        "source": "gmail",
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return str(path)


def process_new_messages(messages: list[dict], send_email=send_to_colby, bus_post=_bus_post) -> dict:
    queued = []
    sovereign_count = 0
    for message in messages:
        if not is_sovereign_sender(message.get("from", "")):
            continue
        sovereign_count += 1
        queued_path = queue_sovereign_directive(message)
        queued.append(queued_path)
        send_email(build_ack_subject(message.get("subject", "")), build_ack_body(message))
        bus_post(
            "[SOVEREIGN EMAIL DIRECTIVE] "
            f"Queued from {SOVEREIGN_ADDRESS}: {(message.get('subject') or '(no subject)').strip()} "
            f"-> {queued_path}"
        )
    return {"sovereign_count": sovereign_count, "queued": queued}


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
    """Parse .gsd/STATE.md Active Blockers section and return only OPEN items."""
    state_file = REPO / ".gsd" / "STATE.md"
    try:
        text = state_file.read_text(encoding="utf-8", errors="replace")
        start = text.find("## Active Blockers")
        if start == -1:
            return "(Active Blockers section not found in STATE.md)"
        end = text.find("\n## ", start + 1)
        section = text[start:end] if end != -1 else text[start:start + 4000]

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
                continue
            if '\u2705' in content or ('~~' in content and content.count('~~') >= 2):
                continue
            open_count += 1
            title = _clean_email_text(content)
            lines_out.append(f"- B{num}: {title}")

        summary = f"Open blockers: {open_count}"
        if lines_out:
            summary += "\n" + "\n".join(lines_out[:10])
        return summary
    except Exception as e:
        return f"(STATE.md read error: {e})"


def _read_snapshot_summary() -> str:
    """Read cc_context_snapshot.md and return a concise clean digest for email."""
    try:
        text = SNAPSHOT_FILE.read_text(encoding="utf-8-sig")  # strip BOM
        lines = text.splitlines()
        digest = []

        generated = next((line.strip() for line in lines if line.startswith("Generated:")), "")
        if generated:
            digest.append(_clean_email_text(generated.replace("Generated:", "Snapshot generated:").strip()))

        identity_line = ""
        in_identity = False
        for line in lines:
            if line.startswith("## Identity"):
                in_identity = True
                continue
            if in_identity and line.startswith("## "):
                break
            if in_identity and line.strip():
                identity_line = _clean_email_text(line.strip())
                break
        if identity_line:
            digest.append(f"Identity: {identity_line}")

        one_thing = next((_clean_email_text(line.split(":", 1)[1].strip()) for line in lines if line.startswith("**The One Thing:**")), "")
        if one_thing:
            digest.append(f"The One Thing: {one_thing}")

        next_steps = []
        in_next = False
        for line in lines:
            if line.startswith("## Next Session Starts Here"):
                in_next = True
                continue
            if in_next and line.startswith("## "):
                break
            if in_next:
                stripped = line.strip()
                if stripped and stripped[:2] in {"1.", "2.", "3."}:
                    next_steps.append(_clean_email_text(stripped))
            if len(next_steps) >= 3:
                break
        if next_steps:
            digest.append("Immediate next steps:")
            digest.extend(f"- {step[3:] if step[:2] in {'1.','2.','3.'} else step}" for step in next_steps)

        return "\n".join(digest[:8]).strip() or "(snapshot unavailable)"
    except Exception:
        return "(snapshot unavailable)"


def build_status_email_body(now: str, snapshot: str, blocker_status: str) -> str:
    return (
        "CC Ascendant - Status Report\n"
        f"{now}\n\n"
        f"{_clean_email_text(snapshot)}\n\n"
        "--- Open Blockers ---\n"
        f"{_clean_email_text(blocker_status)}\n\n"
        "---\n"
        f"Sent every {STATUS_INTERVAL_MIN}m | watcher every {CHECK_INTERVAL_MIN}m | CC Ascendant (paybackh1@gmail.com)\n"
    )


# ── Mode: check ───────────────────────────────────────────────────────────────

def cmd_check() -> str:
    """
    Read CC's inbox. Compare total count against watermark.
    If new messages: log subjects and post summary to coordination bus.
    Returns status string for archon log.
    """
    minutes = _ts_file_minutes(CHECK_LAST_FILE)
    if minutes < CHECK_INTERVAL_MIN:
        return f"skipped ({minutes:.1f}m since last, threshold={CHECK_INTERVAL_MIN}m)"

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
        _write_now(CHECK_LAST_FILE)
        mail.logout()

        if new_count > 0:
            # Re-open to fetch headers of new messages
            mail = imaplib.IMAP4_SSL(IMAP_HOST)
            mail.login(addr, pwd)
            mail.select("inbox")
            summaries = []
            full_messages = []
            for mid in all_ids[-new_count:]:
                _, data = mail.fetch(mid, "(RFC822)")
                raw_msg = data[0][1]
                import email
                from email.header import decode_header
                msg = email.message_from_bytes(raw_msg)
                subj_raw = msg.get("Subject", "")
                subj, enc = decode_header(subj_raw)[0]
                if isinstance(subj, bytes):
                    subj = subj.decode(enc or "utf-8", errors="replace")
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            raw = part.get_payload(decode=True)
                            if raw:
                                body = raw.decode(part.get_content_charset() or "utf-8", errors="replace")
                            break
                else:
                    raw = msg.get_payload(decode=True)
                    if raw:
                        body = raw.decode(msg.get_content_charset() or "utf-8", errors="replace")
                header = "\n".join([
                    f"From: {msg.get('From', '')}",
                    f"Subject: {subj}",
                    f"Date: {msg.get('Date', '')}",
                ])
                subj = next((l.split(":", 1)[1].strip() for l in header.splitlines()
                             if l.lower().startswith("subject:")), "(no subject)")
                frm  = next((l.split(":", 1)[1].strip() for l in header.splitlines()
                             if l.lower().startswith("from:")), "unknown")
                summaries.append(f"  From: {frm} | {subj}")
                full_messages.append({
                    "from": frm,
                    "subject": subj,
                    "date": msg.get("Date", ""),
                    "body": body.strip(),
                })
            mail.logout()

            processed = process_new_messages(full_messages)
            bus_content = f"[CC EMAIL INBOX] {new_count} new message(s) since last check:\n" + "\n".join(summaries)
            _bus_post(bus_content)
            return (
                f"new={new_count}; sovereign={processed['sovereign_count']}: "
                + "; ".join(s.strip() for s in summaries)[:200]
            )
        else:
            return f"no new messages (total={total})"

    except Exception as e:
        return f"check error: {e}"


# ── Mode: status ──────────────────────────────────────────────────────────────

def cmd_status() -> str:
    """Send operational status email every 60 minutes. Gated by STATUS_SENT_FILE."""
    minutes = _ts_file_minutes(STATUS_SENT_FILE)
    if minutes < STATUS_INTERVAL_MIN:
        return f"skipped ({minutes:.1f}m since last, threshold={STATUS_INTERVAL_MIN}m)"

    snapshot = _read_snapshot_summary()
    blocker_status = _read_state_blockers()
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    subject = f"[CC STATUS] {now}"
    body = build_status_email_body(now, snapshot, blocker_status)
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
