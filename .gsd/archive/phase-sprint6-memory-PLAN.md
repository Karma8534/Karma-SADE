# Sprint 6: Memory Operating Discipline — Execution Plan

## Task 1: Tier Classification Engine (7-6)
**What:** Add `classify_tier()` function to K2 cortex that upgrades memcube.tier based on heuristics.
**Where:** julian_cortex.py on K2
**Rules:**
- raw → distilled: entry has been recalled 3+ times OR has extracted facts
- distilled → stable: Vesper promoted the pattern OR 10+ recalls
- any → archived: >90 days old AND <2 recalls in last 30 days
**Verify:** `curl K2:7892/health` shows tier_counts with non-zero distilled
<done>tier_counts in /health response shows >0 distilled entries</done>

## Task 2: Gated Recall (7-8)
**What:** Add relevance scoring to /query. Score each candidate block against the query. Drop below threshold (0.3). Return only top-K (15).
**Where:** julian_cortex.py `/query` endpoint
**Current:** Returns all blocks that keyword-match. No scoring.
**Fix:** cosine similarity between query embedding and block embedding (use nomic-embed-text on K2 Ollama). Gate: score < 0.3 → drop. Top-K: 15.
**Verify:** `curl -X POST K2:7892/query -d '{"query":"test"}' | jq .blocks_returned` < blocks_considered
<done>blocks_returned < blocks_considered in /query response</done>

## Task 3: Query-Conditioned Compression (7-7)
**What:** After gated recall, compress selected blocks into a fact bundle. Instead of injecting raw text, produce: distilled facts + confidence + recency + conflict flags.
**Where:** julian_cortex.py, new `compress_for_context()` function
**Format:** "FACT: [statement] (confidence: [H/M/L], age: [Nd], sources: [N])"
**Verify:** /context response contains "FACT:" formatted lines instead of raw block text
<done>/context response has FACT: formatted lines</done>

## Task 4: Local-Window Priority (7-10)
**What:** Formalize context ordering: (1) current conversation, (2) gated+compressed recall, (3) archival only on explicit request.
**Where:** julian_cortex.py `_build_context()` or equivalent
**Verify:** /context response shows conversation first, then facts, with clear section markers
<done>Section markers visible in /context: "CONVERSATION:" then "RECALLED FACTS:"</done>

## Task 5: Interleaved Multi-Source Recall (7-9)
**What:** Recall assembles from multiple categories simultaneously: stable preference + recent checkpoint + project invariant + contradictory update. Not single-source nearest-neighbor.
**Where:** julian_cortex.py /query
**Fix:** Query FAISS + FalkorDB + cortex knowledge blocks in parallel. Merge results by category. Ensure at least 1 result per category if available.
**Verify:** /query response includes results from 2+ sources
<done>/query response shows source diversity (knowledge + conversation + spine)</done>

## Task 6: Migration/Fusion Rules (7-11)
**What:** Define tier promotion rules in Vesper governor. When governor promotes a pattern → update memcube.tier on the source ledger entries.
**Where:** vesper_governor.py on K2
**Rules:** promotion → tier=stable. 3 promotions from same source → tier=stable on source entries.
**Verify:** After next governor cycle, check spine for entries with tier=stable
<done>Vesper spine has entries with memcube.tier=stable</done>

## Task 7: Deploy + Integration Test
**What:** Deploy all changes to K2, run full recall pipeline test.
**Verify:** Send query through hub.arknexus.net → observe gated+compressed recall in response
<done>Karma response at hub.arknexus.net uses compressed facts from Sprint 6 pipeline</done>
