# Genma4new

*Converted from: Genma4new.PDF*



---
*Page 1*


Google releases Gemma 4 under Apache
2.0 — and that license change may
matter more than benchmarks
Sam Witteveen
April 2, 2026
Credit: VentureBeat made with GPT-Image-1.5


---
*Page 2*


For the past two years, enterprises evaluating open-weight models
have faced an awkward trade-off. Google's Gemma line
consistently delivered strong performance, but its custom license
— with usage restrictions and terms Google could update at will
— pushed many teams toward Mistral or Alibaba's Qwen instead.
Legal review added friction. Compliance teams flagged edge cases.
And capable as Gemma 3 was, "open" with asterisks isn't the same
as open.
Gemma 4 eliminates that friction entirely. Google DeepMind's
Apache 2.0
newest open model family ships under a standard
license
— the same permissive terms used by Qwen, Mistral,
Arcee, and most of the open-weight ecosystem.


---
*Page 3*


GGeemmmmaa 44 HHaass LLaannddeedd!!
Sam Witteveen
No custom clauses, no "Harmful Use" carve-outs that required
legal interpretation, no restrictions on redistribution or
commercial deployment. For enterprise teams that had been
waiting for Google to play on the same licensing terms as the rest
of the field, the wait is over.
Learn More
Skip Ad
AAdd :: ((00::2233))


---
*Page 4*


The timing is notable. As some Chinese AI labs (most notably
Alibaba’s latest Qwen models, Qwen3.5 Omni and Qwen 3.6 Plus)
have begun pulling back from fully open releases for their latest
models, Google is moving in the opposite direction — opening up
its most capable Gemma release yet while explicitly stating the
Gemini 3
architecture draws from its commercial research.
Four models, two tiers: Edge to
workstation in a single family
Gemma 4 arrives as four distinct models organized into two
31B-parameter
deployment tiers. The "workstation" tier includes a
dense model 26B A4B Mixture-of-Experts model
and a — both
supporting text and image input with 256K-token context
E2B E4B
windows. The "edge" tier consists of the and , compact
models designed for phones, embedded devices, and laptops,
supporting text, image, and audio with 128K-token context
windows.


---
*Page 5*


The naming convention takes some unpacking. The "E" prefix
denotes "effective parameters" — the E2B has 2.3 billion effective
parameters but 5.1 billion total, because each decoder layer carries
its own small embedding table through a technique Google calls
Per-Layer Embeddings (PLE)
. These tables are large on disk but
cheap to compute, which is why the model runs like a 2B while
technically weighing more.
The "A" in 26B A4B stands for "active parameters" — only 3.8
billion of the MoE model's 25.2 billion total parameters activate
during inference, meaning it delivers roughly 26B-class
intelligence with compute costs comparable to a 4B model.
For IT leaders sizing GPU requirements, this translates directly to
deployment flexibility. The MoE model can run on consumer-
grade GPUs and should appear quickly in tools like Ollama and LM
Studio. The 31B dense model requires more headroom — think an
NVIDIA H100 or RTX 6000 Pro for unquantized inference — but
Quantization-Aware Training (QAT)
Google is also shipping
checkpoints
to maintain quality at lower precision. On Google
Cloud, both workstation models can now run in a fully serverless
Cloud Run
configuration via with NVIDIA RTX Pro 6000 GPUs,
spinning down to zero when idle.


---
*Page 6*


The MoE bet: 128 small experts
to save on inference costs
The architectural choices inside the 26B A4B model deserve
particular attention from teams evaluating inference economics.
Rather than following the pattern of recent large MoE models that
128 small experts
use a handful of big experts, Google went with ,
activating eight per token plus one shared always-on expert. The
result is a model that benchmarks competitively with dense
models in the 27B–31B range while running at roughly the speed
of a 4B model during inference.
This is not just a benchmark curiosity — it directly affects serving
costs. A model that delivers 27B-class reasoning at 4B-class
throughput means fewer GPUs, lower latency, and cheaper per-
token inference in production. For organizations running coding
assistants, document processing pipelines, or multi-turn agentic
workflows, the MoE variant may be the most practical choice in
the family.
hybrid attention mechanism
Both workstation models use a that
interleaves local sliding window attention with full global
attention, with the final layer always global. This design enables
the 256K context window while keeping memory consumption
manageable — an important consideration for teams processing
long documents, codebases, or multi-turn agent conversations.


---
*Page 7*


