# 9Bbeat20bModel

*Converted from: 9Bbeat20bModel.PDF*



---
*Page 1*


Open in app
1
Search Write
Towards Deep Le…
Member-only story
A 9B Model Just Beat a
120B One. Here’s What
Nobody’s Telling You.
Qwen just released four small models that are
rewriting what “small” even means. Here’s why
this one caught my attention, and what the
headlines are getting wrong.
Sumit Pandey Following 10 min read · 2 days ago
134 3
I have stopped writing about new model releases.
There are simply too many of them. Every week


---
*Page 2*


another lab drops something with a name that
sounds like a Star Wars droid, and half the time the
benchmark numbers are massaged enough that
“breakthrough” has lost all meaning. I made a rule
for myself: if I can’t run it, I won’t write about it.
This one broke my rule.
If you can’t read the article further, than please click
here


---
*Page 3*


Alibaba’s Qwen team just released four new
models: Qwen3.5–0.8B, Qwen3.5–2B, Qwen3.5–4B,
and Qwen3.5–9B. Although I have stopped writing
about models because there is a new model every
day, this one catches my eyes because I can run it
on my laptop. And not just run it in that
“technically works but gives you 2 tokens per
second while your fans scream” kind of way.
Actually run it.
The 9B model, the flagship of this small series,
scores 81.7 on GPQA Diamond, a graduate-level
reasoning benchmark [2][3]. OpenAI’s gpt-oss-120B
scores between 71.5 and 80.9 on the same
benchmark depending on the reasoning level and
whether tools are enabled [4][6]. Even taking the
most generous score for GPT-oss, the 9B model still
edges it out.
But before you run with the “tiny model destroys
giant model” narrative, let me explain why the
comparison is more nuanced than it looks.


---
*Page 4*


The Comparison That Needs Context
GPT-oss-120B has 117 billion total parameters, but
it is a Mixture-of-Experts (MoE) model that only
activates 5.1 billion parameters per forward pass
[1][5]. The Qwen3.5–9B is a dense model that
activates all 9 billion parameters on every token.
So when people say “a 9B model beat a 120B
model,” they are technically correct about total
parameter counts. But in terms of actual compute
per token, the Qwen3.5–9B is activating roughly 1.8
times more parameters than GPT-oss-120B does.
The story is not really about a small model beating
a large one. It is about a 9B dense model
outperforming a model with 5.1B active
parameters that happens to have 117B total
weights sitting in memory.
That is still impressive. But it is a different kind of
impressive than “thirteen times more parameters,


---
*Page 5*


lower score.”
Figure 1: When you can compare active parameters per token instead of
total parameters, the picture changes entirely. Qwen3.5–9B (dense)
actually uses more compute per token than GPT-oss-120B (MoE, 5.1B
active). (taken from multiple sources)
There is also a benchmark reporting discrepancy
worth noting. Qwen’s own benchmark table
appears to compare the 9B against GPT-oss-120B at
71.5 on GPQA Diamond, which some sources
suggest may reflect a lower reasoning level or
could be the gpt-oss-20B score. Third-party
evaluations from Clarifai report GPT-oss-120B at
80.9 with tools enabled at high reasoning level.


---
*Page 6*


VentureBeat reports 80.1. The gap between 81.7
and 71.5 is massive. The gap between 81.7 and 80.9
is marginal and within the range of run-to-run
variance. Which comparison you trust changes the
entire story.
I am going to present the numbers as reported by
multiple sources. You should decide how to weight
them.
What Qwen3.5 Small Actually Is
The Qwen3.5 Small Series is a family of four
compact dense models released on March 2, 2026
[2][6], built on the same foundational architecture
as Qwen’s flagship 397B MoE model [9]. These are
not stripped-down, lobotomized versions of
something bigger. They were designed from the
ground up to be small and efficient, using a hybrid
architecture that combines Gated Delta Networks


---
*Page 7*


with the same design principles that power the
flagship.
The four models are spaced deliberately across
deployment tiers:
Qwen3.5–0.8B and 2B: Designed for edge devices.
Think smartphone chips, IoT hardware, offline
inference. Community benchmarks from
r/LocalLLaMA report the 2B model running
smoothly on an iPhone with MLX optimization,
generating 30 to 50 tokens per second.
Qwen3.5–4B: Positioned as a multimodal base for
lightweight agents. Native multimodal support
through early-fusion training where text and
images share the same latent space from the start.
This is different from older adapter-based
approaches that bolt a vision encoder onto a
language model. The 4B reportedly matches the
performance of the previous-generation Qwen3-


