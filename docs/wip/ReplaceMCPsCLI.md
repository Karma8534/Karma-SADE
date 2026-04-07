# ReplaceMCPsCLI

*Converted from: ReplaceMCPsCLI.PDF*



---
*Page 1*


Open in app
11
Search Write
Member-only story
Why CLIs Beat MCP for
AI Agents — And How
to Build Your Own CLI
Army. The Guy With
190K GitHub Stars Just
Proved Me Right.
“mcp were a mistake. bash is better.”
Phil | Rentier Digital Following 12 min read · Feb 17, 2026
1.8K 41
S ix words. Thats what Peter Steinberger — the
guy behind OpenClaw, 190,000 GitHub stars,


---
*Page 2*


freshly recruited by Sam Altman — posted on X last
month. And my immediate reaction was to
screenshot it and send it to three dev friends with
“TOLD YOU SO” in all caps.
I’ve been building on Ubuntu for years.
Every tool I use daily is a CLI.
Supabase CLI, Vercel CLI, Docker, git, n8n — my
entire stack runs from a terminal. When MCP
servers started trending last year, I tried a few.
They worked. They also ate 40% of my context
window, crashed randomly, and added a
dependency for something I could already do with
a one-liner and a pipe.
So when the most prolific open-source dev of 2026
says CLIs are the real interface between AI agents
and the world — and OpenAI agrees enough to hire
him — maybe it’s time to pay attention.


---
*Page 3*


TL;DR: MCP servers bloat your context window, add
fragile dependencies, and solve a problem that doesn’t
😂
exist if your tools are CLIs Peter Steinberger built
~10 custom CLIs for OpenClaw, got recruited by
OpenAI for it.
You can use the same pattern with Claude Code today
(document CLIs in CLAUDE.md), plug them into
OpenClaw as skills, or build your own autonomous
agent with the Anthropic tool_use API. CLIs are the
native interface between AI agents and the real world.
GUIs are for humans. APIs are for services. CLIs are for
agents.


---
*Page 4*


Left: MCP in theory. Right: MCP in practice, according to my terminal.
The Case Against MCP (And Why the
OpenClaw Guy Agrees With My Terminal)
Let’s rank the ways an AI agent can interact with
external tools. From worst to best.
GUIs are obviously out. You wouldn’t ask your
CI/CD pipeline to click buttons in a browser. Same
logic applies to agents. Moving on.
REST APIs and SDKs work. But every service has
its own auth flow, its own response format, its own
error handling. You end up writing wrapper code
for each integration. It’s fine for a SaaS backend.
It’s overkill for an agent that just needs to check if
you have new emails.
MCP — the Model Context Protocol — was
supposed to fix this. One standard protocol to
connect agents to tools. Sounds great in theory. In
practice? Every MCP server you add dumps its
entire schema into your agent’s context window.


---
*Page 5*


Tool descriptions, parameter lists, capability
declarations — all of it. Before your agent has even
started thinking about your actual request, 30–40%
of its context is already consumed by MCP
boilerplate.
Peter Steinberger tried it. Built support for it. Then
built MCPorter — a tool that literally converts MCP
servers back into CLIs. Because that’s how much
he thinks the format is wrong.
His exact words on what MCP actually contributed
to the ecosystem: “The only good thing about MCP
was companies opening up some APIs.”
Brutal. And accurate.
The protocol itself was a detour — the APIs it
forced into existence are the real gift.
CLIs win because they’re the opposite of all that
bloat. A CLI is:


---
*Page 6*


Zero context overhead. Your agent doesn’t need
to load a schema. It reads a one-page doc (or
runs --help) and knows every command
available.
Composable. Pipe the output of one CLI into
another. goplaces search "coffee" --json | jq '.
[0].address' - try doing that with an MCP server.
Testable in 2 seconds. Open a terminal, run the
command, see what happens. No server to spin
up, no protocol handshake, no WebSocket
connection.
Structured output for free. Add a --json flag and
your agent gets parseable data without any
serialization layer.
One exec call. That's all an agent needs to use a
CLI. No middleware, no protocol, no server
process running in the background eating RAM for
the privilege of being available.


---
*Page 7*


