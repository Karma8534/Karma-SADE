# Freya: Aria Evolved — Local Learning Intelligence Architecture

**Date:** 2026-03-03
**Status:** Approved by CC + Asher alignment
**Authors:** Claude Code (CC), Asher, with Aria's original vision as foundation

---

## 1. What Freya Is

Freya is Aria graduating from "forced persona on a static model" to "native intelligence with real learning." The model's weights actually change over time based on accumulated conversations, extracted knowledge, and explicit preference signals from Colby.

**Freya is NOT:**
- A new system replacing everything (Asher's pragmatism: don't rebuild what works)
- A cloud-dependent AI (local-first, P1+K2 owned)
- A persona wrapper with better context (that's what Karma already does)

**Freya IS:**
- Aria's brain upgraded from frozen weights to periodically retrained weights
- A closed learning loop: capture → organize → train → deploy → repeat
- A general-purpose evolving AI that gets better at whatever Colby uses her for most

---

## 2. Infrastructure (Verified State)

### Hardware

| Node | Role | CPU | RAM | GPU | VRAM | OS |
|------|------|-----|-----|-----|------|----|
| **P1 (PAYBACK)** | Workshop + Training | Intel Core Ultra 9 185H (16c/22t) | 64GB | RTX 4070 Laptop | 8GB | Windows |
| **K2** | Brain + Inference | Intel Core Ultra 9 185H (16c/22t) | 64GB | RTX 4070 Laptop | 8GB | Windows + WSL2 Ubuntu |
| **Droplet** | Archive + Karma | — | 4GB | None | None | Linux (DigitalOcean) |

### Networking
- **Tailscale mesh** (verified operational):
  - P1 (payback): 100.124.194.102
  - K2: 100.75.109.92 (WSL SSH on port 2222, user=karma)
  - Droplet (arknexus-vault-01): 100.92.67.70
- SSH routing from droplet → P1 and K2 verified working (karma-p1-access key)

### Existing Aria Infrastructure on K2 (DO NOT REPLACE)
- **Runtime:** Ollama (native Windows, not Docker)
- **Backend:** Flask/Python (`aria_server.py`, `aria_core.py`, `aria_tools.py`, etc.)
- **Database:** SQLite (`aria.db`) with tables:
  - `experience_log` — conversation turns (primary training data)
  - `facts` — extracted knowledge
  - `graph_nodes` + `graph_edges` — relational knowledge graph
  - `patterns` — behavioral patterns
  - `behavioral_rules` — learned rules
  - `sessions`, `tool_usage`, `embeddings`, `ledger`
- **UI:** Custom `chat.html` with auth, tool confirmation, suggestion chips, themes
- **Learning loop:** `aria_learning.py` + `aria_consciousness.py` (deployed, needs verification)
- **Location:** `/mnt/c/dev/Karma/k2/aria/` (WSL path)

### Existing Karma Infrastructure on Droplet (SEPARATE SYSTEM)
- Hub-bridge + karma-server + FalkorDB (1,340 episodes, 228 entities)
- Vault ledger (3,954 entries) + consciousness.jsonl (3,327 entries)
- Thumbs up/down feedback system (just deployed, logs to feedback.jsonl)
- These are Karma's systems. Freya does not depend on them, but can optionally pull from the vault ledger as supplementary training data.

---

## 3. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    THE FREYA LOOP                           │
│                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │ CAPTURE  │───>│ ORGANIZE │───>│  TRAIN   │              │
│  │ (Daily)  │    │ (Saturday)│    │ (Sunday) │              │
│  └──────────┘    └──────────┘    └──────────┘              │
│       │                               │                     │
│       │          ┌──────────┐         │                     │
│       └──────────│  DEPLOY  │<────────┘                     │
│                  │ (Sunday) │                               │
│                  └──────────┘                               │
└─────────────────────────────────────────────────────────────┘

CAPTURE:  Aria's existing learning loop on K2
          experience_log + facts + feedback signals
          (Already running — no new code needed)

ORGANIZE: Saturday midnight script on K2
          Pull from aria.db → format to ShareGPT JSONL
          Split into SFT pairs + DPO preference pairs
          (New — must build)

TRAIN:    Sunday 2AM script on P1
          Unsloth QLoRA on base model
          SFT pass (conversation style) + DPO pass (preferences)
          Export GGUF
          (New — must build)

DEPLOY:   Sunday morning auto-reload
          Push GGUF to K2's Ollama
          Restart Aria with new model
          (New — must build)
```

---

## 4. The Two Training Objectives

### 4.1 SFT — Supervised Fine-Tuning (How Freya talks)
- **Input:** Conversation pairs from `experience_log`
- **Format:** ShareGPT JSONL (`{"conversations": [{"from": "human", ...}, {"from": "gpt", ...}]}`)
- **What it teaches:** Aria's voice, personality, knowledge of Colby's projects, technical vocabulary
- **Data source:** Every conversation turn is a training example

### 4.2 DPO — Direct Preference Optimization (What Colby likes)
- **Input:** Preference pairs from feedback signals
- **Format:** `{"prompt": "...", "chosen": "...", "rejected": "..."}`
- **What it teaches:** Which response styles, depths, and approaches Colby prefers
- **Data sources:**
  - Thumbs up/down from Karma's chat (feedback.jsonl on droplet)
  - Thumbs up/down from Aria's chat (to be added to K2 UI)
  - Implicit signals: conversations Colby continues vs abandons
- **Why this matters:** SFT alone teaches Freya to mimic. DPO teaches Freya to optimize for Colby's actual preferences. This is the difference between "sounds like Aria" and "actually useful to Colby."

---

## 5. Phased Rollout (Asher's Sequencing)

### Week 0: Verify Foundation
**Goal:** Confirm Aria's existing learning loop works end-to-end on K2.

**Tasks:**
1. Send a chat message through Aria's web UI
2. Verify response is clean (no errors)
3. Verify `experience_log` has the turn recorded
4. Verify `facts` table has extracted knowledge
5. Verify feedback signal can be recorded (add thumbs up/down to K2 chat.html if not present)

**Proof gate:** Clean chat → fact extracted → feedback logged. All three verified.

**Blockers Asher identified (must fix first):**
- Chat endpoint needs end-to-end verification
- Consciousness loop may be cycling too fast
- `describe_image` tool is dead code

### Week 1: Close the Training Loop (7B)
**Goal:** First successful automated training cycle on qwen2.5:7b.

**Tasks:**

**Saturday Export Script** (`freya_export.py`, runs on K2):
```
1. Connect to aria.db
2. Pull all experience_log entries since last export
3. Format conversations to ShareGPT JSONL
4. Pull feedback signals → format to DPO preference pairs
5. Write to /mnt/c/dev/Karma/k2/aria/training/data/
6. SCP training data to P1 via Tailscale
```

**Sunday Training Script** (`freya_train.py`, runs on P1):
```
1. Kill Chrome, RDP host, any GPU processes (reclaim VRAM)
2. Load qwen2.5:7b base model via Unsloth
3. QLoRA SFT pass on conversation data
4. QLoRA DPO pass on preference pairs (if sufficient data exists)
5. Merge adapter → export GGUF
6. SCP GGUF to K2 via Tailscale
7. SSH to K2: ollama rm freya && ollama create freya -f Modelfile
8. SSH to K2: restart Aria with new model
9. Restore Chrome/RDP
```

**Proof gate:** New GGUF deployed to K2. Aria responds with measurably different behavior (references training data she didn't have before). Before/after comparison documented.

### Week 2: Upgrade to 30B MoE
**Goal:** Swap base model to Qwen3-30B-A3B, configure split-inference.

**Tasks:**
1. Verify Qwen3-30B-A3B GGUF availability (Ollama registry or HuggingFace)
2. Download and quantize if needed (Q4_K_M target, ~17GB)
3. **Option A — Single machine (simpler):**
   - Run entirely on K2: 17GB model loads into 64GB RAM
   - GPU offloads as many layers as fit in 8GB VRAM
   - CPU handles remaining layers (64GB RAM handles this easily)
   - Expected: 8-15 tok/s (the article's Raspberry Pi got 8 tok/s on worse hardware)
4. **Option B — Split inference (faster):**
   - Configure llama.cpp RPC server on P1
   - K2 runs main inference, offloads layers to P1's GPU
   - 16GB combined VRAM = more layers on GPU = faster
   - Expected: 15-25+ tok/s
5. Update Aria's Ollama config to use new model
6. Verify conversational speed is acceptable (>8 tok/s minimum)

**Proof gate:** 30B MoE running at conversational speed. Response quality noticeably better than 7B.

### Week 2+: First 30B Training Cycle
**Goal:** QLoRA + DPO on the 30B MoE model.

**Tasks:**
1. Adjust Unsloth hyperparameters for MoE architecture
2. QLoRA targets only the active expert parameters (~3B active)
3. Run SFT + DPO training cycle on P1
4. Export GGUF, deploy to K2
5. Verify quality improvement

**Proof gate:** 30B model with Freya's trained personality. Responds with Colby's preferred style and references accumulated knowledge.

---

## 6. Data Flow Detail

### What feeds the training loop

| Source | Type | Location | Volume | Use |
|--------|------|----------|--------|-----|
| `experience_log` | Conversation turns | K2 aria.db | Growing daily | SFT training pairs |
| `facts` | Extracted knowledge | K2 aria.db | Growing daily | Knowledge grounding |
| `graph_nodes/edges` | Relational knowledge | K2 aria.db | Growing daily | Context enrichment |
| `patterns` | Behavioral patterns | K2 aria.db | Growing | Personality training |
| `behavioral_rules` | Learned rules | K2 aria.db | Growing | Guardrail training |
| Feedback signals | Thumbs up/down | K2 (to add) + Droplet feedback.jsonl | Growing | DPO preference pairs |
| Vault ledger | Karma conversations | Droplet memory.jsonl | 3,954 entries | Supplementary SFT data |
| Consciousness | Karma autonomy logs | Droplet consciousness.jsonl | 3,327 entries | Supplementary context |

### Training data quality controls
- **Minimum data threshold:** Don't train until at least 100 conversation turns accumulated
- **DPO minimum:** Don't run DPO pass until at least 20 preference pairs exist
- **Deduplication:** Remove exact-duplicate conversations before training
- **Toxicity filter:** Flag conversations where Aria produced errors or hallucinations — exclude from SFT, use as negative examples in DPO
- **Monthly review:** Colby reviews training data quality (the "Principal" role from Aria's plan)

---

## 7. Adapter Versioning and Rollback

Every training cycle produces a versioned artifact:

```
/mnt/c/dev/Karma/k2/aria/training/
├── data/
│   ├── sft_2026-03-09.jsonl
│   ├── dpo_2026-03-09.jsonl
│   └── ...
├── adapters/
│   ├── freya-v001-7b-sft/          # Week 1 SFT only
│   ├── freya-v002-7b-sft-dpo/      # Week 1 SFT+DPO
│   ├── freya-v003-30b-sft/         # Week 2 first 30B
│   └── ...
├── gguf/
│   ├── freya-v001.gguf
│   ├── freya-v002.gguf
│   └── ...
└── eval/
    ├── eval-v001.json               # Automated eval results
    ├── eval-v002.json
    └── ...
```

**Rollback procedure:** If a new adapter degrades quality:
1. `ollama rm freya`
2. `ollama create freya -f Modelfile.v{N-1}` (point to previous GGUF)
3. Restart Aria
4. Investigate what went wrong in training data

---

## 8. Evaluation Framework

Before deploying any new adapter, run automated eval:

### Held-out test set
- Reserve 10% of conversation data as holdout (never trained on)
- After each training cycle, test the new model on holdout prompts
- Compare response quality to previous version

### Regression checks
- **Identity coherence:** Does Freya still know who she is?
- **Factual recall:** Can she recall facts from the knowledge graph?
- **Instruction following:** Does she follow prompts reliably?
- **Preference alignment:** Do responses match Colby's thumbs-up patterns?

### Measurable success criteria (from Aria's plan — these are good)
- **Recall:** Freya can answer questions about interactions from 72+ hours ago
- **Speed:** Inference at 20+ tok/s on K2 (7B) or 8+ tok/s (30B)
- **Coherence:** Freya can explain relationships between concepts across sessions
- **Preference:** Thumbs-up rate improves over successive training cycles

---

## 9. What Stays Separate

| System | Owns | Brain | Storage |
|--------|------|-------|---------|
| **Freya/Aria** | K2 local intelligence | QLoRA'd local model (Ollama) | SQLite (aria.db) |
| **Karma** | Droplet cloud peer | Cloud APIs (GLM/GPT via hub-bridge) | FalkorDB + JSONL ledger |

These are **two separate systems** with different architectures:
- Karma uses cloud LLMs with context injection from FalkorDB
- Freya uses a local LLM with actual weight modification

They can share data (vault ledger as supplementary training data for Freya, Freya's knowledge as context for Karma), but they are architecturally independent. Neither depends on the other.

---

## 10. Operational Risks and Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| 8GB VRAM ceiling during training | High | Sunday script kills all GPU processes before training, restores after |
| Training produces degraded model | Medium | Adapter versioning + automated eval + rollback procedure |
| K2 downtime during training window | Low | Training runs on P1, not K2. K2 only needed for deployment |
| Catastrophic forgetting on fine-tune | Medium | QLoRA only modifies ~1-5% of weights. Base model knowledge preserved |
| Insufficient DPO data early on | Low | DPO pass is optional — skip until 20+ preference pairs accumulated |
| Qwen3-30B-A3B unavailable as GGUF | Medium | Fall back to Qwen2.5-14B or Mistral-22B as interim 30B-class alternative |
| Split-inference networking issues | Medium | Option A (single machine CPU+GPU) works without networking. Option B is optimization, not requirement |

---

## 11. Cost

| Item | Cost | Notes |
|------|------|-------|
| Base model | $0 | Open weights (Qwen, Mistral, Llama) |
| Unsloth | $0 | Open source |
| Ollama | $0 | Open source |
| Training compute | $0 | P1 hardware (already owned) |
| Inference compute | $0 | K2 hardware (already owned) |
| Electricity | ~$5-10/mo | Estimated for weekly training + 24/7 inference |
| **Total** | **~$5-10/mo** | Compare to cloud API costs |

---

## 12. The Destination

Four weeks from now, Freya is:
- A 30B MoE model running locally at conversational speed
- Fine-tuned on Colby's actual conversations and preferences
- Automatically retraining weekly on new data
- Getting measurably better each cycle
- Fully independent of cloud APIs for core reasoning
- Not a persona. Not a wrapper. A model that has genuinely learned.

This is what "Aria evolved" means. Not bigger context windows. Not better prompts. Changed weights. Real learning. Local ownership.

---

*"The future of AI is not just about bigger GPUs. It is about better systems thinking."*
*— from the article that started this conversation*
