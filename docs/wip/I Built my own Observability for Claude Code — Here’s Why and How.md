# I Built my own Observability for Claude Code — Here’s Why and How

*Converted from: I Built my own Observability for Claude Code — Here’s Why and How.PDF*



---
*Page 1*


Read in the Substack app Open app
I Built my own Observability for Claude Code —
Here’s Why and How
From markdown logs to structured traces: adding self-hosted Langfuse to capture every
coding session.
DONEYLI DE JESUS
JAN 31, 2026
Why Would Anyone Want to Observe Their AI
Coding Sessions?
what is your AI codin
Here’s a question most people don’t ask until it’s too late:
assistant actually doing?
I use Claude Code as my daily driver — not just for writing code, but for buildin
full applications, debugging complex issues, and architecting systems. One of m
side projects is a Family CFO Dashboard: a personal finance system where I tra
goals like my daughter’s college fund, process payslips, model tax scenarios, and
run “what if” projections across investments.
Screenshot of my Family CFO Dashboard. Numbers are not real :)


---
*Page 2*


64 16 12
On a typical day, I run 20-50 conversation turns across multiple projects. That’s
hundreds of prompts, tool invocations, and responses per week.
And until recently, all of that institutional knowledge vanished the moment I
closed a terminal.
Think about that. The debugging session where Claude helped me fix a goal-
saving bug by tracing through React state, reading error logs, and identifying a
CSRF token issue. The architecture discussion where I asked Claude to design
“trickle-down” system — if I update my salary, it should automatically recalcula
taxes, update net worth projections, and flag any goals that are now underfunde
The prompt where I fed it a podcast transcript about “purpose-driven wealth
management” and asked it to extract actionable features for my dashboard.
All gone.
This isn’t just nostalgia. There’s real value in that data:


---
*Page 3*


