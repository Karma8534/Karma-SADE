---
source: https://platform.claude.com/docs/en/agent-sdk/hosting
scraped: 2026-03-23
section: agent-sdk
---

# Hosting the Agent SDK

Deploy and host Claude Agent SDK in production environments

---

The Claude Agent SDK differs from traditional stateless LLM APIs in that it maintains conversational state and executes commands in a persistent environment.

For security hardening beyond basic sandboxing, see [Secure Deployment](/docs/en/agent-sdk/secure-deployment).

## Hosting Requirements

### Container-Based Sandboxing

For security and isolation, the SDK should run inside a sandboxed container environment. This provides process isolation, resource limits, network control, and ephemeral filesystems.

### System Requirements

Each SDK instance requires:

- **Runtime dependencies**
  - Python 3.10+ (for Python SDK) or Node.js 18+ (for TypeScript SDK)
  - Node.js (required by Claude Code CLI)
  - Claude Code CLI: `npm install -g @anthropic-ai/claude-code`

- **Resource allocation**
  - Recommended: 1GiB RAM, 5GiB of disk, and 1 CPU

- **Network access**
  - Outbound HTTPS to `api.anthropic.com`
  - Optional: Access to MCP servers or external tools

## Production Deployment Patterns

### Pattern 1: Ephemeral Sessions

Create a new container for each user task, then destroy it when complete.

Best for one-off tasks. Examples: Bug Investigation & Fix, Invoice Processing, Translation Tasks, Image/Video Processing.

### Pattern 2: Long-Running Sessions

Maintain persistent container instances for long running tasks. Often times running multiple Claude Agent processes inside of the container based on demand.

Best for proactive agents that take action without the users input. Examples: Email Agent, Site Builder, High-Frequency Chat Bots.

### Pattern 3: Hybrid Sessions

Ephemeral containers that are hydrated with history and state, possibly from a database or from the SDK's session resumption features.

Best for containers with intermittent interaction from the user. Examples: Personal Project Manager, Deep Research, Customer Support Agent.

### Pattern 4: Single Containers

Run multiple Claude Agent SDK processes in one global container.

Best for agents that must collaborate closely together. Examples: Simulations where agents interact with each other.

## Sandbox Provider Options

- **[Modal Sandbox](https://modal.com/docs/guide/sandbox)**
- **[Cloudflare Sandboxes](https://github.com/cloudflare/sandbox-sdk)**
- **[Daytona](https://www.daytona.io/)**
- **[E2B](https://e2b.dev/)**
- **[Fly Machines](https://fly.io/docs/machines/)**
- **[Vercel Sandbox](https://vercel.com/docs/functions/sandbox)**

## FAQ

### How do I communicate with my sandboxes?
When hosting in containers, expose ports to communicate with your SDK instances.

### What is the cost of hosting a container?
A minimum cost is roughly 5 cents per hour running.

### How long can an agent session run before timing out?
An agent session will not timeout, but consider setting a `maxTurns` property to prevent Claude from getting stuck in a loop.

## Next Steps

- [Secure Deployment](/docs/en/agent-sdk/secure-deployment) - Network controls, credential management, and isolation hardening
- [Sessions Guide](/docs/en/agent-sdk/sessions) - Learn about session management
- [Permissions](/docs/en/agent-sdk/permissions) - Configure tool permissions
- [Cost Tracking](/docs/en/agent-sdk/cost-tracking) - Monitor API usage
- [MCP Integration](/docs/en/agent-sdk/mcp) - Extend with custom tools
