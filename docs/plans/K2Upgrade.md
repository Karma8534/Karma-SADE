# K2 Upgrade — Optimal Pre-Built Computer for Local LLM Inference

**Date:** 2026-03-15
**Purpose:** Replace/upgrade K2 for running Karma inference locally (30B-70B models at chat speed)
**Constraint:** Pre-built only (no assembly), desktop form factor preferred

---

## Current K2 Specs (Baseline)

| Spec | Value |
|------|-------|
| CPU | Intel i9-185H (laptop) |
| RAM | 64GB |
| GPU | RTX 4070 Laptop (8GB VRAM) |
| Bottleneck | **8GB VRAM** — 30B models must offload to RAM, causing >2min cold load |

**The problem:** 8GB VRAM can't hold a 30B Q4 model (~18GB). Model layers spill to system RAM, inference crawls. Chat-speed (>10 tok/s) requires the model to fit entirely in fast memory.

---

## What We Need

| Requirement | Value |
|-------------|-------|
| 30B model at chat speed | >15 tok/s sustained |
| 70B model viable | >8 tok/s (nice-to-have) |
| Concurrent services | Ollama + Aria + Codex + consciousness loop |
| Form factor | Desktop (mini PC or studio) |
| Budget signal | Colby evaluating ~$1,500-$6,000 range |

---

## Options (Pre-Built, Buyable Today)

### Tier 1: Budget ($1,400-$1,800)

#### Option A: Apple Mac Mini M4 Pro — 48GB Unified Memory
| Spec | Value |
|------|-------|
| Price | ~$1,599 (48GB/512GB SSD) or ~$1,799 (48GB/1TB) |
| Memory | 48GB unified (ALL available as VRAM for Ollama) |
| CPU | M4 Pro (12-core CPU, 16-core GPU) |
| Memory bandwidth | ~273 GB/s |
| 30B Q4 inference | ~20-25 tok/s (fits entirely in unified memory) |
| 70B Q4 inference | ~8-12 tok/s (40GB model fits in 48GB, tight but viable) |
| Power | ~50W typical |

**Pros:** Best price-to-performance. 48GB unified = 30B models fit easily, 70B barely fits. Silent. Tiny form factor. macOS + Ollama works great. Low power.
**Cons:** 70B is tight (48GB - OS overhead). No upgrade path. GPU compute slower than NVIDIA for pure throughput.

#### Option B: Apple Mac Mini M4 — 32GB Unified Memory
| Spec | Value |
|------|-------|
| Price | ~$1,049 (32GB/512GB) |
| Memory | 32GB unified |
| 30B Q4 inference | ~15-20 tok/s |
| 70B Q4 inference | Not viable (40GB > 32GB) |

**Pros:** Cheapest option that runs 30B at chat speed.
**Cons:** 70B excluded. Less headroom for concurrent services.

---

### Tier 2: Mid-Range ($2,000-$3,500)

#### Option C: Apple Mac Studio M4 Max — 64GB Unified Memory
| Spec | Value |
|------|-------|
| Price | ~$2,499 (64GB/512GB) or ~$2,999 (64GB/1TB) |
| Memory | 64GB unified |
| CPU | M4 Max (14-core CPU, 32-core GPU) |
| Memory bandwidth | ~546 GB/s (2x Mac Mini) |
| 30B Q4 inference | ~35-45 tok/s |
| 70B Q4 inference | ~15-20 tok/s (comfortable fit with headroom) |
| Power | ~75W typical |

**Pros:** Double the memory bandwidth = significantly faster inference. 70B runs comfortably. Room for concurrent services. Proven LLM workhorse.
**Cons:** $900+ more than Mac Mini for ~50% faster inference. Still no upgrade path.

#### Option D: Apple Mac Studio M4 Max — 128GB Unified Memory
| Spec | Value |
|------|-------|
| Price | ~$3,499 (128GB/1TB) |
| Memory | 128GB unified |
| Memory bandwidth | ~546 GB/s |
| 30B Q4 inference | ~35-45 tok/s |
| 70B Q4 inference | ~18-22 tok/s |
| 100B+ models | Viable (Q4 quantized) |

**Pros:** Future-proof. Can run models that don't exist yet. Massive headroom.
**Cons:** Diminishing returns — 128GB mostly benefits 100B+ models. $1,000 premium over 64GB for same throughput on current models.

---

### Tier 3: Premium ($4,000-$6,500)

