# QuOpus

*Converted from: QuOpus.PDF*



---
*Page 1*


Open in app
1
Search Write
Coding Nexus
Member-only story
Someone Stitched
Claude Opus
Reasoning Into Qwen
3.5. It Runs on a Single
RTX 3090.
Sonu Yadav Following 4 min read · Mar 8, 2026
76
Qwen3.5–27B-Claude-4.6-Opus-Reasoning-
Distilled, Qwopus for short, takes the Qwen 3.5 27B
base model and fine-tunes it specifically on Claude
Opus 4.6 reasoning chains. The goal: take a fast,


---
*Page 2*


efficient local model and teach it how Claude
thinks through hard problems.
Not how Claude answers. How does it reason
before answering?
What “Reasoning Distillation” Actually
Means
When Claude Opus 4.6 works through a complex
problem, it doesn’t just output an answer. It builds


---
*Page 3*


a structured internal monologue first — breaking
the problem down, identifying constraints,
planning steps, checking consistency. That process
lives inside <think> tags and never shows up in the
final response unless you look for it.
Distillation means capturing that process and
training a smaller model to imitate it. Not the
answers Claude gives. The reasoning scaffolding
Claude uses to get there.
Qwopus was trained specifically on three datasets
of Claude Opus reasoning trajectories:
DatasetPurposenohurry/Opus-4.6-Reasoning-
3000x-filteredFull Claude 4.6 Opus reasoning
chainsTeichAI/claude-4.5-opus-high-reasoning-
250xHigh-intensity structured
reasoningJackrong/Qwen3.5-reasoning-700xStep-
by-step problem solving diversity
The training pipeline is straightforward:


---
*Page 4*


