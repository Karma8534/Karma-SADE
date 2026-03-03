#!/usr/bin/env python3
"""Graph surgery: fix polluted entity summaries in FalkorDB neo_workspace."""

import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)


def set_summary(name, summary):
    """Update entity summary by name. Escapes for Cypher inline string."""
    safe = summary.replace("\\", "\\\\").replace('"', '\\"')
    q = f'MATCH (n) WHERE n.name = "{name}" SET n.summary = "{safe}" RETURN n.name'
    result = r.execute_command("GRAPH.QUERY", "neo_workspace", q)
    print(f"[OK] {name}: summary updated")
    return result


# 1. PAYBACK - it's a MACHINE, not a project
set_summary(
    "PAYBACK",
    "PAYBACK (also called P1, formerly ANR1) is Colbys primary Windows workstation. "
    "It is a MACHINE, not a project. "
    "Colby runs Claude Code (CC) on PAYBACK. "
    "Colby chats with Karma from PAYBACK. "
    "PAYBACK is on the local network. "
    "K2 (192.168.0.226) is a separate machine on the same LAN. "
    "The droplet (vault-neo / arknexus.net) is where Karma lives. "
    "PAYBACK hosts the Karma_SADE git repository locally.",
)

# 2. Karma_SADE - Karmas own codebase, not just a chrome extension
set_summary(
    "Karma_SADE",
    "Karma_SADE is the git repository that contains Karmas entire codebase. "
    "It includes: hub-bridge (Karmas API bridge), chrome-extension (Universal AI Memory), "
    "identity.json, invariants.json, direction.md (Karmas identity spine), "
    "Memory/ directory (system prompts, session handoffs), and scripts. "
    "Karma_SADE is NOT just a Chrome extension - it is everything that makes Karma work. "
    "The repo lives on GitHub (Karma8534/Karma-SADE) and is cloned locally on PAYBACK and on the droplet.",
)

# 3. Fix the file path entity
safe_path = "C:\\\\Users\\\\raest\\\\Documents\\\\Karma_SADE\\\\chrome-extension"
q_path = (
    f'MATCH (n) WHERE n.name = "{safe_path}" '
    'SET n.summary = "Local path to the Chrome extension component of Karma_SADE on PAYBACK (Colbys workstation). '
    'This is one subdirectory of the larger Karma_SADE repository." '
    "RETURN n.name"
)
r.execute_command("GRAPH.QUERY", "neo_workspace", q_path)
print("[OK] chrome-extension path entity: summary updated")

# 4. Neo - alias for Colby, not a separate person
set_summary(
    "Neo",
    "Neo is Colbys username/alias on his machines. Neo = Colby. They are the same person. "
    "Colby is the real name. Neo appears in system paths and SSH configs. "
    "When Karma sees Neo, it means Colby.",
)

# 5. Colby - primary user, canonical identity
set_summary(
    "Colby",
    "Colby is Karmas primary user and collaborator. Real name: Colby. Also known as Neo (machine username). "
    "Age 55, male. Has a dog named Baxter and a cat named Ollie. "
    "Favorite color: purple. Started learning piano, teacher is Dana, meets Tuesdays at 4pm. "
    "Cognitive style: pattern recognition, gut-feel signal detection, high-level synthesis. "
    "Works with Karma as a peer, not as an assistant relationship. "
    "Colby runs Claude Code on PAYBACK (his workstation). "
    "Colby chats with Karma through hub-bridge. "
    "Colby collaborates with Aria (ChatGPT) for architecture filtering.",
)

print("\n=== Graph surgery complete ===")

# Verify: read back key summaries
print("\n--- Verification ---")
for name in ["PAYBACK", "Karma_SADE", "Neo", "Colby"]:
    q = f'MATCH (n) WHERE n.name = "{name}" RETURN n.name, n.summary LIMIT 1'
    result = r.execute_command("GRAPH.QUERY", "neo_workspace", q)
    print(f"\n{name}:")
    # Parse result - FalkorDB returns nested lists
    if isinstance(result, list) and len(result) > 1:
        for row in result[1]:
            if isinstance(row, list) and len(row) >= 2:
                print(f"  summary: {str(row[1])[:200]}...")
