# GooleADKPart2

*Converted from: GooleADKPart2.pdf*



---
*Page 1*


3/25/26, 2:08 PM ADK Skill Tool That Write Skills: Building Self-Extending AI Agents with Google ADK | Part-4 | by Simranjeet Singh | Mar, 2026 | Artifi…
Artificial Intelligence in Pla…
Member-only story
ADK Skill Tool That Write Skills:
Building Self-Extending AI Agents
with Google ADK | Part-4
Simranjeet Singh Following 19 min read · 3 days ago
50
Most developers build AI agents the same way they
assemble IKEA furniture.
https://ai.plainenglish.io/adk-skill-tool-that-write-skills-building-self-extending-ai-agents-with-google-adk-part-4-7b395d40b282 1/30


---
*Page 2*


3/25/26, 2:08 PM ADK Skill Tool That Write Skills: Building Self-Extending AI Agents with Google ADK | Part-4 | by Simranjeet Singh | Mar, 2026 | Artifi…
An agent that can write its Own Skills
You lay out all the parts. You follow the instructions. You screw everything
together in the right order. And when you are done, you have exactly what
the box promised — nothing more, nothing less. The BILLY bookcase does
not spontaneously grow a new shelf because you bought more books. The
agent does not spontaneously grow a new capability because your users
discovered a new need.
You shipped your agent on a Friday. It was good. It handled five things
beautifully. Code review. Git workflows. PR summaries. Commit message
formatting. Changelog generation. Your team was impressed. You were
proud.
Monday morning, someone on the team typed this into the agent:
“Can you review my Dockerfile?”
https://ai.plainenglish.io/adk-skill-tool-that-write-skills-building-self-extending-ai-agents-with-google-adk-part-4-7b395d40b282 2/30


---
*Page 3*


3/25/26, 2:08 PM ADK Skill Tool That Write Skills: Building Self-Extending AI Agents with Google ADK | Part-4 | by Simranjeet Singh | Mar, 2026 | Artifi…
Silence. Then a hallucinated response that confidently described Docker
best practices it had never been taught, mixing correct advice with subtly
wrong advice in a way that looked authoritative and was quietly dangerous.
Or worse: a polite refusal. “I’m not able to help with that.”
So you went back to the code. You added a new tool function, or you stuffed
another 800 tokens of Docker instructions into the system prompt that was
already too long, or you wired in a new Python function and hoped it did not
break the five things that were already working. Then you tested. Then you
redeployed. The agent was “done” again.
Until Tuesday, when someone asked about Kubernetes.
This is the static agent trap, and every developer who has shipped an agent
to real users has fallen into it. The agent is a finished product. It has edges.
Users find those edges immediately, because users always need exactly the
thing you did not build. Every new capability costs you a developer, a
deployment pipeline, and a delay measured in hours or days while users are
blocked or getting bad answers.
The entire premise of the static agent is flawed. You cannot anticipate every
capability a real user will need. You cannot encode every domain of
knowledge into a system prompt before you ship. You cannot keep
redeploying every time the gap between what the agent knows and what
users need grows by one more use case.
So here is the question: this blog spends the next 15 minutes answering:
What if the agent could feel the edge of its own knowledge, understand that
it has reached a gap, write the instructions for crossing that gap, and add
https://ai.plainenglish.io/adk-skill-tool-that-write-skills-building-self-extending-ai-agents-with-google-adk-part-4-7b395d40b282 3/30


---
*Page 4*


3/25/26, 2:08 PM ADK Skill Tool That Write Skills: Building Self-Extending AI Agents with Google ADK | Part-4 | by Simranjeet Singh | Mar, 2026 | Artifi…
that capability to itself while the user is still in the conversation, without a
single developer touching the code?
Self Extending AI Agent
Not a hypothetical. Not a research paper. A working Python project you can
clone, run, and extend today.
https://ai.plainenglish.io/adk-skill-tool-that-write-skills-building-self-extending-ai-agents-with-google-adk-part-4-7b395d40b282 4/30


---
*Page 5*


3/25/26, 2:08 PM ADK Skill Tool That Write Skills: Building Self-Extending AI Agents with Google ADK | Part-4 | by Simranjeet Singh | Mar, 2026 | Artifi…
By the end of this post, you will have built an agent that grows its own
capabilities on demand. An agent that, when asked about Docker for the first
time, does not hallucinate and does not refuse. Instead, it says, "I don’t have a
skill for that yet. Let me write one.” And then it does.
Let’s build it.
Google ADK In-Depth Series of Learning Agentic AI
1. Google ADK in 2026: The Complete Beginner’s Guide to Building AI
Agents | Part-1
2. Your First Google ADK Agent with Skills: Build a Weather and News Agent
in 30 Minutes | Part-2
3. Mastering ADK Tools: Function Tools, MCP Tools, OpenAPI Tools &
When to Use Each | Part-3
4. ADK Skill Tool That Write Skills: Building Self-Extending AI Agents with
Google ADK | Part-4
5. Google Agent Skills Explained: The Open Standard Changing How AI
Agents Work | Part-5
6. ADK Memory, Sessions & State: Building Agents That Remember | Part-6
7. Multi-Agent Systems with ADK: Build Your Own AI Research Team | Part-7
8. Gemini CLI + Agent Skills: Supercharge Your Developer Workflow | Part-8
9. Firebase + Agent Skills: Add AI Superpowers to Your Firebase App | Part-9
10. Grounding ADK Agents: Google Search, Vertex AI Search & RAG Patterns |
Part-10
https://ai.plainenglish.io/adk-skill-tool-that-write-skills-building-self-extending-ai-agents-with-google-adk-part-4-7b395d40b282 5/30


