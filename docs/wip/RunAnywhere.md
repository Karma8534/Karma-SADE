# RunAnywhere

*Converted from: RunAnywhere.PDF*



---
*Page 1*


Open in app
8
Search Write
Data Science Col…
Member-only story
RunAnywhere: Turning
Your M2 Mac Into A
Serious AI Inference
Box
Sebastian Buzdugan Follow 8 min read · Mar 11, 2026
222 1
Most developers are sitting on a surprisingly
powerful inference machine and barely using it. If
you have an M1 or M2 Mac and you are still routing
everything through a cloud GPU, you are leaving
money and latency on the table.


---
*Page 2*


Click here to read this article for free
Why local inference on Apple Silicon
suddenly matters
Apple Silicon quietly changed the equation for
running models locally. The unified memory, fat
memory bandwidth, and decent GPU / Neural
Engine mean your laptop is no longer just a client.
The problem is that the tooling has been a mess.
Every project has its own runtime, its own model
format, its own CLI, and half of them break on
macOS.


---
*Page 3*


RunAnywhere is trying to flatten that. It gives you
a single CLI (rcli) that can pull, run, and
benchmark models on Apple Silicon using
optimized backends.
The goal is simple. Treat your Mac like a mini
inference server, with one command.
What RunAnywhere actually is
At the core, RunAnywhere is three things.
A CLI tool (rcli) that you install locally. A set of
optimized runtimes for different model types,
tuned for Apple Silicon. A registry of
preconfigured models with sensible defaults.
It is not a new model format. It is not trying to
replace PyTorch or TensorFlow.
Think of it as a thin orchestration layer around
existing engines, plus some smart defaults for


---
*Page 4*


Apple hardware. You tell it what model to run, it
picks the best backend and configuration for your
chip.
Quick mental model: how works
rcli
If you strip away the marketing, rcli does roughly
this.
You run a command like:
rcli run --model deepseek-ai/DeepSeek-R1-Distill-Qwen
Under the hood it will:
Resolve the model name to a real artifact
(Hugging Face, custom URL, or their registry).
Download and cache the model locally.
Pick a runtime (MLX, GGML, ONNX, etc) based
on model type and device.


---
*Page 5*


Pick a compute target (GPU, CPU, or Neural
Engine) based on your chip and flags.
Run the inference loop and stream tokens back
to your terminal.
From your point of view it feels like curl for
models. From the system point of view it is a small
scheduler that knows how to drive Apple Silicon
efficiently.
Installation and first run
If you are on an M1 or later, you can usually get
started with:
brew install runanywhereai/tap/rcli
Or you can grab a binary from their releases. The
tool is written in Rust, so startup is fast and
overhead is low.


---
*Page 6*


Once installed, a basic sanity check is:
rcli run --model runanywhereai/tiny-llama --input "He
You should see streaming output in the terminal.
No API key, no cloud account, no container, just
your Mac.
The interesting part: Apple Silicon
optimization
Most projects treat Apple Silicon as an
afterthought. RunAnywhere leans into it.
Apple Silicon gives you three main compute paths.
CPU: good scalar performance, many cores,
great for smaller models.
GPU: high throughput, great for matrix heavy
ops, ideal for many transformer workloads.


---
*Page 7*


Neural Engine (ANE): specialized, very fast for
supported ops, but picky about formats.
The trick is picking the right path per model and
per size. A 1.5B parameter model might run great
on ANE or GPU. A 7B model might be better on
GPU with low precision weights.
RunAnywhere uses Apple friendly runtimes like
MLX where possible. MLX is Apple’s own array
library for machine learning that talks directly to
the GPU and ANE.
So when you run an LLM through rcli, you are not
just getting a naive CPU loop. You are getting the
best available backend for your chip, with
quantization and layout choices that match the
hardware.
Model formats and runtimes


---
*Page 8*


This is where most engineers get burned. You
download a model, it is in Safetensors, but your
runner wants GGUF, and your converter fails in
silence.
RunAnywhere tries to hide that pain. It works with
multiple formats and wraps multiple engines.
Typical combinations look like this.
GGUF + llama.cpp style runtime for quantized
LLMs.
MLX models for Apple centric deployments.
ONNX or similar for vision or encoder models.
You do not choose the runtime directly in most
cases. You choose the model, and the CLI chooses
the runtime that can handle it.
If you want to be explicit, you can pass flags to
force a backend or a device, but the default path is
usually good.


