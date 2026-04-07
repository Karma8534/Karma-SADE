# WebsiteNTUNER

*Converted from: WebsiteNTUNER.PDF*



---
*Page 1*


Open in app
Search Write
Pub Crawl is happening this week! Sign up to join us!
Member-only story
How to Turn Any
Website into a Fine-
Tuned Local LLM Using
NTTuner,
NTCompanion, and
Ollama
Sebastian Buzdugan Follow 8 min read · Feb 5, 2026
98
Most people talk about local LLM fine-tuning like
you need a 4090, three days, and a pile of broken


---
*Page 2*


shell scripts
That used to be true
It is a lot less true with NTTuner plus Unsloth
Click here to read this article for free
Why NTTuner matters
If you already run Ollama, you are one step away
from something better than “generic local model
chat”
You can actually teach a model your data, export it,
and use it as a first class Ollama model
Traditionally, the flow looks like this:
Scrape and clean the data
Build an instruction or chat dataset
Write Unsloth or PEFT training code
Handle LoRA merge and GGUF conversion


---
*Page 3*


Manually wire it into Ollama
NTTuner turns that into a GUI workflow on top of
Unsloth
NTCompanion handles data, NTTuner handles
fine-tuning, then it exports straight into Ollama
It is not new algorithms
It is the boring but useful wiring that most
engineers do not want to redo
The stack at a glance
There are three main components in this
ecosystem
1. NTCompanion
Scrapes websites and produces JSONL training
data
2. NTTuner
Cross-platform desktop GUI for fine-tuning with
Unsloth and LoRA


---
*Page 4*