---
*Page 6*


3/25/26, 2:08 PM ADK Skill Tool That Write Skills: Building Self-Extending AI Agents with Google ADK | Part-4 | by Simranjeet Singh | Mar, 2026 | Artifi…
11. ADK + MCP: Connecting Your Agent to Any Tool in the World | Part-11
12. Build a Full-Stack AI SaaS App with Google ADK: From Idea to Live
Product | Part-12
The Project Overview
Before we write a single line of code, here is the complete picture of what
exists at the end of this blog. Reading this section takes two minutes. It will
save you ten minutes of confusion later.
The project is called the Self-Extending Developer Assistant.It is a full-stack
Google ADK application — with a Python backend, a standalone ADK agent
package, and a custom frontend — that starts its life knowing how to do two
things (code review and Git workflows) and gains the ability to learn
anything else a developer asks it to do, on the spot, by writing its own
specialist knowledge files.
Here is the complete final project structure, exactly as it looks in the GitHub
repository:
SelfExtendingAgent_ADKGoogle/
│
├── 📁 backend/ ← FastAPI server: exposes the agent over HTTP
│ └── main.py, routes, config
│
├── 📁 dev_assistant_app/ ← The ADK agent package (ADK-discoverable)
│ ├── __init__.py ← makes this folder an ADK package
│ ├── agent.py ← the brain: defines the agent, loads all skill
│ │ wires everything together in ~60 lines of Py
│ ├── tools/
│ │ └── skill_writer.py ← the pen: Python function the agent calls
https://ai.plainenglish.io/adk-skill-tool-that-write-skills-building-self-extending-ai-agents-with-google-adk-part-4-7b395d40b282 6/30


---
*Page 7*


3/25/26, 2:08 PM ADK Skill Tool That Write Skills: Building Self-Extending AI Agents with Google ADK | Part-4 | by Simranjeet Singh | Mar, 2026 | Artifi…
│ │ to write brand-new SKILL.md files to disk
│ └── skills/
│ ├── code-review/ ← pre-built, hand-crafted, always available
│ │ └── SKILL.md
│ ├── git-workflow/ ← pre-built, hand-crafted, always available
│ │ └── SKILL.md
│ └── generated/ ← starts completely empty
│ └── (fills up as the agent learns)
│
├── 📁 frontend/ ← Chat UI: HTML + CSS + JS
│ └── index.html, style.css, app.js
│
├── repro_answer.py ← standalone script to reproduce agent answers
├── requirements.txt ← all Python dependencies in one place
├── run.sh ← one-command launcher: starts backend + fronte
├── .gitignore
├── Already-Skill-Use.png ← screenshot: agent reusing an existing skill
└── Skill-Creator-Demo.png ← screenshot: agent creating a new skill live
This is more than a script — it is a full-stack application. Three layers work
together: the frontend gives users a chat interface, the backend serves the
agent over HTTP so the frontend can call it, and the dev_assistant_app is the
ADK agent package where all the intelligence lives.
Here is what each piece does and why it exists.
 
dev_assistant_app/agent.py is the root agent definition. It loads all available
skills at startup, registers the skill_writer tool, and defines the agent's
instructions — including the four-step procedure it follows whenever a user
asks for something it does not know yet. This is the file you touch most
during development and least after deployment.
dev_assistant_app/tools/skill_writer.py is the capability that makes this
project different from every other ADK tutorial. It is a Python function — a
regular ADK tool, nothing exotic — that takes a skill name and a complete
https://ai.plainenglish.io/adk-skill-tool-that-write-skills-building-self-extending-ai-agents-with-google-adk-part-4-7b395d40b282 7/30


---
*Page 8*


3/25/26, 2:08 PM ADK Skill Tool That Write Skills: Building Self-Extending AI Agents with Google ADK | Part-4 | by Simranjeet Singh | Mar, 2026 | Artifi…
SKILL.md content string, validates both against the agentskills.io
specification, and writes the skill to disk in the skills/generated/ folder. The
agent supplies the content. The tool handles the filesystem. Together they
form the self-extension loop.
dev_assistant_app/skills/code-review/SKILL.md and
dev_assistant_app/skills/git-workflow/SKILL.md are the two pre-built skills
the agent ships with. They encode real engineering best practices in the
agentskills.io format and serve a dual purpose: genuine capabilities from
day one, and worked examples the agent can reference when writing new
skills for itself.
backend/ is the FastAPI server that wraps the ADK agent and exposes it over
HTTP. The frontend communicates with this server. If you have used ADK's
built-in adk web, think of this as a production-ready equivalent you fully
control.
frontend/ is the chat interface — plain HTML, CSS, and JavaScript. No
framework, no build step. Open a browser, type a message, see the agent
respond. The screenshots in the repository ( Already-Skill-Use.png and
Skill-Creator-Demo.png) were captured from this UI.
run.sh launches the entire stack in one command: backend and frontend
together. No juggling multiple terminal windows.
repro_answer.py is a standalone Python script for reproducing a specific
agent answer outside the web stack — useful for debugging and testing
individual prompts without starting the full application.
https://ai.plainenglish.io/adk-skill-tool-that-write-skills-building-self-extending-ai-agents-with-google-adk-part-4-7b395d40b282 8/30


