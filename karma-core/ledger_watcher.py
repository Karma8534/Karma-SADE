"""
Continuous Ledger Ingestion — Monitors ledger for new entries and ingests to FalkorDB.
This ensures hub-bridge entries (and other external writes) are ingested to knowledge graph.
"""
import asyncio
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import config


class LedgerWatcher:
    """Continuously monitors ledger and ingests new entries."""
    
    def __init__(self, ingest_fn):
        self.ingest_fn = ingest_fn
        self.ledger_path = Path(config.LEDGER_PATH)
        self.processed_hashes = set()
        self._running = False
        
    def _load_processed_hashes(self):
        """Load already processed hashes from file."""
        hashes_file = self.ledger_path.parent / "ledger_watcher_hashes.txt"
        if hashes_file.exists():
            with open(hashes_file, "r") as f:
                self.processed_hashes = set(line.strip() for line in f if line.strip())
    
    def _save_processed_hashes(self):
        """Save processed hashes to file."""
        hashes_file = self.ledger_path.parent / "ledger_watcher_hashes.txt"
        with open(hashes_file, "w") as f:
            for h in self.processed_hashes:
                f.write(f"{h}\n")
    
    def _get_entry_hash(self, entry):
        """Generate hash for deduplication."""
        return str(hash(str(entry)))
    
    def _should_ingest(self, entry):
        """Check if entry should be ingested."""
        # Skip entries without user_message + assistant_message
        content = entry.get("content", {})
        if not content.get("user_message") or not content.get("assistant_text"):
            return False
        
        # Skip karma-terminal entries (already ingested live)
        source = entry.get("source", {})
        if source.get("kind") == "tool" and source.get("ref") == "karma-terminal-chat":
            return False
        
        # Skip already processed
        entry_hash = self._get_entry_hash(entry)
        if entry_hash in self.processed_hashes:
            return False
        
        return True
    
    async def _process_ledger(self):
        """Process new ledger entries."""
        new_entries = []
        
        with open(self.ledger_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    if self._should_ingest(entry):
                        new_entries.append(entry)
                except json.JSONDecodeError:
                    continue
        
        for entry in new_entries:
            try:
                content = entry.get("content", {})
                user_msg = content.get("user_message", "")
                assistant_msg = content.get("assistant_text", "")
                source = entry.get("source", {}).get("ref", "ledger-watcher")
                
                await self.ingest_fn(user_msg=user_msg, assistant_msg=assistant_msg, source=source)
                
                # Mark as processed
                self.processed_hashes.add(self._get_entry_hash(entry))
                print(f"[LEDGER_WATCHER] Ingested entry: {entry.get("id", "unknown")}")
            except Exception as e:
                print(f"[LEDGER_WATCHER] Error ingesting entry: {e}")
        
        if new_entries:
            self._save_processed_hashes()
    
    async def start(self):
        """Start continuous monitoring."""
        self._load_processed_hashes()
        self._running = True
        print("[LEDGER_WATCHER] Started — monitoring ledger for new entries")
        
        while self._running:
            try:
                await self._process_ledger()
                await asyncio.sleep(config.CONSCIOUSNESS_INTERVAL)  # Sync with consciousness interval
            except Exception as e:
                print(f"[LEDGER_WATCHER] Error: {e}")
                await asyncio.sleep(10)  # Back off on error
    
    def stop(self):
        """Stop monitoring."""
        self._running = False
        self._save_processed_hashes()
        print("[LEDGER_WATCHER] Stopped")


def start_ledger_watcher(ingest_fn):
    """Start ledger watcher as background task."""
    watcher = LedgerWatcher(ingest_fn)
    asyncio.create_task(watcher.start())
    return watcher