---
*Page 8*


VL-30B-A3B on agent evaluations like ScreenSpot
Pro, despite being nearly eight times smaller.
Qwen3.5–9B: The flagship of the small series. This
is the model that grabbed people’s attention.
The Architecture Doing the Heavy Lifting
All four models use a Gated DeltaNet hybrid
architecture with a 3:1 ratio of linear attention
blocks to full softmax attention blocks [2][8]. The
linear attention layers provide constant memory
complexity, which is how Qwen managed to give
even a 2B model a 262,144-token native context
window without making it unrunnable [7]. The full
attention blocks handle the precision work where
exact token relationships matter.
The training used Scaled Reinforcement Learning
across large simulated environments. This is
distinct from just fine-tuning on benchmark
datasets. According to Qwen’s documentation, the


---
*Page 9*


RL training optimized for real-world adaptability,
including tool usage and structured multi-step
workflows.
They also used multi-token prediction during
training, which speeds up inference by allowing
the model to predict multiple subsequent tokens in
a single step [8]. And the vocabulary covers 248,000
tokens across 201 languages [2][7].
One important note: the small models (0.8B
through 9B) are dense models. The flagship 397B
and some medium models in the Qwen3.5 family
use sparse Mixture-of-Experts, but the small series
does not.
The Numbers, With Proper Attribution
These are the benchmark comparisons I could
verify across multiple sources. All scores for the 9B
are in thinking mode unless noted otherwise.


---
*Page 10*


Language and Reasoning Benchmarks
Figure 2: On language-only benchmarks, the comparison is closer than
headlines suggest. GPT-oss-120B actually leads on MMLU-Pro. The
GPQA Diamond score for GPT-oss varies dramatically by source (71.5 vs
80.9).
Important: GPT-oss-120B wins convincingly on
MMLU-Pro (90.0 vs 82.5). The 9B does not dominate
across the board on language tasks. It wins on GPQA


---
*Page 11*


Diamond and multilingual knowledge, but loses on
broader language reasoning.
Vision and Multimodal Benchmarks
Figure 3: On vision and multimodal tasks, the 9B dominates. But note:
GPT-oss-120B is excluded from this chart because it is a text-only model.
These comparisons are against other multimodal models.


---
*Page 12*


The 9B also outperforms the previous-generation
Qwen3–30B, which is more than three times its
parameter count, on benchmarks like GPQA
Diamond (by 8 points), IFEval (by 3 points), and
LongBench v2 (by 10 points) [8].
These results are strong. But I want to be clear: the
comparisons where the 9B looks most dominant,
especially the vision and multimodal benchmarks,
are against models that were never designed for
those tasks. The language-only comparisons
against GPT-oss-120B are more mixed than the
headline numbers suggest.
Why I Care About “Can I Run It”
I’ve been lucky enough to work with some fairly
large models during my PhD. And the one thing
that experience taught me is that the gap between
“impressive benchmark” and “actually useful for
building things” is enormous.


---
*Page 13*


The Qwen3.5 series closes that gap. A year ago,
running a multimodal model locally meant a 13B+
parameter model and a dedicated GPU with
significant VRAM. The Qwen3.5–4B handles text,
images, and video with a 262K context window.
The 9B model at BF16 precision needs roughly
18GB of VRAM, which means it fits on a 24GB
consumer GPU like an RTX 3090 or RTX 4090
without quantization. With 4-bit quantization, it
drops to around 5GB, making it viable on a wider
range of hardware including Apple Silicon Macs.
Community reports suggest 30 to 50 tokens per
second on consumer hardware, though throughput
varies significantly by setup.
For anyone building healthcare AI tools, agent
pipelines, or local applications that handle
sensitive data, this is a meaningful change. No API
calls. No data leaving the device. No latency from
round-tripping to a cloud endpoint.


---
*Page 14*


That is not a small thing.
Okay, But How Do You Actually Run It?
This is the part I wish more model release posts
included. Benchmarks are nice. A working model
on your machine is better.
The easiest route is Ollama. Install it from
ollama.com (it’s a single app download on Mac,
Linux, and Windows), then run one command:
ollama run qwen3.5
That pulls the 9B by default and drops you into a
chat session. If you want a specific size:
ollama run qwen3.5:4b # lighter, still multimodal
ollama run qwen3.5:2b # for older hardware
ollama run qwen3.5:0.8b # runs on basically anything


