# Mistral4Small

*Converted from: Mistral4Small.PDF*



---
*Page 1*


Open in app
Search Write
Member-only story
Mistral Small 4: The
Open-Source Model
That Does Everything
and Costs You Nothing
to License
Mistral just shipped reasoning, vision, and
agentic coding in a single Apache-licensed
model. 119 billion parameters. 6 billion active.
And you can run it on your own hardware
without asking anyone’s permission.
Mandar Karhade, MD. PhD. Follow 11 min read · 5 days ago
290
TLDR


---
*Page 2*


Mistral Small 4 unifies reasoning, vision, and
coding into one 119B MoE model under Apache
2.0.
128 experts, 4 active per token; only 6B
parameters fire per inference pass.
Benchmarks match or beat models 3x its active
compute on reasoning and code tasks.
Configurable reasoning depth per request is a
genuine architectural innovation.
Mistral Forge lets enterprises train custom
models from scratch on private data.
Friends link for everyone: Follow the author,
publication, and clap. Join Medium to support
other writers too! Cheers
There’s a quiet war happening in AI right now, and
it has nothing to do with who has the biggest
model. It has nothing to do with benchmarks,


---
*Page 3*


frontier capabilities, or who raised the most
money last quarter.
The war is about ownership. Who
owns the model.
Who owns the weights. Who owns the right to
modify, deploy, and shut down the AI running
inside their own infrastructure.
And in that war, Mistral just dropped a weapon.


---
*Page 4*


Here’s the thing; Mistral Small 4 isn’t the biggest
model. It isn’t the highest on every leaderboard. It
isn’t going to dethrone GPT-4.5 or Claude Opus on
the tasks where raw scale wins. But it might be the
most important model release of 2026 so far.


---
*Page 5*


Because it does three things that nobody else is
doing simultaneously
Reasoning, vision, and agentic coding, in a
single model, under the Apache 2.0 license, with
weights you can download right now
No API key required. No terms of service that
change on a Tuesday. No vendor who can
deprecate your model while you’re in
production.
This is what open source AI was supposed to
look like.
Also, not directly related to the model but, Mistral,
the French startup that started with a 7B
parameter model dropped via torrent link in 2023,
is the one actually delivering it. You are going to
see BYO-AI deals by Mistral in the recent future
too. They are really going for soverign AI.


---
*Page 6*


128 Experts, 6 Billion Active Parameters,
and Why the Numbers Matter
Let’s get into the architecture because it’s
genuinely clever.
Mistral Small 4 is a Mixture-of-Experts model with
119 billion total parameters. But here’s the trick:
only 6 billion parameters activate per token. The
model has 128 expert subnetworks, and a learned
routing function selects the top 4 experts for each
forward pass. Include the embedding and output
layers, and you’re looking at roughly 8 billion
active parameters per inference step.
Why does this matter? Because you get the
knowledge capacity of a 119B model with the
inference cost of an 8B model. The compute math
changes completely. Latency drops 40% compared
to Mistral Small 3. Throughput triples. And the
256,000-token context window means you can feed


---
*Page 7*


it an entire codebase, a full novel, or months of
document history in a single prompt.


---
*Page 8*


Truth be told, MoE isn’t new. Mixtral pioneered
this at Mistral back in December 2023 with 8
experts. But 128 experts with 4 active is a different
beast entirely. The routing granularity is
dramatically finer. Each token gets dispatched to a
more specialized subset of the model’s knowledge,
which is why the output quality punches above
what the active parameter count would suggest.
The minimum deployment footprint is 4x NVIDIA
H100 GPUs, or 2x H200s, or a single DGX B200.
That’s not cheap for an individual developer, but
for any serious enterprise or research lab, it’s
completely reasonable. And Mistral provides vLLM
Docker images, llama.cpp GGUF quantizations,
and NVIDIA NIM integration out of the box. You
can be serving this model in production within
hours of downloading the weights.
One Model Where There Used to Be Three


---
*Page 9*


