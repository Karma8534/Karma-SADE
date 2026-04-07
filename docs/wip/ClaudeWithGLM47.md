# ClaudeWithGLM47

*Converted from: ClaudeWithGLM47.PDF*



---
*Page 1*


Open in app
Search Write
Member-only story
I Tried Claude Code
With GLM 4.7 (Here’s
What You Are Missing)
Joe Njenga Following 10 min read · Jan 1, 2026
265 5


---
*Page 2*


I paired GLM 4.7 with Claude Code and quickly
discovered how code 10x faster at zero cost
GLM 4.6 was fast, but GLM 4.7 is on another level
when paired with Claude Code.
Z.AI released GLM 4.7 on December 22, 2025 —
barely a week ago — and I’ve been testing it
nonstop since release.
If you read my GLM 4.6 article, you know I was
impressed. I called it one of the most underrated
coding models available. Well, now I need to
update everything I said.
GLM 4.7 benchmarks jumped significantly, the UI
generation got cleaner, and they added thinking
features that make it way more stable for complex
Claude Code sessions.


---
*Page 3*


But benchmarks are just numbers.
Let me show you what it does.
But just a quick reminder.
If you missed out on my year of Claude Code
updates, where I covered every new feature, tip, and
trick, I got you covered — check out the complete list
of Claude Code tutorials here and do not forget to


---
*Page 4*


follow me here on Medium and my Claude Code
Masterclass newsletter.
Quick Demo: Building a Real-Time App
Same approach as my GLM 4.6 article — show, not
tell.
I’m going to build something more complex this
time.
Not just a basic task manager, but a real-time
collaborative app with multiple features.
Here’s my prompt:
Build me a real-time collaborative todo app with:
- User authentication
- Real-time sync across devices
- Drag-and-drop task ordering
- Dark/light mode toggle
- Clean, modern UI with Tailwind
- Supabase for the backend


---
*Page 5*


Done in under 3 minutes.
But here’s what was different — the code structure
was cleaner than what 4.6 produced.
The component organization made more sense.
The Tailwind classes weren’t just thrown together;
they followed a consistent pattern.


---
*Page 6*


Look at that UI. This is what Z.AI calls “vibe
coding” — and the improvement over 4.6 is visible.
The spacing is better. The color choices are more
cohesive. It appears to be something a designer
has touched.
The real-time sync worked on the first try.
Authentication is hooked up correctly. The drag-and-
drop function worked without me needing to modify
any code.
One shot for a working app is impressive.


---
*Page 7*


Now, I’m not saying GLM 4.7 is better than Claude
Sonnet 4.5. It’s not — at least not for everything. But
for $3/month versus $20–200/month? The value
proposition just got a lot more interesting.
Let me break down what’s new in this release.
What’s New in GLM 4.7
Let’s cut through the marketing and look at the
numbers.
Z.AI published their benchmark comparisons, and the
improvements over GLM 4.6 are significant — not the
usual 1–2% incremental bumps we see with most
model updates.
Benchmarks
Here’s what changed from 4.6 to 4.7:
That Terminal Bench 2.0 jump — from 24.5% to
41% — is wild.


---
*Page 8*


That’s a 16.5 percentage point improvement in
terminal-based coding tasks. Exactly what matters
for Claude Code users.
How It Stacks Up Against the Competition


---
*Page 9*


Z.AI compared GLM 4.7 against GPT-5, GPT-5.1,
Claude Sonnet 4.5, Gemini 3.0 Pro, and DeepSeek-
V3.2.
The highlights:
Beats GPT-5 High on HLE with Tools: 42.8% vs
35.2%. Humanity’s Last Exam is one of the
hardest reasoning benchmarks out there. GLM
4.7 outperforms GPT-5 by over 7 points.
Competitive with Claude Sonnet 4.5 on SWE-
bench: 73.8% vs 77.2%. Only 3.4 points behind —
and at a fraction of the cost.


---
*Page 10*


Beats Claude Sonnet 4.5 on τ²-Bench: 87.4% vs
87.2%. This benchmark tests interactive tool
invocation. GLM 4.7 edges out Claude here.
Open-source SOTA on LiveCodeBench V6: 84.9%
puts it at the top of open-source models, beating
Claude Sonnet 4.5’s 64.0%.
I’m not saying GLM 4.7 beats Claude across the
board — it doesn’t.
Claude Sonnet 4.5 still wins on SWE-bench Verified
and several reasoning tasks. But the gap has
narrowed significantly.
4 Key Improvements
Z.AI focused on four areas for this release:
1. Core Coding
Multilingual agentic coding got a major upgrade.
The +12.9% improvement on SWE-bench
Multilingual means it handles Python, JavaScript,


