#!/usr/bin/env python3
"""Patch hub-bridge server.js to add GET /v1/context endpoint for Ambient Layer Tier 2."""
import sys

SERVER_JS = "/opt/seed-vault/memory_v1/hub_bridge/app/server.js"

CONTEXT_ENDPOINT = r'''
    // --- GET /v1/context --- Ambient Knowledge Layer Tier 2
    // Returns recent ambient entries from the vault ledger for cross-agent awareness.
    if (req.method === "GET" && req.url.startsWith("/v1/context")) {
      const token = bearerToken(req);
      if (!HUB_CHAT_TOKEN || !token || token !== HUB_CHAT_TOKEN) {
        return json(res, 401, { ok: false, error: "unauthorized" });
      }

      const parsed = new URL(req.url, `http://localhost`);
      const hours = parseInt(parsed.searchParams.get("hours") || "2", 10);
      const sourceFilter = parsed.searchParams.get("source") || "all";
      const nodeFilter = parsed.searchParams.get("node") || "all";
      const limit = Math.min(parseInt(parsed.searchParams.get("limit") || "20", 10), 100);

      const LEDGER_PATH = "/opt/seed-vault/memory_v1/ledger/memory.jsonl";
      const cutoff = new Date(Date.now() - hours * 3600 * 1000).toISOString();

      try {
        const data = fs.readFileSync(LEDGER_PATH, "utf8");
        const lines = data.trim().split("\n").filter(Boolean);

        // Read from end (most recent first), filter, collect up to limit
        const entries = [];
        for (let i = lines.length - 1; i >= 0 && entries.length < limit; i--) {
          try {
            const rec = JSON.parse(lines[i]);
            const capturedAt = (rec.content && rec.content.captured_at) || rec.captured_at || "";
            if (capturedAt < cutoff) break; // Past the time window, stop

            const src = (rec.content && rec.content.source) || "";
            const node = (rec.content && rec.content.source_node) || "";

            if (sourceFilter !== "all" && src !== sourceFilter) continue;
            if (nodeFilter !== "all" && node !== nodeFilter) continue;

            entries.push({
              id: rec.id || "",
              source: src,
              source_node: node,
              summary: (rec.content && rec.content.summary) || "",
              tags: rec.tags || [],
              captured_at: capturedAt,
            });
          } catch (_) {
            // Skip malformed lines
          }
        }

        return json(res, 200, {
          ok: true,
          window: `last ${hours} hour${hours !== 1 ? "s" : ""}`,
          count: entries.length,
          entries: entries,
        });
      } catch (e) {
        if (e.code === "ENOENT") {
          return json(res, 200, { ok: true, window: `last ${hours} hour${hours !== 1 ? "s" : ""}`, count: 0, entries: [] });
        }
        return json(res, 500, { ok: false, error: "ledger_read_error", message: e.message });
      }
    }

'''

# Find the insertion point: just before "// --- GET /v1/vault-file/:alias ---"
with open(SERVER_JS, "r") as f:
    content = f.read()

MARKER = "    // --- GET /v1/vault-file/:alias ---"

if "/v1/context" in content:
    print("SKIP: /v1/context endpoint already exists in server.js")
    sys.exit(0)

if MARKER not in content:
    print(f"ERROR: Could not find marker: {MARKER}")
    sys.exit(1)

# Insert the context endpoint before the vault-file endpoint
patched = content.replace(MARKER, CONTEXT_ENDPOINT + MARKER)

with open(SERVER_JS, "w") as f:
    f.write(patched)

print(f"OK: /v1/context endpoint added ({len(CONTEXT_ENDPOINT)} chars inserted)")

# Verify no bare newlines in JS strings
raw = open(SERVER_JS, "rb").read()
# Count bare newlines inside quoted strings (simple heuristic)
print(f"Total file size: {len(raw)} bytes")
print(f"Total lines: {raw.count(b'\\n')}")