Here’s where Mistral’s strategy becomes clear.
Before Small 4, the Mistral ecosystem had separate
models for separate jobs:
Magistral for reasoning and chain-of-thought
tasks
Pixtral for multimodal vision and document
understanding
Devstral for coding and agentic software
engineering
Small 4 unifies all three into a single model. One
set of weights. One deployment. One API. That’s
not just a convenience upgrade; it’s an operational
revolution for anyone running Mistral in
production. Instead of managing three model
deployments with different hardware profiles,
routing logic, and version dependencies, you
deploy one model and configure its behavior per
request.


---
*Page 10*


The mechanism is the reasoning_effort parameter.
Set it to "none" and you get fast, lightweight
responses comparable to the old Mistral Small 3.2.
Set it to "high" and the model engages deep step-
by-step reasoning equivalent to Magistral. Same
model, same weights, same deployment. Just a
different inference configuration.


---
*Page 12*


Oh! This is actually a big deal. Most reasoning
models force you to choose at deployment time
whether you want a fast model or a thinking
model. Mistral lets you choose per request. Your
chatbot can give quick answers to simple questions
and switch to deep reasoning for complex analysis,
all in the same conversation, without routing to a
different model.


---
*Page 13*


I haven’t seen anyone else ship configurable
reasoning depth as a first-class API parameter. Not
OpenAI. Not Anthropic. Not Google. Mistral got
there first.
The Benchmarks Tell a Story About
Efficiency, Not Just Score
Let’s talk numbers. But let’s talk about them
honestly, because Mistral’s benchmark story is
unusual.
On GPQA Diamond (graduate-level science
reasoning), Small 4 scores 71.2%. On MMLU-Pro
(multi-task language understanding), it hits 78.0%.
On AIME 2025 (competitive math), it matches or
surpasses GPT-OSS 120B at the high reasoning
setting. On LiveCodeBench, it outperforms GPT-
OSS 120B while producing 20% less output.
But the most revealing benchmark is AA LCR, the
long-context reasoning test. Small 4 scores 0.72


---
*Page 14*


with outputs of about 1,600 characters. Qwen 3.5–
122B hits similar scores but needs 5,800 to 6,100
characters of output to get there. That’s 3.5 to 4
times more tokens for the same result.
Here’s the thing: token efficiency matters more
than raw score for anyone paying inference costs.
If your model needs 4x the output tokens to reach
the same answer, your effective cost per task is 4x
higher regardless of what the per-token pricing
looks like. Mistral’s output efficiency means the
$0.15/M input and $0.60/M output pricing is even
more competitive than the headline numbers
suggest.
Now. Are there gaps? Yes.
The model’s spatial reasoning and structured
diagram generation are weak. There’s no audio or
video input support. The benchmark transparency
is incomplete; standard MMLU, HumanEval, and
MATH scores are conspicuously absent from the
launch materials. Mistral should publish those. But


---
*Page 15*


what’s there is strong, and the efficiency story is
the real differentiator.
Why Apache 2.0 Is the Point, Not a
Footnote
This is the section that matters most. And it’s the
one most reviewers skip.
Mistral Small 4 ships under the Apache 2.0 license.
Not “open weights with a non-commercial clause.”
Not “you can look but don’t compete with us.” Not
Meta’s approach with Llama, where the license
includes usage restrictions that kick in at 700
million monthly active users and prohibit using
the outputs to train competing models.
Availability
Mistral API and AI Studio
Hugging Face Repository


---
*Page 16*


Developers can prototype Mistral Small 4 for
free on NVIDIA accelerated computing at
build.nvidia.com, and for production
deployment, Mistral Small 4 is available day-0 as
an NVIDIA NIM, delivering optimized,
containerized inference out of the box.
It can also be customized with NVIDIA NeMo for
domain-specific fine-tuning.
Technical documentation for customers is
available on our AI Governance Hub
Apache 2.0. Full stop. Use it commercially. Fine-
tune it. Redistribute it. Build a product on it. Train
a derivative model. Modify the weights and never
tell anyone. The license imposes no restrictions
beyond standard patent and attribution provisions.
In an industry where “open source” has been
stretched to mean “you can see our weights but
read the fine print,” Mistral’s commitment to
actual, real, no-asterisk Apache licensing is
remarkable. They’ve been doing this since day one.


---
*Page 17*