---
*Page 11*


TypeScript, Go, and other languages more
consistently.
Terminal-based tasks improved so much. If you’re
using Claude Code for bash operations, file
management, or system commands, you’ll notice the
difference.
2. Vibe Coding
This is Z.AI’s term for UI generation quality. GLM
4.7 produces:
Cleaner, more modern webpages
Better-looking slides with accurate layout
More polished posters and visual content
I saw this in my demo. The Tailwind classes weren’t
random — they followed design patterns. Spacing,
colors, and typography all felt more intentional.
3. Tool Using
The τ²-Bench score of 87.4% tells the story. When
GLM 4.7 needs to call external tools — APIs,


---
*Page 12*


databases, browsers, MCP servers — it does so
more reliably.
BrowseComp jumped from 45.1% to 52.0% for web
browsing tasks. With context management enabled,
it hits 67.5%.
4. Complex Reasoning
The HLE benchmark tests problems that require
deep reasoning. GLM 4.7 scored 42.8% with tools
— a 12.4 point jump from 4.6.
For context, GPT-5.1 High scores 42.7% on the same
benchmark. GLM 4.7 is right there.
New Thinking Features


---
*Page 13*


This is what I’m most excited about for Claude
Code users.
GLM 4.7 introduces three thinking modes:
Interleaved Thinking
The model thinks before every response and every
tool call. This isn’t new — it started with GLM 4.5 —
but it’s been enhanced.
What this means: Better instruction following.
Higher quality code generation. Fewer moments
where the model misunderstands what you asked.


---
*Page 14*


Preserved Thinking
This is the game-changer for Claude Code sessions.
In coding agent scenarios, GLM 4.7 automatically
retains all thinking blocks across multi-turn
conversations. It reuses existing reasoning instead
of re-deriving everything from scratch.
Long Claude Code sessions often suffer from context
drift. The model forgets what it was doing three
prompts ago. Preserved Thinking reduces this
problem significantly.
For complex refactoring tasks that span multiple
files and multiple prompts, this is huge.
Turn-level Thinking
You can now control reasoning on a per-turn basis
within a session.
Disable thinking to reduce latency and cost for
simple requests but for. Complex tasks enable
thinking for better accuracy.


---
*Page 15*


This flexibility didn’t exist in 4.6.
What This Means for Claude Code Users
The combination of better benchmarks and
preserved thinking makes GLM 4.7 more stable for
agentic coding workflows.
In my testing, it maintained context better across
long sessions. It made fewer mistakes on multi-file
operations. The tool calling was more reliable.
Is it Claude Sonnet 4.5? No.
But the gap is smaller than ever — and the price
difference remains massive.
Let’s talk about that next.
The Cost Reality
Let’s talk money.
Claude Code Pricing


---
*Page 16*


If you’re a heavy user, you’re looking at $100–
200/month. That’s $1,200–2,400/year for a coding
assistant.
GLM 4.7 Pricing
Same $3/month as GLM 4.6 — but now you get a
significantly better model.
Quick Comparison


---
*Page 17*


The math is simple. GLM 4.7 costs 5–6x less for
comparable work.
If you’re already on the GLM Coding Plan from my
4.6 article, you were automatically upgraded to 4.7.
Same price, better model.
GLM 4.7 vs 4.6: Quick Summary
Overall Impressions


---
*Page 18*


Now let me show you how to set it up.
Setting Up GLM 4.7 with Claude Code
This takes about 5 minutes.
Prerequisites
Claude Code installed (version 2.0.33+)
Node.js 18+
Step 1: Install Claude Code (If Needed)
Mac/Linux:
npm install -g @anthropic-ai/claude-code


---
*Page 19*


Windows PowerShell:
irm https://claude.ai/install.ps1 | iex
Verify installation:
claude --version
Step 2: Create Z.AI Account & Get API Key
1. Go to z.ai
2. Sign up (GitHub is fastest)


---
*Page 20*


3. Choose the $3/month plan
4. Go to Profile → API Keys or z.ai/manage-apikey
5. Click Create New Key
6. Name it “Claude Code — GLM 4.7”
7. Copy immediately — it only shows once
Step 3: Configure Claude Code
Option A: Quick Method (Temporary)
Mac/Linux:


---
*Page 21*


