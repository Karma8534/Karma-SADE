# IAmUnbounded_devctx_ Carry context across coding agents_editors_IDEs - Cursor_Windsurf_Claude Code_Antigravity

*Converted from: IAmUnbounded_devctx_ Carry context across coding agents_editors_IDEs - Cursor_Windsurf_Claude Code_Antigravity.PDF*



---
*Page 1*


devctx
Code Issues 3 More
Watch 1
Carry context across coding agents/editors/IDEs - Cursor/Windsurf/Claude Code/Antigravity
189 stars 28 forks 1 watching Branches Activity
Tags
Public repository
1Branch 0Tags Go to file Go to file Add file Code
t
IAmUnbounded docs: clarify AI agent CLI usage in README 7308ec5 · last week
devctx move readme out last week
.gitignore Packaging VS Code extension and … last week
README.md docs: clarify AI agent CLI usage in … last week
README
DevContext 🧠
"Git tracks your code history. DevContext tracks your intent history."
Persistent AI coding context for teams. Never re-explain your codebase to an AI assistant again.
The Problem
You're deep in a Cursor session refactoring a payment service. You've explained the architecture, tried 3
approaches, finally found the right one. Session dies. Next morning — or worse, your teammate picks it up
— and the AI has zero memory. You spend 15 min re-explaining everything. Every. Single. Time.
This is broken across every AI coding tool: Cursor, Claude Code, Copilot, Windsurf — none of them persist
context across sessions, editors, or team members.
The Solution
DevContext is a CLI tool that automatically captures and restores AI coding context, scoped to your repo
and branch.


---
*Page 2*


# Save context after a session
devctx save "Refactoring payment service to use event sourcing"
# Restore context in any editor, any machine
devctx resume
Install
npm install -g devctx
Quick Start
# 1. Initialize in your repo
devctx init
# 2. Work on your code... then save context
devctx save
# → Interactive prompts capture: Task, Approaches, Decisions, Next Steps
# 3. Resume in ANY editor
devctx resume
# → Copies a perfectly formatted prompt to your clipboard
# → Paste into Cursor, Claude, or ChatGPT to restore full context
Features & Commands
Core (No AI Key Required)
These commands work locally with zero dependencies.
Command Description
Initialize DevContext in current repo
devctx init
Save context (interactive or quick mode)
devctx save [msg]
Auto-save context from agent/editor logs (non-interactive)
devctx save --auto
Generate AI prompt & copy to clipboard
devctx resume
View context history for current branch
devctx log
Show changes since last context save
devctx diff
Team & Automation (No AI Key Required)


---
*Page 3*


Command Description
explicit handoff note to a teammate
devctx handoff @user
Commit folder to git for team sync
devctx share .devctx/
Auto-save context on file changes (using )
devctx watch chokidar
Install git post-commit hook for auto-capture
devctx hook install
AI-Powered (Experimental)
AI-Powered (Experimental)
Requires an LLM Provider. Set via env var or .
DEVCTX_AI_KEY devctx config set aiApiKey <key>
Defaults to OpenAI-compatible API.
Command Description
AI-generates context from git diff + recent commits
devctx summarize
AI suggests next steps based on current context
devctx suggest
detailed history into a concise summary
devctx compress
Configuration
Command Description
Set preferences (e.g. , )
devctx config set <key> <val> aiProvider watchInterval
View all configuration
devctx config list
Integrations
🤖 MCP Server (Claude Code, Windsurf)
DevContext provides a Model Context Protocol (MCP) server to allow AI agents to natively read/write
context.
Add to your MCP config:
{
"mcpServers": {
"devctx": {
"command": "npx",
"args": ["-y", "devctx", "mcp"]
}
}
}


---
*Page 4*


Exposes tools: , , and resource .
devctx_save devctx_resume devctx_log devctx://context
🆚 VS Code Extension
Auto-resumes context when you open the project.
💻 Direct CLI Usage
Any AI agent with terminal access (e.g. via or similar tools) can directly run ,
run_command devctx save
, and . This is a universal fallback if MCP is not available.
resume log
How It Works
DevContext stores a folder in your repo. Each entry captures:
.devctx/
Task: What you are doing
Goal: Why you are doing it
Approaches: What you tried (and what failed)
Decisions: Key architectural choices
State: Where you left off
It works with every AI coding tool because it simply manages the prompt — the universal interface for
LLMs.
License
MIT
Releases
No releases published
Packages
No packages published
Languages
TypeScript89.6% JavaScript10.4%