# ccSRCport1 (2)

*Converted from: ccSRCport1 (2).PDF*



---
*Page 1*


ᨒ
Home ❯ AI ❯
Claude Code's Entire Source Code Got
MindDump
Leaked via a Sourcemap in npm, Let's Talk
About it
Search
Claude Code's Entire
Source Code Got
Blogs
Leaked via a
AI
Sourcemap in npm,
Business
Let's Talk About it
Data-Science
Gaming Mar 31, 2026, 17 min read
Music
#AI #ChatGPT #Social-Media
Post-Extended
#Artificial-Intelligence #GenerativeAI
Projects
#Internet #OpenAI #Claude
Reflections
#Anthropic
Social-Media
Earlier today (March 31st, 2026) - Chaofan
Technology
Shou on X discovered something that
Tutorials Anthropic probably didnʼt want the world to
TV see: the entire source code of Claude Code,
Anthropicʼs official AI coding CLI, was sitting
in plain sight on the npm registry via a


---
*Page 2*


sourcemap file bundled into the published
package.
Iʼve maintained a backup of that code on
GitHub here but thatʼs not the fun part


---
*Page 3*


Letʼs dive deep into whatʼs in it, how the leak
happened and most importantly, the things
we now know that were never meant to be
public.
How Did This Even Happen?
This is the part that honestly made me go “…
really?”
When you publish a JavaScript/TypeScript
package to npm, the build toolchain often
generates source map files (.map files).
These files are a bridge between the
minified/bundled production code and the
original source, they exist so that when some-
thing crashes in production the stack trace
can point you to the actual line of code in the
original file, not some unintelligible line 1,
column 48293 of a minified blob.
But the fun part is source maps contain the
original source code. The actual, literal, raw
source code, embedded as strings inside a
JSON file.
The structure of a .map file looks something
like this:


---
*Page 4*


