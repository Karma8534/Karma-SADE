# MCPs4CC

*Converted from: MCPs4CC.PDF*



---
*Page 1*


Open in app
8
Search Write
Towards AI
Member-only story
The 10 Claude Plugins
You Actually Need in
2026 (And What They
Are)
How to transform Claude from a chatbot into
an AI that can code, browse, access your data,
and automate your entire workflow
Rohan Mistry Follow 6 min read · Mar 18, 2026
509 6
Claude just got superpowers.
And most people still think it’s just a chatbot.


---
*Page 2*


On February 24, 2026, Anthropic announced
private plugin marketplaces for enterprise users.
Two weeks earlier, the community published over
1,000 MCP servers that extend Claude’s capabilities
beyond text generation.
The result? Claude can now:
Write and execute code autonomously
Browse the web in real-time
Access your Gmail, Drive, Slack, and databases
Control your browser with Playwright
Query live documentation for any library
Remember context across sessions
This isn’t ChatGPT with plugins bolted on. This is a
fundamentally different architecture built on the
Model Context Protocol (MCP) — and it changes
everything.
Non-Member’s Link!


---
*Page 3*


Here’s what Claude plugins actually are, and the 10
you should install today.
What Are Claude Plugins (And Why They
Matter)
Think of Claude plugins as “arms and legs for your
AI’s brain.”
Without plugins, Claude is trapped in a text box. It
can think, but it can’t act.


---
*Page 4*


With plugins, Claude becomes an autonomous
agent that can:
✅
Pull code from GitHub and create PRs
✅
Query your PostgreSQL database
✅
Search the live web
✅
Read and write files
✅
Control a browser
✅
Access Google Workspace
The Technical Breakthrough: MCP
Claude plugins are built on the Model Context
Protocol (MCP) — an open standard Anthropic
released in December 2025.
MCP standardizes how AI models connect to
external data and tools, eliminating custom
integrations for every new service.
According to Anthropic’s documentation:


---
*Page 5*


“MCP enables AI assistants to discover and use
local and remote resources without needing a
custom integration for each one.”
Translation: One protocol. Thousands of tools.
Zero friction.
Four Types of Plugins
1. MCP Servers — Connect Claude to external
services (GitHub, Slack, databases)
2. Skills — Features Claude automatically activates
when needed
3. Commands — Custom shortcuts (like /code-
review)
4. Hooks — Automation triggered on events (like
enforcing code standards)
Now let’s look at the 10 plugins with the biggest
impact.
The Top 10 Claude Plugins for 2026


---
*Page 6*


1. Feature-Dev (89,000+ Installs)
What it does: Turns feature requests into
production code through a 7-phase workflow
Why it matters:
Most AI tools just generate code. Feature-Dev runs
a senior engineer’s process:
1. Requirements gathering
2. Codebase exploration (parallel agents study your
architecture)
3. Architecture design
4. Implementation
5. Testing
6. Code review
7. Documentation


---
*Page 7*


Invoke with /feature-dev and describe what you
want. Claude handles the rest.
Best for: Building complete features, not just code
snippets
Install:
npx skills add anthropic/feature-dev
2. Frontend-Design (277,000+ Installs)
What it does: Gives Claude professional design
instincts before writing any CSS
Why it matters:
Without this, Claude generates forgettable designs
— the visual signature users recognize as “AI-
generated.”
With frontend-design, Claude considers:


---
*Page 8*


Purpose and tone
Intentional constraints
Visual differentiation
Unexpected typography choices
Asymmetric layouts
Scroll-triggered animations
One developer on Medium wrote:
“People asked me who my designer was. There is
no designer. It’s Claude with frontend-design
installed.”
Best for: Escaping the AI aesthetic
Install:
npx skills add anthropic/frontend-design


---
*Page 9*


3. Context7 (Upstash)
What it does: Gives Claude access to live, version-
specific library documentation
The problem it solves:
Claude’s training data might be months old. When
you’re using Next.js 15, React 19, or Tailwind 4,
outdated docs lead to hallucinated APIs.
Context7 queries the actual current
documentation for the exact version you’re using.
How it works:
Two core tools:
resolve-library-id — Looks up a library
query-docs — Fetches specific documentation
Claude can now say “according to the Next.js 15
docs…” instead of guessing based on training data.


