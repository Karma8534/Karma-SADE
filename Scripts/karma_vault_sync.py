"""
Karma Vault Sync
Synchronizes memories between local Karma and the ArkNexus Vault.
- Pushes local facts/preferences to Vault
- Pulls Vault memories to local on startup
- Maintains sync state to avoid duplicates
"""

import json
import os
import sys
from datetime import datetime, timezone
import hashlib

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(__file__))

from karma_vault_client import VaultClient

# Configuration
MEMORY_DIR = r"C:\Users\raest\Documents\Karma_SADE\Memory"
FACTS_FILE = os.path.join(MEMORY_DIR, "05-user-facts.json")
LEARNINGS_FILE = os.path.join(MEMORY_DIR, "04-session-learnings.md")
SYNC_STATE_FILE = os.path.join(MEMORY_DIR, ".vault_sync_state.json")
VAULT_CACHE_FILE = os.path.join(MEMORY_DIR, "07-vault-cache.json")

# Volatile keys that should never be synced from Vault back to local.
# Keep in sync with generate_karma_prompt.py BLOCKED_KEYS.
BLOCKED_KEYS = {
    "browser_tabs", "open_browser_tabs", "browser", "karma-browser-control/browser_tabs",
    "last_visited_url", "current_tabs", "open_tabs", "preferred_browser", "browser_state",
    "website_title", "github_page_title", "preferred_color",
    "logging_tools", "monitoring_tools", "backup_locations", "karma_sade_description",
    "code_interpreter", "playwright", "chat_window_features", "open_webui_management",
    "previous_conversation", "change_management_rules", "change_management_rules_steps",
    "perplexity_labs", "perplexity_models", "preferred_nickname", "working_machine",
    "memory_system_status", "karma_sade_rebuild_2026_02_10",
    "current_browser", "current_tab", "color_picker", "browser_control_needed",
}


def load_sync_state():
    """Load sync state to track what's been synced."""
    if os.path.exists(SYNC_STATE_FILE):
        with open(SYNC_STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "last_push": None,
        "last_pull": None,
        "pushed_hashes": [],
        "pulled_ids": []
    }


def save_sync_state(state):
    """Save sync state."""
    with open(SYNC_STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)


def hash_item(item):
    """Create a hash of an item to detect changes."""
    return hashlib.sha256(json.dumps(item, sort_keys=True).encode()).hexdigest()[:16]


