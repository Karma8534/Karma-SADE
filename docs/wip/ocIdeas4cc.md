# ocIdeas4cc

*Converted from: ocIdeas4cc.PDF*



---
*Page 1*


Open in app
11
Search Write
Member-only story
Steal This OpenClaw
Setup: The Tools +
Skills Rules That Make
AI Agents Actually
Productive
Mikhail Petrusheuski Follow 5 min read · Feb 24, 2026


---
*Page 2*


I love AI agents. OpenClaw. Local setups. Custom
skills. All of it.
But the “wow” phase ends the same way for most
teams:
agent has too many tools
it picks the wrong one
skills add noise instead of leverage
and suddenly your “copilot” becomes an expensive
chaos machine


---
*Page 3*


The fix isn’t “a smarter model.”
It’s tool rules + skill hygiene + workflow
boundaries.
This post gives you copy-paste ready:
OpenClaw tools baseline (safe + productive)
role-based agent split (coder, support, research)
skills config that doesn’t turn into a junk
drawer
skill gating patterns (requires, env/config)
a simple human rule that prevents most agent
mistakes
The “Make AI behave like your workflow”
setup (Tools policy)
Most teams start with too much access.
That’s the mistake.
Start with a useful default, then tighten it.


---
*Page 4*


~/.openclaw/openclaw.json (copy/paste baseline)
{
"tools": {
"profile": "coding",
"deny": ["gateway", "cron", "sessions_spawn", "se
}
}
Why this works
coding gives a practical base for repo work
deny removes the “persistent control-plane”
foot-guns
agent stays useful without being reckless
This one block eliminates a lot of AI drift because
the agent stops trying to “orchestrate the world”
and focuses on actual work.
Turn one chaotic agent into 3 useful ones
(Role-based agents)
One agent for everything sounds nice.


---
*Page 5*


Until it starts mixing coding, support, and
automation in the same session.
Split by role.
(copy/paste)
agents.list
{
"tools": {
"profile": "coding",
"deny": ["gateway", "cron", "sessions_spawn", "se
},
"agents": {
"list": [
{
"id": "coder",
"tools": {
"profile": "coding",
"deny": ["gateway", "cron"]
}
},
{
"id": "support",
"tools": {
"profile": "messaging",
"allow": ["slack"],
"deny": ["group:runtime", "group:fs", "gate
}
},
{
"id": "research",


---
*Page 6*


"tools": {
"allow": ["group:web", "read", "sessions_li
"deny": ["group:runtime", "group:automation
}
}
]
}
}
What changes immediately
coding agent stops drafting support messages
support agent stops touching files or shell
research agent stops trying to “fix” things
This is the difference between “smart demo” and
“predictable teammate.”
The “smallest useful tool surface” rule
(Use groups, not giant lists)
If your config has 40 tool names, nobody will
maintain it.
Use groups.
Example: safe coding mode (no shell execution)


---
*Page 7*


{
"tools": {
"profile": "coding",
"deny": ["group:runtime"]
}
}
Great for:
refactors
patch generation
code review support
PR summaries
No accidental exec loops.
No random command spam.
Example: research-only mode
{
"tools": {
"allow": ["group:web", "read", "sessions_list", "
"deny": ["group:runtime", "group:automation", "gr


---
*Page 8*


}
}
If you want faster answers, don’t just switch
models.
Shrink the tool surface.
Skills that help (instead of polluting every
prompt)
Skills are powerful.
But “install everything” is the fastest way to make
your agent worse.
The rule:
Every skill must justify one weekly workflow.
If it doesn’t save time weekly, disable it.
config (copy/paste starter)
skills
{
"skills": {
"allowBundled": ["gemini", "peekaboo"],


---
*Page 9*


"load": {
"extraDirs": [
"~/Projects/openclaw-skills-private",
"~/Projects/team-shared-skills"
],
"watch": true,
"watchDebounceMs": 250
},
"entries": {
"peekaboo": { "enabled": true },
"my-team-repo-assistant": {
"enabled": true,
"env": {
"REPO_MODE": "read-only"
},
"config": {
"projectType": "dotnet",
"defaultBranch": "main"
}
},
"old-experiment-skill": { "enabled": false }
}
}
}
Why this matters
extraDirs gives you private/team skills without
clutter
enabled is a fast feature flag


---
*Page 10*


per-skill env / config avoids hardcoding
behavior
watcher speeds up local iteration when building
skills
Make skills self-filtering (so the agent
sees only what can actually run)
A huge source of noise:
skills that look available but can’t work
missing CLI
missing API key
wrong OS
disabled integration
Use requires in SKILL.md.
(copy/paste pattern)
SKILL.md
---
name: jira-helper
description: Create and update Jira tasks using our t
metadata:
openclaw:


---
*Page 11*


requires:
env: ["JIRA_API_TOKEN"]
config: ["integrations.jira.enabled"]
bins: ["git"]
os: ["darwin", "linux"]
primaryEnv: "JIRA_API_TOKEN"
---
Use this skill to:
- create backlog items
- create bugs with repro steps
- create subtasks from a parent task
- format acceptance criteria in team style
This keeps dead skills out of the agent context and
reduces pointless tool attempts.
Less noise.
Lower token usage.
Better behavior.
Provider/model-specific tool limits
(underrated performance trick)
Not every model is equally good at tool use.
Some are great with repo edits.
Some are better for plain reasoning.


---
*Page 12*


Some over-call tools.
Don’t give them all the same access.
(copy/paste idea)
tools.byProvider
{
"tools": {
"profile": "coding",
"byProvider": {
"openai/gpt-5.2": {
"allow": ["group:fs", "group:web", "group:run
},
"google-antigravity": {
"profile": "minimal"
}
}
}
}
Result:
strong tool-user model gets full coding flow
weaker/cheaper/faster endpoint gets a
constrained surface
fewer bad tool calls


---
*Page 13*


better latency/cost tradeoff
Reusable workflows (the part that actually
saves time)
Tools + skills are the foundation.
Workflows are where the payoff happens.
Here are 5 reusable workflows I’d keep in every
engineering setup.
1. Plan-first (before any code)
“Write a 6–10 step plan. For each step: files to
change, risk, and how we’ll test it. Don’t write code
yet.”
2. Smallest diff
“Implement with the smallest possible diff. Don’t
reformat. Don’t rename unrelated things.”
3. Proof-first PR
“Generate a PR summary with: change summary
(max 5 bullets), test proof, risks, rollback note,
reviewer focus.”


---
*Page 14*


4. Root cause first
“Explain the root cause in one paragraph before
proposing a fix. Then propose the smallest safe
fix.”
5. Incident update formatter
“Draft a stakeholder update with: impact, current
status, workaround, next ETA, next action owner.
No speculation.”
These are simple.
That’s the point.
You want workflows the whole team reuses — not
prompts that look clever and nobody runs twice.
The human rule that changes everything:
“Proof or it’s just text”
Here’s the simplest AI policy I’ve seen that actually
works:
✅
AI-generated code is allowed
✅
AI-generated summaries are allowed


---
*Page 15*


✅
AI-generated fixes are allowed
But AI-generated output must include proof:
tests, or
reproducible steps, or
logs/telemetry evidence
If there’s no proof, it’s not “done.”
It’s a draft.
Final takeaway
Most OpenClaw setups fail for the same reason:
too many tools
weak boundaries
skill sprawl
The fix isn’t better prompting.
It’s:
tool policy


---
*Page 16*


skill hygiene
role-based agents
reusable workflows
proof
Set those once, and OpenClaw stops acting like a
demo.
It starts acting like a teammate.
#openclaw #aiagents #developerproductivity
#dotnet #automation #engineeringmanagement
#llm #devtools
Openclaw Aiagents Ai Developer Productivity Dotnet
Engineering Management
Written by Mikhail Petrusheuski
Follow
462 followers · 22 following


---
*Page 17*


No responses yet
To respond to this story,
get the free Medium app.
More from Mikhail Petrusheuski
Mikhail Petrusheuski Mikhail Petrusheuski
🚀
MCP C# SDK v1.0: Stop What’s New in .NET
P ti St t 11 P i 1 A D
I love new SDK releases. .NET doesn’t slow down —
d NET 11 P i 1 i
Feb 27 Feb 22


---
*Page 18*


Mikhail Petrusheuski Mikhail Petrusheuski
The .NET AI Stack Just The .NET Agent Stack
G t R l Thi W k I G i U MCP
2026 isn’t about “AI writes The AI ecosystem is moving
d ” It’ b t hi i f t b t th t i t
Feb 12 Mar 9
See all from Mikhail Petrusheuski
Recommended from Medium
Alex Rozdolskyi Roberto Capodieci


---
*Page 19*


5 OpenClaw AI Agents 006 —
A t ti Th t G O Cl + G l
We don’t have bandwidth” is You probably didn’t set out to
b i td t d b f ll ti il
Feb 16 Mar 12
Mikhail Petrusheuski In by
AI Advanc… Marco Rodrigu…
Beyond Prompt Glue:
10 Tips to Make Your
Wh Thi W k
Lif E i With
The AI conversation is still too
Learn the most useful
b d ith d l
d h t i t ll
Mar 23 Mar 7


---
*Page 20*


In by Reza Rezvani
Bootcamp nardaimonia
AI Agent Skills at Scale:
What Claude Cowork
Wh t B ildi 170
t ll d
The AI skills ecosystem is
The complete breakdown of
i i th d
h t it h dl h t t it
Mar 7 Mar 13
See more recommendations