Native multimodality: Vision,
audio, and function calling
baked in from scratch
Previous generations of open models typically treated
multimodality as an add-on. Vision encoders were bolted onto text
backbones. Audio required an external ASR pipeline like Whisper.
Function calling relied on prompt engineering and hoping the
model cooperated. Gemma 4 integrates all of these capabilities at
the architecture level.
variable aspect-ratio image input
All four models handle with
configurable visual token budgets — a meaningful improvement
over Gemma 3n's older vision encoder, which struggled with OCR
and document understanding. The new encoder supports budgets
from 70 to 1,120 tokens per image, letting developers trade off
detail against compute depending on the task.
Lower budgets work for classification and captioning; higher
budgets handle OCR, document parsing, and fine-grained visual
analysis. Multi-image and video input (processed as frame
sequences) are supported natively, enabling visual reasoning
across multiple documents or screenshots.
native audio processing
The two edge models add — automatic
speech recognition and speech-to-translated-text, all on-device.
The audio encoder has been compressed to 305 million
parameters, down from 681 million in Gemma 3n, while the frame


---
*Page 8*


duration dropped from 160ms to 40ms for more responsive
transcription. For teams building voice-first applications that need
to keep data local — think healthcare, field service, or multilingual
customer interaction — running ASR, translation, reasoning, and
function calling in a single model on a phone or edge device is a
genuine architectural simplification.
Function calling
is also native across all four models, drawing on
FunctionGemma
research from Google's release late last year.
Unlike previous approaches that relied on instruction-following to
coax models into structured tool use, Gemma 4's function calling
was trained into the model from the ground up — optimized for
multi-turn agentic flows with multiple tools. This shows up in
agentic benchmarks, but more importantly, it reduces the prompt
engineering overhead that enterprise teams typically invest when
building tool-using agents.
Benchmarks in context: Where
Gemma 4 lands in a crowded
field
The benchmark numbers tell a clear story of generational
89.2% on AIME 2026
improvement. The 31B dense model scores (a
80.0% on LiveCodeBench
rigorous mathematical reasoning test),
v6 Codeforces ELO of 2,150
, and hits a — numbers that would have
been frontier-class from proprietary models not long ago. On
vision, MMMU Pro reaches 76.9% and MATH-Vision hits 85.6%.


---
*Page 9*


Google Gemma 4 ELO score benchmark chart. Credit: Google


---
*Page 10*


For comparison, Gemma 3 27B scored 20.8% on AIME and 29.1%
on LiveCodeBench without thinking mode.
The MoE model tracks closely: 88.3% on AIME 2026, 77.1% on
LiveCodeBench, and 82.3% on GPQA Diamond — a graduate-level
science reasoning benchmark. The performance gap between the
MoE and dense variants is modest given the significant inference
cost advantage of the MoE architecture.
The edge models punch above their weight class. The E4B hits
42.5% on AIME 2026 and 52.0% on LiveCodeBench — strong for a
model that runs on a T4 GPU. The E2B, smaller still, manages
37.5% and 44.0% respectively. Both significantly outperform
Gemma 3 27B (without thinking) on most benchmarks despite
being a fraction of the size, thanks to the built-in reasoning
capability.
These numbers need to be read against an increasingly
competitive open-weight landscape. Qwen 3.5, GLM-5, and Kimi
K2.5 all compete aggressively in this parameter range, and the
field moves fast. What distinguishes Gemma 4 is less any single
benchmark and more the combination: strong reasoning, native
multimodality across text, vision, and audio, function calling, 256K
context, and a genuinely permissive license — all in a single model
family with deployment options from edge devices to cloud
serverless.
What enterprise teams should


---
*Page 11*


watch next
Google is releasing both pre-trained base models and instruction-
tuned variants, which matters for organizations planning to fine-
tune for specific domains. The Gemma base models have
historically been strong foundations for custom training, and the
Apache 2.0 license now removes any ambiguity about whether
fine-tuned derivatives can be deployed commercially.
The serverless deployment option via Cloud Run with GPU support
is worth watching for teams that need inference capacity that
scales to zero. Paying only for actual compute during inference —
rather than maintaining always-on GPU instances — could
meaningfully change the economics of deploying open models in
production, particularly for internal tools and lower-traffic
applications.
Google has hinted that this may not be the complete Gemma 4
family, with additional model sizes likely to follow. But the
combination available today — workstation-class reasoning
models and edge-class multimodal models, all under Apache 2.0,
all drawing from Gemini 3 research — represents the most
complete open model release Google has shipped. For enterprise
teams that had been waiting for Google's open models to compete
on licensing terms as well as performance, the evaluation can
finally begin without a call to legal first.


