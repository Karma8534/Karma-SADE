# Deploy Skill — Autonomous Docker Build→Deploy→Verify Pipeline

**Purpose:** Encodes the complete Docker Compose deployment workflow with automatic verification gates. Eliminates manual Docker rebuild cycles, silent failures, and missing environment variable issues.

**When to use:** Whenever you need to deploy a service or rebuild a container in the Karma system.

**How to invoke:** `/deploy [service-name] [--remote vault-neo] [--check-env VAR1,VAR2] [--health-endpoint /health]`

---

## The Protocol

This skill runs an autonomous pipeline where **each step must verify before proceeding to the next**. If any step fails, the entire pipeline stops and reports the issue.

### Step 1: Validate Compose Configuration

**What happens:**
```bash
docker compose config -q
```

**Why:** Catches syntax errors, missing services, invalid directives before building.

**Gate:** If validation fails, STOP. Report the exact error from docker compose.

**Success criteria:** `docker compose config` returns with exit code 0 (no output).

---

### Step 2: Extract and Verify Service Configuration

**What happens:**
1. Read the docker-compose.yml file
2. Extract the target service definition
3. Identify: image name (from compose), build context, port mappings, volume mounts
4. Print the extracted config so you can verify it's correct

**Why:** Prevents building the wrong image or deploying to the wrong container.

**Gate:** Stop if the service doesn't exist in compose.yml. Stop if image naming is ambiguous.

**Success criteria:**
- Service found in compose.yml
- Build context is clear (e.g., `context: ../karma-core`)
- Image name determined (e.g., `compose-karma-server`)
- Port mappings printed

**Example output:**
```
Service: karma-server
  Image Name (from compose): compose-karma-server
  Build Context: ../karma-core
  Ports: 127.0.0.1:8340→8340
  Volumes: /opt/seed-vault/memory_v1/Memory, /ledger
```

---

### Step 3: Verify Required Environment Variables

**What happens:**
1. Extract all `environment:` block variables from the service definition
2. Check which ones reference external env vars (format: `${VAR_NAME}`)
3. For each external var, verify it exists in `.env` or is already set in the shell
4. Report missing variables and STOP if any critical ones are missing

**Why:** Prevents deployments with incomplete configuration. This catches the OPENAI_API_KEY and ANALYSIS_MODEL omissions that have caused multiple debugging cycles.

**Gate:** STOP if any required environment variable is missing from `.env` or shell.

**Success criteria:**
```
✓ ANALYSIS_MODEL=gpt-4o-mini (from .env)
✓ GOOGLE_API_KEY=AIzaSy... (from .env)
✓ OPENAI_API_KEY=sk-proj-... (from .env)
✓ VAULT_BEARER=6a5ba4... (from .env)
✓ GLM_API_KEY=47d6a0... (from .env)

All required env vars present. Proceeding to build.
```

---

### Step 4: Build the Docker Image

**What happens:**
```bash
cd /opt/seed-vault/memory_v1/compose  # (or wherever compose.yml lives)
docker compose build --no-cache [service-name]
```

**Why:**
- `docker compose build` (NOT `docker build`) ensures the image name matches what compose expects
- `--no-cache` guarantees fresh code is included (no stale layers)

**Gate:** STOP if build fails. Report the exact Docker error.

**Success criteria:**
- Build completes with exit code 0
- Final image name matches what was identified in Step 2

**Verification step:**
After build, run: `docker compose config | grep -A5 "[service-name]" | grep image`
Confirm the image name matches the target.

---

### Step 5: Deploy the Container

**What happens:**
```bash
docker compose up -d [service-name]
```

**Why:** Start the new container with fresh image and environment variables.

**Gate:** STOP if deployment fails.

**Success criteria:**
```bash
docker compose ps [service-name]
```
Returns: `Status: Up X seconds (healthy)` or `Up X seconds`

**Failure detection:**
- Status: `Exited (1)` or `Exit (non-zero)` → deployment failed
- Status: `Created` but not `Up` → container can't start

---

### Step 6: Verify Container Startup Logs

**What happens:**
```bash
docker compose logs --tail=30 [service-name]
```

**Why:** Catch startup errors, missing dependencies, initialization failures before declaring success.

