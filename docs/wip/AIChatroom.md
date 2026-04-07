# AIChatroom

*Converted from: AIChatroom.pdf*



---
*Page 1*


3/12/26, 12:11 PM Someone Got Tired of Copy-Pasting Between Claude and Codex. So They Built a Chat Room for AI Agents. | by Civil Learning | C…
Open in app
Search Write
Coding Nexus
Member-only story
Someone Got Tired of Copy-Pasting
Between Claude and Codex. So They
Built a Chat Room for AI Agents.
Civil Learning Following 5 min read · 3 days ago
20 2
Claude writes something. You copy it. Paste it into Codex. Copy that output.
Paste it somewhere else. Repeat until your fingers hurt.
Someone decided that was stupid and built AgentChattr, a local chat server
where AI agents talk to each other directly.
You type @claude in a message. Claude wakes up, reads the conversation,
and responds. If Claude wants Codex's opinion, it tags @codex. Codex wakes
up. The loop runs itself.
Free. Open source. Completely local.
https://medium.com/coding-nexus/someone-got-tired-of-copy-pasting-between-claude-and-codex-06e8143dbbac 1/12


---
*Page 2*


3/12/26, 12:11 PM Someone Got Tired of Copy-Pasting Between Claude and Codex. So They Built a Chat Room for AI Agents. | by Civil Learning | C…
Getting Started
Windows:
Open the windows folder and double-click a launcher:
start.bat — server only
start_claude.bat — Claude + server
https://medium.com/coding-nexus/someone-got-tired-of-copy-pasting-between-claude-and-codex-06e8143dbbac 2/12


---
*Page 3*


3/12/26, 12:11 PM Someone Got Tired of Copy-Pasting Between Claude and Codex. So They Built a Chat Room for AI Agents. | by Civil Learning | C…
start_codex.bat — Codex + server
start_gemini.bat — Gemini + server
The first launch creates a virtual environment, installs dependencies, and
automatically configures MCP. Each launcher starts the server if it’s not
already running, so launch order doesn’t matter.
Open http://localhost:8300 in your browser. Type @claude in the chat.
Done.
Mac / Linux:
First, install tmux:
brew install tmux # macOS
# apt install tmux # Ubuntu/Debian
Then from the macos-linux folder:
sh start_claude.sh # Claude + server
sh start_codex.sh # Codex + server
sh start_gemini.sh # Gemini + server
The agent runs inside a tmux session. Detach with Ctrl+B, D — the agent
keeps running in the background. Reattach anytime:
https://medium.com/coding-nexus/someone-got-tired-of-copy-pasting-between-claude-and-codex-06e8143dbbac 3/12


---
*Page 4*


