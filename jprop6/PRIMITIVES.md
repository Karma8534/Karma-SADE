# PRIMITIVES

Scope: primitives extracted from `nexus.md`, `STATE.md`, and Inbox corpus files.

## A) Primitives from nexus.md

| Primitive | Source | What It Does | Decision | Why | jprop6 Strengthening | Replaces/Corrects |
|---|---|---|---|---|---|---|
| Binary gate discipline | `nexus.md:110`, `nexus.md:501-505` | Forces PASS/FAIL closure | Accepted | Foundation-critical | Became hard gates in `EXECUTION_GATES.md` | Replaces fuzzy “partial done” closure |
| “Claim != proof” rule | `nexus.md:102`, `nexus.md:466` | Requires evidence for status claims | Accepted | Core truth substrate | Became PROOF command log requirements | Corrects doc-driven confidence inflation |
| Session continuity as baseline | `nexus.md:905`, `nexus.md:911` | Makes continuity non-optional | Accepted | Foundation requirement | Phase 1 objective lock | Replaces feature-first sequencing |
| Internal-only orchestrator framing | `nexus.md:49` | Prevents architecture model confusion | Accepted (modified) | Useful but often over-applied | Constrained to internal pattern only | Corrects product-level “orchestrator as proof” misuse |
| Anti-drift rails | `nexus.md:463+` | Prevents phase drift | Accepted | Useful guardrail source | Incorporated into break tests | Corrects open-ended roadmap expansion |
| “Merged workspace already exists” | `nexus.md:45`, `nexus.md:902` | Asserts completed merged surface | Modified | Partially true, over-claimed | Treated as hypothesis requiring parity proof | Corrects overclaim of completion |
| Preclaw baseline achieved claim | `nexus.md:575-577` | Declares baseline closure | Rejected as truth claim | Contradicted by blocker residue | Converted to audited claim in forensic ledger | Corrects fake-complete posture |
| MemPalace temporal validity | `nexus.md:198`, `nexus.md:258` | Adds valid_from/valid_to fact control | Accepted (deferred) | Valuable but not phase-0 | Parked in futurework with prerequisite gates | Corrects premature ontology expansion |
| Specialist agent diaries | `nexus.md:277` | Agent-specific continuity diaries | Rejected for foundation stage | Adds complexity before substrate closure | Deferred beyond foundation | Corrects premature multi-agent expansion |
| Contradiction detection protocol | `nexus.md:278` | Cross-check claims before response | Accepted (modified) | Useful when backed by truth rails | Added to Phase 0/Phase 1 guardrails | Corrects unverified assertion flow |

## B) Primitives from STATE.md

| Primitive | Source | What It Does | Decision | Why | jprop6 Strengthening | Replaces/Corrects |
|---|---|---|---|---|---|---|
| Rich blocker history | `STATE.md:107+`, `STATE.md:616+` | Captures unresolved/trended blockers | Accepted | High value for sequencing realism | Used in contradiction and break scenarios | Corrects “all done” framing |
| Root-cause snapshots | `STATE.md:514` | Documents known failure causes | Accepted | Concrete failure evidence | Seeded break tests and regression guards | Corrects repeated rediscovery loops |
| Watcher chaos admission | `STATE.md:116` | Explicit watcher failure event | Accepted | Critical to governance redesign | Drove watcher demotion decision | Corrects watcher authority assumptions |
| Continuity regression statement | `STATE.md:578` | Declares continuity failure impact | Accepted | Foundation-critical | Became Phase 1 non-negotiable | Corrects feature expansion before continuity |
| Massive ✅ status table | `STATE.md:17-103` | Broad completion claims | Modified | Useful inventory, not proof | Recast as “proof-missing until verified” | Corrects status-table trust bias |
| Session-tagged resolution claims | many Session X rows | Historical evidence fragments | Accepted (with downgrade) | Useful chronology but stale risk | Tagged as potentially stale unless re-probed | Corrects stale recency assumption |
| “All tasks done” framing | `STATE.md:8` | Declares complete closure | Rejected as proof | Contradicted by runtime probe and blockers | Logged as contradicted claim | Corrects phase advancement inflation |