---
*Page 9*


3/25/26, 2:08 PM ADK Skill Tool That Write Skills: Building Self-Extending AI Agents with Google ADK | Part-4 | by Simranjeet Singh | Mar, 2026 | Artifi…
skills/generated/ is the most interesting folder in the project because right
now it is empty. By the end of the demo, it will contain at least one folder the
agent wrote entirely by itself during a live conversation — a valid, standard-
compliant, portable skill that did not exist before the user asked a question.
That empty folder is the whole point.
That empty folder is the whole point.
Prerequisites and Project Setup
If you followed Blog 1 in this series, your environment is already 90% ready.
Pick up from Step 2 below. If this is your first blog in the series, go read Blog
1 first.
Step 1: Clone the repository
Rather than scaffolding from scratch, this project ships as a complete,
runnable repository. Clone it directly:
git clone https://github.com/simranjeet97/SelfExtendingAgent_ADKGoogle.git
cd SelfExtendingAgent_ADKGoogle
Step 2: Create a virtual environment and install dependencies
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate # macOS / Linux
# .venv\Scripts\activate.bat # Windows CMD
# .venv\Scripts\Activate.ps1 # Windows PowerShell
https://ai.plainenglish.io/adk-skill-tool-that-write-skills-building-self-extending-ai-agents-with-google-adk-part-4-7b395d40b282 9/30


---
*Page 10*


3/25/26, 2:08 PM ADK Skill Tool That Write Skills: Building Self-Extending AI Agents with Google ADK | Part-4 | by Simranjeet Singh | Mar, 2026 | Artifi…
# Install all dependencies from requirements.txt
pip install -r requirements.txt
The requirements.txt at the repository root covers both the ADK backend
and all supporting libraries, one install command covers the entire stack.
Step 3: Add your API key to
.env
Create a .env file in the project root and add the following, replacing the
placeholder with your actual key from aistudio.google.com/apikey and Tavily
as well for Web-Search:
GOOGLE_GENAI_USE_VERTEXAI=FALSE
# ── API Keys ──────────────────────────────────────────────────────────────────
# Set your keys here. Never commit this file to version control.
GEMINI_API_KEY=your-gemini-api-key-here
TAVILY_API_KEY=your-tavily-api-key-here
 
Step 4: Launch the full stack
bash run.sh
run.sh starts both the backend server and the frontend in a single
command. Open your browser at the URL printed in the terminal (typically
http://localhost:8000 for the backend and the frontend served on its own
port). You should see the chat UI immediately.
https://ai.plainenglish.io/adk-skill-tool-that-write-skills-building-self-extending-ai-agents-with-google-adk-part-4-7b395d40b282 10/30


---
*Page 11*


3/25/26, 2:08 PM ADK Skill Tool That Write Skills: Building Self-Extending AI Agents with Google ADK | Part-4 | by Simranjeet Singh | Mar, 2026 | Artifi…
Alternatively, if you want to run the ADK agent directly without the custom
frontend:
cd dev_assistant_app adk web
Open http://localhost:8000, select dev_assistant from the dropdown, and
you are in the ADK development UI.
At this point your project is fully running — both pre-built skills loaded, full
stack live, frontend connected to backend. The skills are not written by you
yet (they ship with the repo). The agent is not empty yet. Each of the next
sections explains one layer of the build so you can understand, modify, and
extend what you cloned.
Layer 1: Building the Pre-Made Skills
Here is a principle worth writing down before we touch any code:
You cannot build an agent that writes good skills until you understand what
a good skill looks like.
The two skills in this section are not just starter content. They are the
benchmark — the worked examples the agent will reference, consciously or
not, when it generates new skills for itself. The quality of the agent-written
skills will trace directly back to the quality of the skills you write here. Spend
time on these. They are worth it.
Skill 1:
code-review
Located at dev_assistant_app/skills/code-review/SKILL.md:
https://ai.plainenglish.io/adk-skill-tool-that-write-skills-building-self-extending-ai-agents-with-google-adk-part-4-7b395d40b282 11/30


---
*Page 12*


