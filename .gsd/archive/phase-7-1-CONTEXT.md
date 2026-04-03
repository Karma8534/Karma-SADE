# Phase 7-1 CONTEXT: sqrt Dampening in FAISS Entity Scoring

## Problem
FAISS returns results ranked purely by cosine similarity. High-frequency entities (e.g., "Colby" appears in most ledger entries) dominate every query result, reducing diversity and usefulness.

## Solution
Apply sqrt dampening to FAISS results in `fetchSemanticContext()` (hub-bridge/app/server.js, lines 893-920):
1. Request more results from FAISS than needed (topK * 3)
2. Extract entity/token frequency from content previews across the batch
3. Apply dampened rescoring: `effective_score = similarity * (1 / sqrt(entity_freq))`
4. Re-rank by dampened score, take top-K
5. Display dampened score in context output

## Design Decisions
- **Hub-bridge only** — no FAISS service or karma-server changes needed
- **Token extraction** — simple word extraction from content_preview, not NER. Common words (stopwords) excluded.
- **Dampening formula** — Aider pattern: `1 / sqrt(frequency)` applied as multiplier to similarity score
- **Over-fetch ratio** — 3x topK to give enough candidates for re-ranking
- **NOT doing:** changing FAISS service, modifying karma-server context assembly, building entity extraction pipeline

## Acceptance Criteria
- FAISS results show dampened diversity — "Colby" doesn't dominate every result
- No regression in FAISS response time (< 4s timeout maintained)
- buildSystemText() receives dampened results transparently