export ANTHROPIC_BASE_URL=https://api.z.ai/api/anthro
export ANTHROPIC_AUTH_TOKEN=your_api_key_here
claude
Windows PowerShell:
$env:ANTHROPIC_BASE_URL="https://api.z.ai/api/anthrop
$env:ANTHROPIC_AUTH_TOKEN="your_api_key_here"
claude
Option B: Permanent Method (Recommended)
Create or edit ~/.claude/settings.json:


---
*Page 22*


{
"env": {
"ANTHROPIC_BASE_URL": "https://api.z.ai/api/anthr
"ANTHROPIC_AUTH_TOKEN": "your_api_key_here",
"ANTHROPIC_DEFAULT_HAIKU_MODEL": "glm-4.5-air",
"ANTHROPIC_DEFAULT_SONNET_MODEL": "glm-4.7",
"ANTHROPIC_DEFAULT_OPUS_MODEL": "glm-4.7"
}
}
Step 4: Verify Setup
Open a new terminal and run:
claude
/status
You should see:
Anthropic base URL:
https://api.z.ai/api/anthropic
Model mapped to GLM 4.7
Troubleshooting


---
*Page 23*


Changes not applying?
Close ALL Claude Code windows
Open a fresh terminal
Run claude again
Still not working?
Delete ~/.claude/settings.json
Reconfigure from scratch
Auth conflict warning?
Run claude /logout first
Then restart with your Z.AI config
You’re running GLM 4.7.
Real-World Testing
I ran four tests comparing GLM 4.7 to what I
experienced with 4.6.


---
*Page 24*


Test 1: Task Manager (Same as 4.6 Article)
Same prompt I used when testing GLM 4.6:
Build me a simple task manager with:
- User authentication
- Create, read, update, delete tasks
- Mark tasks as complete
- Filter by status (all, active, completed)
- Clean, modern UI with Tailwind
- Use Supabase for the backend
GLM 4.6 result: Working app, decent UI, some
minor styling inconsistencies.
GLM 4.7 result: Working app, noticeably cleaner
UI, better component structure.
The code organization improved. Components were
smaller and more focused. The Tailwind classes
followed a consistent design system instead of
random utility classes thrown together.


---
*Page 25*


Test 2: Multi-File Refactoring
This is where Preserved Thinking should shine.
I took an existing Express API with authentication
spread across 6 files and asked:
Refactor the authentication system to use JWT with re
Update all affected files and make sure the tests sti
Result: GLM 4.7 maintained context across all 6
files. It remembered the changes it made to
auth.js when updating middleware.js. No
contradictions. No forgotten imports.
With 4.6, I usually needed 2–3 follow-up prompts to
fix inconsistencies. With 4.7, it worked on the first
pass.
Test 3: UI Generation (Vibe Coding)
Testing the “cleaner webpages” claim:


---
*Page 26*


Build a modern analytics dashboard with:
- Sidebar navigation
- Header with user profile
- 4 stat cards
- Line chart and bar chart
- Recent activity table
- Dark mode
Result: The UI quality jump is great. Better spacing,
more cohesive colors, proper visual hierarchy. It
looked like a template you’d pay for.
Test 4: Tool Calling with MCP
I connected Playwright via MCP and asked GLM
4.7 to:
Go to my local app at localhost:3000, test the login
with test@example.com / password123, and tell me if i
Result: Clean execution. It launched the browser,
filled the form, clicked submit, and reported back


---
*Page 27*


accurately. The 87.4% τ²-Bench score translates to
real-world reliability.
Final Thoughts
GLM 4.7 is the real deal.
The benchmark improvements are significant. The
Preserved Thinking feature makes long Claude Code
sessions more stable. The UI generation is visibly
cleaner.And it’s still $3/month.
Use GLM:
Solo developers watching their budget
Freelancers who need high-volume coding
Startup founders managing burn rate
Students and side project builders
Anyone hitting Claude usage limits
Use Claude:


---
*Page 28*


You need maximum accuracy for production
code
You’re already happy on Max Ultimate
You rely heavily on Claude’s subagents (still
unmatched)
The hybrid approach I use:
GLM 4.7 for daily coding, prototypes, high-
volume tasks
Claude for critical reviews, complex
architecture, and production deploys
My recommendation: Just try it. Three dollars to test
a model that competes with GPT-5 on reasoning
benchmarks. If it doesn’t work for you, you’re out the
cost of a coffee.
If you’re already using GLM 4.6 from my previous
article, check your settings — you might already be
on 4.7.