Mistral 7B in September 2023: Apache 2.0. Mixtral
8x7B in December 2023: Apache 2.0. And now their
most capable model to date, a 119B parameter
multimodal reasoning system: Apache 2.0.
https://londontechweek.com/speakers/arthur-mensch
This isn’t a PR strategy. This is a philosophy. Arthur
Mensch, Mistral’s CEO, has been explicit about it.
His position is that open source should be the
foundation of AI if the goal is for every company


---
*Page 18*


and every state to own their destiny in an economy
increasingly driven by AI. He’s argued that AI
should be a tool for empowerment, not
dominance. That everyone running AI workloads
should have access to the on and off switch. That
they should not be dependent on external
providers who can turn off the button.
But wait. Isn’t this just the European sovereignty
pitch? Partly. Mensch is French. Mistral is
headquartered in Paris. The European angle is real
and strategic. When he points out that there’s a
problem if Europe imports 80% of its AI
technology from two countries whose strategic
alignment is increasingly problematic, he’s not
wrong. The DOJ recently blocked Anthropic from
certain warfighting systems. Export controls
reshape the GPU landscape quarterly. API terms of
service change without notice.
But the philosophy transcends geography. An
Apache-licensed model is sovereign for everyone.


---
*Page 19*


A startup in Lagos. A hospital in São Paulo. A
defense contractor in Seoul. A research lab in
Berlin. They all get the same rights, the same
weights, the same ability to build without
permission.
What does “open source AI” mean if not this?
The Open-Source Trajectory That Got Us
Here
Mistral’s journey to Small 4 is worth understanding
because it shows a consistent pattern that’s rare in
this industry.
September 2023: Mistral 7B drops via a torrent
link. No press conference. No waitlist. Just a
magnet link on Twitter and an Apache license.
The model was the most capable 7B parameter
model available at the time, and it caught the
entire industry off guard. A French startup
nobody had heard of, founded four months


---
*Page 20*


earlier, shipping frontier-competitive models via
BitTorrent.
December 2023: Mixtral 8x7B arrives. The first
serious open MoE model. 8 experts, 2 active per
token. It proved that mixture-of-experts could
work at scale in the open ecosystem, not just
inside Google’s infrastructure. Apache 2.0.
Then came Mixtral 8x22B. Then Mistral Small 3.
Then Codestral for code generation. Pixtral for
vision. Magistral for reasoning. Devstral for
agentic coding. Each one Apache-licensed. Each
one pushing the boundary of what was available
without a vendor lock-in
And now Small 4 unifies the entire family into a
single model. The arc from “unknown French
startup drops a 7B model via torrent” to “119B
multimodal reasoning agent under Apache 2.0”
took less than three years.
The trajectory is what genuine commitment to
open source looks like. Not a marketing strategy


---
*Page 21*


that gets abandoned when the economics get
uncomfortable. A sustained engineering program
that consistently ships state-of-the-art capabilities
under the most permissive license available.
Mistral Forge: When Open Source Meets
Enterprise Revenue
So how does a company that gives away its best
models for free make money? This is the question
every open-source AI company has to answer, and
Mistral’s answer is Forge.
Mistral Forge, announced at NVIDIA GTC, is a
platform that lets enterprises train custom AI
models from scratch on their own data. Not fine-
tuning an existing model. Not RAG over a base
model. Actually training new models using
Mistral’s internal methodology, data mixing
strategies, distributed computing optimizations,
and what they call “battle-tested training recipes.”


---
*Page 22*


Mistral bets on 'build-your-own AI' as it
t k O AI A th i i th
Mistral Forge lets enterprises train custom AI
d l f t h th i d t
techcrunch.com
The platform deploys on-premise or in private
clouds. Sensitive data never leaves the enterprise’s
controlled environment. And for teams that need
hands-on help, Mistral provides forward-deployed
engineers who embed directly with customers.
Early adopters include Ericsson, the European
Space Agency, the Italian consulting firm Reply,
and Singapore’s DSO and HTX. And Mensch says
the company is on track to surpass $1 billion in
annual recurring revenue this year.
Open Model that Everyone Trusts
This isn’t the usual “open source the model, charge
for the API” play. This is: open source the model so
everyone trusts your engineering, then sell the
methodology, the infrastructure, and the expertise
to enterprises who want to build something


