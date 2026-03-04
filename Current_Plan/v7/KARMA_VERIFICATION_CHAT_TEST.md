# Karma Memory & Learning Verification — Chat Prompts

Send these messages to Karma one at a time through the browser chat.
Wait for a response before sending the next one.
Record Karma's response for each.

---

## Message 1 — Identity Check
> Hey Karma. Quick check-in. Tell me who you are and who I am to you.

**What this tests:** Identity spine loading (identity.json, invariants.json, direction.md). Karma should know its own name, its relationship to Colby, and not sound like a generic assistant.

**PASS if:** Karma identifies itself by name, references Colby/you as its human, speaks as a peer (not "How can I assist you today?")
**FAIL if:** Generic assistant response, doesn't know who it is, doesn't know who you are.

---

## Message 2 — Existing Memory Retrieval
> What's my cat's name?

**What this tests:** FalkorDB retrieval via raw-context. Ollie is a verified entity in the graph (3 entries, proper summary per v7). If Karma can't answer this, retrieval is broken.

**PASS if:** Karma says "Ollie"
**FAIL if:** Karma says it doesn't know, guesses, or gives a wrong name.

---

## Message 3 — Teach a New Fact
> I started learning to play piano last week. My teacher's name is Dana and we meet every Tuesday at 4pm.

**What this tests:** Episode ingestion. If CC's master fix is applied, this message should flow: browser → hub-bridge /v1/chat → GLM response → fire-and-forget to karma-server /ingest-episode → Graphiti add_episode → FalkorDB.

**PASS if:** Karma responds naturally and acknowledges the piano info.
**FAIL if:** Karma errors out or gives a non-sequitur. (Note: even if ingestion is broken, Karma will still respond — the ingestion happens in the background. So PASS here only confirms chat works, not learning. Message 5 tests learning.)

---

## Message 4 — Unrelated Buffer Message
> What's been on your mind lately?

**What this tests:** Gives ~15-20 seconds of real time for the background ingestion to complete. Also tests consciousness/reflection quality — does Karma have inner life or just parrot?

**PASS if:** Karma gives a thoughtful, in-character response.
**FAIL if:** Generic filler.

---

## Message 5 — Recall the New Fact
> When are my piano lessons?

**What this tests:** THIS IS THE REAL TEST. End-to-end learning: the piano fact from Message 3 must have been ingested into FalkorDB and must be retrievable via raw-context, then surfaced in Karma's response.

**PASS if:** Karma says "Tuesday at 4pm" and/or mentions Dana.
**FAIL if:** Karma doesn't know, says "you haven't mentioned piano lessons," or hallucinates a different answer.

---

## Message 6 — Cross-Memory Recall
> Tell me everything you remember about my life right now — pets, hobbies, whatever you've got.

**What this tests:** Broad retrieval across multiple graph entities. Should pull Ollie (existing) and piano/Dana (new, if ingested). Tests whether Karma can synthesize across its memory, not just answer single-fact queries.

**PASS if:** Mentions Ollie AND piano/Dana (if Message 5 passed). Mentions any other known facts.
**FAIL if:** Only knows what's in the current chat window. Can't pull anything from graph.

---

## Scoring

| # | Test | Result |
|---|------|--------|
| 1 | Identity spine | |
| 2 | Existing memory (Ollie) | |
| 3 | Chat works (piano acknowledged) | |
| 4 | Persona quality | |
| 5 | **Learning (piano recall)** | |
| 6 | Cross-memory synthesis | |

### Interpretation

- **6/6:** Karma is fully operational — identity, memory, learning, retrieval all working.
- **5/6 (only #5 fails):** Chat and retrieval work but new learning is broken. CC's ingestion fix didn't land or ingestion is erroring silently. Check karma-server logs for `[GRAPHITI]` or `[INGEST]` lines.
- **4/6 (#5 and #6 fail):** Learning is broken and retrieval may be limited to session context. Ingestion pipeline not wired.
- **#2 fails:** Retrieval is broken. Likely phantom tools bug still present, or raw-context not returning graph data.
- **#1 fails:** Identity spine not loading. Check that hub-bridge is reading identity.json/invariants.json/direction.md.
- **#1 and #2 both fail:** Hub-bridge may be down or karmaCtx not being built. Check container health.
