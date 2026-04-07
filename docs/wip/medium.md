# medium

*Converted from: medium.PDF*



---
*Page 1*


Open in app
2
Search Write
A 2.6B Model Just
Crushed 7B Reasoning
Giants — Not With
More Data, But With a
Smarter Reward Signal
Pawel Following 5 min read · Feb 21, 2026
42
More parameters equal better reasoning. Bigger
models think better. That’s what we hear
frequently. However, a new paper out of Princeton
just challenged that assumption.


---
*Page 2*


Ouro-2.6B-Thinking, a 2.6 billion parameter model
trained with a framework called RLTT (Reward
Latent Thought Trajectories), scored 86% on
MATH-500. DeepSeek-R1 at 7B? 60%. Qwen3 at 4B?
48%.
A smaller model. Fewer parameters. Better results.
Not because it memorized more math problems.
Not because it burned more compute. Because the
researchers changed how the model learns to
reason — and more importantly, how it gets
rewarded for reasoning.
Let’s break down why this matters.
What is a Looped Language Model?
Most language models you know are built on a
straightforward principle: stack transformer
layers. More layers, more capacity, more
intelligence. Each token passes through once, top
to bottom, and gets a prediction at the end.


---
*Page 3*


Looped Language Models (LoopLMs) flip this
design.
Instead of stacking 32 unique layers, a LoopLM
takes a smaller block of layers and runs the input
through them multiple times in a loop. Ouro,
developed by ByteDance Seed in collaboration with
Princeton, UC Santa Cruz, and several other
institutions, uses 4 recurrent iterations through its
shared parameter block.
Think of it this way: a standard transformer says
“look at this problem once, through many different
lenses.” A looped transformer says “look at this
problem four times, refining your understanding
with each pass.”
The result? Same weights in memory. Same
parameter count on disk. But more compute per
token — the model literally thinks longer about each
token before committing to an output.


---
*Page 4*


This isn’t a new idea in isolation. Recurrence has
deep roots in neural network research. But Ouro
made it work at scale — pre-trained on 7.7 trillion
tokens with an entropy-regularized objective that
teaches the model to allocate different
computational depths to different inputs. Easy
tokens exit early. Hard tokens get all four loops.


---
*Page 5*


The Problem: RL Doesn’t Know How to Grade a
Loop
Here’s where things get interesting — and where
the Princeton researchers identified a critical gap.
Reinforcement learning has been the secret
weapon behind the recent reasoning


---
*Page 6*


breakthroughs. DeepSeek-R1 used GRPO (Group
Relative Policy Optimization) to achieve stunning
results. The idea is simple: generate multiple
answers, reward the correct ones, penalize the
wrong ones, update the policy.
But GRPO was designed for standard transformers.
It assigns reward to the final output — the last
token distribution the model produces. For a
normal transformer, that’s fine. The model
processes the input once, produces output, gets
graded.
For a Looped Language Model, this creates a
fundamental mismatch.
When Ouro-2.6B processes a math problem, it
doesn’t just produce one internal representation. It
produces four — one per loop iteration. Each
iteration refines the model’s latent understanding.
Iteration 1 might encode a rough sketch of the


---
*Page 7*


solution. Iteration 2 sharpens it. Iteration 3 catches
an edge case. Iteration 4 converges on the answer.
But under GRPO, only the final iteration —
iteration 4’s output — receives the reward signal.
Iterations 1, 2, and 3? Invisible to the optimizer.
They contributed to the correct answer, but the
learning algorithm has no way to credit them.
This is the classic credit assignment problem, and
in looped models, it’s catastrophic. The gradient
signal has to back-propagate through all four latent
refinement steps, getting diluted at each stage. The
early iterations — arguably the most important
ones, since they set the trajectory — receive the
weakest learning signal.
Previous attempts to apply standard RL to
LoopLMs failed for exactly this reason.
RLTT: Grade the Working, Not Just the Answer
Jonathan Williams and Esin Tureci at Princeton
proposed an elegant fix: don’t just reward the final


---
*Page 8*


answer — reward the entire reasoning trajectory.
RLTT (Reward Latent Thought Trajectories)
distributes the reward signal across every loop
iteration’s predicted next-token distribution.
Instead of forming a single connection between
reward and the final output, RLTT creates a direct
relationship between reward and every
intermediate latent state.
Here’s the intuition: imagine grading a student’s
math exam. GRPO looks at the final answer and
gives a thumbs up or thumbs down. RLTT reads
the entire scratch work — every step, every
intermediate calculation — and distributes credit
accordingly.
Technically, RLTT aggregates the model’s next-
token distributions across all internal loop
iterations and uses this aggregate to shape the
policy gradient. No external verifiers needed. No
auxiliary reward models. Just a smarter way of