def load_local_facts():
    """Load local facts from JSON file."""
    if not os.path.exists(FACTS_FILE):
        return {"facts": [], "preferences": [], "context": []}
    with open(FACTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_local_facts(data):
    """Save local facts to JSON file."""
    with open(FACTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def push_to_vault(client: VaultClient, state: dict):
    """Push local memories to the Vault."""
    print("\n--- PUSH: Local -> Vault ---")
    
    local_data = load_local_facts()
    pushed = 0
    skipped = 0
    failed = 0
    
    # Push facts
    for item in local_data.get("facts", []):
        key = item.get("key", "")
        value = item.get("value", "")
        if not key or not value:
            continue
        
        item_hash = hash_item({"type": "fact", "key": key, "value": value})
        if item_hash in state.get("pushed_hashes", []):
            skipped += 1
            continue
        
        result = client.write_fact(key, str(value), tags=["karma-sade", "fact", "payback"])
        if result.get("ok"):
            print(f"  [+] Pushed fact: {key}")
            state["pushed_hashes"].append(item_hash)
            pushed += 1
        else:
            print(f"  [-] Failed fact: {key} - {result}")
            failed += 1
    
    # Push preferences
    for item in local_data.get("preferences", []):
        key = item.get("key", "")
        value = item.get("value", "")
        if not key or not value:
            continue
        
        item_hash = hash_item({"type": "preference", "key": key, "value": value})
        if item_hash in state.get("pushed_hashes", []):
            skipped += 1
            continue
        
        result = client.write_preference(key, str(value), tags=["karma-sade", "preference", "neo"])
        if result.get("ok"):
            print(f"  [+] Pushed preference: {key}")
            state["pushed_hashes"].append(item_hash)
            pushed += 1
        else:
            print(f"  [-] Failed preference: {key} - {result}")
            failed += 1
    
    # Push context as facts
    for item in local_data.get("context", []):
        key = item.get("key", "")
        value = item.get("value", "")
        if not key or not value:
            continue
        
        item_hash = hash_item({"type": "context", "key": key, "value": value})
        if item_hash in state.get("pushed_hashes", []):
            skipped += 1
            continue
        
        result = client.write_fact(key, str(value), tags=["karma-sade", "context", "payback"])
        if result.get("ok"):
            print(f"  [+] Pushed context: {key}")
            state["pushed_hashes"].append(item_hash)
            pushed += 1
        else:
            print(f"  [-] Failed context: {key} - {result}")
            failed += 1
    
    state["last_push"] = datetime.now(timezone.utc).isoformat()
    print(f"\nPush complete: {pushed} pushed, {skipped} skipped, {failed} failed")
    return pushed, failed


def pull_from_vault(client: VaultClient, state: dict):
    """Pull facts and preferences from Vault to local using /v1/facts endpoint.
    
    Conflict resolution: Vault entry with newer updated_at wins.
    This enables bidirectional sync — facts learned via Hub Bridge
    flow back to Karma's local memory.
    """
    print("\n--- PULL: Vault -> Local ---")
    
    result = client.get_facts()
    if not result or not result.get("ok"):
        print("  [ERROR] Failed to get facts from Vault")
        return 0, 1
    
    vault_facts = result.get("facts", [])
    vault_prefs = result.get("preferences", [])
    meta = result.get("meta", {})
    print(f"  Vault has {meta.get('facts_count', '?')} facts, {meta.get('preferences_count', '?')} preferences")
    
    local_data = load_local_facts()
    pulled = 0
    updated = 0
    skipped = 0
    
    # Cache Vault data
    vault_cache = {
        "pulled_at": datetime.now(timezone.utc).isoformat(),
        "meta": meta,
        "facts_count": len(vault_facts),
        "preferences_count": len(vault_prefs)
    }
    with open(VAULT_CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(vault_cache, f, indent=2, ensure_ascii=False)
    
    # Merge vault facts into local
    for vf in vault_facts:
        key = vf.get("key", "")
        value = vf.get("value", "")
        vault_updated = vf.get("updated_at", "")
        if not key or not value:
            continue
        if key in BLOCKED_KEYS:
            skipped += 1
            continue
        
        # Find by key in local facts OR context (Karma uses both sections for facts)
        existing = next((f for f in local_data.get("facts", []) if f.get("key") == key), None)
        if not existing:
            existing = next((f for f in local_data.get("context", []) if f.get("key") == key), None)
        
        if not existing:
            # New fact from Vault — add it
            local_data.setdefault("facts", []).append({
                "key": key,
                "value": value,
                "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                "vault_id": vf.get("id", "")
            })
            print(f"  [+] New fact from Vault: {key}")
            pulled += 1
        elif existing.get("value") != value:
            # Key exists but value differs — check timestamps
            local_updated = existing.get("updated", "")
            # Vault uses ISO format, local uses "YYYY-MM-DD HH:MM:SS"
            # Normalize for comparison
            vault_ts = vault_updated.replace("T", " ").replace("Z", "")[:19] if vault_updated else ""
            local_ts = local_updated[:19] if local_updated else ""
            
            if vault_ts > local_ts:
                existing["value"] = value
                existing["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                existing["vault_id"] = vf.get("id", "")
                print(f"  [~] Updated from Vault: {key}")
                updated += 1
            else:
                skipped += 1
        else:
            skipped += 1
    
    # Merge vault preferences into local
    for vp in vault_prefs:
        key = vp.get("key", "")
        value = vp.get("value", "")
        vault_updated = vp.get("updated_at", "")
        if not key or not value:
            continue
        if key in BLOCKED_KEYS:
            skipped += 1
            continue
        
        existing = next((p for p in local_data.get("preferences", []) if p.get("key") == key), None)
        
        if not existing:
            local_data.setdefault("preferences", []).append({
                "key": key,
                "value": value,
                "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                "vault_id": vp.get("id", "")
            })
            print(f"  [+] New preference from Vault: {key}")
            pulled += 1
        elif existing.get("value") != value:
            vault_ts = vault_updated.replace("T", " ").replace("Z", "")[:19] if vault_updated else ""
            local_ts = (existing.get("updated", ""))[:19]
            
            if vault_ts > local_ts:
                existing["value"] = value
                existing["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                existing["vault_id"] = vp.get("id", "")
                print(f"  [~] Updated preference from Vault: {key}")
                updated += 1
            else:
                skipped += 1
        else:
            skipped += 1
    
    # Save local data
    save_local_facts(local_data)
    state["last_pull"] = datetime.now(timezone.utc).isoformat()
    
    print(f"\nPull complete: {pulled} new, {updated} updated, {skipped} unchanged")
    return pulled + updated, 0


def sync_log_entry(client: VaultClient):
    """Write a sync log entry to the Vault."""
    result = client.write_log(
        topic="karma-sync",
        message="Karma SADE memory sync completed",
        details={
            "source_machine": "PAYBACK",
            "source_system": "karma-sade",
            "sync_type": "bidirectional"
        },
        tags=["karma-sade", "sync", "log"]
    )
    return result.get("ok", False)


def main():
    print("=" * 60)
    print("Karma-Vault Sync")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Initialize client
    client = VaultClient()
    
    # Health check
    print("\nChecking Vault connection...")
    if not client.health_check():
        print("[ERROR] Vault API unreachable - sync aborted")
        return
    print("[OK] Vault API healthy")
    
    # Load sync state
    state = load_sync_state()
    print(f"Last push: {state.get('last_push', 'never')}")
    print(f"Last pull: {state.get('last_pull', 'never')}")
    
    # Pull first (get latest from Vault)
    pull_from_vault(client, state)
    
    # Then push (send local changes to Vault)
    push_to_vault(client, state)
    
    # Save sync state
    save_sync_state(state)
    
    # Log the sync
    if sync_log_entry(client):
        print("\n[OK] Sync logged to Vault")
    
    print("\n" + "=" * 60)
    print("Sync complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
