# Nexux2 Proposal — MemPalace Forensic Extraction
Generated: 2026-04-07
Source: C:\Users\raest\Documents\Karma_SADE\docs\wip\leaks\mempalace-main\mempalace-main
Files processed: 48 discovered / 30 source-relevant completed (binaries, CI, templates skipped)

---

## Primitives Extraction Report

**Source:** mempalace-main (v3.0.0, Python, MIT, ~3500 LOC core)
**Extracted:** 18 primitives (7 HIGH, 6 MEDIUM, 5 LOW)

---

### TIER 1: Adopt Now (HIGH priority)

| # | Pattern | Effort | What It Does |
|---|---------|--------|-------------|
| 1 | 4-Layer Memory Stack | SMALL | Tiered context loading: L0 identity (~50 tok) + L1 essential story (~500 tok) always loaded; L2 on-demand wing/room retrieval; L3 deep semantic search. Wake-up cost: ~170 tokens. |
| 2 | AAAK Compression Dialect | MEDIUM | Lossless symbolic shorthand for memory entries — 30x compression, readable by any LLM without decoder. Entity codes (3-letter uppercase), emotion codes, flag codes (DECISION, ORIGIN, CORE, PIVOT, TECHNICAL), pipe-separated fields. |
| 3 | Palace Structure (Wing/Room/Hall/Tunnel) | MEDIUM | Hierarchical memory organization: Wings = domains (people/projects), Rooms = specific topics, Halls = memory types (facts/events/discoveries/preferences/advice), Tunnels = cross-wing connections for same room name. +34% retrieval improvement over flat search. |
| 4 | Temporal Knowledge Graph (SQLite) | SMALL | Entity-relationship triples with `valid_from`/`valid_to` temporal windows. Invalidation API marks facts as ended without deletion. Timeline queries. Replaces Neo4j/FalkorDB for local use. Tables: `entities` (id, name, type, properties), `triples` (subject, predicate, object, valid_from, valid_to, confidence, source_closet). |
| 5 | PreCompact Hook | TRIVIAL | CC hook fires before context window compaction. ALWAYS blocks. Forces emergency save of all topics/decisions/quotes/code before context is lost. Direct Karma analog: pre-compaction spine flush. |
| 6 | Periodic Save Hook (Stop hook) | TRIVIAL | CC Stop hook counts human messages via JSONL transcript. Every N messages (default 15), blocks AI stop and injects save instruction as system message. `stop_hook_active` flag prevents infinite loop. Direct Karma analog: periodic mid-session PROMOTE. |
| 7 | General Extractor (5-type classifier) | SMALL | Pure regex/keyword classifier for conversation text into 5 memory types: DECISIONS, PREFERENCES, MILESTONES, PROBLEMS, EMOTIONAL. No LLM required. Includes sentiment disambiguation (resolved problems → milestones) and code-line filtering. |

#### Details

**1. 4-Layer Memory Stack** (`layers.py`)
- `Layer0`: Reads `~/.mempalace/identity.txt` — plain text, user-written, ~100 tokens. **Maps to:** Karma's `00-karma-system-prompt-live.md` identity block.
- `Layer1`: Auto-generated from highest-weight/most-recent ChromaDB drawers. Groups by room, picks top 15 moments, caps at 3200 chars (~800 tokens). Importance scoring via `importance`/`emotional_weight`/`weight` metadata keys. **Maps to:** Karma's `buildSystemText()` memoryMd injection (tail 3000 chars).
- `Layer2`: On-demand retrieval filtered by wing/room. Returns 200-500 tokens per query. **Maps to:** Karma's `karmaCtx` from FalkorDB.
- `Layer3`: Full semantic search via ChromaDB `query()`. Returns similarity scores (1-distance). **Maps to:** Karma's `semanticCtx` from anr-vault-search FAISS.
- `MemoryStack` class unifies all 4 layers. `wake_up(wing=)` returns L0+L1. `recall(wing=, room=)` returns L2. `search(query, wing=, room=)` returns L3. **Maps to:** The exact layered context assembly Karma needs but doesn't have as a clean abstraction.

**Adoption path:** Refactor `buildSystemText()` to explicitly implement L0-L3 with the MemoryStack pattern. L0=identityBlock, L1=memoryMdCache+recurringTopics, L2=karmaCtx, L3=semanticCtx. This names what we already do and makes the token budget per layer explicit.