---
*Page 12*


Subscribe to get latest
news!
Deep insights for enterprise AI, data, and security
leaders
VB Daily AI Weekly AGI Weekly
Security Weekly Data Infrastructure Weekly
VB Events All of them
Enter Your Email
By submitting your email, you agree to our Terms and Privacy
Notice.
Get updates


---
*Page 13*


More


---
*Page 14*


Claude, OpenClaw and the new reality: AI
agents are here — and so is the chaos
The age of agentic AI is upon us — whether we like it or not. What
started with an innocent question-answer banter with ChatGPT
back in 2022 has become an existential debate on job security an…
Dattaraj Rao, Persistent Systems
April 5, 2026
Anthropic cuts off the ability to use Claude
subscriptions with OpenClaw and third-party AI
agents
To be clear, it will still be possible to use Claude models like Opus,
Sonnet, and Haiku to power OpenClaw and similar external agents, but
users will now need to opt into a pay-as-you-go or API.


---
*Page 15*


Carl Franzen
April 3, 2026
Nvidia launches enterprise AI agent platform
with Adobe, Salesforce, SAP among 17
adopters at GTC 2026
The Nvidia CEO unveiled the Agent Toolkit, an open-source
platform for building autonomous AI agents, and then rattled off
the names of the companies that will use it: Adobe, Salesforce, SA…
Michael Nuñez
April 3, 2026


---
*Page 16*


Microsoft launches 3 new AI models in direct
shot at OpenAI and Google
The trio of models — MAI-Transcribe-1, MAI-Voice-1, and MAI-
Image-2 — are available immediately through Microsoft Foundry
and a new MAI Playground. They span three of the most…
Michael Nuñez
April 3, 2026


---
*Page 17*


Arcee's new, open source Trinity-Large-
Thinking is the rare, powerful U.S.-made AI
model that enterprises can download and
customize
As global labs pivot toward proprietary lock-in, Arcee has positioned
Trinity as a sovereign infrastructure layer that developers can finally
control and adapt for long-horizon agentic workflows.
Carl Franzen
April 3, 2026


---
*Page 18*


Slack adds 30 AI features to Slackbot, its most
ambitious update since the Salesforce
acquisition
The announcement, timed to a keynote event that Salesforce CEO
Marc Benioff is headlining Tuesday morning, arrives less than
three months after Slackbot first became generally available on…
Michael Nuñez
March 31, 2026


---
*Page 19*


Claude Code's source code appears to have
leaked: here's what we know
The leak provides competitors—from established giants to nimble rivals
like Cursor—a literal blueprint for how to build a high-agency, reliable,
and commercially viable AI agent.
Carl Franzen
March 31, 2026


---
*Page 20*


Softr launches AI-native platform to help
nontechnical teams build business apps
without code
The company's new AI Co-Builder lets non-technical users
describe in plain language the software they need, and the
platform generates a fully integrated system — database, user…
Michael Nuñez
March 31, 2026


---
*Page 21*


Nvidia-backed ThinkLabs AI raises $28 million
to tackle a growing power grid crunch
The funding marks a significant escalation in the race to apply AI
not just to software and content generation, but to the physical
infrastructure that powers modern life. While most AI investme…
Michael Nuñez
March 31, 2026


---
*Page 22*


Midjourney engineer debuts new vibe coded,
open source standard Pretext to revolutionize
web design
It allows developers to treat text as a fluid substance that can be
recalculated every single frame without dropping a beat.
Carl Franzen
March 30, 2026


---
*Page 23*


When product managers ship code: AI just
broke the software org chart
Last week, one of our product managers (PMs) built and shipped a
feature. Not spec'd it. Not filed a ticket for it. Built it, tested it, and
shipped it to production. In a day.
Andrew Filev, Zencoder
March 29, 2026


---
*Page 24*


When AI turns software development inside-
out: 170% throughput at 80% headcount
Many people have tried AI tools and walked away unimpressed. I
get it — many demos promise magic, but in practice, the results
can feel underwhelming.
Andrew Filev, Zencoder
March 28, 2026


---
*Page 25*


Press Releases
Contact Us
Advertise
Share a News Tip
Contribute
Privacy Policy
Terms of Service
Consent Preferences
Do Not Sell or Share My Personal Information
Limit the Use Of My Sensitive Personal Information
© 2026 VentureBeat. All rights reserved.