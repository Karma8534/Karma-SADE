# agentnativedev.medium

*Converted from: agentnativedev.medium.PDF*



---
*Page 1*


Open in app
2
Search Write
Member-only story
Nemotron 3S >
Qwen3.5: One GPU with
120B/12B Parameters
Agent Native Following 9 min read · 4 hours ago
1 1
Nemotron 3 Super delivers 2.2x faster than GPT-
OSS-120B, 7.5x faster than Qwen3.5–122B, and up
to 451.7 tok/s on optimized API providers.


---
*Page 2*


Comparable accuracies across popular benchmarks but provides the highest
inference throughput
At 12B active parameters, you get throughput
comparable to much smaller models while
retaining the knowledge and reasoning depth of a
120B model.


---
*Page 3*


ArtificialAnalysis on Nemotron 3 Super
For agentic workloads where latency directly
impacts user experience and cost, this is
important.
In this article, I’ll cover the most important aspects
of the release: core design, benchmarks, latent
MoE, multi-token predictions, NVFP4 pretraining,
agentic patterns and deployment patterns.


---
*Page 4*


The Core Design
Nemotron 3 Super is a deliberate fusion of three
architectural paradigms, each solving a specific
bottleneck:
Mamba (State-Space Model): O(1) memory per
token during inference. This is what makes
million-token contexts tractable without the
quadratic attention blowup.
Transformer Attention: Retains precise long-
range retrieval when the model needs it. Pure
Mamba struggles with needle-in-a-haystack
tasks and interleaved attention layers fix this.


---
*Page 5*


Mixture-of-Experts: Only 12B of 120B
parameters activate per token. This gives you a
10x capacity-to-compute ratio, the model
“knows” 10x more than it “thinks about” on any
given token.
The architecture spans 88 layers with 512 experts
using top-22 routing.
Hybrid Mamba-2 and MoE design with strategic global attention layers to
optimize the balance between sequence modeling performance and
inference throughput


---
*Page 6*


This is an unusually high expert count with
relatively high sparsity.
More experts with sparser activation means better
specialization per expert while keeping compute
constant.
Agentic SaaS patterns are powering the most
innovative products of 2026.
You can read it here: Agentic SaaS Patterns
Winning in 2026, packed with real-world
examples, architectures, and workflows you won’t
find anywhere else.
LatentMoE: 4x Experts at the Same Cost
Standard MoE models face a parameter-routing
tradeoff: more experts means more parameters,
which means more memory and larger routing
matrices.
Nemotron 3 Super introduces LatentMoE, which
projects expert activations through a 1024-


---
*Page 7*


dimensional latent space before expanding back
to the full 4096-dimensional hidden state.
Nemotron 3 Super Technical Paper: Standard MoE vs. LatentMoE. In
LatentMoE, tokens are projected from the hidden dimension 𝑑 into a
ℓ
smaller latent dimension for routing and expert computation, reducing
ℓ
routed parameter loads and all-to-all traffic by a factor 𝑑/ . These savings
are used to increase both the total number of experts and the top-𝐾
active experts per token by the same factor, improving model accuracy at
approximately constant inference cost.
This compression means NVIDIA can deploy 4x
more experts with the same memory and compute
overhead as a standard MoE at equivalent capacity.


---
*Page 8*


Think of it as a bottleneck autoencoder applied to
expert routing where each expert “thinks” in a
compressed latent space but operates on the full
representation.
Multi-Token Prediction (MTP): The Model
is Its Own Speculative Decoder
Most speculative decoding systems require a
separate draft model.
Nemotron 3 Super uses 2 shared-weight MTP
layers that predict the next 2+ tokens
simultaneously.
The results are striking:


---
*Page 9*


3.45 average acceptance length (highest
reported for any production model)
~97% acceptance rate on the first two predicted
tokens
Acceptance rates are even higher for structured
outputs (code, JSON, tool calls), the patterns that
dominate agentic workloads
This means the model effectively generates ~3.5
tokens per forward pass for agentic tasks, with no
external draft model and no additional memory
overhead.
The shared-weight design also prevents the “head
divergence” problem that plagues multi-head
prediction architectures at longer draft lengths.
Native NVFP4 Pretraining
This is a first.
Rather than training in BF16 and then quantizing
to FP4 post-hoc (losing accuracy), NVIDIA


---
*Page 10*


pretrained directly in NVFP4 across 25 trillion
tokens.
NVFP4 retains 99.8% of BF16 accuracy, far better
than typical post-training quantization, and FP4
inference on a single H100 was the design target
from day one.
Benchmarks & Model Quality:
Let’s look at where Nemotron 3 Super sits against
its direct competitors — Qwen3.5–122B and GPT-
OSS-120B:
Throughput: The Efficiency Story


