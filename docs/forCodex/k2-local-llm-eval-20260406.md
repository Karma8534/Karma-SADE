# K2 Local LLM Evaluation — 2026-04-06

## Ground Truth

- Live K2/P1-reachable local-model endpoint: `http://100.75.109.92:11434`
- Live K2-side bridge from SSH-visible Linux: `http://host.docker.internal:11434`
- `localhost:11434` on the SSH-visible K2 Linux side is **not** the live Ollama endpoint.
- `sudo -n systemctl status ollama` on K2: no `ollama.service` exists on that Linux side.

## Installed K2 Local Models

- `qwen3.5:4b`
- `gemma4:e4b`
- `nomic-embed-text:latest`

## Candidate Classification

- `qwen3.5:4b`: chat/reasoning candidate
- `gemma4:e4b`: chat/reasoning candidate
- `nomic-embed-text:latest`: embedding model, not a chat-floor candidate

## Runtime Evidence

### Inventory

```text
curl.exe -s http://100.75.109.92:11434/api/tags
```

Returned all three installed models above.

### K2 Host Boundary

```text
ssh karma@192.168.0.226 "python3 - <<'PY'
import urllib.request
for url in ['http://localhost:11434/api/tags','http://127.0.0.1:11434/api/tags','http://host.docker.internal:11434/api/tags']:
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            print(url, r.status)
    except Exception as e:
        print(url, 'ERR', e)
PY"
```

Observed:

- `localhost:11434` -> connection refused
- `127.0.0.1:11434` -> connection refused
- `host.docker.internal:11434` -> `200`

### `nomic-embed-text:latest`

Micro-benchmark on `/api/chat` returned:

- `HTTP 400` on all tested chat tasks

Conclusion:

- not a K2 chat-floor candidate

### `gemma4:e4b`

Bounded runtime benchmark file:

- `tmp/benchmark-gemma4-e4b-bounded.json`

Observed:

- passed:
  - `exact_token`
  - `tool_call_json`
- timed out at `120s` on:
  - `permission_matrix`
  - `transcript_summary`
  - `context_recall`
  - `route_selection`
  - `powershell_command`
  - `structured_diff`
  - `concise_reasoning`
  - `format_discipline`

Warmup:

- `98.12s`

Overall bounded score in saved file:

- `0.2`

### `qwen3.5:4b`

Saved benchmark files:

- `tmp/benchmark-qwen3.5-4b.json`
- `tmp/k2-local-options-microbench.json`

Observed:

- passed completed structured tasks such as:
  - `exact_token`
  - `tool_call_json`
  - `permission_matrix`
  - `context_recall`
  - `structured_diff`
  - `concise_reasoning`
- also showed real timeout weakness on some tasks:
  - `transcript_summary`
  - `route_selection`
  - `powershell_command`
  - `format_discipline`

Important live re-check after restart:

```text
14.76 NEXUS_OK
```

from:

```text
POST http://100.75.109.92:11434/api/chat
model=qwen3.5:4b
prompt=Reply with EXACTLY NEXUS_OK and nothing else.
```

Additional live re-check:

```text
11.51 {"gap_id":"structured_diff_display","verdict":"HAVE"}
```

## Decision

Keep `qwen3.5:4b` as the current K2 local floor.

Reason:

- It is materially better than `gemma4:e4b` on the structured tasks that actually completed.
- `gemma4:e4b` timed out on most bounded structured tasks in the current runtime.
- `nomic-embed-text:latest` is not a chat model.
- The live stack currently routes and verifies cleanly against qwen after correction.

## Important Limitation

This is **not** a claim that `qwen3.5:4b` is perfect.

Ground truth says:

- qwen is the best current K2 local option
- qwen still has timeout weakness on some heavier structured tasks

So the real conclusion is:

- `qwen3.5:4b` is the current operational K2 local floor
- the K2 local floor remains weaker than desired
- `gemma4:e4b` is installed for future reevaluation, but is not the better current choice

## Follow-Through

- Repo defaults corrected to use `host.docker.internal:11434` on K2-side code
- Deployed K2 `karma_regent.py` and `julian_cortex.py` synced and restarted
- Live qwen floor re-verified after restart
