---
source: https://platform.claude.com/docs/en/agent-sdk/secure-deployment
scraped: 2026-03-23
section: agent-sdk
---

# Securely deploying AI agents

A guide to securing Claude Code and Agent SDK deployments with isolation, credential management, and network controls

---

Claude Code and the Agent SDK can execute code, access files, and interact with external services on your behalf. This guide covers practical ways to reduce risk, from built-in features to hardened production architectures.

## Threat model

Agents can take unintended actions due to prompt injection (instructions embedded in content they process) or model error. Defense in depth is good practice.

## Built-in security features

Claude Code includes several security features:

- **Permissions system**: Every tool and bash command can be configured to allow, block, or prompt the user for approval
- **Static analysis**: Before executing bash commands, Claude Code runs static analysis to identify potentially risky operations
- **Web search summarization**: Search results are summarized rather than passing raw content directly into context
- **Sandbox mode**: Bash commands can run in a sandboxed environment that restricts filesystem and network access

## Security principles

### Least privilege

Restrict the agent to only the capabilities required for its specific task:

| Resource | Restriction options |
|----------|---------------------|
| Filesystem | Mount only needed directories, prefer read-only |
| Network | Restrict to specific endpoints via proxy |
| Credentials | Inject via proxy rather than exposing directly |
| System capabilities | Drop Linux capabilities in containers |

## Isolation technologies

| Technology | Isolation strength | Performance overhead | Complexity |
|------------|-------------------|---------------------|------------|
| Sandbox runtime | Good (secure defaults) | Very low | Low |
| Containers (Docker) | Setup dependent | Low | Medium |
| gVisor | Excellent (with correct setup) | Medium/High | Medium |
| VMs (Firecracker, QEMU) | Excellent (with correct setup) | High | Medium/High |

### Sandbox runtime

For lightweight isolation without containers, [sandbox-runtime](https://github.com/anthropic-experimental/sandbox-runtime) enforces filesystem and network restrictions at the OS level.

```bash
npm install @anthropic-ai/sandbox-runtime
```

### Containers

A security-hardened container configuration:

```bash
docker run \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  --security-opt seccomp=/path/to/seccomp-profile.json \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=100m \
  --tmpfs /home/agent:rw,noexec,nosuid,size=500m \
  --network none \
  --memory 2g \
  --cpus 2 \
  --pids-limit 100 \
  --user 1000:1000 \
  -v /path/to/code:/workspace:ro \
  -v /var/run/proxy.sock:/var/run/proxy.sock:ro \
  agent-image
```

> **Warning:** Avoid mounting sensitive host directories like `~/.ssh`, `~/.aws`, or `~/.config`.

### gVisor

gVisor intercepts system calls in userspace before they reach the host kernel. To use with Docker:

```json
// /etc/docker/daemon.json
{
  "runtimes": {
    "runsc": {
      "path": "/usr/local/bin/runsc"
    }
  }
}
```

Then run: `docker run --runtime=runsc agent-image`

## Credential management

### The proxy pattern

Run a proxy outside the agent's security boundary that injects credentials into outgoing requests. The agent never sees the actual credentials.

### Configuring Claude Code to use a proxy

```bash
export ANTHROPIC_BASE_URL="http://localhost:8080"
```

Or for system-wide proxy:

```bash
export HTTP_PROXY="http://localhost:8080"
export HTTPS_PROXY="http://localhost:8080"
```

## Filesystem configuration

### Read-only code mounting

```bash
docker run -v /path/to/code:/workspace:ro agent-image
```

Common files to exclude before mounting:

| File | Risk |
|------|------|
| `.env`, `.env.local` | API keys, database passwords, secrets |
| `~/.aws/credentials` | AWS access keys |
| `~/.config/gcloud/...` | Google Cloud ADC tokens |
| `*.pem`, `*.key` | Private keys |

## Further reading

- [Claude Code security documentation](https://code.claude.com/docs/en/security)
- [Hosting the Agent SDK](/docs/en/agent-sdk/hosting)
- [Sandbox runtime](https://github.com/anthropic-experimental/sandbox-runtime)
- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [gVisor Documentation](https://gvisor.dev/docs/)