---
*Page 11*


As per Artificial Analysis benchmarks, Nemotron 3
Super delivers:
2.2x faster than GPT-OSS-120B
7.5x faster than Qwen3.5–122B
Up to 451.7 tok/s on optimized API providers
At 12B active parameters, you get throughput
comparable to much smaller models while
retaining the knowledge and reasoning depth of a
120B model.
For agentic workloads where latency directly
impacts user experience and cost, this is
transformative.
Agentic Capabilities
NVIDIA built the agentic capabilities into the
training pipeline from the ground up.
Training for Agency
The agentic training pipeline is massive:


---
*Page 12*


21 reinforcement learning environments
spanning tool use, code generation, multi-step
reasoning, and planning
1.2 million RL rollouts for agentic behavior
optimization
GRPO/DAPO reinforcement learning (the same
algorithms behind frontier reasoning model
training)
Synthetic data generated from frontier
reasoning models to bootstrap agentic
capabilities
Real-World Agentic Evaluations
Two independent code review evaluations tell a
more honest story:
Greptile Evaluation
Greptile tested Nemotron 3 Super on real
production code review tasks:
12.5 seconds average response time


---
*Page 13*


2 tool calls per review (focused, not chatty)
Caught a CORS regression that could have
shipped to production
Demonstrated genuine architectural
understanding on how a change propagates
through a codebase
The 2-tool-call average is particularly telling.
Many models either under-use tools (answering
from stale context) or over-use them (making 8–10
calls per review, burning latency).
Nemotron 3 Super shows calibrated tool use, it
knows what it needs and gets it efficiently.
Qodo (formerly CodiumAI) Evaluation
Qodo’s evaluation on their proprietary PinchBench
code review benchmark:
73.4% precision — highest among all open-
source models tested


---
*Page 14*


85.6% overall PinchBench score
Positioned as closing the gap between open-
source and proprietary models for production
code review
73.4% precision is significant because false
positives in code review are worse than misses,


---
*Page 15*


developers stop trusting a reviewer that cries wolf.
High precision means the model’s findings are
reliably actionable.
The Super + Nano Deployment Pattern
NVIDIA explicitly designed a two-tier agentic
deployment:
Nemotron 3 Super (120B/12B): Complex
reasoning, code review, multi-step planning.
Low concurrency.
Nemotron Nano (8B dense): High-throughput
simple tasks — classification, extraction,
routing. Handles concurrent requests without
MoE overhead.
A task-complexity router sits in front, estimating
whether each request needs deep reasoning
(Super) or can be handled with pattern matching
(Nano).


---
*Page 16*


This is the pattern most production agent systems
should follow, regardless of model family.
Deployment & Code Examples
Minimum GPU requirement is a B200-80GB or DGX
Spark.
Three production-grade backends are supported.
vLLM:
pip install -U vllm
vllm serve $MODEL_CKPT \
--served-model-name nvidia/nemotron-3-super \
--async-scheduling \
--dtype auto \
--kv-cache-dtype fp8 \
--tensor-parallel-size 2 \
--swap-space 0 \
--trust-remote-code \
--gpu-memory-utilization 0.9 \
--enable-chunked-prefill \
--enable-auto-tool-choice \
--tool-call-parser qwen3_coder \
--reasoning-parser super_v3


---
*Page 17*


SGLang:
python3 -m sglang.launch_server \
--model PATH/TO/CHECKPOINT \
--served-model-name nvidia/nemotron-3-super \
--trust-remote-code \
--tp 2 --ep 1 \
--tool-call-parser qwen3_coder \
--reasoning-parser super_v3
TensorRT-LLM:
trtllm-serve PATH/TO/CHECKPOINT \
--backend pytorch \
--tp_size 2 --ep_size 2 \
--reasoning_parser nano_v3 \
--tool_parser qwen3_coder
Three Reasoning Modes via OpenAI-
Compatible API
The model supports controllable reasoning depth
through the API.
Reasoning ON (default for complex tasks):


---
*Page 18*