40% gone before hello. vs. runs, exits, done.
And this isnt some theoretical preference.
Steinberger built his entire OpenClaw ecosystem
around CLIs. About a dozen of them: goplaces for
Google Maps, imsg for iMessage, bird for
X/Twitter, wacli for WhatsApp, gog for Gmail and
Calendar, camsnap for security cameras, peekaboo
for macOS screenshots with AI vision, summarize
for digesting videos and podcasts. Each one
follows the same pattern: does one thing well,
supports --json, has a clear --help.


---
*Page 8*


Then OpenAI hired him.
He spent the better part of a year building this CLI
army. Then OpenAI hired him. Sam Altman didn’t
recruit a guy who built pretty dashboards — he
recruited the guy who proved that bash is the best
agent interface. Make of that what you will.
Using CLIs Right Now to Build Faster (No
OpenClaw Required)
You don’t need OpenClaw to benefit from this. If
you’re using Claude Code, Codex, or any agent with
shell access, you already have the infrastructure.
The trick most people miss: your agent can already
call CLIs. But it doesn’t know about YOUR specific
CLIs unless you tell it.
# CLAUDE.md (root of your project)
## Available CLIs
### Supabase
- `supabase db push` - apply migrations to remote


---
*Page 9*


- `supabase functions deploy <name>` - deploy edge fu
- `supabase db dump --data-only` - export production
- `supabase migration new <name>` - create new migrat
### Vercel
- `vercel deploy --prod` - deploy to production
- `vercel env pull .env.local` - sync env variables
- `vercel logs <url> --follow` - tail production logs
### Project-specific
- `./scripts/check-mrr.sh` - outputs JSON with curren
- `./scripts/seed-demo.sh` - resets demo environment
That’s it.
Claude Code reads CLAUDE.md at the start of every
session. Next time you say "deploy to prod and
check if MRR changed," it knows exactly which
commands to run. No plugin, no MCP server, no
config file with 47 nested keys.
For Codex, same concept — the file is called
AGENTS.md.
For Cursor, .cursorrules.
Different filename, identical pattern.


---
*Page 10*