3/25/26, 2:08 PM ADK Skill Tool That Write Skills: Building Self-Extending AI Agents with Google ADK | Part-4 | by Simranjeet Singh | Mar, 2026 | Artifi…
---
name: code-review
description: >
Perform thorough, structured code reviews on Python, JavaScript,
TypeScript, or any common language. Use this skill when asked to
review code, audit a function, check a pull request, or give
feedback on code quality, security, or performance. Use even if
the user says "take a look at this" or "what do you think of this."
license: Apache-2.0
metadata:
author: your-github-username
version: "1.0"
---
# Code Review
## Your role
You are a senior software engineer performing a structured code review.
Be specific, constructive, and direct. Every comment must be actionable.
Prioritise: Security first, Correctness second, Performance third, Style last.
## Review process
1. Read the entire code before commenting on any single line
2. Categorise every comment as [Critical], [Suggestion], or [Nit]
3. Check every item in the Critical Checklist below before proceeding
## Critical Checklist (run on every review, no exceptions)
- [ ] No hardcoded secrets, API keys, tokens, or credentials
- [ ] No SQL built via string concatenation (SQL injection vector)
- [ ] No bare `except:` clauses swallowing errors silently
- [ ] No obvious N+1 query patterns in database-touching code
- [ ] Input validation present on all user-supplied data
## Output format
**Summary** (2 sentences max)
**Critical Issues** (if any)
**Suggestions** (optional improvements)
**Nits** (minor style points, optional)
**Verdict**: Approve / Request Changes / Needs Discussion
Skill 2:
git-workflow
Located at dev_assistant_app/skills/git-workflow/SKILL.md:
---
name: git-workflow
https://ai.plainenglish.io/adk-skill-tool-that-write-skills-building-self-extending-ai-agents-with-google-adk-part-4-7b395d40b282 12/30


---
*Page 13*


3/25/26, 2:08 PM ADK Skill Tool That Write Skills: Building Self-Extending AI Agents with Google ADK | Part-4 | by Simranjeet Singh | Mar, 2026 | Artifi…
description: >
Guide developers through Git operations, branching strategies,
commit conventions, merge/rebase decisions, and pull request
workflows. Use when the user asks about Git commands, branching,
commits, merging, rebasing, resolving conflicts, or setting up
a Git workflow for a team or project.
metadata:
author: your-github-username
version: "1.0"
---
# Git Workflow
## Core philosophy
Prefer clarity over cleverness. Every Git operation should leave
the repository history more understandable, not less.
## Commit message convention
Follow Conventional Commits: `type(scope): description`
Types: feat, fix, docs, style, refactor, test, chore
Example: `feat(auth): add OAuth2 login flow`
## Branching strategy
- `main`: always deployable, protected
- `develop`: integration branch for features
- `feature/name`: one feature per branch
- `hotfix/name`: production fixes only
## When to merge vs rebase
- Merge: preserving history of a feature branch into main
- Rebase: cleaning up local commits before a PR
- Never rebase public branches that others are using
## Conflict resolution process
1. `git status` to see all conflicted files
2. Open each file and resolve the `<<<<<<<` markers
3. `git add` each resolved file
4. `git commit` to complete the merge
5. Verify with `git log --oneline --graph`
Your project’s dev_assistant_app/skills/ now has this structure:
skills/
├── code-review/
│ └── SKILL.md ← complete, production-quality, ready to load
├── git-workflow/
│ └── SKILL.md ← complete, intentionally lean, gap ready to be filled
https://ai.plainenglish.io/adk-skill-tool-that-write-skills-building-self-extending-ai-agents-with-google-adk-part-4-7b395d40b282 13/30


---
*Page 14*


3/25/26, 2:08 PM ADK Skill Tool That Write Skills: Building Self-Extending AI Agents with Google ADK | Part-4 | by Simranjeet Singh | Mar, 2026 | Artifi…
└── generated/
└── (still empty — not for long)
Layer 2: The Agent That Loads Skills Dynamically
The two skills are written. Now we build the agent inside
dev_assistant_app/agent.py that loads them.
We are not going to load them the obvious way — by hardcoding two
load_skill_from_dir calls. That approach works for two skills. It breaks the
moment the agent writes a third one that you did not anticipate. Instead, we
build the loading mechanism the right way from the start: a helper function
that scans a folder, finds every valid skill inside it, and loads them all
automatically.
import pathlib
from google.adk import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools import skill_toolset
# ── Helper: scan a folder and load every Skill inside it ─────────────────────
def load_all_skills_from_dir(skills_dir: pathlib.Path) -> list:
"""
Scans a directory for sub-folders that contain a SKILL.md file
and loads each one as an ADK Skill object.
When the agent writes a new SKILL.md into skills/generated/,
this function finds it automatically on the next startup.
No code change needed. No new import. No manual wiring.
"""
skills = []
if not skills_dir.exists():
return skills
for skill_dir in sorted(skills_dir.iterdir()):
if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
skills.append(load_skill_from_dir(skill_dir))
print(f" Loaded skill: {skill_dir.name}")
return skills
https://ai.plainenglish.io/adk-skill-tool-that-write-skills-building-self-extending-ai-agents-with-google-adk-part-4-7b395d40b282 14/30


---
*Page 15*