---
*Page 15*


Ollama handles GPU acceleration automatically on
both NVIDIA and Apple Silicon. No configuration
needed.
Pick your size based on what you have. The 0.8B
needs about 1GB and will run on CPU if needed.
The 2B needs around 3GB VRAM. The 4B around 4
to 5GB. The 9B at 4-bit quantization fits in about
5GB. At full BF16 precision you need a 24GB GPU.
If you want to use it in code, Ollama exposes an
OpenAI-compatible API at localhost:11434:
from ollama import chat
response = chat(
model='qwen3.5:9b',
messages=[{'role': 'user', 'content':
'Hello!'}],
)
print(response.message.content)
This means any tool that already works with the
OpenAI API can be pointed at your local Qwen3.5


---
*Page 16*


with one config change. No API costs, no rate
limits, no data leaving your machine.
For production workloads or high-throughput
scenarios, the official documentation recommends
dedicated serving engines such as SGLang,
KTransformers, or vLLM over Ollama.
What’s Missing
I want to be honest here because the hype around
these models is already running ahead of the
evidence.
First, the parameter comparison that made
headlines is misleading. Saying “9B beat 120B”
without mentioning that GPT-oss-120B only
activates 5.1B parameters per token is leaving out
the most important context. The Qwen3.5–9B uses
more active compute per token than GPT-oss-120B
does. That does not diminish what Qwen achieved,
but it reframes it.


---
*Page 17*


Second, the GPQA Diamond scores for GPT-oss-
120B vary significantly across sources, from 71.5 to
80.9, depending on reasoning level and tool use
configuration. The comparison looks very
different depending on which number you use.
Benchmark comparisons should specify these
conditions.
Third, the benchmarks are strong. But
benchmarks are controlled environments. Agentic
multi-step workflows are not. The same RL
training that makes these models good at
structured tasks also means that small errors early
in a chain can cascade into nonsense by step five.
For production use, you need to test that yourself.
Fourth, running the 9B on a laptop for personal
experiments is fine. Running it at inference scale
for a real product is a different story. At full
precision you need a 24GB GPU. With quantization
the quality trade-offs need evaluation for your
specific use case.


---
*Page 18*


And fifth, all four models are from Alibaba. If you
are building something where the provenance of
the weights matters, that is a consideration worth
thinking through.
The Bigger Picture
The Qwen3.5 Small release completes the Qwen3.5
family: the 397B flagship (released February 16),
the medium series (February 24), and now the
small models. All with the same architectural DNA.
All natively multimodal. All Apache 2.0 licensed,
which means you can use them commercially.
What this signals is that the performance gap
between “small and local” and “large and cloud” is
collapsing faster than most people expected. Not
because small models are magically matching
trillion-parameter systems on everything, but
because for many practical tasks, a well-
architected 9B model with the right training is now
good enough to replace an API call.


---
*Page 19*


I find that worth paying attention to. Not because
benchmarks are the point, but because it means
the tools we can actually use in the real world are
getting better in ways that matter.
The models are available on HuggingFace and
ModelScope under Apache 2.0. Base models are
included for research and fine-tuning. If you’re
experimenting with local inference, the 4B is probably
the most interesting starting point for multimodal
work. For serving, the official docs recommend
SGLang, vLLM, or KTransformers over simpler tools
like Ollama.
I write about AI, healthcare ML, and things I actually
find worth paying attention to at Towards Deep
Learning. If this was useful, follow along.
References


---
*Page 20*


[1] OpenAI, “Introducing gpt-oss,” August 5, 2025.
https://openai.com/index/introducing-gpt-oss/
[2] Qwen Team, “Qwen3.5–9B Model Card,”
Hugging Face, March 2, 2026.
https://huggingface.co/Qwen/Qwen3.5-9B
[3] VentureBeat, “Alibaba’s small, open source
Qwen3.5–9B beats OpenAI’s gpt-oss-120B and can
run on standard laptops,” March 2, 2026.
https://venturebeat.com/technology/alibabas-
small-open-source-qwen3-5-9b-beats-openais-gpt-
oss-120b-and-can-run
[4] Clarifai, “OpenAI GPT-OSS Benchmarks: How It
Compares to GLM-4.5, Qwen3, DeepSeek, and Kimi
K2,” August 6, 2025.
https://www.clarifai.com/blog/openai-gpt-oss-
benchmarks-how-it-compares-to-glm-4.5-qwen3-
deepseek-and-kimi-k2
[5] OpenAI, “gpt-oss-120b & gpt-oss-20b Model
Card,” August 5, 2025.