1 {
2 "version": 3,
3 "sources": ["../src/main.tsx", "
4 "sourcesContent": ["// The ENTIR
5 "mappings": "AAAA,SAAS,OAAO..."
6 }
That sourcesContent array? Thatʼs every-
thing. Every file. Every comment. Every inter-
nal constant. Every system prompt. All of it,
sitting right there in a JSON file that npm hap-
pily serves to anyone who runs npm pack or
even just browses the package contents.
This is not a novel attack vector. Itʼs happened
before and honestly itʼll happen again.
The mistake is almost always the same: some-
one forgets to add *.map to their
.npmignore or doesnʼt configure their
bundler to skip source map generation for
production builds. With Bunʼs bundler (which
Claude Code uses), source maps are gener-
ated by default unless you explicitly turn
them off.


---
*Page 5*


The funniest part is, thereʼs an entire system
called “Undercover Mode” specifically de-
signed to prevent Anthropicʼs internal infor-
mation from leaking.


---
*Page 6*


They built a whole subsystem to stop their AI
from accidentally revealing internal code-
names in git commits… and then shipped the
entire source in a .map file, likely by Claude.
What’s Claude Under The
Hood?
If youʼve been living under a rock, Claude
Code is Anthropicʼs official CLI tool for coding
with Claude and the most popular AI coding
agent.
From the outside, it looks like a polished but
relatively simple CLI.
main.tsx
From the inside, Itʼs a 785KB en-
try point, a custom React terminal renderer,
40+ tools, a multi-agent orchestration system,
a background memory consolidation engine
called “dream,” and much more
Enough yapping, hereʼs some parts about the
source code that are genuinely cool that I
found after an afternoon deep dive:
BUDDY - A Tamagotchi
Inside Your Terminal


---
*Page 7*


I am not making this up.
Claude Code has a full Tamagotchi-style
companion pet system called “Buddy.” A de-
terministic gacha system with species rarity,
shiny variants, procedurally generated stats,
and a soul description written by Claude on
first hatch like OpenClaw.
buddy/
The entire thing lives in and is
gated behind the BUDDY compile-time fea-
ture flag.
The Gacha System
Your buddyʼs species is determined by a
Mulberry32 PRNG, a fast 32-bit pseudo-ran-
dom number generator seeded from your
userId hash with the salt 'friend-2026-
401':


---
*Page 8*


1 // Mulberry32 PRNG - deterministic
2 function mulberry32(seed: number):
3 return function() {
4 seed |= 0; seed = seed + 0x6D2B
5 var t = Math.imul(seed ^ seed >
6 t = t + Math.imul(t ^ t >>> 7,
7 return ((t ^ t >>> 14) >>> 0) /
8 }
9 }
Same user always gets the same buddy.
18 Species (Obfuscated in Code)
The species names are hidden via
String.fromCharCode() arrays -
Anthropic clearly didnʼt want these showing
up in string searches. Decoded, the full
species list is:
Rarity Species
Pebblecrab, Dustbunny,
Common
Mossfrog, Twigling,
(60%)
Dewdrop, Puddlefish
Uncommon Cloudferret, Gustowl,
(25%) Bramblebear, Thornfox


---
*Page 9*


Rarity Species
Crystaldrake, Deepstag,
Rare (10%)
Lavapup
Stormwyrm, Voidcat,
Epic (4%)
Aetherling
Legendary
Cosmoshale, Nebulynx
(1%)
On top of that, thereʼs a 1% shiny chance
completely independent of rarity. So a Shiny
Legendary Nebulynx has a 0.01% chance of
being rolled. Dang.
Stats, Eyes, Hats, and Soul
Each buddy gets procedurally generated:
5 stats: DEBUGGING, PATIENCE, CHAOS,
WISDOM, SNARK (0-100 each)
6 possible eye styles and 8 hat options
(some gated by rarity)
A “soul” as mentioned, the personality
generated by Claude on first hatch, writ-
ten in character
The sprites are rendered as 5-line-tall, 12-
character-wide ASCII art with multiple ani-


---
*Page 10*


mation frames. There are idle animations, re-
action animations, and they sit next to your
input prompt.
The Lore
The code references April 1-7, 2026 as a
teaser window (so probably for easter?), with
a full launch gated for May 2026. The compan-
ion has a system prompt that tells Claude:
A small {species} named {name} sits
occasionally comments in a speech bu
separate watcher.
So itʼs not just cosmetic - the buddy has its
own personality and can respond when ad-
dressed by name. I really do hope they ship it.
KAIROS - “Always-On
Claude”
assistant/
Inside , thereʼs an entire mode
called KAIROS i.e. a persistent, always-run-
ning Claude assistant that doesnʼt wait for
you to type. It watches, logs, and proactively
acts on things it notices.
This is gated behind the PROACTIVE /
KAIROS compile-time feature flags and is


---
*Page 11*


completely absent from external builds.
How It Works
KAIROS maintains append-only daily log files
- it writes observations, decisions, and ac-
tions throughout the day. On a regular inter-
val, it receives <tick> prompts that let it de-
cide whether to act proactively or stay quiet.
The system has a 15-second blocking budget,
any proactive action that would block the
userʼs workflow for more than 15 seconds
gets deferred. This is Claude trying to be help-
ful without being annoying.
Brief Mode
When KAIROS is active, thereʼs a special out-
put mode called Brief, extremely concise re-
sponses designed for a persistent assistant
that shouldnʼt flood your terminal. Think of it
as the difference between a chatty friend and
a professional assistant who only speaks
when they have something valuable to say.
Exclusive Tools
KAIROS gets tools that regular Claude Code
doesnʼt have:


---
*Page 12*


Tool What It Does
Push files directly to
SendUserFile the user (notifica-
tions, summaries)
Send push notifica-
PushNotification tions to the userʼs
device
Subscribe to and
SubscribePR monitor pull request
activity
ULTRAPLAN - 30-Minute
Remote Planning Sessions
Hereʼs one thatʼs wild from an infrastructure
perspective.
ULTRAPLAN is a mode where Claude Code
offloads a complex planning task to a remote
Cloud Container Runtime (CCR) session run-
ning Opus 4.6, gives it up to 30 minutes to


---
*Page 13*


think, and lets you approve the result from
your browser.
The basic flow:
1. Claude Code identifies a task that needs
deep planning
2. It spins up a remote CCR session via the
tengu_ultraplan_model config
3. Your terminal shows a polling state -
checking every 3 seconds for the result
4. Meanwhile, a browser-based UI lets you
watch the planning happen and
approve/reject it
5. When approved, thereʼs a special sentinel
value
__ULTRAPLAN_TELEPORT_LOCAL__ that
“teleports” the result back to your local
terminal
The “Dream” System -
Claude Literally Dreams
Okay this is genuinely one of the coolest
things in here.
Claude Code has a system called autoDream
(services/autoDream/ ) - a background


---
*Page 14*


memory consolidation engine that runs as a
forked subagent. The naming is very inten-
tional. Itʼs Claude… dreaming.
This is extremely funny because I had the
same idea for LITMUS last week - OpenClaw
subagents creatively having leisure time to
find fun new papers
The Three-Gate Trigger
The dream doesnʼt just run whenever it feels
like it. It has a three-gate trigger system:
1. Time gate: 24 hours since last dream
2. Session gate: At least 5 sessions since last
dream
3. Lock gate: Acquires a consolidation lock
(prevents concurrent dreams)
All three must pass. This prevents both over-
dreaming and under-dreaming.
The Four Phases
When it runs, the dream follows four strict
phases from the prompt in
consolidationPrompt.ts :
Phase 1 - Orient: ls the memory directory,
read MEMORY.md, skim existing topic files to


---
*Page 15*


improve.
Phase 2 - Gather Recent Signal: Find new in-
formation worth persisting. Sources in prior-
ity: daily logs → drifted memories → tran-
script search.
Phase 3 - Consolidate: Write or update mem-
ory files. Convert relative dates to absolute.
Delete contradicted facts.
Phase 4 - Prune and Index: Keep MEMORY.md
under 200 lines AND ~25KB. Remove stale
pointers. Resolve contradictions.
The prompt literally says:
“You are performing a dream - a reflective
pass over your memory files. Synthesize
what youʼve learned recently into durable,
well-organized memories so that future ses-
sions can orient quickly.”
The dream subagent gets read-only bash - it
can look at your project but not modify any-
thing. Itʼs purely a memory consolidation
pass.
Undercover Mode - “Do Not
Blow Your Cover”


---
*Page 16*


This one is fascinating from a corporate strat-
egy perspective.
Anthropic employees (identified by
USER_TYPE === 'ant') use Claude Code
on public/open-source repositories.
utils/undercover.ts
Undercover Mode (
) prevents the AI from accidentally revealing
internal information in commits and PRs.
When active, it injects this into the system
prompt:
## UNDERCOVER MODE - CRITICAL
You are operating UNDERCOVER in a PU
messages, PR titles, and PR bodies M
information. Do not blow your cover.
NEVER include in commit messages or
- Internal model codenames (animal n
- Unreleased model version numbers (
- Internal repo or project names
- Internal tooling, Slack channels,
- The phrase "Claude Code" or any me
- Co-Authored-By lines or any other
The activation logic:
CLAUDE_CODE_UNDERCOVER=1 forces it
ON (even in internal repos)
Otherwise itʼs automatic: active UNLESS
the repo remote matches an internal


---
*Page 17*


allowlist
There is NO force-OFF - “if weʼre not confi-
dent weʼre in an internal repo, we stay
undercover.”
So this confirms:
1. Anthropic employees actively use
Claude Code to contribute to open-
source - and the AI is told to hide that itʼs
an AI
2. Internal model codenames are animal
names - Capybara, Tengu, etc.
3. “Tengu” appears hundreds of times as a
prefix for feature flags and analytics
events - itʼs almost certainly Claude
Codeʼs internal project codename
All of this is dead-code-eliminated from exter-
nal builds. But source maps donʼt care about
dead code elimination.
Makes me wonder how much are they inter-
nally causing havoc to open source repos
Multi-Agent Orchestration -
“Coordinator Mode”


---
*Page 18*


Claude Code has a full multi-agent orchestra-
tion system in coordinator/ , activated
via CLAUDE_CODE_COORDINATOR_MODE=1.
When enabled, Claude Code transforms from
a single agent into a coordinator that spawns,
directs, and manages multiple worker agents
in parallel. The coordinator system prompt in
coordinatorMode.ts
is a masterclass in
multi-agent design:
Phase Who Purpose
Investigat
codebase
Workers find files,
Research
(parallel) under-
stand
problem
Read find-
ings, un-
derstand
Synthesis Coordinator
the prob-
lem, craft
specs


---
*Page 19*


Phase Who Purpose
Make tar-
geted
Implementation Workers changes
per spec,
commit
Test
Verification Workers changes
work
The prompt explicitly teaches parallelism:
“Parallelism is your superpower. Workers are
async. Launch independent workers concur-
rently whenever possible - donʼt serialize
work that can run simultaneously.”
Workers communicate via <task-
notification> XML messages. Thereʼs a
shared scratchpad directory (gated behind
tengu_scratch) for cross-worker durable
knowledge sharing. And the prompt has this
gem banning lazy delegation:
Do NOT say “based on your findings” - read
the actual findings and specify exactly what


---
*Page 20*


to do.
The system also includes Agent
Teams/Swarm capabilities
(tengu_amber_flint feature gate) with in-
process teammates using
AsyncLocalStorage for context isolation,
process-based teammates using tmux/iTerm2
panes, team memory synchronization, and
color assignments for visual distinction.
Fast Mode is Internally
Called “Penguin Mode”
Yeah, they really called it Penguin Mode. The
utils/fastMode.ts
API endpoint in is
literally:
1 const endpoint = `${getOauthConfig
The config key is penguinModeOrgEnabled.
The kill-switch is tengu_penguins_off. The
analytics event on failure is
tengu_org_penguin_mode_fetch_faile
d. Penguins all the way down.


---
*Page 21*


The System Prompt
Architecture
The system prompt isnʼt a single string like
most apps have - itʼs built from modular,
cached sections composed at runtime in
constants/ .
The architecture uses a
SYSTEM_PROMPT_DYNAMIC_BOUNDARY
marker that splits the prompt into:
Static sections - cacheable across organi-
zations (things that donʼt change per
user)
Dynamic sections - user/session-specific
content that breaks cache when changed
Thereʼs a function called
DANGEROUS_uncachedSystemPromptSecti
on() for volatile sections you explicitly want
to break cache. The naming convention alone
tells you someone learned this lesson the
hard way.
The Cyber Risk Instruction
One particularly interesting section is the
CYBER_RISK_INSTRUCTION in


---
*Page 22*


constants/cyberRiskInstruction.ts
,
which has a massive warning header:
IMPORTANT: DO NOT MODIFY THIS INSTRU
This instruction is owned by the Saf
So now we know exactly who at Anthropic
owns the security boundary decisions and
that itʼs governed by named individuals on a
specific team. The instruction itself draws
clear lines: authorized security testing is fine,
destructive techniques and supply chain com-
promise are not.
The Full Tool Registry - 40+
Tools
tools/
Claude Codeʼs tool system lives in
.Hereʼs the complete list:
Tool What It Doe
AgentTool Spawn child a
Shell executio
BashTool / PowerShellTool
sandboxing)
FileReadTool / FileEditTool
File operation
/ FileWriteTool


---
*Page 23*


Tool What It Doe
File search (u
GlobTool / GrepTool
bfs/ugrep w
WebFetchTool /
WebSearchTool / Web access
WebBrowserTool
NotebookEditTool Jupyter noteb
SkillTool Invoke user-d
Interactive VM
REPLTool
mode)
Language Ser
LSPTool
communicati
AskUserQuestionTool Prompt user f
EnterPlanModeTool /
Plan mode co
ExitPlanModeV2Tool
Upload/summ
BriefTool
claude.ai
SendMessageTool /
TeamCreateTool / Agent swarm
TeamDeleteTool


---
*Page 24*


Tool What It Doe
TaskCreateTool /
TaskGetTool / TaskListTool
/ TaskUpdateTool / Background t
TaskOutputTool /
TaskStopTool
TodoWriteTool Write todos (l
ListMcpResourcesTool /
MCP resource
ReadMcpResourceTool
SleepTool Async delays
SnipTool History snipp
ToolSearchTool Tool discover
ListPeersTool List peer agen
MonitorTool Monitor MCP
EnterWorktreeTool /
Git worktree m
ExitWorktreeTool
ScheduleCronTool Schedule cro
RemoteTriggerTool Trigger remot
WorkflowTool Execute work


---
*Page 25*


Tool What It Doe
ConfigTool Modify setting
Advanced fea
TungstenTool
only)
MCPTool Generic MCP
McpAuthTool MCP server au
Structured ou
SyntheticOutputTool
JSON schema
Suggest back
SuggestBackgroundPRTool
ternal only)
Verify plan ex
VerifyPlanExecutionTool
CLAUDE_COD
Context wind
CtxInspectTool (gated by
CONTEXT_CO
Terminal pan
TerminalCaptureTool
by TERMINAL
CronCreateTool / Granular cron
CronDeleteTool / ment (under
CronListTool ScheduleCr


---
*Page 26*


Tool What It Doe
SendUserFile /
PushNotification / KAIROS-exclu
SubscribePR
Tools are registered via getAllBase-
Tools() and filtered by feature gates, user
type, environment flags, and permission deny
rules. Thereʼs a tool schema cache
(toolSchemaCache.ts ) that caches JSON
schemas for prompt efficiency.
The Permission and
Security System
Claude Codeʼs permission system in
tools/permissions/
is far more sophisti-
cated than “allow/deny”:
Permission Modes: default (interactive
prompts), auto (ML-based auto-approval via
transcript classifier), bypass (skip checks),
yolo (deny all - ironically named)
Risk Classification: Every tool action is classi-
fied as LOW, MEDIUM, or HIGH risk. Thereʼs a


---
*Page 27*


YOLO classifier - a fast ML-based permission
decision system that decides automatically.
Protected Files: .gitconfig, .bashrc,
.zshrc, .mcp.json, .claude.json and
others are guarded from automatic editing.
Path Traversal Prevention: URL-encoded tra-
versals, Unicode normalization attacks, back-
slash injection, case-insensitive path manipu-
lation - all handled.
Permission Explainer: A separate LLM call ex-
plains tool risks to the user before they ap-
prove. When Claude says “this command will
modify your git config” - that explanation is it-
self generated by Claude.
Hidden Beta Headers and
Unreleased API Features
constants/betas.ts
The file reveals ev-
ery beta feature Claude Code negotiates with
the API:
1 'interleaved-thinking-2025-05-14'
2 'context-1m-2025-08-07'
3 'structured-outputs-2025-12-15'
4 'web-search-2025-03-05'


---
*Page 28*


5 'advanced-tool-use-2025-11-20'
6 'effort-2025-11-24'
7 'task-budgets-2026-03-13'
8 'prompt-caching-scope-2026-01-05'
9 'fast-mode-2026-02-01'
10 'redact-thinking-2026-02-12'
11 'token-efficient-tools-2026-03-28'
12 'afk-mode-2026-01-31'
13 'cli-internal-2026-02-09'
14 'advisor-tool-2026-03-01'
15 'summarize-connector-text-2026-03-
redact-thinking, afk-mode, and advi-
sor-tool are also not released.
Upcoming Models -
Capybara, Opus 4.7, and
Sonnet 4.8
The codebase contains references to unre-
leased Anthropic models that havenʼt been
publicly announced:
Claude “Capybara” - A new model family
already in version 2, with a variant called
capybara-v2-fast being prepared
with a 1M context window


---
*Page 29*


Capybara comes in “fast” and regular
thinking tiers
Opus 4.7 and Sonnet 4.8 are already ref-
erenced within the code
Production Engineering Around
Capybara
The code reveals that Anthropic observed a
real production failure mode: Capybara can
prematurely stop generating when the
prompt shape resembles a turn boundary af-
ter tool results. Rather than waiting for a
model fix, they mitigated it with prompt-
shape surgery:
1. Force a safe boundary marker (Tool
loaded.) to prevent ambiguous turn
boundaries
2. Relocate risky sibling blocks that could
trigger premature stops
3. Smoosh reminder text into tool results
to maintain generation flow
4. Add non-empty markers for empty tool
outputs to avoid confusing the model
All of this is wrapped with kill-switchable
gates (tengu_* prefixed flags) so rollout can
be staged and reverted quickly.


---
*Page 30*


Comments include concrete A/B test evi-
dence (not hand-wavy), which typically
means this area was launch-critical and
closely monitored
Comments like “un-gate once validated
on external via A/B” confirm that
ant/internal users are canary lanes be-
fore broader rollout
The strongest interpretation: Anthropic is
working toward a Capybara model family
with a fast-tier variant (capybara-v2-
fast), supporting up to 1M context
Nothing confirms a launch date or official SKU
naming, but the implementation signatures
fit a model family that is actively being pre-
pared for release ;)
Feature Gating - Internal vs.
External Builds
This is one of the most architecturally inter-
esting parts of the codebase.
Claude Code uses compile-time feature flags
via Bunʼs feature() function from
bun:bundle. The bundler constant-folds
these and dead-code-eliminates the gated


---
*Page 31*


branches from external builds. The complete
list of known flags:
What It
Flag
Gates
Always-o
PROACTIVE / KAIROS assistan
mode
Brief
KAIROS_BRIEF
comman
Remote
BRIDGE_MODE control v
claude.a
Backgro
DAEMON daemon
mode
VOICE_MODE Voice inp
Workflow
WORKFLOW_SCRIPTS
automat
COORDINATOR_MODE Multi-ag
orchestr


---
*Page 32*


What It
Flag
Gates
tion
AFK mod
TRANSCRIPT_CLASSIFIER (ML auto
approva
Compan
BUDDY
pet syste
Client
NATIVE_CLIENT_ATTESTATION
attestati
History
HISTORY_SNIP
snipping
Skill
EXPERIMENTAL_SKILL_SEARCH
discover
Additionally, USER_TYPE === 'ant' gates
Anthropic-internal features: staging API ac-
cess (claude-ai.staging.ant.dev), inter-
nal beta headers, Undercover mode, the
/security-review command,
ConfigTool, TungstenTool, and debug


---
*Page 33*


prompt dumping to
~/.config/claude/dump-prompts/.
GrowthBook handles runtime feature gating
with aggressively cached values. Feature flags
prefixed with tengu_ control everything
from fast mode to memory consolidation.
Many checks use
getFeatureValue_CACHED_MAY_BE_STALE
() to avoid blocking the main loop - stale
data is considered acceptable for feature
gates.
Other Notable Findings
The Upstream Proxy
upstreamproxy/
The directory contains a
container-aware proxy relay that uses
prctl(PR_SET_DUMPABLE, 0)
to prevent
same-UID ptrace of heap memory. It reads
session tokens from
/run/ccr/session_token in CCR contain-
ers, downloads CA certificates, and starts a lo-
cal CONNECT→WebSocket relay. Anthropic
API, GitHub, npmjs.org, and pypi.org are ex-
plicitly excluded from proxying.


---
*Page 34*


Bridge Mode
A JWT-authenticated bridge system in
bridge/
for integrating with claude.ai.
Supports work modes: 'single-session' |
'worktree' | 'same-dir'. Includes
trusted device tokens for elevated security
tiers.
Model Codenames in Migrations
migrations/
The directory reveals the in-
ternal codename history:
migrateFennecToOpus - “Fennec” (the
fox) was an Opus codename
migrateSonnet1mToSonnet45 - Sonnet
with 1M context became Sonnet 4.5
migrateSonnet45ToSonnet46 - Sonnet
4.5 → Sonnet 4.6
resetProToOpusDefault - Pro users
were reset to Opus at some point
Attribution Header
Every API request includes:
x-anthropic-billing-header: cc_versi
cc_entrypoint={ENTRYPOINT}; cch={AT


---
*Page 35*


The NATIVE_CLIENT_ATTESTATION feature
lets Bunʼs HTTP stack overwrite the
cch=00000 placeholder with a computed
hash - essentially a client authenticity check
so Anthropic can verify the request came from
a real Claude Code install.
Computer Use - “Chicago”
Claude Code includes a full Computer Use im-
plementation, internally codenamed
“Chicago”, built on @ant/computer-use-
mcp. It provides screenshot capture,
click/keyboard input, and coordinate trans-
formation. Gated to Max/Pro subscriptions
(with an ant bypass for internal users).
Pricing
For anyone wondering - all pricing in
utils/modelCost.ts
matches
Anthropicʼs public pricing exactly. Nothing
newsworthy there.
Final Thoughts
This is, without exaggeration, one of the most
comprehensive looks weʼve ever gotten at
how the production AI coding assistant works


---
*Page 36*


under the hood. Through the actual source
code.
A few things stand out:
The engineering is genuinely impressive.
This isnʼt a weekend project wrapped in a CLI.
The multi-agent coordination, the dream sys-
tem, the three-gate trigger architecture, the
compile-time feature elimination - these are
deeply considered systems.
Thereʼs a LOT more coming. KAIROS (always-
on Claude), ULTRAPLAN (30-minute remote
planning), the Buddy companion, coordinator
mode, agent swarms, workflow scripts - the
codebase is significantly ahead of the public
release. Most of these are feature-gated and
invisible in external builds.
The internal culture shows. Animal code-
names (Tengu, Fennec, Capybara), playful
feature names (Penguin Mode, Dream
System), a Tamagotchi pet system with gacha
mechanics. Some people at Anthropic is hav-
ing fun.
If thereʼs one takeaway this has, itʼs that secu-
rity is hard. But .npmignore is harder, ap-
parently :P


---
*Page 37*


A writeup by Kuber Mehta
MindMap
Trending Posts
Claude Code's
Entire Source
Code Got
Leaked via a
Sourcemap in
npm, Let's Talk
About it
Mar 31, 2026
Clawdbot will
be dead in a
month
Jan 28, 2026
The Bubble is
Not What You
Think
Jan 14, 2026


---
*Page 38*


© 2026 kuberwastaken
LinkedIn X GitHub