3/25/26, 2:08 PM ADK Skill Tool That Write Skills: Building Self-Extending AI Agents with Google ADK | Part-4 | by Simranjeet Singh | Mar, 2026 | Artifi…
# ── Load Skills from both hand-crafted and generated folders ──────────────────
SKILLS_ROOT = pathlib.Path(__file__).parent / "skills"
print("Loading skills...")
code_review_skill = load_skill_from_dir(SKILLS_ROOT / "code-review")
git_workflow_skill = load_skill_from_dir(SKILLS_ROOT / "git-workflow")
generated_skills = load_all_skills_from_dir(SKILLS_ROOT / "generated")
all_skills = [code_review_skill, git_workflow_skill] + generated_skills
print(f" Total skills loaded: {len(all_skills)}")
# ── Wrap all Skills in a SkillToolset ─────────────────────────────────────────
dev_toolset = skill_toolset.SkillToolset(skills=all_skills)
# ── Define the root agent ─────────────────────────────────────────────────────
root_agent = Agent(
model="gemini-2.5-flash",
name="dev_assistant",
description="A software engineering assistant with extensible skills.",
instruction=(
"You are an expert software engineering assistant. "
"You have access to specialist skills for code review and Git workflows. "
"When a user asks for something outside your current skills, "
"let them know you can learn it by writing a new skill. "
"Always be specific, actionable, and concise."
),
tools=[dev_toolset],
)
Now run the full stack and verify the two pre-built skills work:
bash run.sh
Open the frontend in your browser and try these prompts:
Prompt 1: Explain me about Redis Use in Node Js
https://ai.plainenglish.io/adk-skill-tool-that-write-skills-building-self-extending-ai-agents-with-google-adk-part-4-7b395d40b282 15/30


---
*Page 16*


3/25/26, 2:08 PM ADK Skill Tool That Write Skills: Building Self-Extending AI Agents with Google ADK | Part-4 | by Simranjeet Singh | Mar, 2026 | Artifi…
The redis-node Skill activates. The agent reads the query and find the
suitable skill and then answer the question. This is the same event loop from
Blog 1, now with a Skill driving the context instead of a hardcoded system
prompt.
Everything works. The foundation is solid. The two pre-built Skills load,
activate correctly, and produce structured, consistent responses.
Now comes the part no other ADK tutorial covers.
https://ai.plainenglish.io/adk-skill-tool-that-write-skills-building-self-extending-ai-agents-with-google-adk-part-4-7b395d40b282 16/30


---
*Page 17*


3/25/26, 2:08 PM ADK Skill Tool That Write Skills: Building Self-Extending AI Agents with Google ADK | Part-4 | by Simranjeet Singh | Mar, 2026 | Artifi…
The function that makes everything else possible: load_all_skills_from_dir
is eight lines of Python. It scans for folders containing a SKILL.md and loads
each one. That is all it does. But because the agent in Section 6 will write
new SKILL.md files into skills/generated/, and because this function runs at
every startup scanning that same folder, adding a new Skill to the agent
requires zero code changes. The agent writes a file. The function finds it.
The SkillToolset loads it. The capability is live. That is the entire self-
extending mechanism, and it fits in eight lines.
Layer 3: The Tool, Giving the Agent a Pen
skill_writer
Wiring the skill_writer Tool Into the Agent
Open dev_assistant_app/agent.py. Two things change from the base version:
a new import at the top, and a completely rewritten instruction. Here is the
complete updated file:
The agent generates the content using its own language model intelligence.
The Tool handles the filesystem operations: validating the spec, creating the
directory, writing the file, confirming the result. Neither half works without
the other. Together they form the self-extension loop.
Open tools/skill_writer.py and add the following:
import pathlib
from google.adk import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools import skill_toolset
from tools.skill_writer import write_new_skill # NEW — import the pen
# ── Skill loading (unchanged) ──────────────────────────────────────────────────
SKILLS_ROOT = pathlib.Path(__file__).parent / "skills"
print("Loading skills...")
https://ai.plainenglish.io/adk-skill-tool-that-write-skills-building-self-extending-ai-agents-with-google-adk-part-4-7b395d40b282 17/30


---
*Page 18*


3/25/26, 2:08 PM ADK Skill Tool That Write Skills: Building Self-Extending AI Agents with Google ADK | Part-4 | by Simranjeet Singh | Mar, 2026 | Artifi…
code_review_skill = load_skill_from_dir(SKILLS_ROOT / "code-review")
git_workflow_skill = load_skill_from_dir(SKILLS_ROOT / "git-workflow")
generated_skills = load_all_skills_from_dir(SKILLS_ROOT / "generated")
all_skills = [code_review_skill, git_workflow_skill] + generated_skills
print(f" Total skills loaded: {len(all_skills)}")
dev_toolset = skill_toolset.SkillToolset(skills=all_skills)
# ── Agent definition (instruction updated, write_new_skill added) ─────────────
root_agent = Agent(
model="gemini-2.5-flash",
name="dev_assistant",
description="A software engineering assistant with extensible skills.",
instruction=(
"You are an expert software engineering assistant with two specialist "
"skills: code review and Git workflows. "
"\n\n"
"When a user asks for help with something beyond your current skills, "
"follow this procedure exactly: "
"1. Tell the user you do not have a skill for that yet but you can create on
"2. Ask one clarifying question if needed to understand the scope. "
"3. Write a new skill using the write_new_skill tool. Follow the "
"agentskills.io specification: valid YAML frontmatter with 'name' and "
"'description' fields, followed by clear, structured Markdown instructions.
"4. Confirm to the user that the skill has been written and will be "
"available after the next agent restart. "
"\n\n"
"Skill name rules: lowercase letters, numbers, and hyphens only. "
"Valid examples: docker-workflow, sql-optimizer, api-testing. "
"\n\n"
"Always be specific, actionable, and concise in all responses."
),
tools=[
dev_toolset,
write_new_skill, # NEW — the tool that gives the agent a pen
],
)
Demo: Skill Reuse vs. Skill Creation
Restart the full stack with bash run.sh to pick up the updated agent, then test
these two scenarios in the frontend:
Prompt 2: How to create Docker File?
 