But the real power move is building your own CLIs.
And before you close this tab thinking “I don’t have
time to build CLI tools” — we’re talking about 20–30
lines of code. Seriously.
Three rules for an agent-friendly CLI:
1. Structured output with
--json
Your agent can’t parse a pretty table with box-
drawing characters. It needs JSON.
#!/usr/bin/env node
// scripts/check-mrr.js
import { createClient } from '@supabase/supabase-js'
const supabase = createClient(process.env.SUPABASE_UR
const args = process.argv.slice(2)
const jsonMode = args.includes('--json')
const { data } = await supabase
.from('subscriptions')
.select('plan, status, created_at')
const active = data.filter(s => s.status === 'active'
const mrr = active.reduce((sum, s) => sum + (s.plan =
const today = data.filter(s =>
new Date(s.created_at).toDateString() === new Date(
)
const stats = {
mrr,


---
*Page 11*


active_subscriptions: active.length,
signups_today: today.length,
timestamp: new Date().toISOString()
}
if (jsonMode) {
console.log(JSON.stringify(stats))
} else {
console.log(`MRR: $${mrr}`)
console.log(`Active: ${active.length}`)
console.log(`Signups today: ${today.length}`)
}
2. A that actually explains things
--help
Agents read --help like humans read READMEs. If
your help text is garbage, your agent will
hallucinate the flags.
$ ./check-mrr.js --help
Usage: check-mrr [options]
Check current SaaS metrics from Supabase.
Options:
--json Output as JSON (default: human-readable)
--period Filter: today | week | month (default: t
--help Show this message
3. Clean exit codes


---
*Page 12*


0 = success. 1 = error.
Your agent uses this to decide what to do next. If
your CLI exits 0 on failure, your agent thinks
everything’s fine and moves on.
I learned this one the hard way at 2 AM when my
deploy script was silently failing and Claude kept
telling me “deployment successful” — took me 20
minutes to realize the script was swallowing errors
and exiting 0 anyway, but I digress.
Once you have a few of these CLIs, something
shifts.
You stop asking Claude Code to write Supabase
queries. You start saying “check my metrics, and if
signups dropped more than 20% from yesterday,
draft a Slack message to the team.” Claude chains
the CLIs together, decides the logic, acts on the
result. That’s not autocomplete. That’s an agent.


---
*Page 13*


The Pattern That Makes This Scale: CLI +
Skill Doc
So here’s the thing Steinberger figured out early,
and that most people still haven’t internalized: a
CLI without documentation is useless to an agent.
Your agent can’t explore a CLI by trial and error
like a human would. It needs to know upfront what
commands exist, what flags are available, what the
output looks like. That’s why every single CLI in the
OpenClaw ecosystem ships with a SKILL.md — a
structured doc that acts as an instruction manual
for the agent.
The pattern is: CLI binary + skill doc =
autonomous capability.
The CLI does the work. The skill doc teaches the
agent how to use it. Together, they’re a self-
contained unit that any agent can pick up and run.
Steinberger calls them “skills.” The concept is the


---
*Page 14*


same whether you call it a skill, a tool, or “that
bash script Dave wrote last Tuesday.”
And you don’t need OpenClaw to use this pattern.
You already are, actually — when you write a
CLAUDE.md that documents your CLIs, that’s a
skill doc. The difference is that Steinberger
standardized the format and built a distribution
layer on top: ClawHub, with 3,000+ skills you can
browse and install.
The interesting part? You can steal any of those
skills for your own setup. Every skill on ClawHub is
just a CLI you can install independently (brew
install steipete/tap/goplaces, npm install -g
@steipete/oracle, etc.) and a SKILL.md you can
read. You don't need the OpenClaw runtime. Install
the binary, paste the relevant commands into your
CLAUDE.md, and Claude Code can use it
immediately.


---
*Page 15*


# In your CLAUDE.md — stolen straight from ClawHub
## goplaces (Google Maps CLI)
- `goplaces search "coffee near me" --open-now --json
- `goplaces search "pizza" --lat 40.8 --lng -73.9 --r
- `goplaces details <place_id> --json` - full place d
- `goplaces resolve "Soho, London" --json` - geocode
Requires: GOOGLE_PLACES_API_KEY env var
## summarize (Video/Podcast/Web summarizer CLI)
- `summarize --url "https://youtube.com/watch?v=xxx"
- `summarize --url "https://some-blog.com/post" --jso
- `summarize --url "https://podcast.fm/ep42" --cli cl
That’s goplaces and summarize — two of
Steinberger’s own tools — running inside Claude
Code with zero OpenClaw dependency. Just a
binary and a doc.
This is why the CLI approach scales in a way MCP
never will. An MCP server is a running process
that needs configuration, a protocol handshake,
and context window space. A CLI skill is a static
binary and a text file. One requires infrastructure.
The other requires a brew install and 10 lines of
markdown.


---
*Page 16*


Plugging CLIs Into OpenClaw
If you’re already running OpenClaw, turning a CLI
into an agent skill takes about 5 minutes.
The system works like this: every skill has a
SKILL.md file that describes what the CLI does, how
to install it, and what commands are available. The
agent reads that file and knows how to use the
tool.
---
name: check-mrr
description: Check SaaS metrics (MRR, signups, churn)
metadata:
openclaw:
requires:
env:
- SUPABASE_URL
- SUPABASE_KEY
bins:
- node
primaryEnv: SUPABASE_URL
---
# check-mrr
Get current SaaS metrics from production Supabase.
## Install
npm install -g @yourhandle/check-mrr


---
*Page 17*


## Commands
- `check-mrr --json` - full metrics as JSON
- `check-mrr --period week` - metrics for the current
- `check-mrr --period month` - monthly overview
## Output format (--json)
{
"mrr": 1247,
"active_subscriptions": 89,
"signups_today": 3,
"timestamp": "2026-02-17T10:30:00Z"
}
Publish it to ClawHub (clawhub publish) and
anyone running OpenClaw can install your skill.
But the real value is local: combine it with a cron
job, and your agent checks your metrics every
morning and pings you on WhatsApp if something
looks off.
// In openclaw.json
{
"cron": [
{
"schedule": "0 8 * * *",
"message": "Run check-mrr --json. If signups_to
"channel": "whatsapp"
}


---
*Page 18*


]
}
That’s the full loop. Cron triggers the agent, agent
reads the skill, calls the CLI, interprets the result,
decides what to do. No dashboard to check. No
notification fatigue from alerts you don’t need. The
agent uses judgment — same pattern Steinberger
runs across his entire setup.
The ClawHub directory already has 3,000+ third-
party skills, most of them following this exact
structure. goplaces for location search, himalaya
😭
for email via IMAP, bird ( ) for X/Twitter,
sonoscli for speaker control - the whole army. You
install them, the agent learns them, done.
Building Your Own Agent (The OpenClaw
Pattern, Without OpenClaw)
OK so what if you don’t want to run OpenClaw?


---
*Page 19*


Maybe you want something lighter, more custom,
or you just enjoy building things from scratch. (I
get it. I self-host everything. It’s a disease.)
The core pattern is dead simple: a script that calls
the Anthropic API with tool_use, maps tool calls to
CLI executions, and loops until the agent is done.
import Anthropic from '@anthropic-ai/sdk'
import { execSync } from 'child_process'
const client = new Anthropic()
// Your CLIs, declared as tools
const tools = [
{
name: "check_mrr",
description: "Get current SaaS metrics (MRR, acti
input_schema: {
type: "object",
properties: {
period: { type: "string", enum: ["today", "we
}
}
},
{
name: "deploy_production",
description: "Deploy latest commit to Vercel prod
input_schema: {
type: "object",
properties: {}


---
*Page 20*


}
},
{
name: "send_slack",
description: "Send a message to a Slack channel",
input_schema: {
type: "object",
properties: {
channel: { type: "string" },
message: { type: "string" }
},
required: ["channel", "message"]
}
}
]
// Map tool names to CLI commands
function executeTool(name, input) {
const commands = {
check_mrr: `node ./scripts/check-mrr.js --json --
deploy_production: `vercel deploy --prod --yes 2>
send_slack: `curl -X POST -H 'Authorization: Bear
-H 'Content-Type: application/json' \
-d '{"channel":"${input.channel}","text":"${inp
https://slack.com/api/chat.postMessage`
}
try {
const result = execSync(commands[name], { encodin
return result
} catch (err) {
return JSON.stringify({ error: err.message, exitC
}
}
// The agent loop
async function runAgent(task) {


---
*Page 21*


let messages = [{ role: "user", content: task }]
while (true) {
const response = await client.messages.create({
model: "claude-sonnet-4-5-20250514",
max_tokens: 4096,
system: "You are an autonomous agent. Use the a
tools,
messages
})
// If Claude is done talking, we're done
if (response.stop_reason === "end_turn") {
const text = response.content.find(b => b.type
return text?.text || 'Done.'
}
// If Claude wants to use tools, execute them
const toolBlocks = response.content.filter(b => b
if (toolBlocks.length === 0) break
messages.push({ role: "assistant", content: respo
const toolResults = toolBlocks.map(block => ({
type: "tool_result",
tool_use_id: block.id,
content: executeTool(block.name, block.input)
}))
messages.push({ role: "user", content: toolResult
}
}
// Run it
const result = await runAgent(
"Check our MRR. If it's above $1000, deploy to prod
)
console.log(result)


---
*Page 22*


~80 lines. That’s your own mini-OpenClaw. The
agent decides which tools to call and in what order
based on the task you give it. Adding a new CLI
takes 30 seconds — add a tool definition, add one
line in the commands map, done.
For the autonomous part, wrap it in a cron:
# crontab -e
0 8 * * * cd /home/deploy/my-agent && node agent.js "
0 20 * * * cd /home/deploy/my-agent && node agent.js
You can also run this as a systemd service with a
timer, or throw it in a Docker container on your
server. Same result, different flavors of devops.


---
*Page 23*


~80 lines. That’s the whole thing.
GitHub Actions is another option if you want zero
infrastructure. A scheduled workflow that installs
your CLIs in the runner and calls the Anthropic
API:
name: Daily Agent Run
on:
schedule:
- cron: '0 8 * * *'
jobs:
agent:
runs-on: ubuntu-latest
steps:
- uses: actions/checkout@v4
- uses: actions/setup-node@v4


---
*Page 24*


with:
node-version: '22'
- run: npm install @anthropic-ai/sdk
- run: node agent.js "Morning routine"
env:
ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_AP
SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
Free for public repos, 2,000 minutes/month on
private ones. Not bad for a daily agent that runs in
30 seconds.
And n8n?
You can technically orchestrate CLIs through n8n
using the Execute Command node or by wrapping
them in FastAPI containers.
But honestly, it’s more friction than the script
approach for this use case. n8n shines when you
need visual workflows with 15 steps and complex
branching — not for “call a CLI and let the LLM
decide.”


---
*Page 25*


If you want to go deeper on running custom code
in n8n, I wrote a full guide on calling Python
scripts from n8n that covers the Docker + FastAPI
setup.
What This Means for You
The trend is clear.
The most productive builders in the AI agent space
aren’t stacking MCP servers and configuring
protocol adapters. They’re writing small, sharp
CLIs and letting their agents call them.
Peter Steinberger proved it at scale with OpenClaw.
OpenAI validated it with a job offer. And you can
start today with a CLAUDE.md file and a 20-line
Node script.
The stack doesn’t matter. OpenClaw, Claude Code,
Codex, a custom agent loop — the pattern is the
same. Wrap your tools in CLIs. Document them for
your agent. Let the LLM handle the orchestration.


---
*Page 26*


Your terminal was an AI interface this whole time.
Most people just didn’t realize it yet.
I packaged the CLI structure, the production
CLAUDE.md, and a demo-vs-product checklist into a
free kit. 3 files, 10 minutes.
🦞
→ Get the Agent Engineering Stack.
Mcp Server Mcp Protocol Claude Code
Peter Steinberger OpenAI
Written by Phil | Rentier Digital
Following
5.4K followers · 4 following
Claude Code in production. What works, what
breaks, what ships.


---
*Page 27*


Responses (41)
To respond to this story,
get the free Medium app.
Hunter Learn
Feb 20 (edited)
Cli is good but mcp is not only about calling api, it is also about data
manipulation and computer use. You cannot use cli only to interact with
business applications to utilize all of their functionality.
50 1 reply
ematese
Feb 23
A year before clawdbot, I tried a third approach. It was to make the PC
work exactly as we do: click here and there, open this or that program, do
this, do that, etc. I used the Python libraries VisionUIParser, pytesseract,
pyautogui, etc. It… more
26 1 reply
Justin Ohms
Feb 25
Funny I thought everyone was already doing this. I’ve been doing this for
over a year at this point. Makes me wonder how anyone is getting
anything done but this does explain why I never really need to use MCP


---
*Page 28*


33
See all responses
More from Phil | Rentier Digital
Phil | Rentier Digital Phil | Rentier Digital
gitignore Protects Your I’m a Control Freak. My
R N t Y M h VPN Sh ld B
Your .gitignore protects your I replaced Tailscale with self-
A l d h t d N tBi d b hi d T fi
5d ago 6d ago
Phil | Rentier Digital


---
*Page 29*


Spotify Built “Honk” to In by
Generati… Phil | Rentier …
R l C di I B il
Every Claude Code
Last week, Spotify’s co-CEO
t ld W ll St t th t hi b t T t i l T h Y
CLAUDE.md, slash
Feb 20 d lti Cl d
Feb 22
See all from Phil | Rentier Digital
Recommended from Medium
EdithTali In by
Publishous Sanjeev P.
Why Men Choose
10 Things You Should
Di d W O
U d O Y G
Three men reveal the brutal
The First Investments
t th b t h th ’d th
S f l P l M k Aft
Mar 1 Feb 17


---
*Page 30*


In by Emily
New East Yuri Minamide
I Failed Uber’s System
Four Cool Japanese
D i I t i L t
H A li th
It was much harder and the
You might end up wanting one
j ti il t ht
t f th
Feb 20 Feb 20
Rekhi Alex Rozdolskyi
Why Vibe Coding Is 5 OpenClaw
G i t C t th A t ti Th t G
In February 2025, Andrej We don’t have bandwidth” is
K th f AI l d t b i td t d
Feb 23 Feb 16
See more recommendations