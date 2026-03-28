# Nexus — Future Work (builds ON Sovereign Harness)

**Source:** VS Code 1.113 (2026-03-25) + Sovereign directives (S151)
**Baseline:** Sovereign Harness plan (Karma2/PLAN.md) must be complete first.

---

## Primitives from VS Code 1.113

### N-F1: Chat Customizations Editor
**VS Code:** Centralized UI for prompt files, custom instructions, custom agents, agent skills — tabs with syntax highlighting.
**Nexus:** `/settings` page at hub.arknexus.net — edit Karma's system prompt sections live, toggle tools, define custom instructions, manage agent skills. CC can self-edit these via the harness.

### N-F2: AI-Generated Customization Content
**VS Code:** Auto-generates customization content based on project context.
**Nexus:** Cortex generates mode/instruction drafts from current knowledge. "Create a mode for code review" → cortex proposes config.

### N-F3: MCP Server Bridge to External Agents
**VS Code:** MCP servers registered in VS Code now bridge to Copilot CLI and Claude agents.
**Nexus:** K2's FastMCP server discoverable by external agents. Add `/mcp/manifest` endpoint.

### N-F4: Subagent-to-Subagent Invocation
**VS Code:** Subagents invoke other subagents for multi-step workflows.
**Nexus:** Karma→CC, CC→Karma, Karma→Kiki, Kiki→CC delegation via coordination bus. `delegate` message type with depth counter (max 3).

### N-F5: Thinking Effort Controls
**VS Code:** "Thinking Effort" submenu in model picker controls reasoning depth.
**Nexus:** `thinking_effort` param in /v1/chat. `low`=cortex($0), `medium`=cortex+mini, `high`=cortex+GPT-5.4, `max`=cortex+Sonnet verifier.

### N-F6: Full Image Viewer
**VS Code:** Click image attachment to open in full viewer.
**Nexus:** Lightbox component in unified.html for tool evidence images, screenshots, graph visualizations.

### N-F7: Weekly Release Cadence
**VS Code:** Monthly→weekly releases.
**Nexus:** Already possible — CC self-edits + deploys via harness. Formalize: auto-increment version tag at wrap-session.

## Sovereign Corrections (S151)

- **Voice: AVAILABLE** — CC wrapper has native voice. NOT a blocker.
- **Video: BLOCKED** — requires implementation.
- **3D Presence: BLOCKED** — requires implementation.
- **Everything else is buildable now** on the Sovereign Harness foundation.

### N-F8: Claude SDK Session Management
**VS Code:** Adopts official Claude Agent SDK API for listing sessions and messages — replaces JSON file parsing.
**Nexus:** cc_server_p1.py currently parses `--output-format json` manually. Migrate to official SDK calls for session state, eliminating sync risks. Session persistence becomes SDK-native.

### N-F9: Subagent Recursion Safeguards
**VS Code:** Subagents can invoke other subagents with depth counter to prevent infinite loops.
**Nexus:** Add `delegation_depth` to coordination bus messages. Max depth=3. Reject messages exceeding depth. Prevents Karma→CC→Karma→CC infinite delegation.

## Priority

| # | What | Effort | Depends on |
|---|------|--------|------------|
| 1 | N-F5 Thinking effort controls | Small | Harness complete |
| 2 | N-F4 Subagent delegation | Medium | Coordination bus |
| 3 | N-F3 MCP manifest on K2 | Small | FastMCP server |
| 4 | N-F1 Customizations editor | Large | unified.html |
| 5 | N-F2 AI-generated modes | Small | Cortex |
| 6 | N-F6 Image lightbox | Small | unified.html |
| 7 | N-F7 Auto-version | Trivial | wrap-session |
| 8 | N-F8 SDK session mgmt | Medium | Claude Agent SDK |
| 9 | N-F9 Recursion safeguards | Small | Coordination bus |
