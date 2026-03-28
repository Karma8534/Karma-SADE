# Phase 7-1 PLAN: sqrt Dampening in FAISS Entity Scoring

## Task 1: Implement dampening in fetchSemanticContext()
**What:** Modify fetchSemanticContext() to over-fetch, extract entity frequencies, apply sqrt dampening, re-rank.
**Verify:** Read modified function, confirm formula applied correctly.
**Done:** Code compiles without syntax errors (node -c check).

## Task 2: Test with live FAISS endpoint
**What:** SSH to vault-neo, curl FAISS with a test query, verify results differ from raw similarity ranking.
**Verify:** Compare raw vs dampened results — high-frequency entities should score lower.
**Done:** At least one previously-dominant entity moved down in ranking.

## Task 3: Deploy and verify end-to-end
**What:** Deploy hub-bridge to vault-neo, test /v1/chat response quality.
**Verify:** Karma response names entities accurately without Colby dominating.
**Done:** Deployed, health check passes, chat test returns diverse context.
