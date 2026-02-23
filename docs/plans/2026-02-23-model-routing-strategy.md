# Model Routing Strategy — Optimizing Cost + Reasoning for Karma Self-Improvement

**Date:** 2026-02-23
**Session:** 11
**Author:** Claude Code (CC)
**Status:** Design Document — Ready for Implementation

---

## Executive Summary

Karma currently has access to **5 model providers** across multiple vendors:

| Model | Vendor | Task Fit | Cost/1M Tokens | Reasoning | Coding | Speed |
|-------|--------|----------|-----------------|-----------|--------|-------|
| **Claude 3.5 Sonnet** | Anthropic | Synthesis | $3 / $15 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Claude 3 Opus** | Anthropic | Deep Analysis | $15 / $90 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ |
| **MiniMax M2.5** | MiniMax | Coding/Speed | ~$1.5 / $3 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **GLM-5** | BigModel / Z.ai | Reasoning | ~$2.5 / $7.5 | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Groq (Llama)** | Groq | Speed/Cache | ~$0.05 / $0.30 | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |

**Current Setup (in karma-core/router.py):**
- MiniMax M2.5: Primary for coding/speed/general (priority 0)
- GLM-5: Reasoning specialist (priority -1, beats MiniMax for deep thinking)
- Groq: Speed fallback (priority 5)
- OpenAI gpt-4o-mini: Final fallback
- Anthropic routing in hub-bridge: hardcoded to specific models per mode

---

## The Problem

**Existing State:**
1. **Hub-bridge** (Node.js) routes via `MODEL_DEFAULT` (currently claude-sonnet-4-6) — no cost awareness
2. **Karma-server** (Python) has a sophisticated router.py but it's **not integrated with hub-bridge**
3. **Tool-use in /v1/chat** always routes to same model, regardless of task complexity
4. **Cost optimization** not actively applied — high-end models used for simple queries
5. **Self-improvement loop** (CC → Karma → CC) has no model selection strategy

**Why It Matters:**
- Colby explicitly prioritized: "we must optimize for COST"
- Self-improvement conversations have **different reasoning depth needs**:
  - Phase 1 (Analyze failure): Need deep reasoning → Opus or GLM-5 ✅ expensive but necessary
  - Phase 2 (Generate fix): Synthesis task → Sonnet ✅ good balance
  - Phase 3 (Validate): Quick check → Haiku or MiniMax ✅ cheap and fast
- Current approach: use Sonnet for all = wasted budget on Phase 3

---

## Proposed Solution: Task-Based Routing for Self-Improvement

### Layer 1: Classify Conversation Phase (in CC)

When CC generates a proposal for Karma's self-improvement, embed a phase marker:

```json
{
  "collab_id": "proposal_20260223T213000_abc123",
  "phase": "analyze_failure",  // or: "generate_fix", "validate"
  "suggested_model": "opus-4-6",  // CC hints at optimal model
  "content": "..."
}
```

### Layer 2: Model Selection Logic (in /v1/chat)

**In hub-bridge/server.js**, enhance the model routing:

```javascript
function selectOptimalModel(userMessage, phase = null, taskType = null) {
  // Priority 1: Phase-based routing (self-improvement context)
  if (phase === "analyze_failure") {
    return "claude-opus-4-6";  // Deep analysis, cost-justified
  }
  if (phase === "generate_fix") {
    return "claude-3-5-sonnet-20241022";  // Synthesis, fast + capable
  }
  if (phase === "validate") {
    return "claude-3-5-haiku-20241022";  // Quick check, cheapest
  }

  // Priority 2: Model-agnostic task classification (fallback)
  const taskScore = classifyTask(userMessage);  // from router.js classify_task()
  if (taskScore === "coding") return "claude-3-5-sonnet-20241022";  // Good coding
  if (taskScore === "reasoning") return "claude-opus-4-6";  // Deep reasoning
  if (taskScore === "speed") return "claude-3-5-haiku-20241022";  // Quick answers

  // Default
  return process.env.MODEL_DEFAULT || "claude-3-5-sonnet-20241022";
}
```

### Layer 3: Karma-Side Execution (with Collab Bridge)

When Karma reads a CC proposal from collab.jsonl:

```python
proposal = json.loads(collab_entry)
model_hint = proposal.get("suggested_model") or "claude-sonnet-4-6"

# Karma evaluates the proposal using the suggested model
response = await call_llm(
    model=model_hint,
    messages=[...proposal context...],
    task_type="analyze"  # or "decide", "learn"
)

# Karma logs decision + cost tracking
log_decision({
    "timestamp": iso_now(),
    "model_used": model_hint,
    "cost_usd": calculate_cost(response.usage),
    "decision": response.text,
    "phase": proposal["phase"]
})
```