**Gate:** STOP if logs show errors like:
- `ModuleNotFoundError`, `ImportError` (missing dependencies)
- `KeyError`, `TypeError` (runtime config errors)
- `Connection refused` (can't connect to downstream services)
- `FATAL`, `ERROR` (application-level failures)

**Success criteria:**
Logs show successful initialization. Examples:
- `[ROUTER] GLM-5 registered` (for karma-server)
- `listening on :8340` (server started)
- `App starting up` or similar startup message

---

### Step 7: Run Health Check Endpoint

**What happens:**
If the service exposes a health endpoint (e.g., `/health`, `/healthz`):
```bash
curl -s http://127.0.0.1:[PORT]/health
```

**Why:** Verify the service is not just running, but actually responding to requests.

**Gate:** STOP if:
- Health check returns HTTP 500 or 404
- Response is empty or malformed
- Service times out (no response after 5 seconds)

**Success criteria:**
- Health endpoint returns HTTP 200
- Response body contains expected fields (e.g., `{"status":"ok"}`)

---

### Step 8: Final Verification

**What happens:**
1. Confirm container is still healthy: `docker compose ps [service-name]`
2. Confirm no error logs appeared: `docker compose logs --tail=5 [service-name]` shows no ERROR/FATAL
3. If applicable, run a smoke test (e.g., `/v1/chat` endpoint call with auth token)

**Why:** Catch late-stage failures (container crashes after initial startup, memory issues, etc.).

**Gate:** STOP if any verification fails.

**Success criteria:** All checks pass.

---

## Example Invocation

```
/deploy karma-server --remote vault-neo --check-env OPENAI_API_KEY,GLM_API_KEY --health-endpoint /health
```

This will:
1. SSH to vault-neo
2. Validate docker-compose.yml exists and is valid
3. Check that OPENAI_API_KEY and GLM_API_KEY are in .env
4. Build the karma-server image (using docker compose, not docker build)
5. Deploy with `docker compose up -d`
6. Wait 5 seconds
7. Verify container is healthy via `curl http://127.0.0.1:8340/health`
8. Report success or failure with exact diagnostic info

---

## Common Pitfalls This Prevents

| Pitfall | This Skill Catches | How |
|---------|-------------------|-----|
| Wrong image name (docker build vs docker compose) | ✓ | Step 2 compares expected vs actual image name |
| Missing environment variables | ✓ | Step 3 validates all ${VAR} references are in .env |
| Stale Docker image (old code) | ✓ | Step 4 uses --no-cache to force rebuild |
| Container fails to start silently | ✓ | Step 5-6 check ps output and logs |
| Service running but not responding | ✓ | Step 7 calls health endpoint |
| Container crashes after 30 seconds | ✓ | Step 8 re-checks health after all steps complete |
| Wrong compose file location | ✓ | Step 1 validates config before doing anything |

---

## Error Recovery

If the skill encounters a failure:

1. **Build fails:** You need to fix the Dockerfile or source code. Check the error from Step 4. Modify the code, then re-run `/deploy` — the skill will rebuild from scratch.

2. **Missing env var:** Add it to `.env`, then re-run `/deploy`. The skill will pick it up.

3. **Health check fails:** The container is running but the service isn't responding. Check logs from Step 6. Common fixes:
   - Wrong port mapping
   - Service trying to connect to unavailable downstream service (e.g., karma-server can't reach vault-api)
   - Service config error (wrong model name, missing API key)

4. **Container crashes:** Check logs from Step 6. Look for:
   - `ModuleNotFoundError` → missing Python package
   - `KeyError` → missing config or env var
   - `Connection refused` → can't reach another service

---

## Safety Rails

- **Never force push to main.** This skill only deploys to running containers; it doesn't touch git.
- **Automatic rollback not supported.** If deployment fails, the old container remains running. You can manually revert by running `/deploy` with the previous image tag.
- **Health checks are optional.** If you don't specify `--health-endpoint`, the skill stops after Step 6 (logs verification).
- **Remote vs. local.** Use `--remote vault-neo` to deploy to the droplet via SSH. Without it, assumes local docker daemon.

---

## Full Workflow Example

```
User: /deploy karma-server --remote vault-neo --health-endpoint /health

Skill execution:
├─ Step 1: Validate compose.yml ✓
├─ Step 2: Extract service config ✓
│   karma-server → compose-karma-server image
├─ Step 3: Check env vars ✓
│   ✓ OPENAI_API_KEY
│   ✓ ANALYSIS_MODEL
│   ✓ VAULT_BEARER
│   ✓ GLM_API_KEY
├─ Step 4: Build image ✓
│   Built compose-karma-server:latest
├─ Step 5: Deploy container ✓
│   Container started
├─ Step 6: Verify logs ✓
│   [ROUTER] GLM-5 registered ← OK
│   [ROUTER] OpenAI registered ← OK
├─ Step 7: Health check ✓
│   GET http://127.0.0.1:8340/health → 200 OK
├─ Step 8: Final verification ✓
│   Container still healthy
│   No error logs
│
Result: DEPLOYMENT SUCCESS
```

---

## Implementation Notes

This skill is designed to be called by Claude Code operators or automated hooks. It can be invoked as:

- **Interactive:** `/deploy karma-server`
- **With options:** `/deploy karma-server --check-env OPENAI_API_KEY,GLM_API_KEY --health-endpoint /health`
- **Remote:** `/deploy karma-server --remote vault-neo` (SSH to droplet and run all steps there)

The skill should fail fast and report exactly what went wrong, so the operator can fix the root cause and retry.