**2. AAAK Compression Dialect** (`dialect.py`)
- `Dialect` class with `compress(text, metadata)` → AAAK string.
- Auto-detects: entities in text (known or capitalized words), topics (frequency-ranked non-stopwords), key sentences (scored by decision-words + length), emotions (keyword signals), flags (DECISION/ORIGIN/CORE/PIVOT/TECHNICAL).
- Format: `header|content` where content = `ZID:ENTITIES|topics|"key_quote"|emotions|flags`
- `compress_all(dir)` → single `.aaak` file from all zettels.
- `generate_layer1(dir)` → auto-generates wake-up file from high-weight entries.
- `decode(dialect_text)` → dict for programmatic reading.
- `compression_stats()` → ratio calculation.
- Token estimation: `len(text) // 3` for structured text.

**Adoption path:** Build a `compress_observation()` function that takes a claude-mem observation and returns an AAAK-compressed version for the cortex working memory. This would let K2's 32K context window hold 30x more memory spine data. The entity-code registry (3-letter codes for known entities) maps directly to Karma's people_map concept.

**3. Palace Structure** (`palace_graph.py`, `mcp_server.py`)
- `build_graph(col)` → nodes (rooms with wings/halls/counts) + edges (tunnels = rooms spanning 2+ wings).
- `traverse(start_room, max_hops=2)` → BFS graph walk from a room, finds connected rooms through shared wings. Returns path with hop distance.
- `find_tunnels(wing_a, wing_b)` → rooms bridging two wings.
- Hall types: `hall_facts`, `hall_events`, `hall_discoveries`, `hall_preferences`, `hall_advice`.
- Metadata fields per drawer: `wing`, `room`, `hall`, `source_file`, `chunk_index`, `added_by`, `filed_at`, `date`, `type`, `ingest_mode`, `extract_mode`.

**Adoption path:** Map to Karma's existing FalkorDB structure. Wings = Entity nodes. Rooms = Episodic node clusters. Halls = edge types (currently only MENTIONS). Tunnels = cross-entity co-occurrence (what we already compute with MENTIONS co-occurrence cross-join). The naming vocabulary is better than ours. Adopt the 5 hall types as relationship sub-types on MENTIONS edges.

**4. Temporal Knowledge Graph** (`knowledge_graph.py`)
- `KnowledgeGraph` class backed by SQLite. Schema: `entities` table + `triples` table.
- `add_triple(subject, predicate, object, valid_from, valid_to, confidence, source_closet)` — auto-creates entities, dedup checks for existing valid triples.
- `invalidate(subject, predicate, object, ended)` — sets `valid_to` on open triples. Historical queries still return them.
- `query_entity(name, as_of, direction)` — outgoing/incoming/both with temporal filtering.
- `query_relationship(predicate, as_of)` — all triples of a relationship type.
- `timeline(entity)` — chronological ordered facts.
- `seed_from_entity_facts(dict)` — bootstrap from known ground truth.
- Triple ID format: `t_{sub_id}_{pred}_{obj_id}_{hash8}`

**Adoption path:** This is what we need for Karma's fact layer. FalkorDB stores episodes and entities but has no clean fact-validity API. The `invalidate()` pattern solves the stale-fact problem Karma has (e.g., "Kai works on Orion" stays forever even after Kai left). Could be added as a SQLite sidecar to karma-server, or as validity columns on FalkorDB Entity nodes.

**5-6. Hooks** (`hooks/`)
- Save hook: Counts `role=user` messages in JSONL transcript, skipping `<command-message>` system messages. Tracks `$STATE_DIR/${SESSION_ID}_last_save` watermark. When `SINCE_LAST >= SAVE_INTERVAL`, returns `{"decision": "block", "reason": "AUTO-SAVE checkpoint..."}`. Next Stop fires with `stop_hook_active=true` → passes through. **Exactly the pattern** Karma needs for mid-session PROMOTE.
- PreCompact hook: Always blocks. Returns save instruction as system message before context compression. **We have nothing like this** — our compaction loses everything not in MEMORY.md.

**Adoption path:** TRIVIAL. Port the exact hook pattern. Save hook → `hooks/mid-session-promote.sh` that fires every 15 messages and promotes to MEMORY.md + claude-mem. PreCompact hook → `hooks/pre-compact-flush.sh` that forces full state dump before window shrinks.

**7. General Extractor** (`general_extractor.py`)
- 5 marker sets: `DECISION_MARKERS` (20 regexes), `PREFERENCE_MARKERS` (15), `MILESTONE_MARKERS` (30), `PROBLEM_MARKERS` (17), `EMOTION_MARKERS` (20).
- `extract_memories(text, min_confidence=0.3)` → list of `{"content", "memory_type", "chunk_index"}`.
- Splits text by speaker turns (if `>` markers or `Human:`/`Assistant:` detected) or paragraphs.
- Scoring: regex match count per type, length bonus (>500 chars = +2, >200 = +1).
- Disambiguation: resolved problems (has fix + positive sentiment) → reclassified as milestone.
- Code line filtering: strips shell commands, imports, braces, low-alpha-ratio lines before scoring.

