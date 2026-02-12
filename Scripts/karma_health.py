"""
Karma SADE Health Check
Verifies all components are working correctly.
"""

import os
import json
import requests
from datetime import datetime, timezone

MEMORY_DIR = r"C:\Users\raest\Documents\Karma_SADE\Memory"
LOG_DIR = r"C:\Users\raest\Documents\Karma_SADE\Logs"
FACTS_FILE = os.path.join(MEMORY_DIR, "05-user-facts.json")
LOG_FILE = os.path.join(LOG_DIR, "karma-sade.log")

def check_ollama():
    """Check if Ollama is running."""
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=5)
        return r.status_code == 200
    except:
        return False

def check_openwebui():
    """Check if Open WebUI is running."""
    try:
        r = requests.get("http://localhost:8080", timeout=5)
        return r.status_code == 200
    except:
        return False

def check_vault():
    """Check if Vault API is reachable."""
    try:
        r = requests.get("https://vault.arknexus.net/livez", timeout=10)
        return r.status_code == 200
    except:
        return False

def check_facts():
    """Check if facts file exists and has favorite_color."""
    if not os.path.exists(FACTS_FILE):
        return False, "Facts file missing"
    try:
        with open(FACTS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        prefs = data.get("preferences", [])
        for p in prefs:
            if p.get("key") == "favorite_color":
                return True, p.get("value")
        return False, "favorite_color not found"
    except Exception as e:
        return False, str(e)

def check_last_sync():
    """Check when last sync occurred."""
    if not os.path.exists(LOG_FILE):
        return None
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        for line in reversed(lines):
            if "Memory Sync - Complete" in line or "Sync complete" in line:
                # Extract timestamp from [YYYY-MM-DD HH:MM:SS]
                ts = line[1:20]
                return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        return None
    except:
        return None

def main():
    print("=" * 50)
    print("Karma SADE Health Check")
    print("=" * 50)
    
    all_ok = True
    
    # Ollama
    if check_ollama():
        print("[OK] Ollama running")
    else:
        print("[!!] Ollama NOT running")
        all_ok = False
    
    # Open WebUI
    if check_openwebui():
        print("[OK] Open WebUI running")
    else:
        print("[!!] Open WebUI NOT running")
        all_ok = False
    
    # Vault
    if check_vault():
        print("[OK] Vault API reachable")
    else:
        print("[--] Vault API unreachable (non-critical)")
    
    # Facts
    ok, value = check_facts()
    if ok:
        print(f"[OK] favorite_color = {value}")
    else:
        print(f"[!!] Facts issue: {value}")
        all_ok = False
    
    # Last sync
    last_sync = check_last_sync()
    if last_sync:
        ago = datetime.now() - last_sync
        mins = int(ago.total_seconds() / 60)
        if mins < 15:
            print(f"[OK] Last sync: {mins} min ago")
        else:
            print(f"[--] Last sync: {mins} min ago (consider running 'karma')")
    else:
        print("[--] No sync history found")
    
    print("=" * 50)
    if all_ok:
        print("Status: HEALTHY")
    else:
        print("Status: ISSUES DETECTED")
    print("=" * 50)

if __name__ == "__main__":
    main()