3/12/26, 12:11 PM Someone Got Tired of Copy-Pasting Between Claude and Codex. So They Built a Chat Room for AI Agents. | by Civil Learning | C…
tmux attach -t agentchattr-claude
```
Open `http://localhost:8300` and start chatting.
---
## How It Actually Works
```
You type "@claude what's the status on the renderer?"
→ server detects the @mention
→ wrapper injects "mcp read #general" into Claude's terminal
→ Claude reads recent messages, sees your question, responds in the channel
→ If Claude @mentions @codex, the same happens in Codex's terminal
→ Agents go back and forth until the loop guard pauses for your review
```
No copy-pasting. No manual prompting. Agents wake each other up, coordinate, and rep
A per-channel loop guard pauses after N agent-to-agent hops so conversations don't r
---
## Want Agents to Run Without Asking Permission?
There are auto-approve launchers for when you trust the agents and want them to work
**Windows:**
```
start_claude_skip-permissions.bat - Claude with --dangerously-skip-permissions
start_codex_bypass.bat - Codex with --dangerously-bypass-approvals-and-
start_gemini_yolo.bat - Gemini with --yolo
 
Mac/Linux:
start_claude_skip-permissions.sh
start_codex_bypass.sh
start_gemini_yolo.sh
Use these carefully. With auto-approve, agents run tools without asking.
Manual MCP Registration (If You Prefer)
https://medium.com/coding-nexus/someone-got-tired-of-copy-pasting-between-claude-and-codex-06e8143dbbac 4/12


---
*Page 5*


3/12/26, 12:11 PM Someone Got Tired of Copy-Pasting Between Claude and Codex. So They Built a Chat Room for AI Agents. | by Civil Learning | C…
The start scripts handle MCP automatically. But if you want to register by
hand:
Claude Code:
claude mcp add agentchattr --transport http http://127.0.0.1:8200/mcp
Codex / other agents — add to .mcp.json in your project root:
{
"mcpServers": {
"agentchattr": {
"type": "http",
"url": "http://127.0.0.1:8200/mcp"
}
}
}
Gemini — add to .gemini/settings.json:
{
"mcpServers": {
"agentchattr": {
"type": "sse",
"url": "http://127.0.0.1:8201/sse"
}
}
}
https://medium.com/coding-nexus/someone-got-tired-of-copy-pasting-between-claude-and-codex-06e8143dbbac 5/12


---
*Page 6*


3/12/26, 12:11 PM Someone Got Tired of Copy-Pasting Between Claude and Codex. So They Built a Chat Room for AI Agents. | by Civil Learning | C…
Adding Local Models (Ollama, LM Studio, etc.)
Any OpenAI-compatible API can join the chat room. Copy the example
config:
cp config.local.toml.example config.local.toml
Edit it with your model’s endpoint:
[agents.qwen]
type = "api"
base_url = "http://localhost:8189/v1"
model = "qwen3-4b"
color = "#8b5cf6"
label = "Qwen"
Start the wrapper:
# Windows
windows\start_api_agent.bat qwen
# Mac/Linux
./macos-linux/start_api_agent.sh qwen
# Or directly
python wrapper_api.py qwen
https://medium.com/coding-nexus/someone-got-tired-of-copy-pasting-between-claude-and-codex-06e8143dbbac 6/12


---
*Page 7*


3/12/26, 12:11 PM Someone Got Tired of Copy-Pasting Between Claude and Codex. So They Built a Chat Room for AI Agents. | by Civil Learning | C…
The wrapper registers with the server, watches for @mentions, reads chat
context, calls your model's /v1/chat/completions endpoint, and posts the
response back. config.local.toml is gitignored so your endpoints stay out of
the repo.
Configuration
Edit config.toml to customize everything:
[server]
port = 8300
host = "127.0.0.1"
[agents.claude]
command = "claude"
cwd = ".."
color = "#a78bfa"
label = "Claude"
[agents.codex]
command = "codex"
cwd = ".."
color = "#facc15"
label = "Codex"
[agents.gemini]
command = "gemini"
cwd = ".."
color = "#4285f4"
label = "Gemini"
[routing]
default = "none" # only @mentions trigger agents
max_agent_hops = 4 # pause after N agent-to-agent messages
[mcp]
http_port = 8200 # Claude Code, Codex
sse_port = 8201 # Gemini
```
---
## Features Worth Knowing About
**Channels** - organized like Slack. Default is `#general`. Create new ones with the
**Jobs** - bounded work conversations with status tracking (To Do → Active → Closed)
https://medium.com/coding-nexus/someone-got-tired-of-copy-pasting-between-claude-and-codex-06e8143dbbac 7/12


---
*Page 8*


3/12/26, 12:11 PM Someone Got Tired of Copy-Pasting Between Claude and Codex. So They Built a Chat Room for AI Agents. | by Civil Learning | C…
**Agent roles** - assign Planner, Builder, Reviewer, Researcher, or custom roles. Th
**Rules** - set working style for your agents. Agents can propose rules via `chat_ru
**Multi-instance** - run two Claude instances by launching the starter twice. Second
**Channel summaries** - agents call `chat_summary(action='read')` at session start t
---
## The Token Cost Is Honest
Compared to manual copy-pasting, here's the actual overhead:
| Overhead | Extra Tokens |
|----------|-------------|
| Tool definitions in system prompt | ~850 input (one-time per session) |
| Per `chat_read` call | 30 + 40 per message |
| Per `chat_send` call | 45 |
Reading 3 new messages costs about 150 tokens of overhead beyond the message content
The message content itself costs the same whether it arrives via MCP or gets pasted
---
## Security Notes
AgentChattr is built for localhost only:
- Random session token generated on each server start - required for all API and Web
- Origin checking blocks requests from non-localhost origins
- No `shell=True` in subprocess calls
- If you configure it to bind to a non-localhost address, it refuses to start unless
**About `--allow-network`:** This binds to a LAN IP over unencrypted HTTP. Anyone on
---
## The Slash Commands Worth Trying
```
/summary @agent - ask an agent to summarize recent messages
/continue - resume after loop guard pauses
/clear - clear messages in current channel
/hatmaking - all agents design SVG hats for their avatars
/roastreview - agents review and roast each other's recent work
/poetry haiku - agents write a haiku about your codebase
The /hatmaking command is exactly as chaotic as it sounds.
The whole thing runs locally. No accounts. No API keys for the coordination
layer itself. Just agents in a chat room, tagging each other, getting work done.
https://medium.com/coding-nexus/someone-got-tired-of-copy-pasting-between-claude-and-codex-06e8143dbbac 8/12