**Adoption path:** Use to auto-classify consciousness.jsonl entries and cc-session-brief.md content. Instead of treating all session observations as flat text, classify into DECISION/PREFERENCE/MILESTONE/PROBLEM/EMOTIONAL. This feeds directly into the AAAK flags and the 5 hall types. The regex marker sets are a goldmine — port them as-is.

---

### TIER 2: Consider (MEDIUM priority)

| # | Pattern | Effort | What It Does |
|---|---------|--------|-------------|
| 8 | Specialist Agent Diaries | SMALL | Each agent gets its own wing + diary room in the palace. Entries written in AAAK. `diary_write(agent_name, entry, topic)` / `diary_read(agent_name, last_n)`. Agents build expertise by reading their own history. |
| 9 | Entity Detector (NER without LLM) | MEDIUM | Two-pass: extract capitalized proper noun candidates (freq>=3), then score person-vs-project using verb patterns, dialogue markers, pronoun proximity, and versioned/code-ref signals. 15 person verb patterns, 15 project verb patterns, 4 dialogue patterns. |
| 10 | Entity Registry with Disambiguation | MEDIUM | Persistent JSON registry at `~/.mempalace/entity_registry.json`. Knows people vs projects vs ambiguous words. Context-based disambiguation for words that are both names and common English (e.g., "Max", "Grace"). Wikipedia fallback for unknown capitalized words. |
| 11 | Conversation Normalizer (5 formats) | SMALL | `normalize(filepath)` converts Claude.ai JSON, ChatGPT `conversations.json` (mapping tree walker), Claude Code JSONL, Slack JSON, and plain text to unified `> user\nassistant` transcript format. |
| 12 | Duplicate Detection Before Filing | TRIVIAL | `tool_check_duplicate(content, threshold=0.9)` → queries ChromaDB for similar content, returns `is_duplicate` bool + matches. Called automatically before `tool_add_drawer`. Prevents duplicate observations. |
| 13 | Contradiction Detection Protocol | SMALL | Memory protocol: before responding about any person/project/past event, query KG first. Cross-check attribution (who did what), temporal facts (ages, tenures, dates), and stale data. Surface conflicts as warnings. |

---

### TIER 3: Note for Later (LOW priority)

| # | Pattern | Effort | What It Does |
|---|---------|--------|-------------|
| 14 | Graph Traversal / Tunnel Finding | SMALL | BFS walk through room graph with hop distance. `find_tunnels(wing_a, wing_b)` finds cross-domain topic bridges. Fuzzy room matching for typos. |
| 15 | Room Detection (keyword scoring) | TRIVIAL | Routes files to rooms by: folder path match → filename match → content keyword score → fallback "general". Topic keyword sets for technical/architecture/planning/decisions/problems. |
| 16 | Chunking Strategy (exchange pairs) | TRIVIAL | Conversations chunked as user+assistant pairs (not arbitrary token windows). Paragraph fallback for non-conversation text. 800-char chunks with 100-char overlap for project files. |
| 17 | MCP Server (19 tools, JSONRPC) | SMALL | Native JSONRPC MCP server with read tools (status, list, search, taxonomy, traverse, tunnels, graph_stats, aaak_spec, check_duplicate), write tools (add_drawer, delete_drawer), KG tools (query, add, invalidate, timeline, stats), diary tools (write, read). |
| 18 | Wake-up Command | TRIVIAL | `mempalace wake-up` → dumps L0+L1 to stdout for pasting into local model system prompt. Wing-specific variant for project-focused sessions. |

---

### Conflicts with Karma Doctrine

1. **ChromaDB dependency** — MemPalace uses ChromaDB for vector search. Karma uses FAISS via anr-vault-search. No conflict — both are local-only, zero-API vector stores. ChromaDB has a richer metadata filter API (`$and`, `where` clauses) that FAISS lacks. Consider whether switching anr-vault-search to ChromaDB would give us the wing/room filter capability for free.

2. **No conflict with zero-API goal** — MemPalace's core (96.6% LongMemEval) requires zero API calls. The 100% hybrid mode uses optional Haiku rerank. This aligns perfectly with Karma's zero-external-API-dependence north star.

3. **SQLite vs FalkorDB** — MemPalace's temporal KG uses SQLite. Karma already has FalkorDB. No need to replace — but the temporal validity pattern (valid_from/valid_to) should be ported to FalkorDB Entity/Episodic nodes.