---
*Page 29*


Links:
Z.AI Signup
GLM 4.7 Documentation
My GLM 4.6 Article
Have you tried GLM 4.7? Let's know your experience
in the comments.
Claude Code Course
Every day I’m working hard on building the ultimate
Claude Code course that demonstrates how to build
workflows that coordinate multiple agents for
complex development tasks. It’s due for release soon.
It will take what you have learned from this article
to the next level of complete automation.
New features are added to Claude Code daily, and
keeping up is tough.


---
*Page 30*


The course explores subagents, hooks, advanced
workflows, and productivity techniques that many
developers may not be aware of.
Once you join, you’ll receive all the updates as new
features are rolled out.
This course will cover:
Advanced subagent patterns and workflows
Production-ready hook configurations
MCP server integrations for external tools
Team collaboration strategies
Enterprise deployment patterns
Real-world case studies from my consulting work
If you’re interested in getting notified when the
Claude Code course launches, click here to join
the early access list →
( Currently, I have 3000+ already signed-up
developers)


---
*Page 31*


I’ll share exclusive previews, early access pricing,
and bonus materials with people on the list.
Let’s Connect!
If you are new to my content, my name is Joe
Njenga
Join thousands of other software engineers, AI
engineers, and solopreneurs who read my content
daily on Medium and on YouTube where I review the
latest AI engineering tools and trends. If you are
more curious about my projects and want to receive
detailed guides and tutorials, join thousands of other
AI enthusiasts in my weekly AI Software engineer
newsletter
If you would like to connect directly, you can reach
out here:
AI Integration Software Engineer (10+
Y E i )
Software Engineer specializing in AI
i t ti d t ti E t i


---
*Page 32*


njengah.com
Follow me on Medium | YouTube Channel | X |
LinkedIn
Claude Code Anthropic Claude Code Glm Ai Coding
Ai Code Generation
Written by Joe Njenga
Following
17.3K followers · 98 following
Software & AI Automation Engineer, Tech Writer
& Educator. Vision: Enlighten, Educate, Entertain.
One story at a time. Work with me:
mail.njengah@gmail.com
Responses (5)


---
*Page 33*


To respond to this story,
get the free Medium app.
Deepak Battini
Jan 3
GLM is strong at generating code from scratch, but it lacks depth in
problem-solving when issues arise. In my testing with both Claude
Sonnet 4.5 and GLM 4.7, Claude resolved the problem in a single attempt
by reviewing all related files and… more
41
Baivulcho
Jan 5 (edited)
Something is wrong with this setup approach. I did the settings.json file
and even thought the VS Code console tells me that claude is using the
GLM model and the claude chat window loads as expected, after I type a
command it prompts me to provide… more
4
Swalk
Jan 4
Using 4.7 a lot now in Windsurf, close to free, it is really good
Might try Claude setup
1
See all responses


---
*Page 34*


More from Joe Njenga
Joe Njenga In by
AI Software Engi… Joe Nje…
Everything Claude
I Finally Tested (New)
C d Th R Th t
Ki i C d CLI Lik
If you slept through this or
It turns out Kimi K2.5 is one of
i d t E thi Cl d
th b t t t AI
Jan 22 Jan 30


---
*Page 35*


In by Joe Njenga
AI Software Engi… Joe Nje…
Claude Code
GLM 5 Arrive With a
H k th $100K i
B F Vib
Anthropic just launched a
A few days after Anthropic
i t l h k th l b ti
l d Cl d O 4 6
Feb 11 Feb 7
See all from Joe Njenga
Recommended from Medium
In by In by
Realworld AI Use… Chris Du… Vibe Coding Alex Dunlop


---
*Page 36*


I tested Cursor vs Claude Code’s Creator,
Cl d C d O t 100 PR W k Hi
A direct speed and accuracy Simple principles most
i b ildi th d l l k
Nov 14, 2025 Jan 15
Reza Rezvani ZIRU
I Tested Every Major How I Set Up OpenClaw
Cl d O 4 6 M M Mi i M4
After 24 hours of real testing Everything I learned after
d il kfl k f t i d b i
Feb 6 Feb 16


---
*Page 37*


Marco Kotrotsos In by
Obsidian Obser… Theo Sto…
GPT-5.3 Codex Isn’t a
My Claude Code Now
C d G t
H It O S d
One developer said they built
How I turned it into a personal
i f h th th
i t t th t li i
Feb 8 Feb 19
See more recommendations