# LocalClaudePowerhouse

*Converted from: LocalClaudePowerhouse.PDF*



---
*Page 1*


Open in app
2
Search Write
Claude Code + LM
Studio = Local AI
Powerhouse (Step-by-
Step Setup)
Sharvasuresh Following 4 min read · 2 days ago
3
Source: www.anthropic.com/claude-code


---
*Page 2*


WHY?
I’m sure you have heard about Claude Code, but a
hefty payment of 200$, to use a coding agent might
have prevented you from leveraging its power. If
you weren’t informed, you can now use LM Studio
to run free local models with Claude Code,
opening new opportunities for developers.
Additionally, your code is completely private, so
there is no worry about critical functions leaking.
Photo by Anthony Roberts on Unsplash


---
*Page 3*


Beware
Keep your expectations realistic. You cannot
expect frontier-level performance from a 14–30b
model, but it does offer more price-to-
performance. Another watchout point is to test the
TPS (tokens per second) of a model like gpt-
oss:20b. This can offer an idea of which model size
is compatible with your setup. LLMs can also take
up a hefty amount of your storage. The minimum
spec requirements to start using local models for
coding are: 8GB VRAM, a midrange CPU, and at
least 8GB system RAM, or a Mac mini. This is
because you need models that can accurately make
tool calls and be good at coding, while managing
operating system overhead.


---
*Page 4*


Image taken from:https://blog.n8n.io/open-source-llm/
Setup
To check out my hardware, here’s the link to my blog
about my PC build.
Choosing the model
When choosing your model, make sure to consider
the quantisation of the model. Preferably Q4KM
because it balances the performance and
capability of the model, while shrinking the size in
half. Gpt-oss:20b, a model recently released by
OpenAI, is an impressive model. It can be


---
*Page 5*


deployed on a 16 GB VRAM GPU or Unified
Memory because its performance is similar to
qwen Q8 4B, which is just 8gb in size. The model
packs a punch in numerous benchmarks, as it is an
MOE. A lightweight model, that is still optimal, is
qwen 2.5 coder 7b/14b. For more advanced
workflows, the go-to is glm-4.7-flash, which is a
beast. It beats significantly larger models, while
being just 16gb in size. Once you have chosen your
model, test it with an LM Studio chat interface
where the tokens per second is displayed. This
evaluates whether your system can handle the
model.


---
*Page 6*


Photo by Rodion Kutsaiev on Unsplash
Setup guide
1. Install Claude Code from
https://code.claude.com/docs/en/overview
2. Install LM studio if you haven’t already, and
install the model of your choice.
3. Set these environment variables so the claude
CLI talks to your local LM Studio server:


---
*Page 7*


ANTHROPIC_BASE_URL=http://localhost:1234
ANTHROPIC_AUTH_TOKEN=lmstudio
Tip: Enable the local LLM service, so it is always accesible
3. Start your LM studio server, and load your model
of choice with a context size suitable for your
project
4. Run it with the command:


---
*Page 8*


claude — model [model of your choice]
It’s that simple!
Photo by Matthew Waring on Unsplash
Best Practices
Ensure you have chosen a model that can deliver
about 40TPS; if not, then it will lead to a headache.
Switch models according to uses; a simple edit can
be done by a less competitive model, but deep
analysis can only be done by a superior model.


---
*Page 9*


Make sure to update your CUDA and Vulkan
engines, as they offer performance optimisations.
Immerse yourself in the skills of prompt
engineering and the appropriate use of Claude
Code. I have been able to build projects in minutes
using my setup with gpt-oss:20b medium and glm-
4.7-flash.
I will post a blog about projects constructed with this
setup sometime later.
Coding Claude Code AI Agentic Ai Local Llm
Written by Sharvasuresh
Following
6 followers · 3 following
No responses yet


---
*Page 10*


To respond to this story,
get the free Medium app.
More from Sharvasuresh
Sharvasuresh Sharvasuresh
Here’s how you can run The Productivity Shift:
th D k i i M ltit ki ith AI i
If you have a graphics The quote made me reflect on
i it d t lf & f d th
Feb 4, 2025 May 17, 2025
Sharvasuresh Sharvasuresh
Cryptocurrency in Quantum Computing:
2024 Still l t? Th F t


---
*Page 11*


Beginners Guide Quantum computing is a
th d f ti th t
Aug 30, 2024
Aug 3, 2024
See all from Sharvasuresh
Recommended from Medium
John Maeda In by
Towards AI Felix Pappe
Get Started with Agent
From Notes to
Skill i GitH b C il
K l d Th Cl
By the time you read this,
How to combine human
thi l d h
i i ht ith AI i f
Feb 2 Feb 7


---
*Page 12*


Hari Prakash Natarajan Bill WANG
Claude Code and Understanding
S b t H t O Cl A
With Claude Code, you can Introduction
b ild kfl h
Dec 14, 2025 Feb 17
Gigi Sayfan Solana Levelup
Claude Code Deep Dive PicoClaw and Nanobot
B i VS O Cl Th Ri
My way for studying anything PicoClaw and nanobot have
i i ti /b ildi t d th tt ti f
Jan 3 Feb 17
See more recommendations