---

## Cross-File Relationships

| Concept | Files | Relationship |
|---------|-------|-------------|
| Wing/Room metadata | config.py, miner.py, convo_miner.py, searcher.py, palace_graph.py, mcp_server.py, layers.py | All read/write `wing`/`room` metadata on ChromaDB drawers |
| Entity codes | dialect.py, entity_registry.py, entity_detector.py, onboarding.py | 3-letter uppercase codes flow from onboarding → registry → dialect → AAAK output |
| Memory classification | general_extractor.py, convo_miner.py, dialect.py | 5 memory types (decision/preference/milestone/problem/emotional) → room names → AAAK flags |
| Temporal validity | knowledge_graph.py, mcp_server.py | KG triples have valid_from/valid_to; MCP exposes invalidate + as_of queries |
| Hook → Save → Palace | hooks/mempal_save_hook.sh, hooks/mempal_precompact_hook.sh, mcp_server.py | Hooks trigger save; AI calls MCP tools to file memories |
| L0-L3 stack | layers.py, mcp_server.py, searcher.py | MemoryStack wraps searcher.py; MCP status returns protocol + AAAK spec on first wake-up |

---

## Incorporation Recommendations (nexus.md mapping)

| # | Primitive | Nexus Component | Recommendation | Priority |
|---|-----------|----------------|----------------|----------|
| 1 | 4-Layer Memory Stack | buildSystemText() / cortex hydration | Name the existing layers explicitly. L0=identity prompt, L1=MEMORY.md tail + recurring topics, L2=karmaCtx (FalkorDB), L3=semanticCtx (FAISS). Add token budgets per layer. | HIGH |
| 2 | AAAK Compression | K2 cortex working memory | Build `compress_for_cortex()` that compresses spine data into AAAK before injecting into K2's 32K window. 30x compression means 32K holds ~960K worth of memory data. | HIGH |
| 3 | Palace Structure naming | FalkorDB neo_workspace ontology | Adopt wing/room/hall/tunnel vocabulary in documentation and karmaCtx section headers. Map halls to relationship sub-types. | MEDIUM |
| 4 | Temporal validity on facts | FalkorDB Entity nodes / new SQLite sidecar | Add `valid_from`/`valid_to` properties to Entity nodes. Implement `invalidate()` pattern. This solves stale-fact accumulation. | HIGH |
| 5 | PreCompact hook | .claude/hooks/ | Port directly. Fire before context compaction. Flush all in-context state to MEMORY.md + claude-mem. TRIVIAL — copy the shell script, adapt paths. | HIGH |
| 6 | Periodic save hook | .claude/hooks/ | Port directly. Count human messages, promote every 15. Replaces manual "PROMOTE after significant change" rule with automated enforcement. | HIGH |
| 7 | General Extractor | consciousness loop / session ingestion | Use the 5-type classifier on session transcripts and consciousness.jsonl entries. Auto-tag as DECISION/MILESTONE/etc. Feed tags into FalkorDB Episodic node metadata. | HIGH |
| 8 | Agent Diaries | Vesper pipeline / Kiki | Each agent (CC, Kiki, Codex, Karma) gets a diary wing. Written in AAAK. Read at session start for agent-specific continuity. | MEDIUM |
| 9 | Entity Detector | batch_ingest.py / ledger processing | Use person-vs-project NER patterns to auto-classify entities during batch ingest, reducing Graphiti entity dedup overhead. | MEDIUM |
| 10 | Entity Registry | K2 cache / onboarding | Persistent entity registry for Karma's known people/projects. Feeds AAAK entity codes and prevents name confusion. | MEDIUM |
| 11 | Conversation Normalizer | session ingestion pipeline | Use the 5-format normalizer for ingesting CC session transcripts, ChatGPT exports, and Slack exports into the ledger. | MEDIUM |
| 12 | Duplicate Detection | /v1/ambient, /v1/ingest | Before appending to ledger, check semantic similarity against recent entries. Prevents duplicate observations (a known problem with dual-write to claude-mem + MEMORY.md). | MEDIUM |
| 13 | Contradiction Detection | Karma chat pipeline | Before Karma asserts facts about people/projects, query KG. Surface conflicts. Prevents Karma from confidently stating stale or wrong facts. | MEDIUM |

---

## Completion Verification
- [x] All folders from the manifest were visited
- [x] All readable files have Raw Findings (incorporated into primitives above)
- [x] Binary/image file skipped with reason (mempalace_logo.png — PNG image)
- [x] Cross-file relationships generated
- [x] Incorporation recommendations generated with nexus.md mapping
- [x] Output file written successfully
