# Gemma4

*Converted from: Gemma4.PDF*



---
*Page 1*


Open in app
11
Search Write
AI Software Engi…
Member-only story
Gemma 4: Google Just
Released an Open
Source AI Model for
Developers
Joe Njenga Following 5 min read · 1 day ago
108


---
*Page 2*


Gemma 4 is Google’s latest and most capable AI
model, which just shattered expectations and gave
us one of the best open-source alternatives to
Chinese models.
In fact, it runs so well with Claude Code, which
makes me excited since I can now finally use a
Google AI model easily for coding with Claude Code.
But before I lose you, let’s start by answering this
question :


---
*Page 3*


Did we need another Google
model? And what sets it apart from
the other Gemini models?
Gemma 4 Model
Google has released several AI models over the
past year, but Gemma 4 stands out for three
reasons:


---
*Page 4*


Apache 2.0 License — Comes with no restrictions on
commercial use, fine-tuning, or deployment.
Built for Agentic Workflows — Supports native
function calling, structured JSON output, and
multi-step reasoning.
Runs Locally on Your Hardware — From Raspberry
Pi to workstation GPUs.
Model Family
Gemma 4 comes in four sizes, each designed for
different hardware and use cases:
The 31B model currently ranks #3 on Arena AI’s
open model leaderboard, outperforming models


---
*Page 5*


20 times its size.
In this article, I’ll break down what Gemma 4 brings
to the table and why developers should try it as an
alternative to similar models.
Gemma 4 Features
Google built Gemma 4 from the same research and
technology behind Gemini 3.
The difference is that you can run it locally without
depending on Google’s cloud.


---
*Page 6*


Here’s what makes this release interesting for
developers:
Reasoning and Multi-Step Logic
Gemma 4 handles complex reasoning tasks out of
the box. All models in the family come with
configurable thinking modes.
You can toggle between fast responses and deeper
step-by-step reasoning depending on the task.
On the AIME 2026 benchmark, the 31B model
scored 89.2% without tools. For context, Gemma 3
scored 20.8% on the same test.
Multimodal Support
All four models process text and images with
variable aspect ratios and resolutions.
The smaller E2B and E4B models also support native
audio input for speech recognition.


---
*Page 7*


This is useful if you’re building apps that need to
understand documents, charts, or screenshots
alongside text prompts.
Longer Context Windows
The edge models (E2B, E4B) support 128K tokens.
The larger models (26B, 31B) go up to 256K tokens.
In practice you can pass entire codebases or long
documents in a single prompt without chunking.
Code Generation
Gemma 4 scored 80% on LiveCodeBench v6 and hit
a Codeforces ELO of 2150 with the 31B model.
These are serious numbers for an open-source model
you can run offline.
140+ Languages


---
*Page 8*


Google trained Gemma 4 on over 140 languages
natively.
If you’re building for a global audience, you don’t
need separate fine-tuned models for different
regions.
Gemma 4 Built for Developers


---
*Page 9*


Unlike the previous Gemma releases, which came
with usage restrictions that made commercial
deployment complicated, Gemma 4 is released with the
Apache 2.0 license.
You can fine-tune Gemma 4, deploy it in production,
build products on top of it, and sell those products
without licensing headaches.
Running Locally
When you run a model locally, three things
happen:
Privacy — Your code and data never leave your
machine.
Cost — Once you have the hardware, inference is
free.
Latency — Responses come as fast as your GPU
can generate them.


---
*Page 10*


For developers working on sensitive codebases or in
regulated industries, this is more important than
benchmark scores.
Hardware Requirements
The model sizes map directly to hardware tiers:
The 26B MoE model activates only 3.8B parameters
during inference, which is why it fits in less VRAM
than you’d expect and runs faster than the 31B dense
model.


---
*Page 11*


Integration Options
Gemma 4 has day-one support across the tools we
already use:
Ollama — One command to pull and run
Hugging Face — Transformers, TRL, vLLM
Claude Code — Direct integration via Ollama
LM Studio — GUI for local model management
Google AI Studio — Browser-based testing for 26B
and 31B
Running Gemma 4 with Claude Code
Claude Code now integrates with Ollama, which
lets you swap in any local model, including
Gemma 4.
Here’s how to set it up:
Step 1: Install Ollama


---
*Page 12*


If you don’t have Ollama installed:
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh
# Windows (PowerShell)
irm https://ollama.com/install.ps1 | iex
Step 2: Pull Gemma 4
Choose the model size that fits your hardware:
# For laptops (9.6GB download)
ollama pull gemma4:e4b
# For workstations with 18GB+ VRAM


---
*Page 13*


ollama pull gemma4:26b
# For maximum quality (20GB+ VRAM)
ollama pull gemma4:31b
Step 3: Launch Claude Code with Gemma 4
ollama launch claude --model gemma4
Claude Code will now use Gemma 4, which levels up
with the previous Chinese models we have been
testing.


---
*Page 14*


Let’s Connect!
If you are new to my content, my name is Joe
Njenga
Join thousands of other software engineers, AI
engineers, and solopreneurs who read my content
daily on Medium and on YouTube where I review
the latest AI engineering tools and trends. If you
are more curious about my projects and want to
receive detailed guides and tutorials, join
thousands of other AI enthusiasts in my weekly AI
Software engineer newsletter
If you would like to connect directly, you can reach
out here:
AI Integration Software Engineer (10+
Y E i )
Software Engineer specializing in AI
i t ti d t ti E t i
njengah.com


---
*Page 15*


Follow me on Medium | YouTube Channel | X |
LinkedIn
Google Ai Gemma Gemma4 Google Gemini Gemini
Published in AI Software Engineer
Follow
3.4K followers · Last published 1 day ago
Sharing ideas about using AI for software
development and integrating AI systems into existing
software workflows. We explores practical
approaches for developers and teams who want to
use AI tools in their coding process.
Written by Joe Njenga
Following
21K followers · 98 following
Software & AI Automation Engineer, Tech Writer
& Educator. Vision: Enlighten, Educate, Entertain.
One story at a time. Work with me:
mail.njengah@gmail.com
No responses yet


---
*Page 16*


To respond to this story,
get the free Medium app.
More from Joe Njenga and AI Software
Engineer
Joe Njenga In by
AI Software Engi… Joe Nje…
Everything Claude
OpenCode +
C d Th R Th t
A ti it A th
If you slept through this or
Just about when we thought
i d t E thi Cl d
O C d d d j
Jan 22 Jan 19


---
*Page 17*


In by Joe Njenga
AI Software Engi… Joe Nje…
I Tested Oh My Claude
7 Ralph Loop Mistakes
C d Th O l A t
Th t A B i Y
Oh My Claude Code makes
Ralph Loop is everywhere
lti t h t ti
i ht b t
Jan 22 Jan 25
See all from Joe Njenga See all from AI Software Engineer
Recommended from Medium


---
*Page 18*


Ewan Mak In by
Bootcamp Katherine Yeh
Mac Mini M4 vs AMD
A Designer’s Guide to
Mi i PC f L l AI
Cl d C d
The single most important
How I organized Skills, Tools,
b h b i l l
d E i t i t
5d ago Mar 26
In by
Obsidian Obser… Theo Sto…
The TL;DR of Claude
C d I id Ob idi
If you’ve not been keeping up
ith th j bl f i
6d ago
See more recommendations