---
*Page 9*


A concrete example: running DeepSeek
locally
Let us use a real model many people care about.
DeepSeek R1 Distill Qwen 1.5B is a small reasoning
model that runs well on consumer hardware.
With RunAnywhere:
rcli run \
--model deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B \
--input "You are a senior engineer. Explain what a
This will:
Pull the model from Hugging Face (or cache if
present).
Choose an Apple friendly backend.
Run generation with streaming output.


---
*Page 10*


You can add flags like --max-tokens 256 or --
temperature 0.2 to control behavior. If you are
building a local dev tool, this is enough to wire into
a simple CLI or TUI.
Using it as an HTTP server
Most real projects do not want a CLI, they want an
API. RunAnywhere lets you turn your Mac into a
local inference server with one command.
rcli serve \
--model deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B \
--port 8080
That spins up an HTTP endpoint on
localhost:8080. The API is usually OpenAI
compatible or close enough that you can point
existing clients at it.
A minimal curl call might look like:


---
*Page 11*


curl http://localhost:8080/v1/chat/completions \
-H "Content-Type: application/json" \
-d '{
"model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.
"messages": [{"role": "user", "content": "Write a
}'
Now you can plug this into your app, editor plugin,
or internal tools. No external API costs, no PII
leaving your laptop.
Benchmarking: know if your Mac is
actually fast
A lot of people guess about performance.
RunAnywhere ships with a benchmarking mode so
you can get real numbers.
rcli bench \
--model deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B \
--input "Explain the difference between CPU and GPU


---
*Page 12*


You will get output like tokens per second, latency
to first token, and total duration. This is crucial if
you want to compare:
Different models at the same size.
Different quantization levels.
CPU vs GPU vs ANE choices.
Once you have numbers, you can make real
tradeoffs. For example, you might accept slightly
lower quality for a 2x speedup in a coding
assistant.
Integrating with your own code
If you prefer to own the loop, you can treat rcli as
a subprocess. This is not fancy, but it is robust.
In Python:
import subprocess, json, sys


---
*Page 13*


prompt = "Summarize the SOLID principles in 3 sentenc
proc = subprocess.Popen(
["rcli", "run", "--model", "runanywhereai/tiny-ll
stdout=subprocess.PIPE,
text=True,
)
for line in proc.stdout:
sys.stdout.write(line)
You can also hit the HTTP server instead and use
any OpenAI compatible client. That decouples
your app from the local runtime and lets you swap
in a remote endpoint later.
Why this is different from just using
Ollama
If you are already running models locally, you
might be thinking: this sounds like Ollama. There
is overlap, but there are some differences that
matter for engineers.
Ollama focuses heavily on a curated model list and
a very simple UX. It is fantastic for general users


---
*Page 14*


and many developers.
RunAnywhere leans more into performance
tuning for Apple Silicon and flexible model
sources. You can point it at Hugging Face models
directly, and it is designed to be a thin layer over
optimized runtimes rather than a full managed
ecosystem.
If you want a polished desktop experience, Ollama
is hard to beat. If you want a tool that behaves
more like a low level inference runner with Apple
specific optimizations, RunAnywhere is worth a
look.
Practical use cases that actually benefit
A lot of local inference talk is hype. Let us narrow
it to use cases where RunAnywhere on Apple
Silicon is genuinely strong.


---
*Page 15*


Local coding assistants integrated into your
editor, with no API latency or cost.
Privacy sensitive text processing, like internal
logs or customer data, that you cannot send to a
cloud LLM.
Prototyping new prompts or small workflows
before you commit to a big hosted model.
Running small reasoning models like DeepSeek
R1 distills for experimentation without renting
GPUs.
If your workload is batch heavy or you need 70B
parameter models, you still want a data center. If
your workload is interactive and fits in 16 to 32 GB,
your Mac can handle more than you think.
Limitations and gotchas
This is not magic. There are real constraints you
should keep in mind.


---
*Page 16*


Apple Silicon memory is unified, but it is still
finite. Large models will happily eat your RAM and
swap if you are not careful.
The Neural Engine only supports certain
operations and model formats. Not every model
will run on ANE, even if the marketing implies it.
Quantization is a tradeoff. 4 bit weights might be
fast, but you can lose quality, especially for small
models.
RunAnywhere is also a young project. Expect some
rough edges, missing models, or occasional
backend issues.
Treat it like a sharp tool, not a fully managed
platform. You will get the most out of it if you are
comfortable reading error messages and tweaking
flags.


---
*Page 17*


When to reach for RunAnywhere in your
stack
If you are building an AI heavy product, you
probably want a mix of local and remote inference.
RunAnywhere fits nicely into a few layers.
Use it in development to iterate on prompts and
flows without burning API credits. Use it for offline
capable features, like a local summarizer or code
assistant.
Use cloud LLMs for heavy reasoning, large context
windows, or production scale traffic. Use your Mac
as a fast, cheap, and private sidecar.
The key is to treat local inference as a first class
resource, not a toy. Once you have a CLI like rcli
wired into your tooling, it becomes natural to ask:
should this call really go to the cloud?
Final thoughts


---
*Page 18*


Most of us upgraded to M1 or M2 for battery life
and build quality. We accidentally bought pretty
decent inference hardware.
RunAnywhere is interesting because it respects
that hardware. It gives you a simple interface on
top of optimized runtimes that actually use the
GPU and Neural Engine.
If you are a developer who cares about latency,
cost, and control, you should at least benchmark
your use case locally. RunAnywhere makes that
experiment a one line command instead of a
weekend of glue code.
The cloud is not going away. But your laptop is a lot
more than a thin client now.
Resources & References
RunAnywhere rcli – GitHub Repository
RunAnywhereAI Organization on GitHub


---
*Page 19*


Apple Silicon Architecture Overview — Apple
Developer
Metal Performance Shaders for Machine
Learning — Apple Developer
Core ML: Integrating Machine Learning Models
on Apple Platforms
Stay in Touch
Short takes and discussions on X →
https://x.com/sebuzdugan
Practical AI / ML videos on YouTube →
https://www.youtube.com/@sebuzdugan/
Partnerships & collabs → sebuzdugan@gmail.com
Artificial Intelligence Machine Learning Technology


---
*Page 20*


Published in Data Science Collective
Following
906K followers · Last published 1 day ago
Advice, insights, and ideas from the Medium data
science community
Written by Sebastian Buzdugan
Follow
928 followers · 504 following
ML Engineer | PhD Student in AI
Responses (1)
To respond to this story,
get the free Medium app.
Jari Pekki
6 days ago
A very good article. However, it seems that on March 27, 2026 this
updated installation command works better on macOS26:
brew tap RunanywhereAI/rcli
https://github.com/RunanywhereAI/RCLI.git
brew install rcli
rcli setup


---
*Page 21*


2 1 reply
More from Sebastian Buzdugan and Data
Science Collective
In by In by
Data Science … Sebastian B… Data Science … Arunn The…
Why Microsoft BitNet How I’m Upskilling as a
C ld B th E d f S i AI E i i
Everyone is busy chasing My blueprint for staying AI-
bi GPU b t Mi ft l t i 2026 & b d
Mar 12 Feb 7
In by In by
Data Science C… Andres Vo… Data Science … Sebastian B…


---
*Page 22*


What My Senior Data Why Cursor’s “In-
S i ti t R l H ” M d l I R ll
Working at a scale-up with
t AI d ti
Mar 9 Mar 23
See all from Sebastian See all from Data Science
Buzdugan Collective
Recommended from Medium
In by In by
Generativ… Gaurav Shriva… Towards AI Ari Vance
I Threw Out My Vector This 196B Open-Source
D t b RAG G t M d l B t Cl d
Here’s what happens when Every week, the same models
l t LLM i t d i t Li k dI /
Mar 24 Mar 23


---
*Page 23*


In by Ege Karaosmanoglu
Level Up Coding David Lee
Apache Camel Was
The Rules NASA Uses
Al d G t AI
t W it C d Th t
There’s a quiet reason Apache
In 2006, a NASA engineer
C l i b i f th
t t l f iti
Mar 18 Mar 17
In by In by
AI Software Engi… Joe Nje… Stackademic Brevis
Anthropic Leaks (New) 10 Most(ly Dead)
Cl d M th (A d I fl ti l
Claude Mythos is the new The languages everyone
AI d l A th i f t b t d
5d ago Feb 21
See more recommendations