---
*Page 10*


Best for: Fast-moving frameworks where versions
matter
Install: Via MCP in Claude Desktop config
4. GitHub MCP Server
What it does: Lets Claude search repos, read code,
open issues, and create pull requests
Why it matters:
Instead of manually copying code snippets, you
can ask:
“Analyze the src/ directory and suggest a fix for issue
#42”
Claude will:
1. Search the repository
2. Read relevant files


---
*Page 11*


3. Propose a fix
4. Create a PR with the changes
Best for: Software developers working with GitHub
Install: Available in official Anthropic marketplace
5. PostgreSQL MCP
What it does: Direct read-only access to your
PostgreSQL databases
Why it matters:
Ask natural language questions like:
“Show me the top 5 users by spend last month”
Claude will:
1. Inspect your database schema automatically
2. Generate the SQL query


---
*Page 12*


3. Execute it
4. Return real data
No copying table names. No SQL syntax
debugging. Just results.
Best for: Data analysts and engineers
Security note: Read-only access prevents
accidental data modifications
6. Playwright MCP
What it does: Claude controls a live Chrome
browser to test your web apps
Why it matters:
Instead of writing Playwright test scripts, you say:
“Test the checkout flow: browse products, add to cart,
fill in test card, pay, verify confirmation”


---
*Page 13*


Claude opens a visible browser window and
executes the test while you watch.
The game-changer: For authenticated features, log
in manually, then Claude takes over from there.
Best for: Frontend developers testing web apps
Warning: Can be resource-intensive
7. Brave Search MCP
What it does: Connects Claude to the live internet
Why it matters:
Claude’s training data has a cutoff (January 2025).
Brave Search lets it:
Research current events
Check stock prices
Find the latest library documentation


---
*Page 14*


Verify facts in real-time
Ask: “What are the latest AI releases this week?”
Claude searches the web and synthesizes current
information.
Best for: Research, fact-checking, current events
8. Google Workspace via CLI (4,900
gws
Stars in 3 Days)
What it does: Unified CLI for all Google
Workspace APIs with built-in MCP
The breakthrough:
Before gws, connecting Claude to Google required
separate OAuth setups for Drive, Gmail, Calendar,
Sheets.
Google shipped gws and changed everything.


---
*Page 15*


Install:
npm install -g @googleworkspace/cli
gws mcp -s drive,gmail,calendar,sheets
Now Claude has direct access to your entire
Google Workspace.
Example workflow:
“Read my unread emails, draft responses to anything
urgent, update my quarterly metrics spreadsheet,
create calendar events for upcoming deadlines,
generate a summary doc.”
One prompt. Zero copy-pasting.
Best for: Knowledge workers living in Google
Workspace
9. Slack MCP Server


---
*Page 16*


What it does: Reads channel history, summarizes
threads, posts messages
Why it matters:
The January 2026 update added interactive
drafting — you can now:
1. Draft a Slack message
2. Preview it in Claude
3. Review and edit
4. Approve before posting
The overlooked use case:
“Summarize the #engineering channel from the last 2
days before I respond”
Get full context without reading 500 messages.
Best for: Anyone working across multiple Slack
workspaces


---
*Page 17*


10. Memory Bank / Claude-Mem
What it does: Gives Claude persistent memory
across sessions
The problem it solves:
LLMs forget context between conversations.
Memory Bank creates a .memory folder that stores:
User preferences
Project details
Past decisions
Coding standards
The result:
Claude remembers your authentication patterns,
error handling conventions, and testing
requirements permanently.
You explain once. Claude remembers forever.


---
*Page 18*


