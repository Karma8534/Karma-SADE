# Canonical Data Map — Read This Before Touching Any File

## THE RULE
Before writing ANY new file or plan: check this map first.
If something already exists here → USE IT, don't duplicate.
If something is missing → ADD IT HERE after creating it.

---

## Ground Truth Index (auto-maintained)

### Karma2/ — Structural Ground Truth (P1 local)
```
Karma2/
  PLAN.md                      ← Karma baseline capability plan + active blockers
  karma_contract_policy.md     ← STABLE. SovereignPeer policy. Cache this. Sovereign approval to change.
  karma_contract_execution.md  ← VOLATILE. Inject fresh each session. Contains live state paths.
  map/
    services.md                ← All running services (K2, vault-neo, P1) with status + file paths
    file-structure.md          ← Every important file on K2, vault-neo, P1 with canonical paths
    data-flows.md              ← How data moves between services
    identity-state.md          ← Current identity/spine state
    tools-and-apis.md          ← All tools and API endpoints
    active-issues.md           ← Open blockers and issues
```

### docs/plans/ — Design + Implementation Plans
```
docs/plans/
  YYYY-MM-DD-<topic>-design.md    ← Architecture decisions (brainstorming output)
  YYYY-MM-DD-<topic>-plan.md      ← Implementation tasks (writing-plans output)
```

### docs/ccSessions/ — CC Session Transcripts (for ingestion)
```
docs/ccSessions/
  CCSession032026A.md             ← Session 109 transcript (2026-03-20, this session)
```
Use these as input to the session ingestion pipeline (Task 1 alternative to IndexedDB).
These are Colby's manually saved session exports — ingest before IndexedDB extraction.
**Current active plans:**
- `2026-03-20-session-ingestion-pipeline-design.md` — session pipeline architecture
- `2026-03-20-session-ingestion-pipeline-plan.md` — session pipeline tasks

### .claude/rules/ — Auto-loaded Every Session
```
.claude/rules/
  architecture.md              ← Hub-bridge, karma-server, FalkorDB, data flow
  deployment.md                ← Server ops, Docker, health checks
  data-map.md                  ← THIS FILE — canonical index of where everything lives
```

---

## Canonical File Paths (never guess these)

### P1 (This Machine)
| What | Path |
|------|------|
| This repo | `C:\Users\raest\Documents\Karma_SADE\` |
| Ground truth map | `Karma2/map/` |
| Capability plan | `Karma2/PLAN.md` |
| SovereignPeer policy | `Karma2/karma_contract_policy.md` |
| Execution prompt | `Karma2/karma_contract_execution.md` |
| Skills | `.claude/skills/` |
| API keys | `C:\Users\raest\OneDrive\Documents\Aria1\NFO\mylocks1.txt` |

### vault-neo (SSH: `ssh vault-neo`)
| What | Path |
|------|------|
| Repo root | `/home/neo/karma-sade/` |
| MEMORY.md | `/home/neo/karma-sade/MEMORY.md` |
| CC session brief | `/home/neo/karma-sade/cc-session-brief.md` |
| CC scratchpad | `/home/neo/karma-sade/cc_scratchpad.md` (wait — see note) |
| System prompt live | `/home/neo/karma-sade/Memory/00-karma-system-prompt-live.md` |
| hub-bridge BUILD SOURCE | `/opt/seed-vault/memory_v1/hub_bridge/app/server.js` |
| karma-server BUILD SOURCE | `/opt/seed-vault/memory_v1/karma-core/` |
| Hub auth token | `/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt` |
| Hub compose | `/opt/seed-vault/memory_v1/hub_bridge/compose.hub.yml` |

### K2 (via `ssh vault-neo "ssh -p 2223 -l karma localhost '...'"`)
| What | Path |
|------|------|
| Agent code | `/mnt/c/dev/Karma/k2/aria/` |
| Live cache | `/mnt/c/dev/Karma/k2/cache/` |
| **Spine** | `/mnt/c/dev/Karma/k2/cache/vesper_identity_spine.json` |
| Session state | `/mnt/c/dev/Karma/k2/cache/regent_control/session_state.json` |
| Pipeline status | `/mnt/c/dev/Karma/k2/cache/regent_control/vesper_pipeline_status.json` |
| CC scratchpad | `/mnt/c/dev/Karma/k2/cache/cc_scratchpad.md` |
| Governor audit | `/mnt/c/dev/Karma/k2/cache/vesper_governor_audit.jsonl` |
| Scripts | `/mnt/c/dev/Karma/k2/scripts/` |
| Regent log | `/mnt/c/dev/Karma/k2/cache/regent.log` |

---

## Data Lives Here, Not There

| Data type | CORRECT location | WRONG (don't use) |
|-----------|-----------------|-------------------|
| File structure map | `Karma2/map/file-structure.md` | Session notes, MEMORY.md prose |
| Active services | `Karma2/map/services.md` | Random discovery |
| Capability plan | `Karma2/PLAN.md` | docs/plans/ |
| SovereignPeer policy | `Karma2/karma_contract_policy.md` | CLAUDE.md |
| Identity spine | K2 `vesper_identity_spine.json` | `cc_identity_spine.json` (CC-only, deprecated) |
| Hub build source | vault-neo `/opt/seed-vault/.../hub_bridge/` | git repo directly |
| Session ingestion plan | `docs/plans/2026-03-20-session-ingestion-*` | Karma2/ |

---

## When Something Changes

Update the relevant map file IMMEDIATELY:
- New service → `Karma2/map/services.md`
- New file path → `Karma2/map/file-structure.md`
- New blocker → `Karma2/map/active-issues.md`
- Policy change → `Karma2/karma_contract_policy.md` (Sovereign approval required)
- New plan → `docs/plans/`

Do NOT put structural facts in MEMORY.md prose — that's a log, not a map.