---
*Page 9*


attributing credit to the computation that actually
happened.
The implementation is remarkably clean — it’s a
drop-in replacement for GRPO with negligible
computational overhead. Same training
infrastructure. Same reward function. Same
rollout budget. The only thing that changes is how
the reward gets distributed.
The Numbers
Williams and Tureci ran extensive experiments
comparing RLTT against GRPO on Ouro-2.6B-
Thinking under strictly controlled conditions —
identical training data, identical optimization
settings, identical advantage normalization. The
only variable was the credit assignment strategy.


---
*Page 10*


The results are not incremental. They’re dramatic.
Mathematical Reasoning:
MATH-500: 86.0% (RLTT) vs. 71.6% (GRPO) — a
+14.4% improvement
GSM8K: 94.0% vs. 59.7% — a staggering +34.3%
gain
AIME24: +16.6% improvement
BeyondAIME: +10.0% improvement
Cross-Domain Transfer (trained exclusively on
math, tested on everything else):
GPQA (Science): 38.4% vs. 19.7% — nearly
doubled
MBPP (Coding): +3.3% improvement
MMLU-ST (Factual Recall): +3.5% improvement
ARC-C: improvement across the board


---
*Page 11*


Every single result is statistically significant (p <
0.05). And the training itself was 10% faster —
RLTT converges in fewer tokens because the
denser reward signal produces more informative
gradient updates from the start.
The Bigger Picture: Reward Shaping Is the Next
Frontier
If there’s one meta-insight from this paper, it’s that
how you reward a model matters as much as how
you train it.
The AI community has spent enormous energy on
data quality, model architecture, and training
scale. RLTT shows that the reward signal — the
mechanism by which a model learns what “good
reasoning” looks like — is an equally powerful
lever.
GRPO was designed for a world where
computation is a single forward pass. Looped
models live in a different world — one where
internal computation unfolds over multiple


---
*Page 12*


refinement steps. Matching the reward structure to
the computational structure unlocked
performance that was always latent in the
architecture.
The paper’s title says it perfectly: Prioritize the
Process, Not Just the Outcome.
This principle will extend far beyond looped
language models. Any architecture that performs
iterative internal computation — mixture-of-
experts with routing, speculative decoding
pipelines, multi-agent reasoning chains — will
eventually face the same credit assignment
challenge. RLTT provides a template for solving it.
Paper: “Prioritize the Process, Not Just the Outcome:
Rewarding Latent Thought Trajectories Improves
Reasoning in Looped Language Models” by Jonathan
Williams and Esin Tureci (Princeton University).
Published February 2026. Available at
arXiv:2602.10520.


---
*Page 13*


The Ouro model family: “Scaling Latent Reasoning via
Looped Language Models” (ByteDance Seed, UC Santa
Cruz, Princeton University et al.). Available at
arXiv:2510.25741. Models available on HuggingFace.
AI Genai Reinforcement Learning
Written by Pawel
Following
369 followers · 4 following
Gen AI director with a focus on AI & Data Strategy,
FinOps, MLOps & LLM/LMMOps.
No responses yet
To respond to this story,
get the free Medium app.


---
*Page 14*


More from Pawel
Pawel Pawel
A 5B Model that Proves Google’s A2UI Protocol
S t A hit t J t Ch d H AI
5 billion parameters. Beating Two weeks ago, Google open-
80 billi t d d thi th t i
Feb 15 Dec 28, 2025
Pawel Pawel
XGrammar 2: How a 3B A 3B Model Beating Big
M d l B t 70B LLM t D t
CMU & NVIDIA’s new DeepSeek-AI has just released
t t d ti i D S k OCR 2 f ll
Jan 10 Jan 29


---
*Page 15*


See all from Pawel
Recommended from Medium
In by ADITHYA GIRIDHARAN
AI Advances Harish K
Zvec: Alibaba Just
I Tested 5 OCR Models
O S d “Th
6 R l W ld
Every decade or so, someone
There’s no single “best” OCR
t k f l t h l
i T t i f t t
Feb 15 Feb 13
Eduard Ruzga In by
Graph P… Alexander Shere…


---
*Page 16*


MCP Apps: AI Just Got Five Papers Quietly
F t d A d W Killi th LLM T i
Back when I worked at Standard GraphRAG spends
I f d P i f 75% f it t k b d t b f
Feb 26
Feb 24
In by Kamal Dhungana
Level Up … Mandar Karhad…
Google’s LangExtract
GLiNER v2 60M: A
E l i d Wh S
M d l F Ed AI!
Turn any unstructured text
Scaling GLiNER to 60M
i t t t d ifi bl d t
P t ith t th H
Feb 24 Feb 13
See more recommendations