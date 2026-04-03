# Sprint 6: Memory Operating Discipline — PLAN

## Tasks (execute in order)

### Task 1: MemCube Schema (7-5)
**What:** Extend ledger entry schema with lifecycle metadata.
**Where:** proxy.js `/v1/ambient` and `/v1/chat` write paths.
**Add fields:** `memcube: {version: 1, tier: "raw", lineage: null, promotion_state: "none", decay_policy: "default", provenance: {session, agent, method}}`
**Backward compat:** Old entries without `memcube` default to `{version: 0, tier: "raw", promotion_state: "none", decay_policy: "default"}`
<verify>
```bash
# Write test entry with MemCube fields
curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"type":"log","content":"MemCube test","tags":["test","memcube"]}' \
  https://hub.arknexus.net/v1/ambient
# Read last entry — must have memcube field
ssh vault-neo "tail -1 /opt/seed-vault/memory_v1/ledger/memory.jsonl | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get(\"memcube\",\"MISSING\"))'"
```
</verify>
<done>Last ledger entry has `memcube.version: 1` and `memcube.tier: "raw"`</done>

### Task 2: Typed Memory Tiers (7-6)
**What:** Add tier classification to entries. Vesper promotion changes tier.
**Where:** vesper_governor.py `_apply_to_spine()` — when promoting, update entry tier.
**Tiers:** raw → distilled → stable → archived
**Rule:** New entries start as "raw". Watchdog extraction → "distilled". Governor promotion → "stable". 90-day no-access → "archived".
<verify>
```bash
# Check governor writes tier field
ssh karma@192.168.0.226 "grep -c 'tier' /mnt/c/dev/Karma/k2/aria/vesper_governor.py"
```
</verify>
<done>Governor promotion writes `memcube.tier: "stable"` to promoted entries</done>

### Task 3: Gated Recall (7-8)
**What:** Add relevance scoring between FAISS retrieval and cortex ingestion.
**Where:** julian_cortex.py `/context` endpoint — after retrieving knowledge blocks, score each against the current query, drop below threshold.
**Gate:** Ollama generates relevance score (0-1) for each block vs query. Top-K (K=10) pass. Below 0.3 = dropped.
**Fallback:** If Ollama scoring fails, pass all blocks (no gate = degraded, not broken).
<verify>
```bash
curl -sf http://192.168.0.226:7892/context | python3 -c "import sys,json; d=json.load(sys.stdin); print('blocks_returned:', len(d.get('context','').split('\\n\\n')))"
```
</verify>
<done>Context returns filtered blocks, count < total knowledge blocks</done>

### Task 4: Query-Conditioned Compression (7-7)
**What:** Before feeding memories to cortex, compress into fact bundles.
**Where:** julian_cortex.py — new `_compress_for_query(query, blocks)` function.
**Method:** Send blocks + query to Ollama with prompt: "Extract only facts relevant to this query. Output: bullet list of facts with confidence and source."
**Output:** Compressed fact bundle (~500 tokens) instead of raw blocks (~5000 tokens).
<verify>
```bash
curl -sf -X POST http://192.168.0.226:7892/query -H "Content-Type: application/json" \
  -d '{"query":"what is the current architecture?"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print('response_len:', len(d.get('response','')))"
```
</verify>
<done>Query response uses compressed fact bundle, response references facts with confidence</done>

### Task 5: Interleaved Multi-Source Recall (7-9)
**What:** Retrieve from multiple memory categories simultaneously.
**Where:** julian_cortex.py `/context` — assemble from: stable patterns + recent session + project invariants + contradictions.
**Method:** Tag knowledge blocks with categories. /context pulls top-K from EACH category, interleaves.
**Categories:** stable_preference, session_checkpoint, project_invariant, contradiction, general.
<verify>
```bash
curl -sf http://192.168.0.226:7892/context | python3 -c "import sys,json; d=json.load(sys.stdin); c=d.get('context',''); cats=set(); [cats.add(l.split(']')[0][1:]) for l in c.split('\\n') if l.startswith('[')]; print('categories:', cats)"
```
</verify>
<done>Context contains blocks from 3+ categories</done>

### Task 6: Local-Window Priority (7-10)
**What:** Cortex prioritizes: (1) current turn, (2) recent persistent, (3) archival on demand.
**Where:** julian_cortex.py — reorder context assembly: conversation tail first, then recent knowledge, then old.
**Method:** Sort knowledge blocks by recency. Last 5 conversation pairs always included. Knowledge blocks sorted by ingestion time, most recent first. Archival blocks only included if explicitly requested.
<verify>
```bash
curl -sf http://192.168.0.226:7892/context | python3 -c "import sys,json; d=json.load(sys.stdin); c=d.get('context',''); lines=c.split('\\n'); print('first_section:', lines[0][:80] if lines else 'EMPTY')"
```
</verify>
<done>Context starts with most recent conversation/session data, not oldest knowledge</done>

### Task 7: Memory Migration/Fusion (7-11)
**What:** Define promotion rules in Vesper pipeline.
**Where:** vesper_watchdog.py `extract_candidates()` — add new candidate types for migration.
**Rules:**
- raw event → extracted fact (watchdog sees pattern 3+ times)
- repeated fact → stable preference (governor sees 5+ episodes)
- repeated workflow → policy/invariant (governor sees 10+ episodes)
- clustered old sessions → checkpoint summary (daily cron)
- conflicts → explicit conflict set (watchdog detects contradiction)
<verify>
```bash
ssh karma@192.168.0.226 "grep -c 'migration\|fusion\|MIGRATION\|FUSION' /mnt/c/dev/Karma/k2/aria/vesper_watchdog.py"
```
</verify>
<done>Watchdog has migration candidate types, governor handles tier promotion</done>