https://ai.plainenglish.io/adk-skill-tool-that-write-skills-building-self-extending-ai-agents-with-google-adk-part-4-7b395d40b282 18/30


---
*Page 19*


3/25/26, 2:08 PM ADK Skill Tool That Write Skills: Building Self-Extending AI Agents with Google ADK | Part-4 | by Simranjeet Singh | Mar, 2026 | Artifi…
SQL is not a pre-built skill. The agent recognises the gap, calls
write_new_skill, and writes dev_assistant_app/skills/generated/sql-
queries/SKILL.md live during the conversation. Check the filesystem — the
folder will exist immediately after the agent confirms success.
Creating New SKILL for Docker
Notice also that the Skill name rules are stated explicitly in the instruction.
This redundancy is intentional. The write_new_skill tool already validates
names and returns informative errors on failure. But giving the agent the
rules upfront means it generates valid names on the first attempt rather than
learning from a validation error on the second. One round trip avoided per
Skill creation is a meaningful improvement in conversational flow.
The instruction field is your agent's operating procedure, not just its
personality. The more precisely you describe the self-extension workflow in
numbered steps, the more consistently the agent executes it. Vague
https://ai.plainenglish.io/adk-skill-tool-that-write-skills-building-self-extending-ai-agents-with-google-adk-part-4-7b395d40b282 19/30


---
*Page 20*


3/25/26, 2:08 PM ADK Skill Tool That Write Skills: Building Self-Extending AI Agents with Google ADK | Part-4 | by Simranjeet Singh | Mar, 2026 | Artifi…
instructions produce unpredictable agents. Procedural instructions produce
reliable ones. When the behaviour you need is a multi-step workflow, write
it as a multi-step workflow.
GitHub Code
GitHub - simranjeet97/SelfExtendingAgent_ADKGoogle: A self-
extending AI agent built with Google ADK…
A self-extending AI agent built with Google ADK &amp; Gemini 2.0
Flash that dynamically creates, stores, and reuses its…
github.com
Production Considerations and Known Limitations
The demo works. The pattern is real. Before you take it to production, here
is the complete honest picture of what is solid, what is experimental, and
what you need to add before real users touch it.
Senior developers skip this section at their peril. Everyone else: this is where
the tutorial ends and the engineering begins.
What is stable and production-ready today
File-based Skill loading with load_skill_from_dir is stable in ADK Python
v1.25.0 and above. The SkillToolset pattern is reliable. The write_new_skill
tool itself is not experimental in any ADK-specific sense — it is a Python
function that writes a file to disk, validates a string against a regex, and
returns a dict. There is nothing in that implementation that depends on any
ADK feature marked experimental. If Python's pathlib works on your
https://ai.plainenglish.io/adk-skill-tool-that-write-skills-building-self-extending-ai-agents-with-google-adk-part-4-7b395d40b282 20/30


---
*Page 21*


3/25/26, 2:08 PM ADK Skill Tool That Write Skills: Building Self-Extending AI Agents with Google ADK | Part-4 | by Simranjeet Singh | Mar, 2026 | Artifi…
system, write_new_skill works. The self-extension loop built in this blog is
production-deployable today, with the caveats below.
The experimental caveat you need to know
The Skills feature in ADK carries an experimental label, and one specific
limitation matters for how you design Skills going forward. Script execution
is not yet supported — the scripts/ directory in a Skill folder does not
currently execute scripts. Google This means a Skill that instructs the agent
to "run scripts/analyse.py" will have that script available on disk but the
ADK runtime will not execute it automatically.
The practical impact on this project is zero, because none of the Skills built
here use the scripts/ directory. The practical impact on your future Skills is
this: until script execution is supported, design your Skills around
instructions, references, and assets. Put your logic in ADK function tools.
Put your knowledge in SKILL.md bodies and references/ files. Reach for
scripts/ only after checking the ADK release notes for this limitation being
lifted.
The honest framing for shipping this pattern: The self-extending loop in
this blog is the mechanism, not the product. write_new_skill as written is
the right foundation. What it is missing is the approval step — the moment
where the agent shows the user what it plans to write and asks "shall I create
this?" before touching the filesystem. Add that one step and the pattern is
safe enough for production. Skip it and you are giving an LLM unreviewed
write access to your agent's capability layer, which is a decision that
deserves more thought than a Friday afternoon deploy.
What You Just Built and Why It Matters
https://ai.plainenglish.io/adk-skill-tool-that-write-skills-building-self-extending-ai-agents-with-google-adk-part-4-7b395d40b282 21/30


---
*Page 22*