from openai import OpenAI
client = OpenAI(base_url="http://localhost:8000/v1",
response = client.chat.completions.create(
model="nvidia/nemotron-3-super",
messages=[{"role": "user", "content": "Explain th
max_tokens=16000,
temperature=1.0,
top_p=0.95,
extra_body={"chat_template_kwargs": {"enable_thin
)
Low-Effort Mode (reduced reasoning overhead
which is ideal for PR summaries, quick lookups):
response = client.chat.completions.create(
model="nvidia/nemotron-3-super",
messages=[{"role": "user", "content": "Summarize
max_tokens=16000,
temperature=1.0,
top_p=0.95,
extra_body={"chat_template_kwargs": {
"enable_thinking": True,
"low_effort": True
}}
)


---
*Page 19*


Reasoning OFF (simple queries with fastest
response and no thinking tokens):
response = client.chat.completions.create(
model="nvidia/nemotron-3-super",
messages=[{"role": "user", "content": "What is 2+
max_tokens=16000,
temperature=1.0,
top_p=0.95,
extra_body={"chat_template_kwargs": {"enable_thin
)
Tool Calling (OpenAI-Compatible)
tools = [
{
"type": "function",
"function": {
"name": "get_weather",
"description": "Get current weather for a
"parameters": {
"type": "object",
"properties": {
"location": {"type": "string"},
"unit": {
"type": "string",
"enum": ["celsius", "fahrenhe
}
},


---
*Page 20*


"required": ["location"]
}
}
}
]
response = client.chat.completions.create(
model="nvidia/nemotron-3-super",
messages=[{"role": "user",
"content": "What's the weather in Amste
tools=tools,
tool_choice="auto",
extra_body={"chat_template_kwargs":
{"enable_thinking": True}}
)
Budget-Controlled Reasoning
This is the power-user pattern.
The ThinkingBudgetClient class lets you cap
reasoning depth by truncating the thinking trace
and continuing generation from the closed
context:
class ThinkingBudgetClient:
def __init__(self, base_url, api_key,
tokenizer_name_or_path):
self.tokenizer = AutoTokenizer.from_pretraine


---
*Page 21*


tokenizer_name_or_path)
self.client = openai.OpenAI(
base_url=base_url, api_key=api_key)
def chat_completion(self, model, messages,
reasoning_budget=512,
max_tokens=1024, **kwargs
# Step 1: Generate reasoning trace up to budg
response = self.client.chat.completions.creat
model=model, messages=messages,
max_tokens=reasoning_budget, **kwargs)
reasoning = response.choices[0].message.conte
# Force close reasoning if not already closed
if "</think>" not in reasoning:
reasoning = f"{reasoning}.\n\n</think>\n"
# Step 2: Continue from closed reasoning trac
messages.append(
{"role": "assistant", "content": reasonin
prompt = self.tokenizer.apply_chat_template(
messages, tokenize=False,
continue_final_message=True)
response = self.client.completions.create(
model=model, prompt=prompt,
max_tokens=max_tokens, **kwargs)
return {"reasoning": reasoning,
"content": response.choices[0].text}
This is particularly useful for agentic loops where
you want to enforce latency budgets, i.e. let the
model think for up to N tokens, then force an
answer.


---
*Page 22*


OpenCode Agent Configuration
For local coding agent setup with OpenCode:
{
"$schema": "https://opencode.ai/config.json",
"model": "local/nvidia-nemotron-3-super",
"provider": {
"local": {
"npm": "@ai-sdk/openai-compatible",
"options": {
"baseURL": "http://localhost:8000/v1",
"apiKey": "EMPTY"
},
"models": {
"nvidia-nemotron-3-super": {
"name": "nvidia/nemotron-3-super",
"limit": {
"context": 1000000,
"output": 32768
}
}
}
}
}
}
MoE Concurrency
This is critical for production planning.


---
*Page 23*


Low Concurrency (1–5 requests): The Sweet Spot
At low concurrency, MoE models excel.
Only 12B active parameters are loaded per request,
yielding fast inference with minimal memory
bandwidth consumption.
This is the sweet spot for single-user or small-team
deployments.
As concurrent requests grow, the set of unique
active experts increases across all requests.
Different tokens in different requests may route to
different experts, and eventually all 120B
parameters need to be resident in GPU memory.
On bandwidth-limited hardware, this becomes the
primary bottleneck.
Community reports confirm that performance
degrades noticeably beyond ~5 concurrent
requests.


---
*Page 24*


Fine-Tuning & Customization Cookbook
NVIDIA provides three primary fine-tuning
pathways, all available through the NeMo
ecosystem:
LoRA SFT using NeMo Megatron-Bridge: The
standard approach for enterprise fine-tuning.
Leverages Megatron’s distributed training
infrastructure for multi-GPU LoRA adaptation.
LoRA SFT using NeMo Automodel: A simplified
API for single-node fine-tuning with automatic
parallelism configuration.
GRPO/DAPO using NeMo RL: For reinforcement
learning-based agentic reasoning improvement.
Uses the same infrastructure that trained the
base model.
Practical Recommendations
DGX Spark / ZGX with 128GB: Use NVFP4
weights + FP8 KV cache. Model footprint ~69.5


---
*Page 25*


GiB, KV cache ~33.6 GiB. Reported throughput:
~16.6 tok/s (Marlin weight-only dequant).
High-concurrency agentic flows (>5 concurrent
agents): Consider dense models (e.g., Qwen3.5
9B) where all parameters are always active and
throughput scales predictably.
Low-concurrency complex reasoning:
Nemotron 3 Super is optimal, the 10x capacity-
to-compute ratio provides maximum
intelligence per token.
Hybrid approach: Use Nano for high-
concurrency simple tasks, Super for low-
concurrency complex reasoning, routing based
on task complexity estimation.
For further information you can refer to technical
paper.
Concluding Thoughts
Nemotron 3 Super is not universally the best
model but it could be the most efficient model in


---
*Page 26*


the market for agentic, long-context, and tool-
augmented workloads right now.
For raw knowledge tasks or maximum coding
accuracy, denser competitors may be preferable.
The optimal strategy is often a tiered deployment
combining Nano, Super, and proprietary models
based on task complexity.
Bonus Articles
7 Local LLM Families To Replace
Cl d /C d (f d t k )
Open-source model families you can run
l ll th t d li i l ld
agentnativedev.medium.com
I Ignored 30+ OpenClaw Alternatives Until
O F
Fully open-source Agent Operating System,
itt ti l i R t hi i i l
agentnativedev.medium.com
Qwen 3.5 35B-A3B: Why Your $800 GPU
J t B F ti Cl AI
I have been running local models for a while
d I th ht I h d tt d


---
*Page 27*


agentnativedev.medium.com
GET SH*T DONE: Meta-prompting and
S d i D l t f Cl d C d
GSD (“Get Shit Done”) aims to solve context
t th lit d d ti th d l’
agentnativedev.medium.com
OpenClaw Memory Systems That Don’t
F t QMD M 0 C Ob idi
If your agent has ever randomly ignored a
d i i k t ld it it’ t
agentnativedev.medium.com
Fully Autonomous Companies: OpenClaw
G t + R ti + A t
Whether you think it’s hype or not, people are
l d t i t f ll t
agentnativedev.medium.com
Why Codex Became My Default Over
Cl d C d (f N )
If you haven’t tried Codex yet, I’ve got a brief
t k th t i ht f h
agentnativedev.medium.com
I deleted all my MCPs: Skills + CLI
t f t 20 l t
MCP servers inject 10,000–55,000 tokens of
t l h b t CLI t l t 200 500
agentnativedev.medium.com


---
*Page 28*


Nvidia Nemotron Qwen Gpt Agentic Ai AI Agent
Written by Agent Native
Following
6.3K followers · 0 following
Hyperscalers, open-source developments, startup
activity and the emerging enterprise patterns
shaping agentic AI.
Responses (1)
To respond to this story,
get the free Medium app.
Some Guy
57 mins ago
I check models by having them code a solution to the trapping rainwater
problem, then i have grok evaluate the solution. This is the first local
model I've run that got the solution perfectly, according to grok.


---
*Page 29*


More from Agent Native
Agent Native Agent Native
I deleted all my MCPs: The P99 Problem:
Skill + CLI t f D i i LLM
MCP servers inject 10,000– One prompt. One model.
55 000 t k f t l Cl h d N i
1d ago Jan 17
Agent Native Agent Native
‑
Qwen3 TTS Over Can’t self-host
El L b O L G h? Skill i
‑
Qwen3 TTS is a suite of You build a LangGraph
ltili l t t t h kfl it k
Jan 25 Feb 18


---
*Page 30*


See all from Agent Native
Recommended from Medium
Will Lockett ADITHYA GIRIDHARAN
Sam Altman Is Zvec: Alibaba Just
D l B i O S d “Th
Was that a hint of dystopian Every decade or so, someone
d ti t h i ? t k f l t h l
Feb 28 Feb 13
In by In by
Level Up Coding Florian June Towar… Mandar Karhade, …


---
*Page 31*


MonkeyOCR v1.5: The Anthropic
M ki C l PDF Sh k Wh
If you’ve ever worked with real When an AI model does in
d d t PDF i t h t h
Feb 6 Feb 22
In by Alden Do Rosario
CodeX MayhemCode
No, PageIndex Will Not
Apple Silicon and TPUs
“Kill” RAG B t It I
f AI Th D l
An independent benchmark
When I told my infrastructure
li h t b d
t d l i
Feb 9 Jan 31
See more recommendations