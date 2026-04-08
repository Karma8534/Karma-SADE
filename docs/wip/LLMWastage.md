# LLMWastage

*Converted from: LLMWastage.PDF*



---
*Page 1*


Open in app
1
Search Write
Member-only story
Your LLM Is Wasting
Most of Its Memory.
TurboQuant-GPU Fixes
That.
Code Coup Following 4 min read · Just now
5
Here’s something most people don’t think about
when running large language models locally. The
bottleneck usually isn’t the model weights. It’s the
KV cache. For every token the model generates, it
stores key and value vectors for each attention
head. That pile grows fast. For long contexts, it


---
*Page 2*


becomes the thing eating your GPU memory — not
the weights themselves.
So what do you do? You either limit context length,
buy more VRAM, or find a smarter way to store
that cache.
TurboQuant-GPU is the third option.
What It Actually Does
It compresses the KV cache in real time. Not
approximately — well, technically yes


---
*Page 3*


approximately, but with 0.98 cosine similarity.
That’s close enough that the model barely notices.
Numbers from running Mistral-7B:
1,408 KB → 275 KB
That’s 5.02x compression. For comparison,
NVIDIA’s own FP4 formats get around 3.56x to
3.76x. TurboQuant beats both because it’s doing
something smarter than general-purpose
quantization.
The Math Behind It
Raw KV cache values have an irregular
distribution. Quantizing them directly wastes bits
covering ranges that rarely get used.
TurboQuant first applies a random orthogonal
rotation to the vectors. After rotation, the values
become approximately Gaussian — the classic bell


---
*Page 4*


curve. And for a Gaussian distribution, there’s a
quantization method called Lloyd-Max that’s
theoretically optimal.
So: rotate first, then quantize. You get much better
compression for the same number of bits.
Keys and values are treated slightly differently.
Keys get 2-bit MSE quantization plus 1-bit QJL bias
correction. Values get 3-bit MSE quantization. Both
happen in a single fused kernel launch per
attention head, so there’s no extra overhead from
running two separate operations.
Getting Started
Install is one line:
pip install turboquant-gpu


---
*Page 5*


If you want the cuTile GPU kernels (requires CUDA
13.0+):
pip install cuda-tile[tileiras] --extra-index-url htt
If that’s not available or your driver is older, no
problem. It falls back to PyTorch automatically.
Everything still works.
Running It
from transformers import AutoModelForCausalLM, AutoTo
from turboquant_gpu import TurboQuantEngine
import torch
model_id = "mistralai/Mistral-7B-v0.1"
model = AutoModelForCausalLM.from_pretrained(model_id
tok = AutoTokenizer.from_pretrained(model_id)
engine = TurboQuantEngine(head_dim=128, total_bits=3,
result = engine.generate(model, tok, "The University
print(result["text"])
print(f"{result['tokens']} tokens | {result['stats'][


---
*Page 6*


Three lines after loading the model. That’s it.
Step by Step
The one-call generate is convenient, but you can
also do it manually:
engine = TurboQuantEngine(head_dim=128, total_bits=3,
# one-call generation
result = engine.generate(model, tokenizer, "your prom
# step-by-step
compressed = engine.compress_kv_cache(out.past_key_va
cache = engine.build_cache(compressed)
stats = engine.compression_stats(out.past_key_va
# auto-tune for your GPU (benchmarks cutile vs pytorc
engine.auto_tune(seq_len=512)
The auto_tune method is worth running once on
your setup. It benchmarks cuTile against PyTorch
for your specific GPU and finds the best bit
configuration for your sequence length. Takes a
minute, saves you from guessing.


---
*Page 7*


GPU Support
Works on pretty much anything NVIDIA:
| GPU | cuTile kernels | PyTorch
| ------------------ | ------------------- | --------
| A100 (sm_80) | CUDA 13.2+ | always w
| H100 (sm_90) | not yet (tileiras) | always w
| RTX 4090 (sm_89) | CUDA 13.2+ | always w
| B200 (sm_100) | CUDA 13.0+ | always w
| Any other CUDA GPU | depends on tileiras | always w
H100 cuTile support is listed as “not yet” — the
PyTorch path still works fine on it though.
The Kernels Under the Hood
If you’re curious what’s actually running on the
GPU:
| Kernel | What it does
| ------------------- | -----------------------------
| `compress_kv_3bit` | Fused K+V compression in one
| `compress_keys` | Normalize, rotate, Lloyd-Max,


---
*Page 8*


| `compress_values` | Normalize, rotate, Lloyd-Max
| `decompress_values` | Dequantize, un-rotate, rescal
| `fused_attention` | Scores + online softmax + V a
The fused kernel design matters. Most
compression approaches add overhead because
they run separate passes. Here, everything that
happens in one launch is for attention.
Who This Is For
If you’re running inference on consumer GPUs and
hitting VRAM limits at longer contexts — this is
worth trying immediately.
If you’re on a server with A100S or B200S running
batch inference, 5x KV cache reduction means you
can fit larger batches or longer sequences for the
same hardware cost.
If you’re just experimenting with local models, it
makes longer conversations much more practical


---
*Page 9*


on mid-range cards.
Quick Links
GitHub: turboquant-gpu
Install: pip install turboquant-gpu
Written in cuTile (CUDA 12, 13) with PyTorch
fallbacks
The KV cache problem isn’t going away as models
get larger. A compression algorithm that actually
works at this ratio, with this little code to integrate,
is genuinely useful.
LLM AI Gpu Pytorch AI Agent
Written by Code Coup
Following
3.9K followers · 1 following
Code Coup: Seize the Code, Stage a Coup!


---
*Page 10*


No responses yet
To respond to this story,
get the free Medium app.
More from Code Coup
Code Coup Code Coup
I Reverse-Engineered Why Your AI Agent
Cl d C d ’ L k d N d D t b N
I spent a few days examining Everyone’s excited about
thi I did ’t t t i i AI t t
5d ago Mar 13


---
*Page 11*


Code Coup Code Coup
I Trained an LLM on Most People Use
A l ’ N l E i Cl d Lik S h
Every Apple Silicon Mac has I’ve spent the last few months
th t it th CP t hi l Cl d
Mar 10 Mar 12
See all from Code Coup
Recommended from Medium
Tahir In by
Towar… Anthony Menghi - a…


---
*Page 12*


TurboQuant vs You Don’t Need RAG.
T diti l Y N d S ti
TLDR:TurboQuant enables How I solved a chunk selection
l l 3 bit KV h bl th t th t t t
Mar 27
Mar 27
In by Pankaj Kumar
Activated… Adi Insights and…
Palantir Foundry
I Ignored 40+
O t l H It
O F Alt ti
Palantir’s $400B valuation is
Everyone is building agent
b ilt d O t l
f k M t P th
Mar 21 Mar 22
See more recommendations