Base Model (Qwen3.5-27B)
│
▼
Supervised Fine-Tuning (SFT) + LoRA
│
▼
Final Model (Claude-4.6-Opus-Reasoning-Distilled, tex
One detail worth noting: training used
train_on_responses_only, which masks the
instruction side. The model only learns from the
generation of <think> sequences and the final
answers. Not from the prompts. This keeps the
training signal clean — the model learns reasoning
structure, not prompt pattern-matching.
Every training sample was normalized to enforce a
strict output format:
<think> {internal reasoning} </think>
{final answer}


---
*Page 5*


The Reasoning Pattern It Learned
Base Qwen 3.5 has a known tendency toward
repetitive, circular reasoning on simple queries. It
second-guesses itself, loops back, restates the
same point in different words. Fine for hard
problems. Wasteful on straightforward ones.
Qwopus addresses this by distilling Claude Opus’s
more structured approach. Instead of exploratory
trial-and-error, the think block follows a consistent
pattern:
Let me analyze this request carefully:
1. Identify the core objective of the problem.
2. Break the task into clearly defined subcomponents.
3. Evaluate constraints and edge cases.
4. Formulate a step-by-step solution plan.
5. Execute the reasoning sequentially and verify cons
That’s not a prompt template. That’s what the
model actually generates internally before
producing a response. Confident parsing upfront.


---
*Page 6*


Outlined plan in the think block. Sequential
execution rather than backtracking.
The practical result: fewer redundant reasoning
loops, faster time to answer on simple queries, and
preserved deep analytical capacity on hard ones.
Why It Matters for Local Coding Agents
This is where Qwopus earns its place over vanilla
Qwen 3.5 27B.
Every modern coding agent — OpenCode, Claude
Code, anything built for software development —
sends a developer role in its messages. Base Qwen
3.5's chat template doesn't recognize it. The
template hits raise_exception('Unexpected message
role.') and your server returns 500s in a loop
before a single token generates.
The common workaround is --chat-template
chatml. It stops the crash but silently disables


---
*Page 7*


thinking mode. Server logs show thinking = 0. No
think blocks. No chain of thought. You're running a
reasoning model without the reasoning.
Qwopus doesn’t have this problem. It natively
handles the developer role. No Jinja template
patches. No ChatML workarounds. Logs confirm
thinking = 1 on startup and it stays there.
Beyond the template fix, community testing by
@sudoingX on a single RTX 3090 showed something
more interesting: Qwopus ran autonomously for
over 9 minutes without human intervention during
coding tasks. It waited for tool responses, read
outputs, self-corrected errors, and even generated
a README automatically. The base model stalls or
freezes mid-execution in the same scenarios.
That’s the reasoning distillation doing its job. A
model that knows how to plan and verify its own
steps handles agentic loops better than one that
pattern-matches and hopes.


---
*Page 8*


Hardware Requirements
This is a 27B model. The numbers:
VRAM: ~16.5 GB with Q4_K_M quantization
Speed: 29–35 tok/s
Context: Full 262K — no compromise
Fits on a single RTX 3090. No dual-GPU setup. No
CPU offload degrading your speed.
The command to run it:
llama-server -m Qwen3.5-27B-Claude-4.6-Opus-Reasoning
-ngl 99 \
-c 262144 \
-fa on \
--cache-type-k q4_0 \
--cache-type-v q4_0
No --chat-template flag needed. No patched Jinja
file. Just load and run.


---
*Page 9*


Weights:
https://huggingface.co/Jackrong/Qwen3.5-27B-
Claude-4.6-Opus-Reasoning-Distilled-GGUF
What It’s Good For
The intended use cases are analytical rather than
general:
Coding — especially with agentic tools where
multi-step reasoning matters
Math — structured breakdown of complex
problems
Logic-heavy tasks — anything where you want to
see the reasoning, not just the answer
Offline analytical work — the transparent
<think> block lets you follow the model's
internal logic
What it’s not designed for: real-time factual
retrieval or tasks requiring verified external


---
*Page 10*


knowledge. It’s still an autoregressive LLM. The
reasoning is structured but not grounded — facts
generated during the think sequence can
hallucinate just like any other output.
One Honest Caveat
The model page calls this a preview build and
means it. The reasoning quality is solid. The
hardware efficiency is real. The coding agent
compatibility is a genuine improvement over base
Qwen.
But the surrounding ecosystem — inference
templates, fine-tuning pipelines, tooling
integrations — is still catching up. You might hit
edge cases. Compatibility quirks with less common
setups are possible.
Claude Qwen Rtx AI LLM


---
*Page 11*


Published in Coding Nexus
Following
19.1K followers · Last published 2 days ago
Coding Nexus is a community of developers, tech
enthusiasts, and aspiring coders. Whether you’re
exploring the depths of Python, diving into data
science, mastering web development, or staying
updated on the latest trends in AI, Coding Nexus has
something for you.
Written by Sonu Yadav
Following
461 followers · 6 following
I simplify programming concepts and make coding
accessible for everyone!
No responses yet
To respond to this story,
get the free Medium app.


---
*Page 12*


More from Sonu Yadav and Coding Nexus
Sonu Yadav In by
Coding Nexus Code Pulse
Claude Can Now Draw
Google Just Shipped a
Di (A d Th
CLI f All f G l
I’ve been asking AI to create
If you’ve ever had to write curl
di f Th
ll i t G l ’ REST
Feb 24 Mar 4


---
*Page 13*


In by In by
Coding Nexus Jatin Prasad Coding Nexus Sonu Yadav
Unlock Claude AI’s Cloudflare crawl: One
S ith 10 API C ll Th t C l
Transform Your Workflow with Web scraping used to require
B ttl T t d P ti h l t S i
Feb 11 Mar 10
See all from Sonu Yadav See all from Coding Nexus
Recommended from Medium
Keuri Castillo Luong NGUYEN


---
*Page 14*


Using Claude Code for Setting Up Claude
F C d L ll ith
I was in those days, where I Claude Code with local model
h th li it i Q 3 d 30b
Oct 30, 2025 Nov 2, 2025
Dára Sobaloju In by
Mac O’… Alex Gear & Tech …
How to Set Up and Use
macOS is Good. These
Cl d C d A t
9 A M k It P f t
If you’ve been using Claude
M-Series Macs are monsters,
C d f hil ’
b t OS it lf till h
Feb 6 Feb 8


---
*Page 15*


In by Ewan Mak
AI Software Engi… Joe Nje…
Mac Mini M4 vs AMD
I Found ClawHub
Mi i PC f L l AI
(N ) Offi i l W t
The single most important
You could be wasting time or
b h b i l l
tti f l d b i
3d ago 6d ago
See more recommendations