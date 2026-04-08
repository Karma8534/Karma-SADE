# UltraTtainingNPU

*Converted from: UltraTtainingNPU.PDF*



---
*Page 1*


Open in app
1
Search Write
Coding Nexus
Member-only story
I Trained an LLM on
Apple’s Neural Engine.
The Chip Apple Never
Meant For This.
Code Coup Following 6 min read · Mar 11, 2026
25 1
Every Apple Silicon Mac has three compute units:
the CPU, the GPU, and the Neural Engine (ANE).
Apple constantly talks about the first two. The
Neural Engine is mentioned on marketing slides as
“up to 38 TOPS!” and then basically disappears.


---
*Page 2*


Why? Because Apple only exposes it for inference.
Running a model, not training one. The APIs for
accessing the ANE at the hardware level are
private, undocumented, and not intended for
regular developers.
Someone reverse-engineered them anyway.
A developer named Maderix published native Obj-
C code that directly accesses the ANE through
Apple’s private APIs. No CoreML. No abstraction
layer. Direct hardware access.
That’s where this project started.


---
*Page 3*


The Idea
The goal was to train a real language model — a
GPT-style transformer — on the Neural Engine. Not
just run one. Train one. Forward pass, backward
pass, weight updates, the whole thing.
And then benchmark it against Karpathy’s H100
baseline, running on a consumer MacBook.
To make it a fair comparison, the same Mac would
run three separate training jobs simultaneously:


---
*Page 4*


ANE — native Obj-C, Apple Neural Engine
MLX — Apple’s official ML framework, GPU
MPS — PyTorch with Metal backend, GPU
Same chip. Same data. Same architecture.
Different compute paths.
It Exploded. Three Times.
The first working version hit the Neural Engine
and immediately went unstable.
v1: Activations hit the range [-339, +467] at step
13,000. That's not training — that's a fire. When
your activation values are in the hundreds and
your gradients are in the thousands, everything
diverges.
v2: Set up a cosine learning rate schedule,
calculated for 330,000 steps. The run lasted a few


---
*Page 5*


hours. The schedule barely decayed. Diverged at
15,000 steps.
v3: Applied multiple fixes, dropped the learning
rate to 5e-4. Still too aggressive. Diverged at 55,000
steps.
Three runs. Three failures. But each one lasted
longer than the last, which meant something was
working.


---
*Page 6*


What Actually Fixed It
After 55 experiments, three changes made the
difference:
1. Zero-init output projections
When you initialize the output projection weights
at zero, the model starts with clean gradient flow.
No random noise in the weights means no chaotic
early gradients. Small thing, big effect.
2. Logit softcapping (cap=15)
This is the same technique Anthropic uses in
Claude. Hard cap on logit values before the
softmax. Gradients cannot physically exceed the
cap. If activations were the fire, this is the
sprinkler system.
3. Split learning rates


---
*Page 7*


Weight matrices and embeddings behave
differently. Treating them the same is a mistake.
After an 18-experiment sweep, the optimal split
was:
Weight matrices: 0.05x the base learning rate
Embeddings: 5x the base learning rate
That’s a 100x difference between the two. Wild that
it works. But it does.
The Numbers


---
*Page 8*


With all three fixes applied and the learning rate
halved (what they call v3b):
val_bpb: 2.227 → 1.635
Improvement: 27%
Steps: 72,000
Wall time: 4.8 hours
Model: 67.6M parameters, 6 layers, SEQ=512
Bits-per-byte (val_bpb) is how well the model
predicts text. Lower is better. Karpathy’s H100
baseline sits at 0.998. This isn’t there yet — but it’s
running on a laptop chip nobody designed for
training.
Running It Yourself
The repo is forked from Karpathy’s autoresearch
project. Three separate training paths, all on Apple
Silicon.
ANE (Neural Engine — native Obj-C):


---
*Page 9*


cd native && make all
make test-ane # verify ANE hardware acce
make bench-sram # probe SRAM performance c
./build/train_overnight_nl6_s512 --steps 10000 --scra
--data data/train.bin --val data/val.bin
MLX (recommended for GPU on Apple Silicon):
cd mlx && uv sync
uv run prepare.py --num-shards 8
uv run train.py
MPS (retired, kept for reference):
cp pyproject_mac.toml pyproject.toml && uv sync
uv run prepare.py --num-shards 8
uv run train_mac.py
Autonomous agent mode (runs overnight
experiments on its own):
claude --dangerously-skip-permissions -p "Read progra


---
*Page 10*


That last one is the autoresearch loop — an AI
agent that modifies the training code, runs 5-
minute experiments, evaluates the result, keeps or
discards changes, and loops. Overnight. Without
you.
The Wild Part: They Run at the Same Time
When MLX trains on the GPU, the fans spin up.
The Mac gets warm. Activity Monitor shows 97%
GPU usage. You feel it.
When the ANE trains — nothing. Cool. Silent.
Activity Monitor doesn’t even register it. The
Neural Engine is invisible to the OS.
Both ran simultaneously. Two models training on
the same MacBook. Zero interference with each
other.


