"""Karma Memory Sync - Master Orchestrator"""
import subprocess, sys, os
from datetime import datetime

SCRIPTS_DIR = r"C:\Users\raest\Documents\Karma_SADE\Scripts"
LOG_DIR = r"C:\Users\raest\Documents\Karma_SADE\Logs"
LOG_FILE = os.path.join(LOG_DIR, "karma-sade.log")

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def run_script(name, step, total):
    log(f"\n[Step {step}/{total}] Running {name}...")
    script_path = os.path.join(SCRIPTS_DIR, name)
    if not os.path.exists(script_path):
        log(f"  [ERROR] Script not found: {script_path}")
        return False
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, timeout=180)
    if result.stdout:
        log(f"  Output: {result.stdout.strip()[:200]}...")
    if result.returncode != 0:
        log(f"  [ERROR] Exit {result.returncode}")
        if result.stderr:
            log(f"  stderr: {result.stderr.strip()[:400]}")
        return False
    log("  [OK] Complete")
    return True

def main():
    log("="*60)
    log("Karma Memory Sync - Starting")
    log("="*60)
    steps = [
        "karma_chat_extractor.py",
        "generate_karma_prompt.py",
        "karma_vault_sync.py",
        "git_sync.py"
    ]
    completed = 0
    for idx, script in enumerate(steps, 1):
        if run_script(script, idx, len(steps)):
            completed += 1
    log("\n" + "="*60)
    log(f"Karma Memory Sync - Complete ({completed}/{len(steps)} steps)")
    log("="*60)
    if completed == len(steps):
        log("[OK] Memory system updated successfully")
    else:
        log("[WARNING] Incomplete sync - see logs")

if __name__ == "__main__":
    main()