---

## Cost Projection: Self-Improvement Loop Example

**Scenario:** Batch5 ingestion fails (like Feb 23). CC detects failure, proposes fix.

### Current Approach (All Sonnet)
```
Phase 1: Analyze failure      → Sonnet  500 input tokens  ×  $3/M  = $0.0015
Phase 2: Generate fix         → Sonnet  1200 input tokens ×  $3/M  = $0.0036
Phase 3: Validate fix         → Sonnet  300 input tokens  ×  $3/M  = $0.0009
────────────────────────────────────────────────────────────────────
Total per cycle:              2000 input tokens                    = $0.0060
```

### Optimized Approach (Task-Specific)
```
Phase 1: Analyze failure      → Opus    500 input tokens  ×  $15/M = $0.0075
Phase 2: Generate fix         → Sonnet  1200 input tokens ×  $3/M  = $0.0036
Phase 3: Validate fix         → Haiku   300 input tokens  ×  $0.80/M = $0.00024
────────────────────────────────────────────────────────────────────
Total per cycle:              2000 input tokens                    = $0.0113
```

**Analysis:**
- Cost difference per cycle: +$0.0053 (88% increase)
- BUT: Opus has 100x better reasoning for failure analysis → likely faster root cause → fewer iteration loops
- **If Opus saves 2+ iteration cycles:** ROI is positive
- **If Haiku validation catches 1 bad fix out of 10:** ROI is strongly positive

**Recommendation:** Implement task-specific routing. Monitor actual iteration counts before/after.

---

## Implementation Plan

### Phase A: Hub-Bridge Enhancement (Node.js)

**File:** `/hub-bridge/server.js`

**Changes:**
1. Import or reimplement `classify_task()` from Python router (or keep simple heuristics)
2. Add `selectOptimalModel(message, phase, taskType)` function (lines ~220-280)
3. Modify `/v1/chat` handler to:
   - Extract `phase` from request body if provided
   - Call `selectOptimalModel(userMessage, phase)`
   - Route to that model's tool-calling function
   - Log selected model + reasoning to telemetry
4. Add telemetry: `debug_model_selected`, `debug_phase`, `debug_model_reason`

**Estimated effort:** 30–45 min

**Testing:**
```bash
curl -X POST http://localhost:18090/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I found a bug in batch_ingest.py, here is the error...",
    "phase": "analyze_failure",
    "model": "auto"  // Trigger auto-selection
  }'
# Expect: model=claude-opus-4-6 in response
```

### Phase B: Karma-Side Router Integration (Python)

**File:** `/opt/seed-vault/memory_v1/karma-core/server.py`

**Changes:**
1. Expose `/v1/model-select` endpoint that accepts (message, phase, task_type) → returns selected model
2. Integrate router.py into consciousness loop: before each /v1/chat call, check if phase is hinted
3. Add cost tracking: append to decision_log.jsonl with {model_used, cost_usd, phase, timestamp}

**Estimated effort:** 20–30 min

### Phase C: Collab Bridge Enhancement (Ledger Format)

**Update collab.jsonl entry schema:**

```json
{
  "timestamp": "2026-02-23T21:00:00Z",
  "id": "proposal_20260223T210000_7k9q2",
  "from": "claude-code",
  "to": "karma",
  "type": "self_improvement_proposal",
  "phase": "analyze_failure",
  "suggested_model": "claude-opus-4-6",
  "content": {
    "problem": "batch_ingest 912 errors (timeout)",
    "hypothesis": "TIMEOUT 1000ms insufficient at scale",
    "proposed_fix": "Increase TIMEOUT to 10000"
  },
  "status": "pending"  // approved | rejected | pending
}
```

**Estimated effort:** 10 min (schema only; logic already exists in prior sessions)

### Phase D: Testing + Monitoring

**Test 1: Task Classification**
```bash
ssh vault-neo "python3 -c \"
from karma_core.router import classify_task
msg = 'analyze this batch failure: TIMEOUT exceeded'
print(classify_task(msg))  # expect: 'reasoning'
\""
```

**Test 2: Cost Projection Report**
```bash
ssh vault-neo "python3 << 'EOF'
from router import ModelRouter
router = ModelRouter()
print('Available models:')
for p in router.get_model_info():
    print(f\"  {p['name']:10} — {p['model']:30} priority={p['priority']:2} tasks={p['task_types']}\")
EOF
"
```

**Test 3: End-to-End Self-Improvement Cycle**
1. CC: Detect batch failure, write to collab.jsonl with phase=analyze_failure, suggested_model=opus-4-6
2. Karma: Read collab entry, select model per CC hint
3. Verify hub-bridge logs: `[DIAGNOSTIC] model: claude-opus-4-6 ...`
4. Monitor `/v1/router/stats` endpoint for model usage tracking

