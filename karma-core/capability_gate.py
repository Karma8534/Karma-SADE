"""
Step 2.6: Capability Gate — Read vs Write Token Scoping

Token scopes:
- READ:  Can call /v1/retrieve, /v1/health, GET endpoints
- WRITE: Can call /v1/admit, /v1/retrieve, /v1/memory/update, /v1/memory/delete, /v1/reflect
         (plus all READ operations)

Implementation: Bearer token carries scope metadata.
Token format: "Bearer <token>" where token maps to scope in a config.

For Phase 2, we use a simple approach:
- Hub bridge token (existing) = WRITE scope (full access)
- Read-only tokens can be generated for dashboards/monitoring
"""

import os
import hashlib
import json
from datetime import datetime, timezone

# Token → scope mapping
# The hub bridge auth token is the master WRITE token
WRITE_TOKEN = os.getenv(
    "AUTH_TOKEN",
    "cb5617b2ce67470d389dcff1e1fe417aa2626ae699c7d5f831b133cb1f4d450e"
)

# Generate a deterministic read-only token from the write token
READ_TOKEN = hashlib.sha256(f"readonly:{WRITE_TOKEN}".encode()).hexdigest()

# Scope definitions
SCOPES = {
    "read": {
        "allowed_endpoints": {
            "/v1/retrieve", "/v1/health", "/v1/budget",
            "/v1/observations", "/v1/scenes",
        },
        "allowed_methods": {"GET", "POST"},
        "description": "Read-only access to memory retrieval and monitoring",
    },
    "write": {
        "allowed_endpoints": {
            "/v1/admit", "/v1/retrieve", "/v1/memory/update",
            "/v1/memory/delete", "/v1/reflect", "/v1/health",
            "/v1/budget", "/v1/observations", "/v1/scenes",
            "/v1/staleness/scan", "/v1/tools/execute",
        },
        "allowed_methods": {"GET", "POST", "PUT", "PATCH", "DELETE"},
        "description": "Full read+write access to all memory operations",
    },
}

# Token → scope registry
TOKEN_REGISTRY = {
    WRITE_TOKEN: "write",
    READ_TOKEN: "read",
}


def get_token_scope(token: str) -> str:
    """
    Resolve a bearer token to its scope.
    Returns: 'read', 'write', or 'denied'
    """
    clean = token.replace("Bearer ", "").strip()
    return TOKEN_REGISTRY.get(clean, "denied")


def check_access(token: str, endpoint: str, method: str = "POST") -> dict:
    """
    Gate check: can this token access this endpoint with this method?

    Returns: {allowed: True/False, scope: str, reason: str}
    """
    scope = get_token_scope(token)

    if scope == "denied":
        return {
            "allowed": False,
            "scope": "denied",
            "reason": "Invalid or unrecognized token",
        }

    scope_config = SCOPES.get(scope, {})
    allowed_endpoints = scope_config.get("allowed_endpoints", set())
    allowed_methods = scope_config.get("allowed_methods", set())

    if endpoint not in allowed_endpoints:
        return {
            "allowed": False,
            "scope": scope,
            "reason": f"Endpoint '{endpoint}' not allowed for scope '{scope}'",
        }

    if method.upper() not in allowed_methods:
        return {
            "allowed": False,
            "scope": scope,
            "reason": f"Method '{method}' not allowed for scope '{scope}'",
        }

    return {
        "allowed": True,
        "scope": scope,
        "reason": "Access granted",
    }


def get_read_token() -> str:
    """Return the read-only token for monitoring/dashboards."""
    return READ_TOKEN


def get_scope_info() -> dict:
    """Return info about all scopes (for /v1/health)."""
    return {
        "scopes": {
            name: {
                "endpoints": sorted(config["allowed_endpoints"]),
                "methods": sorted(config["allowed_methods"]),
                "description": config["description"],
            }
            for name, config in SCOPES.items()
        },
        "read_token_preview": READ_TOKEN[:12] + "...",
    }