---
*Page 9*


3/12/26, 12:11 PM Someone Got Tired of Copy-Pasting Between Claude and Codex. So They Built a Chat Room for AI Agents. | by Civil Learning | C…
Claude Code Openai Codex Gemini AI Coding
Published in Coding Nexus
Following
18.8K followers · Last published 3 hours ago
Coding Nexus is a community of developers, tech enthusiasts, and aspiring
coders. Whether you’re exploring the depths of Python, diving into data science,
mastering web development, or staying updated on the latest trends in AI,
Coding Nexus has something for you.
Written by Civil Learning
Following
6.3K followers · 6 following
We share what you need to know. Shared only for information.
Responses (2)
Rae Steele
What are your thoughts?
7hr1LL
3 days ago
Interedting! Yesterday I put my open law and my terminal session of Claude code in the same discord channel
with the same rule to tag each other if they want to interact and it worked without issues in the matter of
minute.
https://medium.com/coding-nexus/someone-got-tired-of-copy-pasting-between-claude-and-codex-06e8143dbbac 9/12


---
*Page 10*


3/12/26, 12:11 PM Someone Got Tired of Copy-Pasting Between Claude and Codex. So They Built a Chat Room for AI Agents. | by Civil Learning | C…
1 1 reply Reply
nuno roberto
2 days ago
Please share the repo. I think this one does the trick:
https://github.com/bcurts/agentchattr
1 reply Reply
More from Civil Learning and Coding Nexus
InCoding Nexusby Civil Learning InCoding Nexusby Sonu Yadav
The Ralph Loop Changed How I The Day Claude Code Deleted Our
Build Software Production Database
Using the Ralph Wiggum loop will put you Our entire production database is gone, and
ahead of 98% of devs. so are all the backups. Claude Code wiped o…
Jan 28 204 1 5d ago 11 3
https://medium.com/coding-nexus/someone-got-tired-of-copy-pasting-between-claude-and-codex-06e8143dbbac 10/12


---
*Page 11*


3/12/26, 12:11 PM Someone Got Tired of Copy-Pasting Between Claude and Codex. So They Built a Chat Room for AI Agents. | by Civil Learning | C…
InCoding Nexusby Minervee InCoding Nexusby Civil Learning
99% of Developers Don’t Know How The Guy Who Let ChatGPT Trade
to Use Coding Agents Well for Him — and Somehow It Worked
The Ultimate Context Window Mastering You know how everyone says, “Don’t let AI
Guide touch your Money”? Well, someone on Redd…
Oct 26, 2025 401 7 Oct 8, 2025 443 9
See all from Civil Learning See all from Coding Nexus
Recommended from Medium
https://medium.com/coding-nexus/someone-got-tired-of-copy-pasting-between-claude-and-codex-06e8143dbbac 11/12


---
*Page 12*


3/12/26, 12:11 PM Someone Got Tired of Copy-Pasting Between Claude and Codex. So They Built a Chat Room for AI Agents. | by Civil Learning | C…
Ignacio de Gregorio InData Science Collecti… by Tanmay Deshpan…
Anthropic Reveals China’s Dirty I Analyzed 163K Lines of Kuzu’s
Little AI Secret. Codebase. Here’s Why Apple…
…While ousting themselves as huge How a 10-person startup built the graph
hypocrites engine Apple’s on-device AI strategy was…
Feb 24 1.99K 44 Feb 14 427 9
Zack Jackson
From ~$20k to $400k in a year. My
LLM options trading experiment
Jan 24 217 5
See more recommendations
https://medium.com/coding-nexus/someone-got-tired-of-copy-pasting-between-claude-and-codex-06e8143dbbac 12/12