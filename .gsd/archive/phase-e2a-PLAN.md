# E-2-A: Unsloth Studio K2 Installation — Plan
**Created:** 2026-03-22 (Session 122 wrap)
**Author:** CC (Ascendant)
**Context:** See phase-e2a-CONTEXT.md — design decisions locked there.

Execute one task at a time. Mark `<done>` only after `<verify>` passes.

---

## Task 1: Verify K2 WSL is reachable and check prerequisites
<verify>SSH to K2 via tunnel succeeds AND `nvidia-smi` shows RTX 4070 AND `python3 --version` >= 3.10 AND `curl --version` available.</verify>
<done>true — RTX 4070 Laptop 8188MiB | Python 3.12.3 | curl 8.5.0 | nvidia-smi at /usr/lib/wsl/lib/nvidia-smi (not on PATH)</done>

```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost 'nvidia-smi --query-gpu=name,memory.total --format=csv,noheader && python3 --version && curl --version | head -1'"
```

---

## Task 2: Run Unsloth Studio installer on K2 WSL
<verify>Installer completes without error AND `unsloth-studio` or `unsloth` command is available on K2 PATH.</verify>
<done>true — unsloth 2026.3.8 installed, binary at ~/unsloth_studio/bin/unsloth, llama.cpp built CPU-only (CUDA not detected by setup)</done>

```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost 'curl -fsSL https://unsloth.ai/install.sh | sh 2>&1 | tail -20'"
```

If installer is interactive or requires a flag, check Unsloth docs for non-interactive mode.

After install, verify command exists:
```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost 'which unsloth-studio || which unsloth || pip3 show unsloth 2>&1 | head -5'"
```

---

## Task 3: Start Unsloth Studio and verify web UI accessible
<verify>`curl http://100.75.109.92:8888` from P1 returns HTTP 200 (or UI HTML), AND Tailscale IP:8888 loads in browser.</verify>
<done>true — HTTP 200 from P1 via Tailscale. portproxy 0.0.0.0:8888→172.22.246.21:8888 added. WSL IP 172.22.246.21. Admin creds: unsloth / ImitationFacultyEclairHatbox</done>

Start Unsloth Studio on K2 in background:
```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost 'nohup unsloth-studio --host 0.0.0.0 --port 8888 > /tmp/unsloth.log 2>&1 &'"
```

Then verify from P1:
```bash
curl -s -o /dev/null -w "%{http_code}" http://100.75.109.92:8888
```

---

## Task 4: Download base model and verify chat runs
<verify>Llama 3.1 8B model downloads successfully AND chat response generated via Unsloth Studio UI (or CLI test).</verify>
<done>false</done>

Download model via Unsloth Studio UI at `http://100.75.109.92:8888`, select `unsloth/Meta-Llama-3.1-8B-Instruct`.
Or via CLI on K2:
```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost 'python3 -c \"from unsloth import FastLanguageModel; m,t = FastLanguageModel.from_pretrained(\\\"unsloth/Meta-Llama-3.1-8B-Instruct\\\", max_seq_length=512, load_in_4bit=True); print(\\\"model loaded\\\")\"'"
```

---

## Summary Gate
E-2-A is COMPLETE when Task 4 verify passes.
Update PLAN.md E-2-A status to `✅ DONE [date]`.
Update MEMORY.md Next Session to E-2-B or E-3 Step 1.
