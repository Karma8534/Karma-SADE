# levelup.gitconnected

*Converted from: levelup.gitconnected.PDF*



---
*Page 1*


Open in app
Search Write
Level Up Coding
Member-only story
Use GLM-5 in Claude
Code and Save 60% on
Tokens
Running GLM-5 Inside Claude Code: Setup
and Best Workflow
Youssef Hosni Follow 4 min read · 6 hours ago
127 1
Claude Code is one of the best coding assistants
you can run in your terminal. It understands large
codebases, writes clean implementations, and
handles complex refactors surprisingly well. For


---
*Page 2*


many developers, it feels like having a strong pair
programmer available at all times.
The problem? If you’re using it heavily with models
like Sonnet or Opus, the cost adds up quickly. The
$200/month Max plan isn’t cheap, especially if
you’re running it daily for planning,
documentation, debugging, and implementation.
But here’s the interesting part:
You don’t have to use Claude’s models all the time.
You can route Claude Code through GLM-5 and get
very close performance for a fraction of the cost.
In this blog, I’ll show you how to set it up in
minutes, how to verify it’s actually using GLM, and
the smartest workflow to balance cost and
performance.


---
*Page 3*


GLM-5: Open Weights, Strong, Cheap
GLM-5 is the latest flagship large language model
from Z.AI (Zhipu AI). It has a Mixture-of-Experts
architecture with hundreds of billions of
parameters but uses only a subset during
inference. Benchmarks show it rivals leading
proprietary models in coding and agentic tasks,
while being much cheaper per token and even
open source.


---
*Page 4*


If your goal is cost efficiency without a huge drop
in quality, GLM-5 is excellent:
Benchmarks show strong coding and reasoning
performance that’s competitive with closed
models.
GLM-5 is accessible through Claude Code by
routing Claude’s requests via an Anthropic-
compatible endpoint from Z.ai.
It means the same TUI and workflow, just with
much cheaper tokens.


---
*Page 5*


How to Add GLM-5 to Claude Code (Step-
by-Step)?
1. Install or Open Claude Code
If you’re already using Claude Code, you’re set.
Otherwise, install or open it as normal.
2. Run the GLM-5 Setup
From your terminal:
npx @z_ai/coding-helper


---
*Page 6*


Follow the prompts and enter your Z.ai API
credentials. You can get the api keys from here.


---
*Page 7*


This will configure Claude Code so that instead of
hitting Anthropic’s default models, it routes
requests to GLM-5 via Z.ai’s Anthropic-compatible
endpoint.


---
*Page 8*


After running the helper and starting Claude Code,
don’t assume it automatically switched to GLM-5.
To verify the active model, simply type:
/model
It will print the current model and available
models. If it works correctly, you should see GLM-
5. If it is still using Anthropic’s model, even if the
helper says configuration is synced, Claude Code
may still default to Sonnet or Opus unless the
ANTHROPIC_BASE_URL is properly overridden.
To confirm GLM routing is active:
1. Open ~/.claude/settings.json
2. Ensure you have:
{
"env": {
"ANTHROPIC_AUTH_TOKEN": "your_zai_api_key",
"ANTHROPIC_BASE_URL": "https://api.z.ai/api/anthr


---
*Page 9*


}
}
3. Fully close Claude Code
4. Open a new terminal and run claude again
Restarting is important; Claude only reads the
environment configuration at startup. After that,
you can select the model using the /model
command.
3. Revert to Claude Models (if needed)
1. Open your Claude settings file:
~/.claude/settings.json
2. Remove or comment out:
"ANTHROPIC_AUTH_TOKEN"
"ANTHROPIC_BASE_URL"


---
*Page 10*


3. Save the file, and Claude Code will fall back to
Anthropic’s servers.
Best Workflow for Tokens and
Productivity
Here’s a strategy that works for many devs and
keeps costs down:
Use GLM-5 for:
Planning tasks and brainstorming
Rough drafts of functions and documentation
Routine code generation and basic problem
solving
Since GLM-5 is less costly per token, you can afford
more experimentation and iteration here.
Switch to Opus 4.6 for:
Complex reasoning or deep architecture
questions
Large refactors or migrations


---
*Page 11*


Production-ready code, such as complete
systems or expert audits
This way, Opus is used when its strengths really
matter, and you don’t burn tokens on routine work.
Claude Code Glm 5 AI LLM Data Science
Published in Level Up Coding
Follow
303K followers · Last published 6 hours ago
Coding tutorials and news. The developer homepage
gitconnected.com && skilled.dev && levelup.dev
Written by Youssef Hosni
Follow
32K followers · 95 following
Applied AI @ GreenStep | AI Researcher @ Aalto
University | Founder @ To Data & Beyond | Subscribe
to my Newsletter: https://youssefh.substack.com/


---
*Page 12*


Responses (1)
To respond to this story,
get the free Medium app.
Ahmedsabri
6 hours ago
Thanx for the tip , but GLM-5 is way slower and not so smart with tools,
haiku is smarter in tool usage! . If one can afford the 200$ , it is the best
and best alternative is what you described here , Ramadan kareem
More from Youssef Hosni and Level Up
Coding
In by In by
To Data & Bey… Youssef Ho… Level Up Codi… Youssef Ho…


---
*Page 13*


Stop Calculating LLM Managing Agentic
M R i t M ith
If you’ve worked with large Welcome to the fourth part of
d l f H i F i b ildi
4d ago Feb 2
In by In by
Level Up Codi… Youssef Ho… Towards AI Youssef Hosni
Top Large Language Important LLM Papers
M d l (LLM ) f th W k F
Demystifying Large Language Stay Updated with Recent
M d l (LLM ) K I t i L L M d l
Sep 5, 2023 Jan 20
See all from Youssef Hosni See all from Level Up Coding
Recommended from Medium


---
*Page 14*


In by In by
Activated Thin… Shane Coll… Towards AI Felix Pappe
Why the Smartest From Notes to
P l i T h A K l d Th Cl
The water is rising fast, and How to combine human
f i f Ch tGPT i i ht ith AI i f
Feb 13 Feb 7
Steve Yegge Joe Njenga
The Anthropic Hive How I Use Claude Code
Mi d SSH t C t t A
As you’ve probably noticed, Recently, Claude Code added
thi i h i SSH t th Cl d
Feb 6 Feb 15


---
*Page 15*


In by In by
Data Science C… Ida Silfver… AI Advanc… Jose Crespo, P…
Testing a Naive RAG Anthropic is Killing
Pi li Bit i
Which wins where and why? The AI-native currency
l d i t hidi i
6d ago 6d ago
See more recommendations