---
*Page 21*


https://arxiv.org/html/2508.10925v1
[6] OfficeChai, “Alibaba Releases Qwen 3.5 Small
Model Series, Achieves GPT-OSS-Level
Performance With A Fraction Of The Parameters,”
March 3, 2026. https://officechai.com/ai/alibaba-
qwen-3-5-0-8b-2b-4b-9b-benchmarks/
[7] Qwen Team, “Qwen3.5 GitHub Repository,”
March 2, 2026.
https://github.com/QwenLM/Qwen3.5
[8] Awesome Agents, “Qwen3.5–9B Model
Overview,” March 2, 2026.
https://awesomeagents.ai/models/qwen-3-5-9b/
[9] MarkTechPost, “Alibaba just released Qwen 3.5
Small models: a family of 0.8B to 9B parameters
built for on-device applications,” March 2, 2026.
https://www.marktechpost.com/2026/03/02/alibaba
-just-released-qwen-3-5-small-models-a-family-of-
0-8b-to-9b-parameters-built-for-on-device-
applications/


---
*Page 22*


[10] Ollama, “Qwen3.5:9b Model Page.”
https://ollama.com/library/qwen3.5:9b
Deep Learning Artificial Intelligence Machine Learning
Qwen Large Language Models
Published in Towards Deep Learning
Following
2.5K followers · Last published 2 days ago
Our publication is dedicated to simplifying the latest
research and applications in deep learning.
Written by Sumit Pandey
Following
4.2K followers · 15 following
PhD in Machine Learning • AI researcher &
Kaggle competitor • Exploring how Deep
Learning shapes health, business & daily life •
Founder Towards Deep Learning
Responses (3)


---
*Page 23*


To respond to this story,
get the free Medium app.
Sbayer
2 days ago
I pulled the Q4_K_M version from Ollama to run local on macbook m4 24
GB , In the Ollama app on my mac this works great , the image analysis is
best I have seen for 9b model ever. Wish Ollama could fix the parameter
to stop the thinking stream, but… more
3
Scollay Petry
2 days ago
>> And not just run it in that “technically works but gives you 2 tokens
per second while your fans scream” kind of way. Actually run it.
This cracked me up because in a recent attempt to run Quen16B in my
fairly robust Macbook Pro, this is exactly… more
5
April Masoncarolan
2 days ago
I don't understand a word of what most of these articles are saying..I
know Grok..Has four agents inside..but mine dont argue..lol


---
*Page 24*


More from Sumit Pandey and Towards
Deep Learning
In by In by
Towards Deep L… Sumit Pa… Towards Deep L… Sumit Pa…
Mojo: The New YOLO26 Just Dropped:
P i Th F t t Obj t
Mojo is 68,000x faster than The new king of computer
P th B ilt b S ift’ t i i i h d it’ t j t
Jan 5 Jan 15
In by In by
Towards Deep L… Sumit Pa… Towards Deep L… Sumit Pa…
TikTok’s Parent Stop Writing Prompts.
C J t B t St t P i
When a social media Stanford’s DSPy framework is
’ h l b h i h b ild AI


---
*Page 25*


Jan 20 Feb 3
See all from Sumit Pandey See all from Towards Deep Learning
Recommended from Medium
In by In by
Predict srgg6701 GoPenAI Allohvk
The Death of Coding Is Why Energy Based
C ll d Wh Y M d l (EBM )
At the start of the project, it Intuition & applications of
lik D i B t EBM
Feb 21 Feb 24


---
*Page 26*


In by In by
AI Advances Delanoe Pirard Activated … Mandar Karhad…
A Discord Community OpenAI Traded Its Soul
B t M t ’ LL MA f St t d P
RWKV-7 scores 72.8% vs OpenAI’s pivot from “Benefit
LL MA’ 697% ith 3 f H it ” t “P fit t All
Feb 22 Feb 8
Ignacio de Gregorio Christian Marques
Anthropic Reveals The Ghost in the
Chi ’ Di t Littl AI M d lb t
…While ousting themselves as A class called Artificial Life
h h it i b f L í
Feb 24 Feb 22
See more recommendations