3. Ollama integration
Converts and imports the resulting model into
Ollama, usually via GGUF + quantization
Unsloth is the training engine under the hood
That is where you get the 2–5x speed and memory
efficiency vs naive Hugging Face setups, especially
on NVIDIA GPUs
Instead of writing Python like this:
from unsloth import FastLanguageModel
from datasets import load_dataset
model, tokenizer = FastLanguageModel.from_pretrained(
model_name = "unsloth/llama-3-8b-bnb-4bit",
load_in_4bit = True,
)
dataset = load_dataset("json", data_files="dataset.js
FastLanguageModel.for_inference(model)
# training loop here
You click through a few panels
NTTuner builds a similar pipeline for you, keeps


---
*Page 5*


key parameters exposed, and runs Unsloth
underneath
Hardware reality: what actually works
Unsloth is efficient, but VRAM and bandwidth still
matter
NVIDIA GPUs
NVIDIA is the best supported path
Rough guidance:
8 GB VRAM
7B models in 4-bit or QLoRA style setups, small
batch size
12–24 GB VRAM
13B models and larger batches, more
comfortable runs
Compared to a naive HF Trainer:


---
*Page 6*


2–5x speed improvements
Lower memory per batch
So a laptop with a 3060 goes from “barely can run a
model” to “can fine-tune a 7B with LoRA”
AMD, Intel, Apple Silicon
Enhanced NTTuner builds add support for non-
NVIDIA GPUs with multiple backends
Think ROCm, DirectML, Metal
Reality:
It often works, but
Driver and backend setup can be annoying
Performance typically trails CUDA
If you are on these platforms, treat it as “good
when it works” rather than guaranteed turnkey
CPU only


---
*Page 7*


NTTuner can fall back to CPU
That is useful, but you need to be realistic
Use CPU for:
Smaller models (1–3B)
Small datasets (hundreds to a few thousand
records)
Prototyping and parameter exploration
Tips for CPU survival:
Use the smallest model that fits your use case
Lower LoRA rank, for example r = 4 or r = 8
Use fewer epochs, prioritize data quality
Train on a subset first to validate your pipeline
From website to JSONL with
NTCompanion


---
*Page 8*


Fine-tuning is only as good as your dataset
NTCompanion is the front door to that
The basic workflow:
1. Point NTCompanion at a site (docs, blog,
recipes, etc.)
2. It crawls pages and strips HTML
3. It structures content into JSONL, typically
instruction-style
Example record:
{
"instruction": "Explain how to configure the backup
"input": "",
"output": "To configure the backup job, open the se
"source_url": "https://example.com/docs/backup"
}
For recipes, you might see:


---
*Page 9*


{
"instruction": "Convert this recipe to structured J
"input": "Title: Chocolate Chip Cookies\nIngredient
"output": "{ \"title\": \"Chocolate Chip Cookies\",
}
NTCompanion offers presets like:
Docs / tutorials
Recipes
Blogs
Big caveat
It is not a full headless browser yet
If the site renders everything with heavy
JavaScript, the crawler may see very little
Static or mostly static content is where it shines


---
*Page 10*


Chat templates: the invisible footgun
If chat templates are fuzzy for you, fix that now
They are one of the easiest ways to silently break a
fine-tune


---
*Page 11*


Each model family expects specific wrapping for
chat:
System message tokens
User / assistant roles
Special markers like <|user|> or <s>
Llama, Qwen, Mistral, Gemma, all differ slightly
During fine-tuning, your prompts must match that
template
If not, the model is learning on malformed context
and will respond strangely
A simplified Llama-style template might look like:
<s>[SYSTEM]
You are a helpful assistant.
[/SYSTEM]
[USER]
How do I deploy this on Kubernetes?
[/USER]
[ASSISTANT]


---
*Page 12*


You can deploy this on Kubernetes by...
</s>
NTTuner helps by:
Letting you choose the base model family
Applying the matching chat template
Auto-wrapping JSONL data into proper prompts
Beginner setups often fail here
The GUI solves a genuinely non-trivial gotcha that
is easy to overlook in ad-hoc scripts
What NTTuner does during training
Under the hood, a fine-tune in NTTuner looks a lot
like a standard Unsloth LoRA setup
High level steps:
1. Load model and tokenizer via Unsloth
2. Load JSONL dataset


---
*Page 13*


3. Apply LoRA adapters to chosen modules
4. Configure training hyperparameters
5. Train and log metrics
6. Export adapter or merged weights
The GUI exposes knobs you would usually define
in code:
Base model name (for example unsloth/llama-3-
8b-bnb-4bit)
Target modules for LoRA (q_proj, k_proj,
v_proj, o_proj, etc.)
LoRA rank r, alpha, dropout
Batch size and gradient accumulation
Epochs and learning rate
Max sequence length
Chat template choice
You can save all of this to a JSON config, for
example:


---
*Page 14*


{
"model_name": "unsloth/llama-3-8b-bnb-4bit",
"lora_r": 16,
"lora_alpha": 32,
"lora_dropout": 0.05,
"batch_size": 4,
"gradient_accumulation_steps": 4,
"learning_rate": 2e-4,
"num_epochs": 3,
"max_seq_length": 2048,
"target_modules": ["q_proj", "v_proj"],
"dataset_path": "data/docs.jsonl",
"chat_template": "llama-3"
}
That is your runnable “experiment spec”
Without writing a training script
Logging that does not lock up the UI
This is small but important in practice
NTTuner streams logs and progress while keeping
the interface responsive
You can:


---
*Page 15*


Watch step and epoch counts
See loss trends in real time
Read raw Unsloth / torch logs
Stop a run that is clearly misconfigured
If you have ever used a “train” button that freezes
the entire app, you know why this matters
It makes NTTuner feel like a tool, not a demo
From LoRA adapter to Ollama model
Fine-tuning is half the story
You still need a deployable artifact
NTTuner pushes the pipeline all the way into
Ollama
The deployment flow is roughly:
1. Take base model and LoRA adapter


---
*Page 16*


2. Merge or otherwise combine into a single model
representation
3. Convert to GGUF format
4. Optionally quantize (Q4, Q5, etc.)
5. Import into Ollama as a named model
Once imported, you can simply do:
ollama run my-docs-llama
Or define a Modelfile:
FROM my-docs-llama
PARAMETER temperature 0.2
SYSTEM "You are a domain expert on our internal docs.
On some CPU-only setups, GGUF conversion might
require separate tools from the llama.cpp
ecosystem


---
*Page 17*


So there can still be a manual step depending on
platform
But overall, the handoff from “just trained” to
“Ollama-ready” is much smoother than stitching
scripts together


---
*Page 18*


Fine-tuning vs RAG: where NTTuner fits
Not every “I have data” problem wants fine-tuning
Sometimes you just need a good RAG pipeline
Rough split:
You probably want RAG when:
Data changes frequently
Corpus is large
You mainly need accurate retrieval of facts
You probably want fine-tuning when:
You care about consistent tone or style
You need highly structured outputs (recipes,
JSON templates, code style)
Your core knowledge base is relatively stable and
not enormous


---
*Page 19*


Examples where NTTuner is a strong fit:
Training a support bot in your company’s reply
style and knowledge
Converting a recipe blog into a “generate recipes
in my exact format” model
Teaching a model your internal coding
conventions and review patterns
RAG is for remembering
Fine-tuning is for behaving
You can combine them, but it helps to be clear
which problem you are actually solving
Common mistakes and how the GUI helps
You can still create a bad model with a nice GUI
NTTuner just makes some problems easier to spot
Overfitting


---
*Page 20*


Small dataset, too many epochs
The model memorizes examples, outputs look
great on training prompts, then fall apart
elsewhere
Mitigation:
Start with 1–3 epochs
If you have very few samples, prioritize variety
Optionally hold out a small set for manual
evaluation
Dirty scraped data
If NTCompanion pulled in navigation links, cookie
banners, or broken HTML, the model will happily
train on that noise
Mitigation:
Open the JSONL and skim random records
Filter obvious junk via simple scripts or regular
expressions


---
*Page 21*


Smaller but cleaner beats larger and noisy
Wrong template or base
If your dataset and chat template do not match the
base model, outputs will be weird
NTTuner reduces this by tying preset templates to
families, but you should still double check:
Base model name
Template type
Any system prompts you bake into training
A realistic “one afternoon” plan
Here is a concrete scenario to anchor all this
Goal: a local assistant that knows your homelab
docs at https://homelab.example.com
Steps:
1. Crawl the docs


---
*Page 22*


In NTCompanion, point at the docs URL
Use a “docs/tutorials” preset
Export homelab.jsonl
2. Pick a base model
In NTTuner, select something like Llama 3 8B via
an Unsloth compatible name
Choose the llama-3 chat template
3. Configure LoRA
r = 16, alpha = 32, small dropout
Target q_proj and v_proj
Set max_seq_length to cover your chunk length
4. Training parameters
Batch size tuned to your VRAM (start small)
2 epochs
Learning rate around 2e-4


---
*Page 23*


5. Train and watch
Monitor logs and loss
If it diverges or crashes, adjust batch size or
sequence length
6. Export to Ollama
Use NTTuner to convert and import to Ollama
Name it homelab-expert
Query it with real troubleshooting questions and
compare with your docs
No training script
No manual GGUF invocation if your setup is
supported
Final thoughts
NTTuner is not trying to replace serious ML
pipelines


---
*Page 24*


It is trying to make a practical, local fine-tune a
daytime task instead of a multi-day project
If you already know Unsloth and Hugging Face,
NTTuner is a productivity tool
If you are a developer who understands your
domain but not the ML plumbing, it is the shortest
path to a usable custom model on your own
machine
There are still rough edges
JavaScript-heavy sites, non-English scoring, and
CPU-only workflows are not perfectly smooth yet
But the direction is obvious
Local fine-tuning is becoming something any
serious engineer with a decent machine can do,
not just ML specialists
Start with a small, real dataset you care about
That is usually when this stops feeling like a demo
and starts feeling like infrastructure


---
*Page 25*


Resources
NTTuner GitHub:
https://github.com/noosed/NTTuner
Fluid / NTTuner landing page:
https://www.fluid.sh/
Unsloth GitHub:
https://github.com/unslothai/unsloth
Open Source Friday: Exploring Unsloth
(YouTube): https://www.youtube.com/watch?
v=sHHsOfIwfBY
Fine-tuning local LLMs with Unsloth & Ollama
(YouTube): https://www.youtube.com/watch?
v=W_xh6qNSfAQ
If you build a local expert model with this stack,
note your hardware and dataset size, then iterate
from there.


---
*Page 26*


LLM Machine Learning Developer Tools Open Source
Mlops
Written by Sebastian Buzdugan
Follow
785 followers · 434 following
ML Engineer | PhD Student in AI
No responses yet
To respond to this story,
get the free Medium app.
More from Sebastian Buzdugan


---
*Page 27*


Sebastian Buzdugan In by
Data Science … Florent P…
Rowboat, turning your
How to Generate 3D
k i t
M d l f I
Most “AI copilots” feel smart
Learn to create 3D models
til k thi th t
( l i t l d 3D
Feb 10 Feb 11
In by In by
Data Scienc… Rachel Drael… Data Science … Sebastian B…
Why I Shut Down My Timber is Ollama for
B t t d H lth th d l t l
A Founder’s Postmortem Your LLM sandbox is fun But
th d l th t t ll
Feb 21 Mar 2
See all from Sebastian Buzdugan


---
*Page 28*


Recommended from Medium
In by In by
AI Advances Harish K Write A Catalyst NAJEEB
I Tested 5 OCR Models How I Built a Low-
6 R l W ld L t V i AI A
There’s no single “best” OCR Enterprise tools like Vapi or
i T t i f t t Bl d AI h “ l tf
Feb 15 Feb 21


---
*Page 29*


In by In by
Activated Thi… Shreyas Na… Data Science Co… Paolo Pe…
Build MCP Server From Cursor vs Claude Code
S t h
The AI coding tool decision
Learn how to build an MCP
’t id
i 10 i t i
Jan 19 6d ago
Anil Chandra Naidu Matcha Sebastian Buzdugan
Building Open Diffusion LLMs: How
Hi fi ld AI A O M 2 M k
Most LLMs still “type” at you
t k t ti lik l
Feb 14 Feb 25
See more recommendations