Prompt patterns
— Which prompts consistently produce great results? Wh
ones need rework?
Tool usage
— How is Claude actually using file reads, grep searches, and ba
commands to solve problems?
Session structure
— What does a productive 45-minute session look like vs
one that spins its wheels?
Cross-project learning
— Are there patterns from one codebase that transf
to another?
I’m a Principal AI Architect. I spend my days helping enterprises build product
AI systems with proper observability, evaluation, and monitoring. The irony of
having that for my own AI tool wasn’t lost on me.
So I built it.
What I Tried First: The Markdown Log
log-prompt.py
My first attempt was straightforward. I wrote a Python hook (
that captured every prompt I submitted to Claude Code and appended it to a
markdown file.
Here’s what it looked like:
# The old approach: capture user prompts to a flat markdown file
def log_prompt(prompt: str, staging_file: Path) -> None:
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
formatted_prompt = format_prompt_for_log(prompt)
entry = f"\n`[{timestamp}]` {formatted_prompt}\n→ *[outcome pending]*\n"


---
*Page 4*


with open(staging_file, 'a') as f:
f.write(entry)
UserPromptSubmit
The hook fired on — every time I hit Enter in Claude Co
.claude/PROMPT_LOG_STAGING.md
It wrote to , which I’d periodically revie
PROMPT_LOG.md
and promote the best prompts to a curated .
The output looked like this:
# Prompt Log Staging
`[2026-01-18 14:30]` I downloaded all my payslips from my new job at ClickHouse. Analyz
them and extract the data to update my financial situation...
→ *[outcome pending]*
`[2026-01-20 09:15]` Planning ahead, show me the current architecture. I want to
implement trickle-down activities — if I update salary, it should recalculate taxes and
impact net worth...
→ *[outcome pending]*
`[2026-01-22 21:00]` Im trying to update an existing goal and its not saving. I click o
"save changes" and it just stays there...
→ *[outcome pending]*
Simple. Worked. For about two weeks.
Where the Markdown Approach Broke Down
Seven problems became obvious fast:


---
*Page 5*


1. Unbounded file growth
The staging file grew indefinitely. After two weeks of active use, it was thousan
of lines. No rotation, no archival, just an ever-growing markdown file.
2. Prompts truncated to 500 characters
To keep the file readable, I truncated long prompts. But the prompts that matte
most — the detailed ones with context, constraints, and examples — are exactly
the ones that get cut off.
3. No responses captured
The hook only captured what I sent. What Claude did with it? What it responde
Which tools it used? None of that was recorded. I had half the conversation.
4. No queryable structure
Want to find “all prompts related to tax calculations” or “every debugging sessi
for the Goals feature”? Good luck grepping through markdown. Flat text files
can’t answer analytical questions.
5. No session context
Prompts weren’t grouped by session. A 9-turn debugging session where I went
→ → →
from “goal not saving” “showing error logs” “CSRF token missing” “sti
→ →
not working” “hard refresh needed” “UX still not ideal” looked like 9
disconnected entries. The narrative — the back-and-forth refinement that mak
AI coding productive — was lost.
6. Outcomes stayed “[pending]” forever


---
*Page 6*


The workflow required me to manually review the staging file and annotate
outcomes. I did this exactly twice before it became another task I never got to.
7. No cross-project patterns
Each project had its own log file. There was no way to see patterns across proje
— which prompt structures work universally, which tools get used most, where
waste time.
I realized I was building a toy system for a problem that had production-grade
solutions.
The “Aha” Moment: This Is Just LLM
Observability
I stepped back and recognized what I actually needed:
Structured trace capture
— inputs, outputs, tool calls, timing
Session grouping
— group turns into conversations
Queryable storage
— filter by project, time range, tool usage


---
*Page 7*


A UI for exploration
— not grepping markdown files
Cross-project aggregation
— one system serving all repos
This is literally what LLM observability platforms do. I’d been building a worse
version of something that already exists.
To top it off, ClickHouse join forces with Langfuse, one of the leading AI/LLM
Observability solutions. Was this a sign? LOL
Langfuse joins ClickHouse
Langfuse
ticked all the boxes for my use case:
Self-hosted
1. — Data stays on my machine. No third-party seeing my prompt
code, or project details.
Purpose-built
2. — Traces, spans, sessions, generations — exactly the data
model I need.
Web UI
3. — Built-in dashboard for exploring sessions without writing querie
API access
4. — Can query programmatically for future automation.
Open source
5. — No vendor lock-in, no usage limits, no subscription.


---
*Page 8*


The Architecture
Here’s what the system looks like:


---
*Page 9*


localhost:3050
Six services. All running locally in Docker. The web UI at gi
you a full observability dashboard.
Step-by-Step: Build This Yourself
I’ve published a template repository with everything you need. Here’s the
walkthrough.
Prerequisites
Docker Desktop
(or Docker Engine + Compose)
Python 3.11+
(3.12 recommended)
Claude Code CLI
installed and working
Step 1: Clone the Template


---
*Page 10*


git clone https://github.com/doneyli/claude-code-langfuse-template.git ~/langfuse-local
cd ~/langfuse-local
Step 2: Generate Credentials
./scripts/generate-env.sh
.env
This creates a file with cryptographically random passwords for every
service — PostgreSQL, ClickHouse, Redis, MinIO, and Langfuse’s encryption
keys. It also sets up your initial user account and API keys.
.env
The generated will look like:
# Auto-generated credentials
POSTGRES_PASSWORD=a7f2e9...
ENCRYPTION_KEY=4da7ae253b65e670...
NEXTAUTH_SECRET=9f07ea85e0424df5...
SALT=1ff573d1b24f42c1...
CLICKHOUSE_PASSWORD=ch_4d9a...
MINIO_ROOT_PASSWORD=minio_ae4a...
REDIS_AUTH=redis_4954...
# Langfuse project keys (used by the hook)
LANGFUSE_INIT_PROJECT_PUBLIC_KEY=pk-lf-local-claude-code
LANGFUSE_INIT_PROJECT_SECRET_KEY=sk-lf-local-...
# Your login credentials
LANGFUSE_INIT_USER_EMAIL=you@example.com
LANGFUSE_INIT_USER_PASSWORD=change-me-on-first-login


---
*Page 11*


Important:
Change the password on your first login to the Langfuse UI.
Step 3: Start Langfuse
docker compose up -d
This pulls and starts six containers:
Wait for all services to be healthy:
docker compose ps
Up (healthy)
You should see all six services with status .
Resource note:
This stack uses ~4-6GB RAM. Stop it when you’re not using
docker compose down
Claude Code: (data persists in Docker volumes).
Step 4: Verify Langfuse Is Running


---
*Page 12*


curl -s http://localhost:3050/api/public/health | python3 -m json.tool
Expected output:
{
"status": "OK",
"version": "3.x.x"
}
Open http://localhost:3050 in your browser. Log in with the email and password
.env
from your file.
Step 5: Install the Hook
./scripts/install-hook.sh
This script does three things:
Installs the Langfuse Python SDK
pip install langfuse
1. —
Copies the hook script
langfuse_hook.py
2. — Places in
~/.claude/hooks/
Configures Claude Code settings
3. — Adds the Stop hook and Langfuse env
~/.claude/settings.json
vars to
~/.claude/settings.json
After running, your will include:
{
"env": {


---
*Page 13*


"TRACE_TO_LANGFUSE": "true",
"LANGFUSE_PUBLIC_KEY": "pk-lf-local-claude-code",
"LANGFUSE_SECRET_KEY": "sk-lf-local-...",
"LANGFUSE_HOST": "http://localhost:3050"
},
"hooks": {
"Stop": [
{
"hooks": [
{
"type": "command",
"command": "python3 ~/.claude/hooks/langfuse_hook.py"
}
]
}
]
}
}
Step 6: Use Claude Code Normally
That’s it. No changes to your workflow. Open Claude Code in any project and
start working:
cd ~/your-project
claude
Every conversation turn is now being captured. The hook runs silently after eac
response — you won’t notice it.
Step 7: Explore Your Traces


---
*Page 14*


Traces
Open http://localhost:3050 and navigate to .
[SCREENSHOT: Langfuse traces list showing multiple conversation turns]
Click into any trace to see the full conversation turn:


---
*Page 15*


[SCREENSHOT: Single trace detail view showing user input, assistant
response, and tool spans]
Each trace contains:
User prompt
— Full text, no truncation
Assistant response
— Complete output
Tool calls
— Every Read, Write, Edit, Bash, Grep, Glob invocation with inp
and outputs
Model info
— Which Claude model was used
Timing
— How long the turn took
Sessions
Navigate to to see grouped conversations:
[SCREENSHOT: Sessions view showing conversations grouped by session ID


---
*Page 16*


How the Hook Actually Works
The hook is a Python script that runs as a Claude Code “Stop hook” — it fires
after every assistant response. Here’s the key logic:
1. Find the latest transcript
.jsonl
Claude Code stores conversation transcripts as files in
~/.claude/projects/<project-dir>/
. The hook finds the most recently
modified one:
def find_latest_transcript():
projects_dir = Path.home() / ".claude" / "projects"
# Find the .jsonl file with the newest modification time
for project_dir in projects_dir.iterdir():
for transcript_file in project_dir.glob("*.jsonl"):
# Track the newest file across all projects
2. Incremental processing
The hook tracks how far it’s read in each session using a state file
~/.claude/state/langfuse_state.json
( ). On each run, it only processe
new lines:
session_state = state.get(session_id, {})
last_line = session_state.get("last_line", 0)
lines = transcript_file.read_text().strip().split("\n")
# Only process lines[last_line:]


---
*Page 17*


This means the hook runs in under a second, even after hundreds of conversatio
turns.
3. Group messages into turns
The transcript is a flat list of messages. The hook groups them into turns: user
→ →
prompt assistant response(s) tool results.
for msg in new_messages:
role = msg.get("type") or msg.get("message", {}).get("role")
if role == "user":
# New turn starts — finalize previous turn
if current_user and current_assistants:
create_trace(...)
current_user = msg
elif role == "assistant":
# Accumulate assistant messages (may be split across multiple)
current_assistants.append(msg)
4. Create structured Langfuse traces
Each turn becomes a trace with child spans:
with langfuse.start_as_current_span(name=f"Turn {turn_num}", ...):
# Root span = the full turn
with langfuse.start_as_current_observation(
name="Claude Response", as_type="generation", ...
):


---
*Page 18*


pass # LLM generation observation
for tool_call in all_tool_calls:
with langfuse.start_as_current_span(
name=f"Tool: {tool_call['name']}", ...
):
pass # Tool invocation span
5. Graceful failure
Every exception exits with code 0. The hook should never block your Claude Co
session:
except Exception as e:
log("ERROR", f"Failed to process transcript: {e}")
finally:
langfuse.shutdown()
sys.exit(0) # Always non-blocking
Making It Resilient: The Offline Queue
what happens
There’s an edge case the basic implementation doesn’t handle:
when Langfuse is down?
Maybe Docker stopped. Maybe you rebooted and forgot to start the containers.
Maybe the Langfuse services crashed. In the original implementation, those tra
were silently lost.


---
*Page 19*


That bothered me. I’m capturing this data precisely because I want a complete
record. Gaps defeat the purpose.
So I added a fallback: a local queue that catches traces when Langfuse is
unreachable and drains them automatically when the connection returns.
The flow
Hook runs
│
▼
Health check (2s socket timeout)
│
├── UP ───► Drain queue ───► Process current turn ───► Send to Langfuse
│
└── DOWN ──► Parse turn ───► Queue to local JSONL
How it works
1. Fast health check
Before doing anything, the hook tests if Langfuse is reachable with a 2-second
socket connection:
def check_langfuse_health(host: str, timeout: float = 2.0) -> bool:
"""Fast check if Langfuse is reachable."""
try:
parsed = urllib.parse.urlparse(host)
hostname = parsed.hostname or "localhost"
port = parsed.port or (443 if parsed.scheme == "https" else 80)


---
*Page 20*


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(timeout)
sock.connect((hostname, port))
sock.close()
return True
except (socket.timeout, socket.error, OSError):
return False
Why a raw socket instead of an HTTP request? Speed. The hook runs after ever
Claude response — it needs to be fast. A socket connection test completes in
milliseconds when the server is up, and fails quickly (2 seconds max) when it’s n
2. Local JSONL queue
When Langfuse is down, traces go to
~/.claude/state/pending_traces.jsonl
:
QUEUE_FILE = Path.home() / ".claude" / "state" / "pending_traces.jsonl"
def queue_trace(trace_data: dict) -> None:
"""Append a trace to the local queue for later delivery."""
trace_data["queued_at"] = datetime.now(timezone.utc).isoformat()
QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
with open(QUEUE_FILE, "a") as f:
f.write(json.dumps(trace_data) + "\n")
queued_at
Each queued trace includes a timestamp so you can see how long i
waited.
3. Automatic drain on reconnection


---
*Page 21*


The next time Langfuse is reachable, the hook drains the queue before processi
the current turn:
def drain_queue(langfuse: Langfuse) -> int:
"""Send all queued traces to Langfuse. Returns count sent."""
if not QUEUE_FILE.exists():
return 0
traces = load_queued_traces()
if not traces:
return 0
sent = 0
for trace_data in traces:
try:
create_trace_from_data(langfuse, trace_data)
sent += 1
except Exception as e:
log("ERROR", f"Failed to send queued trace: {e}")
# Stop on first failure, preserve remaining traces
break
if sent == len(traces):
# All sent successfully — clear the queue
QUEUE_FILE.unlink()
else:
# Partial send — keep unsent traces
remaining = traces[sent:]
QUEUE_FILE.write_text("\n".join(json.dumps(t) for t in remaining) + "\n")
return sent


---
*Page 22*


Notice the conservative approach: if any trace fails to send, the hook stops and
preserves the remaining queue. No data loss.
4. State still advances
last_line
Even when queuing offline, the hook advances its state ( ,
turn_count
). This prevents duplicate processing — you don’t want the same
traces queued multiple times if Langfuse stays down across several conversatio
Why not a background daemon?
I considered running a separate process that periodically retries the queue. But
that adds complexity: another thing to install, another thing to monitor, anothe
thing to fail.
The simple approach is better: the queue drains when you next use Claude Cod
with Langfuse running. Since I’m actively coding when traces matter, the queue
drains naturally through normal usage. If I’m not coding, the traces can wait.
Checking the queue
If you’re curious whether anything is queued:
# Count pending traces
wc -l ~/.claude/state/pending_traces.jsonl
# View queued traces (one JSON object per line)
cat ~/.claude/state/pending_traces.jsonl | python3 -m json.tool --json-lines


---
*Page 23*


When Langfuse comes back up, the next Claude Code response will drain the
queue automatically. You’ll see in the hook log:
2026-01-28 15:23:45 [INFO] Drained 7 traces from queue
2026-01-28 15:23:46 [INFO] Processed 1 turns in 0.8s
Global vs. Per-Project Configuration
By default, the install script enables Langfuse globally — every project is traced
This is what I recommend.
Opt out of a specific project
If you have a project where you don’t want tracing (sensitive client work, for
.claude/settings.local.json
example), add this to the project’s :
{
"env": {
"TRACE_TO_LANGFUSE": "false"
}
}
Claude Code merges project-level settings over global settings, so this override
takes effect cleanly.
Opt-in model (alternative)
If you prefer to opt in per project instead of globally:


---
*Page 24*


env ~/.claude/settings.json
1. Remove the block from
.claude/settings.local.json
2. Add the env block to each project’s
where you want tracing
What You Can Do With the Data
Once you have a few days of traces, the Langfuse dashboard becomes genuinely
useful:
Filter by project
Every trace is tagged with the project name. Filter to see only traces from a
specific codebase.
[SCREENSHOT: Langfuse filtered by project tag]


---
*Page 25*


Analyze tool usage patterns
Which tools does Claude use most? Are there patterns in how it solves problem
The tool spans give you visibility into Claude’s “thinking process” — the file
reads, searches, and edits it performs.
Find your best prompts
Search traces by input text to find prompts that produced great results. That
architecture prompt where I asked Claude to “design trickle-down activities for
salary changes”? I can find it, see exactly how I phrased it, and reuse the pattern
for similar requests.
Session replay
Click into a session to replay an entire conversation chronologically. That 9-tur
debugging session for the goal-saving bug? I can see exactly how it progressed:
the initial report, the error logs I pasted, Claude’s hypothesis about CSRF token
the fix that didn’t work, and finally the cache invalidation solution that did.
Cost awareness
If you’re tracking model usage, Langfuse captures which model handled each tu
Useful for understanding your usage patterns across Haiku, Sonnet, and Opus.
What This Replaced
Here’s the before-and-after:


---
*Page 26*


log-prompt.py
The old hook captured maybe 10% of what actually happens i
Claude Code session. The Langfuse hook captures everything — and doesn’t lo
data when the backend is temporarily unavailable.
Operational Notes
Starting and stopping
But I keep it running 24/7 in my dedicated Home Server
# Start (data persists in Docker volumes)
cd ~/langfuse-local && docker compose up -d
# Stop (when you're done coding for the day)


---
*Page 27*


cd ~/langfuse-local && docker compose down
# Update to latest Langfuse
cd ~/langfuse-local && docker compose pull && docker compose up -d
Monitoring the hook
# Check hook logs
tail -f ~/.claude/state/langfuse_hook.log
# Check hook state
cat ~/.claude/state/langfuse_state.json | python3 -m json.tool
# Check pending queue (if any)
cat ~/.claude/state/pending_traces.jsonl 2>/dev/null | wc -l
# Enable debug logging
export CC_LANGFUSE_DEBUG=true
Resource usage
RAM:
~4-6GB when all six services are running
Disk:
~2-5GB for Docker images, plus data growth over time
CPU:
Minimal when idle. The hook itself runs in under a second.
If I stop Langfuse when I’m not actively coding, no problem. Data persists in
Docker volumes, so nothing is lost. And if I forget to start it? The queue catche
everything until I do.
Port conflicts


---
*Page 28*


The template uses these ports: 3050 (web), 5433 (postgres), 8124 (clickhouse), 637
(redis), 9090 (minio). If any conflict with your existing services, adjust them in
docker-compose.yml
.
What’s Next
pattern analys
This system captures the raw data. The next layer I’m building is
— a skill that queries the Langfuse API to surface insights:
“What were my most complex debugging sessions this week?”
“Which architecture prompts produced the best implementation plans?”
“How many turns did it take to resolve the Goals feature bugs vs. the Tax
calculation bugs?”
The data is structured now. I can finally answer questions like “what’s my most
productive prompt structure” with evidence instead of intuition.
Get Started
Everything you need is in the template repo:
github.com/doneyli/claude-code-langfuse-template
Five commands to go from zero to full observability:
git clone https://github.com/doneyli/claude-code-langfuse-template.git ~/langfuse-local
cd ~/langfuse-local
./scripts/generate-env.sh


---
*Page 29*


docker compose up -d
./scripts/install-hook.sh
Then open Claude Code and work normally. Your sessions are being captured —
even if Langfuse isn’t running yet.
I’m building this in public as part of my broader work on AI tooling and
infrastructure. If you’re interested in how I use Claude Code as a daily
development tool — and the systems I build around it — subscribe to my
newsletter or connect on LinkedIn.
Subscribe to Signal Over Noise — by Doneyli
By Doneyli De Jesus · Launched 2 years ago
Making AI and Data infrastructure understandable. Practical frameworks from the front lines of enterpris
for technical leaders and executives alike.
Type your email... Subscribe
By subscribing, I agree toSubstack'sTerms of Use, and acknowledge
itsInformation Collection NoticeandPrivacy Policy.
64 Likes ∙ 12 Restacks
Previous Next
Discussion about this post
Comments Restacks


---
*Page 30*


Write a comment...
Charles Schiermeyer 1d
Liked by Doneyli De Jesus
Thank you for making the tutorial on how to set this up for our own systems! All the detail is real
helpful for getting up and running. At the same time, isn't this really just creating a lot of extra bu
work for ourselves in addition to the actual development work? Reading and reviewing the
prompt/output history, etc seems like a lot of effort for an unknown purpose, based on what I rea
the article. I'm going to follow this tutorial but I also know myself and don't think I will ever look a
these output logs of the entire conversation with Claude.
does this approach work with Gemini and codex?
Also, have you ever heard of YNAB?
LIKE (1) REPLY
4 replies by Doneyli De Jesus and others
Michael 2d
Liked by Doneyli De Jesus
Fun "Family CFO Dashboard" you have here. :) Did you build it from scratch or do you use any spe
framework / libs tailored towards finances? I've been thinking about building something similar f
own.
LIKE (1) REPLY
2 replies by Doneyli De Jesus and others
14 more comments...


---
*Page 31*


© 2026Doneyli De Jesus · Privacy ∙ Terms ∙ Collection notice
Substackis the home for great culture