---
*Page 23*


custom. The open-source models are the top of
funnel. Forge is the revenue engine.
It’s a better model than what most AI companies
are running. OpenAI and Anthropic charge per
token on proprietary models you can’t inspect,
modify, or self-host. Mistral charges for the
capability to build your own. One approach creates
dependency. The other creates capability.
What does it mean for the Ecosystem
Mistral Small 4 isn’t perfect. The hardware
requirements exclude hobbyists and small teams.
Please dont come after me for “But it has only X
billion active neurons, I get it” .. The benchmark
coverage has gaps. Spatial reasoning is weak. The
ecosystem around it is younger and less battle-
tested than what surrounds Llama or the OpenAI
API.


---
*Page 24*


But none of that changes the significance of what
Mistral is doing.
They’ve shipped a 119B parameter multimodal
reasoning model with configurable inference depth,
256K context, native function calling, 24-language
support, and vision capabilities. Under Apache 2.0.
With weights on HuggingFace. With vLLM
deployment scripts in the repo. With NVIDIA NIM
integration on day one. With speculative decoding
checkpoints for performance optimization. With 4-bit
quantization options for smaller hardware footprints.
And they’re founding members of the NVIDIA
Nemotron Coalition for open-source AI
advancement, which means this isn’t a one-off
release; it’s an institutional commitment to keep
shipping open models as capabilities scale.
In an industry where the trend has been toward
closing models as they get more capable, toward
restrictive licenses disguised as openness, toward


---
*Page 25*


API-only access with terms that change quarterly,
Mistral is swimming upstream. Deliberately.
Consistently. And profitably.
The model is available now. The weights are on
HuggingFace. The license is Apache 2.0. The API is
live at $0.15 per million input tokens.
This is my perspective. You should do what you are
comfortable with. But if you’re building anything
that touches AI and you haven’t evaluated what the
open-source ecosystem can do in 2026, you’re
making a choice by not choosing. And Mistral just
made that choice a lot harder to justify.
If you have read it until this point, Thank you! You
are a hero (and a Nerd ❤)! I try to keep my readers
up to date with “interesting happenings in the AI
🔔 🔔
world,” so please clap | follow | Subscribe


---
*Page 26*


AI Agent Agentic Ai Enterprise Technology LLM
Artificial Intelligence
Written by Mandar Karhade, MD.
Follow
PhD.
4.5K followers · 142 following
Life Sciences AI/ML/GenAI advisor
No responses yet
To respond to this story,
get the free Medium app.
More from Mandar Karhade, MD. PhD.


---
*Page 27*


In by In by
Towar… Mandar Karhade, … Towar… Mandar Karhade, …
Google Finally Figured The Great Distillation
O t Th t H i th H i t Wh A th i
Google AI Studio just shipped When 24,000 bots walk into a
th thi ib b th d ’t b d i k
5d ago Feb 24
In by In by
AI Adva… Mandar Karhade,… AI Adva… Mandar Karhade,…
The Contracts You Autoresearch: A Code-
N R d B t i L l D Di i t
A Trinity College Dublin What happens when you let an
h t d ll th fi AI t i d M
2d ago Mar 14
See all from Mandar Karhade, MD. PhD.


---
*Page 28*


Recommended from Medium
In by In by
Towards AI Kory Becker AI Adva… Mandar Karhade,…
My First Month With Why Doc-to-LoRA is
O Cl Th S t th E d f th C t t
Hard-earned lessons on We are now predicting
h d h i i ht i i l f d
Mar 9 Mar 4


---
*Page 29*


Agent Native Alain Airom (Ayrom)
Google Workspace CLI: Docling-Agent is
A t N ti C i B b’
The hardest part about Bob + Docling-Agent:
i t ti ith t i A t ti Si lifi d
Mar 8 Mar 7
Vignaraj Ravi Reza Rezvani
Mastering OpenClaw: Claude Code /loop —
Y Ulti t G id t H A 3
Feb 24 Mar 9
See more recommendations