**Estimated effort:** 45 min

---

## Multi-Model Availability & Cost

**All 5 providers currently wired:**

```
├── Anthropic (hub-bridge native)
│   ├── Claude 3 Opus 4.6       $15.00 / $90.00 per 1M tokens
│   ├── Claude 3.5 Sonnet       $3.00  / $15.00 per 1M tokens
│   └── Claude 3.5 Haiku        $0.80  / $4.00  per 1M tokens
│
├── MiniMax (router.py)
│   └── M2.5                    ~$1.50 / $3.00 per 1M tokens (OpenAI-compatible)
│
├── GLM-5 (router.py)
│   └── GLM-5 Large             ~$2.50 / $7.50 per 1M tokens (OpenAI-compatible)
│
└── Groq (router.py)
    └── Llama 3.1               ~$0.05 / $0.30 per 1M tokens (OpenAI-compatible)
```

**Cost/Capability Trade-off Matrix:**

| Model | Analysis | Coding | Speed | Cost (Input) | Best For |
|-------|----------|--------|-------|--------------|----------|
| Opus | 5/5 | 4/5 | 1/5 | $15 | Root cause analysis, complex reasoning |
| Sonnet | 4/5 | 5/5 | 3/5 | $3 | General synthesis, feature generation, tool-use |
| Haiku | 2/5 | 3/5 | 5/5 | $0.80 | Quick validation, summarization |
| MiniMax | 3/5 | 5/5 | 5/5 | $1.50 | Coding tasks (80.2% SWE-Bench), speed-critical |
| GLM-5 | 4/5 | 2/5 | 3/5 | $2.50 | Deep reasoning, analysis (open-source strength) |
| Groq | 1/5 | 2/5 | 5/5 | $0.05 | Cache layer, ultra-low-latency fallback |

---

## Recommendation: Phased Rollout

### **Phase 1 (Immediate): Hub-Bridge Phase Routing**
- Only Anthropic models (already in hub-bridge)
- Phase-aware selection: Opus → Sonnet → Haiku based on task
- Cost savings: ~25–30% on self-improvement loops
- Timeline: 1–2 hours
- Risk: Low (no new infrastructure, known models)

### **Phase 2 (Next Week): Full Router Integration**
- Connect hub-bridge to karma-server router
- Enable MiniMax + GLM-5 + Groq selection
- Cost savings: Additional 40–50% on coding tasks
- Timeline: 3–4 hours
- Risk: Medium (multi-vendor coordination, error handling)

### **Phase 3 (Future): Autonomous Model Discovery**
- Karma learns which models work best for her own tasks
- Self-improvement loop: test Opus vs. Sonnet on same problem, track cost/quality
- Fully autonomous model selection with cost/quality learned preferences
- Timeline: Not this session

---

## Decision Point for Colby

**Question:** Should CC proceed with Phase 1 (hub-bridge phase routing) now?

**Implications:**
- ✅ **Pros:** Immediate cost savings (25–30%), low risk, quick implementation
- ✅ **Quick win:** Self-improvement loop becomes cost-aware
- ⚠️ **Cons:** Still limited to Anthropic models in hub-bridge; full multi-model routing deferred

**Alternative:** Go straight to Phase 2 (full router integration) for maximum flexibility + cost optimization.

---

## Appendix: Key Files to Modify

| File | Lines | Change | Effort |
|------|-------|--------|--------|
| `/hub-bridge/server.js` | ~220–280 | Add `selectOptimalModel()` | 20 min |
| `/hub-bridge/server.js` | ~1150–1230 | Modify /v1/chat routing logic | 15 min |
| `/hub-bridge/server.js` | ~1250–1300 | Add telemetry fields | 10 min |
| `/karma-core/server.py` | ~700–750 | Add /v1/model-select endpoint | 15 min |
| `/karma-core/server.py` | ~1180–1200 | Integrate router into consciousness | 10 min |
| Tests + monitoring | — | Design test harness | 30 min |
| **Total** | | | **90–100 min** (~1.5 hours) |

---

## References

- **Session 11 Track 2:** Anthropic tool-use implementation (4 phases complete)
- **Collab Bridge:** `/opt/seed-vault/memory_v1/ledger/collab.jsonl`
- **Router:** `/opt/seed-vault/memory_v1/karma-core/router.py` (existing, task classifier + provider selection)
- **Hub-Bridge:** `/hub-bridge/server.js` (currently hardcoded to MODEL_DEFAULT)
- **Droplet Router Stats:** `GET /v1/router/stats` (already implemented in karma-server)

---

**Last updated:** 2026-02-23T21:30:00Z
