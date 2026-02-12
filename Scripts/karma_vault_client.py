"""
Karma Vault Client
Handles communication with the ArkNexus Memory Vault API.
"""

import requests
import json
import os
from datetime import datetime
import uuid
import hashlib

# Configuration
VAULT_BASE_URL = "https://vault.arknexus.net"
VAULT_TOKEN_FILE = os.path.join(os.path.dirname(__file__), ".vault_token")
MEMORY_DIR = r"C:\Users\raest\Documents\Karma_SADE\Memory"

# Default token (will be overwritten by file if exists)
DEFAULT_TOKEN = "6a5ba4cdc661886d33e7a19741be3d9c2847451b88029be1f4a51b6da929fc78"


class VaultClient:
    def __init__(self, base_url=VAULT_BASE_URL, token=None):
        self.base_url = base_url.rstrip('/')
        self.token = token or self._load_token()
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def _load_token(self):
        """Load token from file or use default."""
        if os.path.exists(VAULT_TOKEN_FILE):
            with open(VAULT_TOKEN_FILE, 'r') as f:
                return f.read().strip()
        return DEFAULT_TOKEN
    
    def _generate_id(self, prefix="mem"):
        """Generate a unique memory ID."""
        # Use format similar to Vault: mem_XXXXXXXXXXXX
        unique = hashlib.sha256(
            f"{datetime.utcnow().isoformat()}{uuid.uuid4()}".encode()
        ).hexdigest()[:16]
        return f"{prefix}_{unique}"
    
    def health_check(self):
        """Check if Vault API is healthy."""
        try:
            response = requests.get(
                f"{self.base_url}/livez",
                headers=self.headers,
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
    
    def get_bootstrap(self, n=25):
        """Get bootstrap data with recent memories."""
        try:
            response = requests.get(
                f"{self.base_url}/v1/bootstrap",
                params={"n": n},
                headers=self.headers,
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Bootstrap error: {e}")
            return None
    
    def write_memory(self, memory_type, content, tags=None, source_kind="tool", 
                     source_ref="karma-sade", confidence=0.9, notes=""):
        """
        Write a memory to the Vault.
        
        Args:
            memory_type: One of: fact, preference, project, artifact, log, contact
            content: Dict with memory content
            tags: List of string tags
            source_kind: One of: user, system, import, tool, web
            source_ref: Reference string for source
            confidence: Float 0-1
            notes: Verification notes
        
        Returns:
            Response dict or None on failure
        """
        memory_id = self._generate_id()
        now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
        
        payload = {
            "id": memory_id,
            "type": memory_type,
            "content": content if isinstance(content, dict) else {"value": content},
            "tags": tags or [],
            "source": {
                "kind": source_kind,
                "ref": source_ref
            },
            "created_at": now,
            "updated_at": now,
            "confidence": confidence,
            "verification": {
                "protocol_version": "0.1",
                "verified_at": now,
                "verifier": "karma-sade-architect",
                "status": "verified",
                "notes": notes or f"Synced from Karma SADE on PAYBACK"
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/memory",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                return {"ok": True, "id": memory_id, "response": response.json()}
            else:
                return {"ok": False, "status": response.status_code, "body": response.text}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def write_fact(self, key, value, tags=None, confidence=0.9):
        """Write a fact to the Vault."""
        return self.write_memory(
            memory_type="fact",
            content={"key": key, "value": value},
            tags=tags or ["karma-sade", "fact"],
            confidence=confidence,
            notes=f"Fact: {key}"
        )
    
    def write_preference(self, key, value, tags=None, confidence=0.95):
        """Write a preference to the Vault."""
        return self.write_memory(
            memory_type="preference",
            content={"key": key, "value": value},
            tags=tags or ["karma-sade", "preference", "neo"],
            confidence=confidence,
            notes=f"User preference: {key}"
        )
    
    def write_log(self, topic, message, details=None, tags=None):
        """Write a log entry to the Vault."""
        content = {
            "topic": topic,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "source_system": "karma-sade"
        }
        if details:
            content["details"] = details
        
        return self.write_memory(
            memory_type="log",
            content=content,
            tags=tags or ["karma-sade", "log", topic],
            confidence=1.0,
            notes=f"Log: {topic}"
        )
    
    def get_facts(self):
        """
        Get deduplicated facts and preferences from Vault.
        Uses the /v1/facts endpoint (added in vault-api v0.3.0).
        Returns dict with 'facts', 'preferences', 'meta' keys, or None on failure.
        """
        try:
            response = requests.get(
                f"{self.base_url}/v1/facts",
                headers=self.headers,
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            print(f"get_facts: HTTP {response.status_code}")
            return None
        except Exception as e:
            print(f"get_facts error: {e}")
            return None

    def search_memories(self, query=None, memory_type=None, limit=50):
        """
        Search memories from bootstrap.
        Note: Vault doesn't have a search endpoint yet, so we filter bootstrap.
        """
        bootstrap = self.get_bootstrap(n=limit)
        if not bootstrap or "recent" not in bootstrap:
            return []
        
        items = bootstrap.get("recent", [])
        
        # Filter by type if specified
        if memory_type:
            items = [i for i in items if i.get("type") == memory_type]
        
        # Filter by query in content if specified
        if query:
            query_lower = query.lower()
            filtered = []
            for item in items:
                content = json.dumps(item.get("content", {})).lower()
                if query_lower in content:
                    filtered.append(item)
            items = filtered
        
        return items


def test_connection():
    """Test the Vault connection."""
    client = VaultClient()
    
    print("Testing Vault connection...")
    if client.health_check():
        print("✓ Vault API is healthy")
    else:
        print("✗ Vault API unreachable")
        return False
    
    print("\nFetching bootstrap...")
    bootstrap = client.get_bootstrap(n=3)
    if bootstrap:
        meta = bootstrap.get("meta", {})
        print(f"✓ Bootstrap received")
        print(f"  Ledger lines: {meta.get('ledger_lines', 'unknown')}")
        print(f"  Last ID: {meta.get('last_id', 'unknown')}")
        return True
    else:
        print("✗ Bootstrap failed")
        return False


if __name__ == "__main__":
    test_connection()
