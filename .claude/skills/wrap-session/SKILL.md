---
name: wrap-session
description: Lean session wrap-up. Use when Colby says "wrap up", "end session", or "save and close". Replaces the bloated 10-step protocol with 5 essential + 3 optional steps.
---

# Session Wrap-Up (v2 — Cortex-First)

## MUST DO (5 steps, in order)

### 1. Save observations + dump to cortex

Scan session for uncaptured DECISION/PROOF/PITFALL/DIRECTION/INSIGHT.
Call `save_observation` for each + bus post (dual-write protocol).

Then dump session summary to cortex (direct LAN, not SSH-through-vault-neo):
```bash
curl -sf -X POST http://192.168.0.226:7892/ingest \
  -H "Content-Type: application/json" \
  -d '{"label":"session-end-[TIMESTAMP]","text":"Session [N]: [what was done]. Decisions: [list]. Pitfalls: [list]. Next: [item 2]."}'
```

### 1.5. FORENSIC GATE VERIFICATION (P089 — mandatory before ANY status update)

Before updating MEMORY.md or PLAN.md, run the live endpoint audit.
Previous sessions have written "PASS" without testing. This stops that.

```bash
TOKEN=$(ssh vault-neo 'cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt')
echo "=== WRAP GATE AUDIT ===" && \
curl -sf -o /dev/null -w "/health: %{http_code}\n" https://hub.arknexus.net/health && \
curl -sf -o /dev/null -w "/v1/status: %{http_code}\n" -H "Authorization: Bearer $TOKEN" https://hub.arknexus.net/v1/status && \
curl -sf -o /dev/null -w "/v1/trace: %{http_code}\n" -H "Authorization: Bearer $TOKEN" https://hub.arknexus.net/v1/trace && \
curl -sf -o /dev/null -w "/v1/learnings: %{http_code}\n" -H "Authorization: Bearer $TOKEN" https://hub.arknexus.net/v1/learnings && \
curl -sf -o /dev/null -w "/agora: %{http_code}\n" https://hub.arknexus.net/agora && \
curl -sf -o /dev/null -w "P1:7891/health: %{http_code}\n" http://localhost:7891/health
```

**RULES:**
- Any endpoint returning 404 = OPEN GATE in MEMORY.md "Next Session" — never write "all PASS"
- Any truth table item that wasn't live-tested THIS session = UNVERIFIED, not PASS
- MEMORY.md item 2 MUST list every open gate by number and description
- If a gate was OPEN at resurrect and no code was deployed to fix it this session, it is STILL OPEN
- Sovereign directives about gate status override any CC-generated truth table

**HARD GATE:** MEMORY.md "Next Session Starts Here" item 2 MUST NOT claim completion of gates that returned non-200 in this audit. Writing false completion status is a P089 violation.

### 2. Update MEMORY.md + PLAN.md + pre-create GSD docs

**2a.** Append MEMORY.md session section (bullet points, not paragraphs).

**2b.** Cross-check PLAN.md — mark completed items `✅ DONE [date]`.
**CRITICAL (P059/P060 prevention):** If this session CHANGED which plan is active (new plan supersedes old), PLAN.md MUST be updated to reflect the NEW plan before wrap completes. Archive old plan to `Karma2/PLAN-ARCHIVED-*.md`. Failing to do this caused S151 to follow a dead plan for an entire session.

**2c.** Pre-create GSD docs for next task (MANDATORY):
- Check: does `.gsd/phase-[next-task]-PLAN.md` exist?
- If NO: write it now from PLAN.md spec or directive text.
- Task 1 = the first atomic action the next session will take.

**2d.** Write MEMORY.md "Next Session Starts Here":
```
## Next Session Starts Here
1. /resurrect
2. [task-id] Step 1: [exact first action — verb + file/tool + purpose]
```
Item 2 MUST be ONE specific action. "X OR Y" = protocol violation.

### 3. Update STATE.md
- Session number, timestamp
- Component status (only rows that changed)
- Active blockers (resolve completed, add new)

### 3.5. Run /simplify on session changes

Before committing, run `/simplify` to catch code quality issues:
- Launches 3 parallel review agents (reuse, quality, efficiency)
- Fix critical findings before committing
- Skip if session had zero code changes (docs-only sessions)

### 4. Secret scan + commit + push

```bash
# Secret scan
grep -rn "Bearer\|token\|secret\|password\|api_key" --include="*.js" --include="*.py" --include="*.json" --include="*.md" . | grep -v node_modules | grep -v .git
```

If clean, commit via PowerShell (D003):
```powershell
git add -u; git add MEMORY.md .gsd/STATE.md Karma2/PLAN.md; git commit -m 'chore(wrap): session-N — [summary]'; git push origin main
```

Also stage skill files if modified:
```powershell
git add C:\Users\raest\.claude\skills\resurrect\SKILL.md C:\Users\raest\.claude\skills\wrap-session\SKILL.md
```

Bus post (dual-write):
```bash
ssh vault-neo 'TOKEN=$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt) && python3 -c "
import json, urllib.request, datetime
token = open(\"/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt\").read().strip()
ts = datetime.datetime.utcnow().strftime(\"%Y-%m-%dT%H:%M:%SZ\")
msg = \"SESSION WRAP [CC]: [summary]. Next: [item 2]. \" + ts
payload = json.dumps({\"from\":\"cc\",\"to\":\"all\",\"type\":\"inform\",\"urgency\":\"informational\",\"content\":msg}).encode()
req = urllib.request.Request(\"https://hub.arknexus.net/v1/coordination/post\", data=payload, headers={\"Authorization\":\"Bearer \"+token,\"Content-Type\":\"application/json\"}, method=\"POST\")
with urllib.request.urlopen(req, timeout=10) as r: d=json.loads(r.read()); print(\"bus posted:\", d.get(\"id\",\"\")[:30])
"'
```

### 5. Sync vault-neo + health check
```bash
ssh vault-neo "cd /home/neo/karma-sade && git pull && git log -1 --oneline && docker ps --format '{{.Names}} | {{.Status}}' | grep -E 'karma|hub|vault'"
```
Verify: commit hash matches. All containers "Up".

---

## OPTIONAL (only if relevant)

### 6. Update ROADMAP.md
Only if milestones completed or phases started.

### 7. Update direction.md on vault-neo
Only if architecture changed.

### 8. Problems-log entry
Only if bugs were debugged this session.

---

## DROPPED (from old protocol)
- SSH-through-vault-neo cognitive snapshots → replaced by direct cortex POST
- cc_context_snapshot.md manual write → replaced by cortex state persistence
- cc_regent --integrate trigger → cortex handles context now
- Cache hygiene, mirror sync, quality gap audit → never executed
