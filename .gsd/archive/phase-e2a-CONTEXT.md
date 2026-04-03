# E-2-A: Unsloth Studio K2 Installation — Context
**Created:** 2026-03-22 (Session 122 wrap)
**Author:** CC (Ascendant)

## What We're Doing
Installing Unsloth Studio on K2 WSL so we have a local fine-tuning environment ready to consume the corpus built in E-1-A.

## Design Decisions (LOCKED)

### Run on K2 WSL, not P1
K2 has RTX 4070 8GB. Both K2 and P1 share the same GPU class — but K2 WSL is the target because Linux is the native Unsloth environment. P1 Windows install (E-2-C) comes after K2 is verified.

### Use curl installer
Per PLAN.md spec: `curl -fsSL https://unsloth.ai/install.sh | sh` — do not install via pip in isolation. The shell installer handles deps (CUDA, torch version pinning) correctly for the target hardware.

### Access via Tailscale only
K2:8888 must not be exposed publicly. Access from P1 via Tailscale: `http://100.75.109.92:8888`. Firewall check is part of the install gate.

### Base model: Llama 3.1 8B
Same family as Ollama llama3.1:8b already running on P1. 4-bit quant fits in 8GB VRAM. Upgrade path to 70B on Mac Mini when hardware arrives.

## What We're NOT Doing
- Not installing P1 Windows version yet (E-2-C is separate)
- Not starting fine-tuning yet (E-3 through E-5)
- Not downloading model until install verified
- Not exposing K2:8888 outside Tailscale

## Acceptance Criterion
Unsloth Studio web UI loads at `http://100.75.109.92:8888` from P1 browser. Model download works. Chat runs on base GGUF.