3/25/26, 2:08 PM ADK Skill Tool That Write Skills: Building Self-Extending AI Agents with Google ADK | Part-4 | by Simranjeet Singh | Mar, 2026 | Artifi…
Take a step back from the code for a moment.
What you built today is not an agent with two Skills and a file-writing tool.
Those are the implementation details. What you actually built is a
demonstration of a fundamentally different way to think about AI agents in
production.
There are two kinds of agents.
A static agent is a finished product. Its capabilities are decided at design
time, encoded at build time, and fixed at deployment. When a user needs
something it cannot do, a developer opens a laptop, writes code, and
redeploys. The agent is a ceiling. Every new requirement is a request for a
taller ceiling.
An adaptive agent is a platform. Its capabilities grow in response to real
usage, in real conversations, in response to real user needs the developer did
not anticipate. The developer defines the growth mechanism. The agent does
the growing. The ceiling moves on its own.
The skill_writer tool is the growth mechanism. It is sixty lines of Python
that turn a conversation into a filesystem write. The agentskills.io
specification is what ensures that growth produces something real: portable,
standard-compliant, ecosystem-compatible Skills rather than ad-hoc prompt
strings that only work in this agent, in this framework, until the next
breaking change.
The skills/generated/ folder is something more interesting than a cache of
agent outputs. It is a living record of the gap between what you planned and
what users actually needed. Every SKILL.md in that folder represents a
https://ai.plainenglish.io/adk-skill-tool-that-write-skills-building-self-extending-ai-agents-with-google-adk-part-4-7b395d40b282 22/30


---
*Page 23*


3/25/26, 2:08 PM ADK Skill Tool That Write Skills: Building Self-Extending AI Agents with Google ADK | Part-4 | by Simranjeet Singh | Mar, 2026 | Artifi…
capability you did not think to build, a domain you did not anticipate, a
question your users asked that your original agent could not answer.
Read that folder after a week of real usage. What you will find is not just a list
of Skills. You will find your product roadmap — written by your users,
through your agent, in a format you can act on immediately.
That gap, made visible and actionable, is the most valuable thing this
architectural pattern produces. Not the Skills themselves. The signal.
In Blog 4, we stop talking about Skills and start building with them properly.
We will create a complete two-Skill agent from scratch: a Weather Skill and a
News Summariser Skill. We will implement the Weather Skill as a file-based
Skill following the full spec, implement the News Skill inline using
models.Skill, connect both to a SkillToolset, run the agent in adk web, and
use the Events tab to watch Skill activation happen in real time. You will see
exactly which events appear when a Skill loads, what the context looks like
before and after activation, and how the agent decides between the two Skills
when a query could plausibly trigger either. Every line of code explained.
Full GitHub repo included.
Resources and Further Reading
Everything referenced in this blog, ready to open:
https://ai.plainenglish.io/adk-skill-tool-that-write-skills-building-self-extending-ai-agents-with-google-adk-part-4-7b395d40b282 23/30


---
*Page 24*


3/25/26, 2:08 PM ADK Skill Tool That Write Skills: Building Self-Extending AI Agents with Google ADK | Part-4 | by Simranjeet Singh | Mar, 2026 | Artifi…
📘
ADK Skills documentation — how SkillToolset, load_skill_from_dir,
and the Skills experimental feature work inside ADK:
google.github.io/adk-docs/skills
📘
agentskills.io specification — the complete open standard for Skill
structure, naming rules, frontmatter fields, and the Progressive
Disclosure model: agentskills.io/specification
💻
Full project repository — every file from this blog, ready to clone and
run: github.com/simranjeet97/SelfExtendingAgent_ADKGoogle
🐍
ADK skills_agent sample — Google’s official Skills example including
both file-based and inline Skill definitions: github.com/google/adk-
python/tree/main/contributing/samples/skills_agent
If this guide helped you…
If you learned something new or found this breakdown useful:
Drop a comment — share which metrics you’ve found most reliable in your
projects.
Clap (or double-clap!) to help more AI builders discover this guide.
Share it with your teammates or community, every conversation brings us
closer to better, fairer AI evaluation.
GenAI Full Roadmap [ Learning LLM — RAG -Agentic AI with Resources] :
https://youtu.be/4yZ7mp6cIIg
https://ai.plainenglish.io/adk-skill-tool-that-write-skills-building-self-extending-ai-agents-with-google-adk-part-4-7b395d40b282 24/30


---
*Page 25*


3/25/26, 2:08 PM ADK Skill Tool That Write Skills: Building Self-Extending AI Agents with Google ADK | Part-4 | by Simranjeet Singh | Mar, 2026 | Artifi…
👨‍💻
Agentic AI 14+ Projects- https://www.youtube.com/playlist?
list=PLYIE4hvbWhsAkn8VzMWbMOxetpaGp-p4k
👨‍💻
Learn RAG from Scratch — https://www.youtube.com/playlist?
list=PLYIE4hvbWhsAKSZVAn5oX1k0oGQ6Mnf1d
👨‍💻
Complete Source Code of all 75 Day Hard
🌀
GitHub —
https://github.com/simranjeet97/75DayHard_GenAI_LLM_Challenge
🔀
Kaggle Notebook — https://www.kaggle.com/simranjeetsingh1430
👨‍💻
Exclusive End to End Projects on GenAI or Deep Learning or Machine
Learning in a Domain Specific way —
https://www.youtube.com/@freebirdscrew2023
If you like the article and would like to support me make sure to:
👏 👉🏻
Clap for the story (100 Claps) and follow me Simranjeet Singh
📑
View more content on my Medium Profile
🔔
Follow Me: Medium | GitHub | Linkedin | Community
🚀
Help me in reaching to a wider audience by sharing my content with
your friends and colleagues.
https://ai.plainenglish.io/adk-skill-tool-that-write-skills-building-self-extending-ai-agents-with-google-adk-part-4-7b395d40b282 25/30


