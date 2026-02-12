"""DEPRECATED — Replaced by git_sync.py (2026-02-12).

The vault-neo droplet now pulls from GitHub via cron instead of receiving
SCP pushes. This file is kept for reference only.

Replacement: git_sync.py (step 4 of karma_memory_sync.py pipeline)
"""
import subprocess, os, json
from datetime import datetime, timezone

MEMORY_DIR = r"C:\Users\raest\Documents\Karma_SADE\Memory"
SCRIPTS_DIR = r"C:\Users\raest\Documents\Karma_SADE\Scripts"
LOG_DIR = r"C:\Users\raest\Documents\Karma_SADE\Logs"
LOG_FILE = os.path.join(LOG_DIR, "karma-sade.log")

DROPLET_HOST = "vault-neo"
DROPLET_PATH = "~/karma-sade-docs/"

FILES = [
    "05-user-facts.json",
    "08-session-handoff.md",
    "09-rebuild-complete.md",
    "10-session-startup-instructions.md"
]

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def run(cmd, **kwargs):
    kwargs.setdefault("capture_output", True)
    kwargs.setdefault("text", True)
    result = subprocess.run(cmd, **kwargs)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return result.stdout.strip()

def sync_file(name):
    path = os.path.join(MEMORY_DIR, name)
    if not os.path.exists(path):
        log(f"  [SKIP] {name} not found")
        return False
    run(["scp", path, f"{DROPLET_HOST}:{DROPLET_PATH}"])
    size = os.path.getsize(path)
    log(f"  [OK] {name} ({size} bytes)")
    return True

def update_readme():
    facts = preferences = context = 0
    favorite = "purple"
    try:
        with open(os.path.join(MEMORY_DIR, "05-user-facts.json"), "r", encoding="utf-8") as f:
            data = json.load(f)
        facts = len(data.get("facts", []))
        preferences = len(data.get("preferences", []))
        context = len(data.get("context", []))
        for pref in data.get("preferences", []):
            if pref.get("key") == "favorite_color":
                favorite = pref.get("value", favorite)
    except Exception as exc:
        log(f"  [WARN] Failed to read facts file: {exc}")
    readme = f"""# Karma SADE Documentation

This directory contains the complete documentation for the Karma SADE memory system rebuild.

## Files
- **09-rebuild-complete.md** - Prompt-First rebuild documentation
- **08-session-handoff.md** - Original planning document
- **05-user-facts.json** - {facts} facts / {preferences} preferences / {context} context (favorite_color={favorite})
- **10-session-startup-instructions.md** - Session automation guide

## Status
- Memory sync every 30 minutes
- Vault backup operational
- Droplet sync automated at session start

## Updated
{datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}
"""
    run(["ssh", DROPLET_HOST, f"cat > {DROPLET_PATH}README.md"], input=readme, text=True)
    log("  [OK] README updated")

def update_timestamp():
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    run(["ssh", DROPLET_HOST, f"echo {timestamp} > {DROPLET_PATH}.last_sync"])
    log("  [OK] Timestamp updated")

def main():
    log("="*60)
    log("Karma SADE Documentation Sync to Droplet")
    log("="*60)
    run(["ssh", DROPLET_HOST, "echo OK"])
    run(["ssh", DROPLET_HOST, f"mkdir -p {DROPLET_PATH}"])
    synced = 0
    for file in FILES:
        if sync_file(file):
            synced += 1
    update_readme()
    update_timestamp()
    log(f"\nSync complete: {synced}/{len(FILES)} files")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        log(f"[ERROR] {exc}")
        raise