Best for: Long-term projects where context
matters
How to Install Plugins (3 Methods)
Method 1: Claude Desktop Config (MCP Servers)
Edit claude_desktop_config.json:
{
"mcpServers": {
"postgres": {
"command": "npx",
"args": ["-y", "@modelcontextprotocol/server-po
}
}
}
Restart Claude Desktop.
Method 2: Skills via npm
npx skills add anthropic/frontend-design
npx skills add anthropic/feature-dev


---
*Page 19*


Method 3: Claude Code Plugin System
/plugin install feature-dev@claude-plugins-official
Which Plugins Should You Install First?
If you’re a developer:
1. Feature-Dev
2. GitHub MCP
3. Context7
4. Playwright MCP
5. PostgreSQL MCP (if using databases)
If you’re a knowledge worker:
1. Google Workspace (gws)
2. Slack MCP
3. Brave Search


---
*Page 20*


4. Memory Bank
5. Frontend-Design (if building any UI)
If you’re a founder/product person:
1. Feature-Dev
2. Frontend-Design
3. Brave Search
4. Slack MCP
5. Memory Bank
The Ecosystem Numbers (March 2026)
1,000+ MCP servers available
351,000+ agent skills across marketplaces
8M+ total plugin installs tracked
18 AI agents support MCP protocol
50+ official Anthropic connectors


---
*Page 21*


According to TurboDocx’s analysis:
“Developers using 15+ plugins ship features 3–4x
faster than those using raw Claude.”
Plugins aren’t optional. They’re the difference
between a chatbot and a team member.
Sources: Anthropic MCP Documentation, Claude
Plugins Official Repository, TurboDocx Plugin
Analysis, ClaudeFast MCP Guide, Firecrawl Plugin
Reviews, Composio Plugin Directory, Fast.io MCP
Resources — March 2026
Artificial Intelligence Claude Ai Tools Automation
Developer Productivity
Published in Towards AI
Following


---
*Page 22*


119K followers · Last published just now
We build Enterprise AI. We teach what we learn. Join
100K+ AI practitioners on Towards AI Academy. Free:
6-day Agentic AI Engineering Email Guide:
https://email-course.towardsai.net/
Written by Rohan Mistry
Follow
709 followers · 40 following
I am a Master's student in Artificial Intelligence and
Machine Learning, with a focus on real-world AI
solutions.
Responses (6)
To respond to this story,
get the free Medium app.
Thorsten Domke
1 day ago
Good article, but I can‘t install feature-dev („could not resolve to a
Repository with the name anthropic/feature-dev“) what do I need to do?
Please support …
12 1 reply


---
*Page 23*


Jacek Pawlak
1 day ago
Nice article, but installation of Frontend-Design fails.
5 1 reply
rezwits
1 day ago
Thanks, now I can go back to using Claude, but I have to set this up... LOL
on my two machines... ugh, but it'll be fun thanks to this!
4 1 reply
See all responses
More from Rohan Mistry and Towards AI
In by In by
Towards AI Rohan Mistry Towards AI Divy Yadav
Claude Code Has 50+ LLM Observability: The
C d M t Mi i L i M t


---
*Page 24*


The complete guide to slash For developers who shipped
d CLI fl LLM li ti d t
Mar 15 Mar 14
In by In by
Towards AI Alpha Iterations Towards AI Rohan Mistry
Agentic AI Project: The 8 Types of AI
B ild C t M d l P i
End to end implementation of Understanding How Different
A ti AI b d t AI M d l W k T th
Mar 26 Mar 2
See all from Rohan Mistry See all from Towards AI
Recommended from Medium


---
*Page 25*


In by Joe Njenga
UX Planet Nick Babich
When I Tried MiniMax
Proven way to improve
2 7 Cl d C d
d lit t
It was an ignorant mistake; I
How to use /simplify to get the
t i tt ti t
b t ibl d f
Mar 26 3d ago
Kristopher Dunham Anil Mathew
Paperclip: The Open- 10 Claude Code Skills
S Pl tf E D l N
Something strange happened Most developers are using
h b i t t d Cl d C d t 20% f it
Mar 25 Mar 20


---
*Page 26*


In by In by
Bootcamp nardaimonia Let’s Code Fut… Deep conc…
What Claude Cowork 20 Most Important AI
t ll d C t E l i d i
The complete breakdown of Beginner-Friendly Guide
h t it h dl h t t it
Mar 7 5d ago
See more recommendations