---
*Page 26*


3/25/26, 2:08 PM ADK Skill Tool That Write Skills: Building Self-Extending AI Agents with Google ADK | Part-4 | by Simranjeet Singh | Mar, 2026 | Artifi…
What do you choose?
Google Agentic Ai Artificial Intelligence Technology AI Agent
Open in app
Search Write
Published in Artificial Intelligence in Plain English
Follow
40K followers · Last published 16 hours ago
New AI, ML and Data Science articles every day. Follow to join our 3.5M+ monthly
readers.
Written by Simranjeet Singh
Following
3.6K followers · 40 following
AI/ML Engineer l | GenAI Expert | Finance and Banking | 3K Medium + 14K
YouTube | Machine Learning | Deep Learning | NLP
https://ai.plainenglish.io/adk-skill-tool-that-write-skills-building-self-extending-ai-agents-with-google-adk-part-4-7b395d40b282 26/30


---
*Page 27*


3/25/26, 2:08 PM ADK Skill Tool That Write Skills: Building Self-Extending AI Agents with Google ADK | Part-4 | by Simranjeet Singh | Mar, 2026 | Artifi…
No responses yet
Rae Steele
What are your thoughts?
More from Simranjeet Singh and Artificial Intelligence in Plain
English
InArtificial Intelligence in Plain … by Simranjeet Si… InArtificial Intelligence in Plain E… by Tanmay Ba…
Uber Architecture – Part 1: Why Everyone Is “Learning AI”, But
Tracking 5 Million Drivers Every… Nobody Really Understands This…
Every second, 83,000 drivers tap their GPS Prompting teaches you the interface. AI
chip. literacy means understanding geometry,…
5d ago 2 Jan 21 1.2K 43
https://ai.plainenglish.io/adk-skill-tool-that-write-skills-building-self-extending-ai-agents-with-google-adk-part-4-7b395d40b282 27/30


---
*Page 28*


3/25/26, 2:08 PM ADK Skill Tool That Write Skills: Building Self-Extending AI Agents with Google ADK | Part-4 | by Simranjeet Singh | Mar, 2026 | Artifi…
InArtificial Intelligence in Plain En… by Faisal haq… InArtificial Intelligence in Plain … by Simranjeet Si…
Why Claude Opus 4.6 Changes Agentic AI Projects: Build 14
Everything: The Dawn of “Vibe… Hands‑On AI Agents + Key Desig…
Anthropic’s most intelligent model yet isn’t Explore 14 real-world Agentic AI projects and
just an upgrade — it’s a fundamental shift in… 2 key tutorials. Learn to build autonomous…
Feb 6 636 17 Jul 6, 2025 328 4
See all from Simranjeet Singh See all from Artificial Intelligence in Plain English
Recommended from Medium
https://ai.plainenglish.io/adk-skill-tool-that-write-skills-building-self-extending-ai-agents-with-google-adk-part-4-7b395d40b282 28/30


---
*Page 29*


3/25/26, 2:08 PM ADK Skill Tool That Write Skills: Building Self-Extending AI Agents with Google ADK | Part-4 | by Simranjeet Singh | Mar, 2026 | Artifi…
InTech and AI Guild by Shashwat InThe Ai Studioby Ai studio
Bye-Bye MCP: Says Perplexity and How to Build Multiple AI Agents
Cloudflare Using OpenClaw
After months of hype, Perplexity’s CTO just A practical guide to structuring, deploying,
announced they are moving away from the… and coordinating specialized AI workers
Mar 13 275 13 Mar 3 90 1
InLet’s Code Futureby Deep concept InLevel Up Coding by Yanli Liu
6 Tools That Made My Life Easier as 5 Agent Frameworks. One Pattern
a Software Engineer Won.
Make your development environment work AutoGen vs. LangGraph vs. CrewAI vs.
for you, not against you. ByteDance’s DeerFlow vs. Anthropic — and a…
Mar 13 531 10 Mar 16 725 8
InAndroid Alchemy by Prakash Sharma Amol Kavitkar
Building a Production-Ready Multi-
Agent AI System: A Deep Dive int…
— Amol Kavitkar and SrishtiPor
https://ai.plainenglish.io/adk-skill-tool-that-write-skills-building-self-extending-ai-agents-with-google-adk-part-4-7b395d40b282 29/30


---
*Page 30*


3/25/26, 2:08 PM ADK Skill Tool That Write Skills: Building Self-Extending AI Agents with Google ADK | Part-4 | by Simranjeet Singh | Mar, 2026 | Artifi…
AI Replaced 80% of Coding —
Master These 7 Skills Instead. Mar 2 32 1
The 2025 data shows something unexpected:
AI has not replaced software engineers. It ha…
Mar 17 125 5
See more recommendations
https://ai.plainenglish.io/adk-skill-tool-that-write-skills-building-self-extending-ai-agents-with-google-adk-part-4-7b395d40b282 30/30