#### Option E: Apple Mac Studio M4 Ultra — 192GB Unified Memory
| Spec | Value |
|------|-------|
| Price | ~$5,999 (192GB/1TB) or ~$6,499 (192GB/2TB) |
| Memory | 192GB unified |
| CPU | M4 Ultra (28-core CPU, 64-core GPU) |
| Memory bandwidth | ~819 GB/s |
| 30B Q4 inference | ~50-60 tok/s |
| 70B Q4 inference | ~25-35 tok/s |
| 100B+ models | Comfortable (120B+ Q4 fits easily) |

**Pros:** Ultimate local inference. Runs anything. Fastest Apple Silicon bandwidth. Could run the entire Karma stack + multiple models simultaneously.
**Cons:** $6K. Overkill for current needs. Same money could buy cloud credits for years.

---

## Why Apple Silicon for LLM Inference?

1. **Unified memory = all RAM is VRAM.** NVIDIA cards have a fixed VRAM ceiling (24GB on 4090). Apple's 48GB/64GB/128GB/192GB is ALL available to the model.
2. **Memory bandwidth is the bottleneck for LLM inference** — not compute. Apple Silicon has excellent bandwidth per dollar.
3. **Token generation is memory-bound** — each token reads the entire model weights. More bandwidth = more tok/s. The M4 Max at 546 GB/s beats most consumer NVIDIA setups for large models.
4. **Power efficiency** — 50-75W vs 350W+ for NVIDIA desktop. Runs 24/7 as K2 replacement without heating the room.
5. **Ollama native support** — Ollama on macOS + Apple Silicon is first-class. Metal acceleration works out of the box.

---

## CC Recommendation

### Best Value: Option A — Mac Mini M4 Pro 48GB ($1,599)
- 30B at chat speed: YES (~20-25 tok/s)
- 70B viable: BARELY (tight fit, ~8-12 tok/s)
- Replaces K2 entirely for Karma inference
- $1,599 is less than 3 months of aggressive API usage
- ROI: pays for itself in 3-6 months of eliminated API costs

### Best Balance: Option C — Mac Studio M4 Max 64GB ($2,499)
- 30B at chat speed: YES, fast (~35-45 tok/s)
- 70B comfortable: YES (~15-20 tok/s)
- Double the bandwidth of Mac Mini = noticeably faster
- Future-proof for 2+ years of model growth
- **This is what I'd choose** if budget allows $2,500

### If budget is open: Option D — Mac Studio M4 Max 128GB ($3,499)
- Same speed as 64GB for current models
- Unlocks 100B+ models when they arrive
- Maximum future-proofing without Ultra pricing

---

## Comparison to Current K2

| Metric | Current K2 (RTX 4070 8GB) | Mac Mini M4 Pro 48GB | Mac Studio M4 Max 64GB |
|--------|---------------------------|----------------------|------------------------|
| 30B inference | >2min cold load, ~3-5 tok/s | ~20-25 tok/s | ~35-45 tok/s |
| 70B viable | No | Barely | Yes, comfortable |
| Available VRAM | 8GB | 48GB (6x) | 64GB (8x) |
| Power | ~120W (laptop) | ~50W | ~75W |
| Form factor | Laptop | Mini desktop | Compact desktop |
| Price | (already owned) | $1,599 | $2,499 |
| Concurrent services | Limited by VRAM | Yes | Yes, with headroom |

---

## Migration Plan (once purchased)

1. Install macOS, Ollama, pull qwen3:30b + devstral + nomic-embed-text
2. Set up Tailscale on new machine (replaces K2's 100.75.109.92)
3. Update hub.env K2_OLLAMA_URL to new Tailscale IP
4. Wire callWithK2Fallback as primary (one-line change, already tested Session 98)
5. Move Aria service, Codex supervisor, consciousness loop to new machine
6. Verify all K2 tools (k2_*, shell_run) work via new endpoint
7. Decommission old K2 or repurpose as backup

---

## Notes

- Pricing as of early 2026. Apple pricing is stable but verify at apple.com before purchase.
- tok/s estimates are for Q4_K_M quantization (standard Ollama default). FP16 models need 2x memory and run slower.
- Apple Silicon inference speeds based on community benchmarks (llama.cpp, Ollama metal backend).
- All options run Ollama natively with Metal acceleration — no Docker needed for inference.
- NVIDIA alternatives (RTX 5090 32GB in a pre-built): faster per-token but 32GB VRAM ceiling limits model size. Apple's 48-192GB unified memory wins for flexibility.

**Bottom line:** Mac Mini M4 Pro 48GB at $1,599 solves the immediate problem. Mac Studio M4 Max 64GB at $2,499 solves it for the next 2-3 years.