---
*Page 11*


50+ hours of total compute squeezed into about 19
hours of wall time. That’s the efficiency of using
compute that would otherwise sit idle.
How the ANE Pipeline Works
The core engineering insight here is the dynamic
weight pipeline.
Standard approach: bake weights into compiled
kernels. Every weight update means recompiling.
Slow.
This approach: weights are packed into the
IOSurface input alongside activations. Kernels
compile once at startup. Weight updates are just
memcpy — copying bytes from one place to another.
No recompilation ever.
Kernels → compiled once at startup
Weights → packed into IOSurface input


---
*Page 12*


Weight update → memcpy (fast)
Training step → ANE runs compiled kernel with new we
What They Found
A few unexpected results from the experiments:
ANE ran a 6x bigger model 8x faster than MPS
on the same chip. MPS is the “official” GPU path.
ANE, using private APIs, crushed it.
bf16 on Apple Silicon is 2.6x slower than fp32.
This is backwards from NVIDIA behavior. The
whole ML world assumes bf16 is faster. On this
chip, it isn’t.
Findings from H100 experiments don’t transfer
to Apple Silicon. What Karpathy found
optimizing on NVIDIA hardware didn’t work
here. Different architecture, different intuitions
required.
There’s a depth sweet spot at SEQ=512. 6 layers
beats both 4 and 8 layers. More depth isn’t


---
*Page 13*


always better.
Cosine schedule length must match actual run
length exactly. If the schedule is calculated for
330K steps but the run ends at 15K, activations
go nuclear. This caused v2’s failure.
What’s Next
The current v3b ran at sequence length 512. MLX
runs at 1024 — double the context. That means
better language modeling and 2x the training data
per step.
The next ANE run also targets SEQ=1024. Same
sequence length as MLX. First real apples-to-
apples comparison between the two.
Target: val_bpb below 1.3.


---
*Page 14*


Why This Matters
The Neural Engine sits in every Apple Silicon Mac
doing almost nothing most of the time. Apple built
it for narrow tasks — Siri, photo processing, Face
ID. The ML community mostly ignores it because
the documentation doesn’t exist.
But the hardware is there. The compute is real.
And it runs without touching the GPU, without


---
*Page 15*


spinning the fans, without affecting anything else
the machine is doing.
The question of what’s actually possible on
commodity hardware, not cloud GPUs, not
research clusters, is worth answering. This project
is trying to answer it from the bottom up, one
failed training run at a time.
Three failures to get to v3b. Each one got further.
That’s usually how it goes.
LLM Llm Applications AI Neural Networks Apple
Published in Coding Nexus
Following
19.1K followers · Last published 2 days ago
Coding Nexus is a community of developers, tech
enthusiasts, and aspiring coders. Whether you’re
exploring the depths of Python, diving into data
science, mastering web development, or staying
updated on the latest trends in AI, Coding Nexus has
something for you.


---
*Page 16*


Written by Code Coup
Following
3.9K followers · 1 following
Code Coup: Seize the Code, Stage a Coup!
Responses (1)
To respond to this story,
get the free Medium app.
Omgeosh
1 day ago
I mean, he kind of did it. I guess.
github / joshmorgan1000 / ane
More from Code Coup and Coding Nexus


---
*Page 17*


In by In by
Coding Nexus Code Coup Coding Nexus Tattva Tarang
Most People Use They Replaced 30
Cl d Lik S h E i With 30 AI
I’ve spent the last few months 44,000 lines of TypeScript. 175
t hi l Cl d ll t 1 500+ t t A
Mar 12 Mar 4
In by In by
Coding Nexus Sonu Yadav Coding Nexus Code Coup
Someone Stitched How I’d Build and Sell
Cl d O AI A t f
Qwen3.5–27B-Claude-4.6- I’ve been writing about tech
O R i Di till d f fi d I’ b ilt
Mar 8 Jun 25, 2025
See all from Code Coup See all from Coding Nexus


---
*Page 18*


Recommended from Medium
In by Balu Kosuri
Mac O’… Alex Gear & Tech …
I Turned Andrej
macOS is Good. These
K th ’
9 A M k It P f t
By Balasubramanyam Kosuri
M-Series Macs are monsters,
b t OS it lf till h
Feb 8 Mar 21


---
*Page 19*


In by In by
Data Science C… Shreyans… Artificial Intelligen… Damia…
TurboQuant by Google AI Is Quietly Replacing
M d it P ibl t R Th 7 D il T k
It unveils a 5x KV cache The biggest shift isn’t obvious
i b kth h it’ h i i th
3d ago Mar 29
Pudding Entertainment In by
Towards Deep L… Sumit Pa…
Using Raspberry Pi 5 as
Claude Code’s Entire
l l AI di
S J t L k d
Can Raspberry Pi 5 really
A missing .npmignore line
l Cl d C d
d 512 000 li f
Mar 29 5d ago
See more recommendations