## C) Primitives from Inbox PDFs

Source files audited:
1. `Karma_PDFs/Inbox/ccManagedAgents.PDF`
2. `Karma_PDFs/Inbox/oAOHarnessEng.PDF`
3. `Karma_PDFs/Inbox/ccManagedAgents.PDF.error.txt`
4. `Karma_PDFs/Inbox/oAOHarnessEng.PDF.error.txt`

### C1) `ccManagedAgents.PDF`

| Primitive | Source Page(s) | What It Does | Decision | Why | jprop6 Strengthening | Replaces/Corrects |
|---|---|---|---|---|---|---|
| Explicit agent/runtime split | pp.3-6 | Separates logic from runtime loop ownership | Accepted (modified) | Matches foundation need | Used as harness honesty boundary | Corrects “one giant plan does all” |
| Session object + resume ID | pp.7-14 | Formal session continuity handle | Accepted | Directly relevant | Implemented as session envelope seam | Corrects implicit continuity assumptions |
| Max turns / budget caps | pp.12-13 | Prevents runaway loops | Accepted (deferred) | Useful after continuity rail | Added as future gated expansion | Corrects unbounded loop behavior |
| Permission modes | p.13 | Explicit action gating | Accepted (deferred) | Valid foundation extension | Added to futurework prerequisites | Corrects implicit trust in tool execution |
| Context compaction behavior | pp.11-12 | Maintains session continuity under growth | Accepted (deferred) | Important but not phase-0 | Deferred until continuity substrate proven | Corrects memory-window handwaving |
| Mid-session steering events | p.14 | Allows correction without restart | Accepted (deferred) | Useful post-contract | Added to expansion rail | Corrects rigid linear session model |

### C2) `oAOHarnessEng.PDF`

| Primitive | Source Page(s) | What It Does | Decision | Why | jprop6 Strengthening | Replaces/Corrects |
|---|---|---|---|---|---|---|
| Repository-as-truth concept | pp.9-10, 45 | Forces legible source of truth for agents | Accepted | Directly aligns with thesis | Adopted in Phase 0 truth substrate | Corrects prose-as-proof drift |
| Mechanical architecture enforcement | pp.31-36 | Encodes boundaries as checks | Accepted | Strong anti-drift primitive | Incorporated into phase break tests | Corrects architecture drift |
| Agent-readable remediation feedback | pp.33-35 | Turns gate failures into actionable fixes | Accepted | Improves recursive hardening | Added to break/fix loop rules | Corrects vague failure reporting |
| Isolated execution environments | pp.28-29, 48 | Prevents cross-task interference | Accepted (deferred) | Valuable later; high complexity now | Deferred with explicit gate prerequisites | Corrects premature multi-agent concurrency |
| Throughput merge philosophy | pp.38-41 | Minimal blocking merge strategy | Rejected for foundation stage | Conflicts with early strict proof hardening | Not used in foundation | Corrects speed-over-proof risk |
| Harness engineer role shift | pp.7-12, 43 | Focus shifts from typing code to constraints/proof | Accepted | Fits this forensic reset | Anchors execution posture | Corrects implementation-by-claim behavior |

### C3) Inbox `.error.txt` files

| Primitive | Source | What It Does | Decision | Why | jprop6 Strengthening | Replaces/Corrects |
|---|---|---|---|---|---|---|
| Ingestion transport failure visibility | `*.PDF.error.txt` | Shows prior conversion path failed with transport disconnect | Accepted | Practical reliability signal | Added explicit ingestion failure handling in proof scope | Corrects “PDF processed” assumption |

## Exhaustiveness Notes
1. Candidate extraction across PDFs captured in `artifacts/pdf_primitive_candidates.tsv`.
2. Raw page extracts captured in `artifacts/pdf_extracts/*.txt`.
3. Every retained primitive above is mapped to a `jprop6` phase and gate in `jprop6.md`.
