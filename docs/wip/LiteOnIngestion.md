# LiteOnIngestion

*Converted from: LiteOnIngestion.PDF*



---
*Page 1*


Open in app
11
Search Write
Member-only story
Which Small vLLM OCR
Model Is the Best For
Private Use in 2026?
Code Included
A weekend experiment that started with “just
get me the text” and ended with a 1B model
embarrassing everything else in the room.
Mandar Karhade, MD. PhD. Following 14 min read · 4 days ago
144 1
TLDR
A 1-billion parameter model (LightOnOCR)
produced cleaner, more structured output than


---
*Page 2*


models 2.5x and 3x its size; on real scanned
medical forms, not cherry-picked benchmarks.
MinerU-Diffusion’s parallel diffusion decoding is
architecturally fascinating but hallucinates on
small text and duplicates content on busy pages.
LiteParse is blazing fast for native-text PDFs but
falls apart on scanned documents; it’s not even
in the same category.
Chandra took 66 seconds for a single page. On a
4090. Sorry but no.
License filtering alone eliminated half the
candidates before a single line of code ran.
Friends Link for everyone: Follow the author,
publication, and clap. Join Medium to support
other writers too! Cheers
Please follow my new profile
https://medium.com/@ThisWorld where I will be
covering Health tech, Global tech, and AI Governance
through multi-part deep investigative articles. I will


---
*Page 3*


appreciate if you can follow and subscribe on the new
channel.
It all started with my need for having a fast OCR
drop in replacement that I could run on my 4090
laptop GPU efficiently. I needed something that
can run in the background day in day out and
churn a set of client documents purely locally until
everything is done. I needed something that can
provide me the text, formatting, tables, and images
(like 90% of those who need OCR). I did not need
the exact coordinate of each word but I needed the
OCR to be fast and accurate.
So…. I set to cook my list of OCR models I was
interested in, and started developing some quick
and dirty benchmarks and implementations
The License Graveyard


---
*Page 4*


Before writing a single line of inference code, I had
to thin the herd. And the machete wasn’t technical;
it was legal.
The best open-source OCR models are rarely truly
open-source. Like half of them aren’t actually open
source in any meaningful way. They’re GPL-3.0 or
AGPL-3.0, which means the moment you integrate
them into a product, your entire codebase
becomes subject to copyleft obligations.
Decision for me: The kill list was brutal
Marker (PDF to markdown): GPL-3.0. Out.
Surya (OCR + layout): GPL-3.0. Out.
MinerU 2.5 (the regular autoregressive version):
AGPL-3.0. Out.
GLM-OCR: API-dependent, requires cloud keys.
Out.
PaddleOCR: Apache 2.0, which is great, but no
layout detection. It extracts text. That’s it. No


---
*Page 5*


tables, no structure, no understanding of what’s
a heading versus what’s a footnote. Out.
GOT-OCR2: Apache 2.0, academically
interesting, but low community adoption and no
compelling reason to include it over the others.
Out.
Docling (IBM): MIT license, actually permissive,
but it tries to do everything: PDFs, DOCX, PPTX,
XLSX, HTML, images, LaTeX. Too fat. When the
goal is not that I win, but you lose; Docling is
trying to win at everything and optimizing for
nothing. Btw I love docling.. but for now Out
What survived: four methods with genuinely
permissive licenses (MIT or Apache 2.0) and
enough technical substance to be worth
benchmarking.
The Four Contenders
Here’s what made the cut:


---
*Page 6*


MinerU-Diffusion (2.5B parameters, MIT):
The diffusion decoder. Instead of generating
tokens left-to-right, it masks everything and
iteratively unmasks based on confidence scores.
Uses a custom engine called nano_dvlm (a
lightweight vLLM-like implementation built
specifically for this model’s block-wise diffusion
denoising). Cannot run on standard vLLM because
the decoding strategy is fundamentally different
from autoregressive generation. (I covered this
mode here https://ai.gopubby.com/mineru-


---
*Page 7*


diffusion-ocr-has-been-reading-left-to-right-for-no-
good-reason-839338ed678e)
LightOnOCR (1B parameters, Apache 2.0):
The underdog. The latest new kid on the block. A
tiny model that claims state-of-the-art accuracy on
OlmOCR-Bench while being 9x smaller than
Chandra. Standard autoregressive decoder; runs
on vanilla vLLM. Has a bbox variant that outputs
bounding boxes for embedded images.
LiteParse (MIT):


---
*Page 8*


Not a model at all. A Node.js-based PDF text
extractor with optional Tesseract OCR fallback for
image-heavy pages. Extracts text directly from the
PDF’s internal structure when available, falls back
to OCR when it isn’t. Requires Node.js, which is
annoying, but the Python wrapper makes it
tolerable. I thought I could use it as the first pass to
process PDFs with embedded xml data. Easy
blazing fast extraction.
Chandra (~3B parameters, Apache 2.0):


---
*Page 9*


From the same team that makes Surya and Marker
(datalab-to). Full layout detection with bounding
boxes for every chunk. Outputs markdown, HTML,
and structured blocks. Can run locally via
HuggingFace transformers or through a vLLM
server.
Here is the comparison of basics of these models.


---
*Page 10*


Setting Up the Arena
The test environment:
a single NVIDIA RTX 4090 Laptop GPU with 16GB
VRAM. Not an H100 in a data center. Not a multi-
GPU rig. A laptop. This matters because most
benchmarks are run on hardware that nobody
actually uses in practice.
Every method received the same input:
PDF pages rendered at 200 DPI and capped at
1540px on the longest dimension. This
normalization is critical. If you let one method
render at 300 DPI and another at 150 DPI, you’re


---
*Page 11*


not comparing models; you’re comparing
preprocessing pipelines.
The test documents:
scanned medical records (30 pages of redacted
clinic notes, intake forms, medication lists,
surgical histories) and an academic paper like
from arxiv (33 pages with two-column layout,
tables, LaTeX equations, figures).
Medical records are the worst-case scenario for
OCR. Scanned from paper. Redaction bars
covering patient data. Tiny fonts. Mixed layouts:
sometimes a structured form with checkboxes,
sometimes free-text clinical notes, sometimes a
table of medications. If it works here, it works
anywhere.
Before we move ahead lets spend some time on
how the two groups (Miner-U diffusion model and
LightOnOCR / chandra differ). One is a diffusion


---
*Page 12*


other group is a decoder model. The diffusion
model needs a parallel LLM processor to be
efficient so I used the recommended dvlm stack
from their repo. I used vLLM for LightOnOCR and
Chandra (system installation, not docker image.
How Does MinerU-Diffusion Actually
Decode?
Before the numbers, a quick detour into why
MinerU-Diffusion is architecturally interesting.
This isn’t the usual transformer-generates-tokens
story.
Traditional OCR models generate text left-to-
right:
predict token 1, feed it back, predict token 2, feed
both back, predict token 3. Sequential. Slow. And if
token 47 is wrong, tokens 48 through 200 are
probably wrong too because they were conditioned
on a mistake.


---
*Page 13*


MinerU-Diffusion does something different. It
starts with a block of 32 masked tokens. Every
position is unknown. Then it runs the model, gets
confidence scores for every position
simultaneously, unmasks the high-confidence
positions, and reruns the model on the updated
sequence. Repeat until everything is unmasked.
It’s like filling in a crossword puzzle where you do
the easy clues first, then use those letters to solve
the harder ones. Parallel, iterative, and self-
correcting.
But there is always a butt.
The standard vLLM inference server has no idea
what to do with this. vLLM expects autoregressive
decoding: one token at a time, left to right, with a
KV cache that grows monotonically. Diffusion
decoding needs custom masking logic, remasking
strategies, confidence thresholds, and block-level
denoising loops. None of that exists in standard
vLLM.


---
*Page 14*


So MinerU-Diffusion ships with its
own engine, nano_dvlm, a stripped-
down inference engine that
implements the diffusion-specific
sampling logic. It has batching, KV
caches, and a scheduler, but it’s
custom code. Which means you
can’t just and call it a
vllm serve
day.
The Optimization Rabbit Hole
Before even comparing methods, I spent a full day
optimizing MinerU-Diffusion’s throughput. The
model ships with @torch.compile decorators
scattered across the codebase (layernorm, rotary
embeddings, sampler, vision transformer). These
require Python dev headers and triton
compilation.


---
*Page 15*


On a fresh Ubuntu install without python3.12-dev,
the model crashes immediately with a Python.h: No
such file or directory error.
Are we serious? A production OCR model that
crashes because of a missing C header file?
After installing the dev headers, I benchmarked
four optimization configurations across 20 pages
of scanned medical records:
The optimizations were done using the common
capabilities of all of these models like using
batching, cuda graph with warmup, and
torch.compile with warmup.
Batch optimization was the clear winner.


---
*Page 16*


2.4x faster than the sequential baseline. Instead of
running each detected block through the model
one at a time, batch mode sends all blocks for a
page in a single generate_messages() call, letting
the scheduler pack them efficiently.
CUDA graph capture helped (1.8x faster) but ate
1.8GB of VRAM for the captured graphs, leaving
too little room for batched inference on a 16GB
card. And torch.compile? It made things slower on
short runs because the compilation overhead (7+
seconds) wiped out any kernel fusion gains.
On a 16GB laptop GPU, the answer is simple: use
batch optimization, skip everything else.
What Does 3.7 Seconds Buy You?
Now the main event.
All four methods, same scanned medical record,
page 1. A dense intake form with a clinic header,


---
*Page 17*


appointment reasons, medication lists, surgical
history, and family history.
Speed:
LightOnOCR, the 1B model, was the fastest GPU-
based method. Nearly 3x faster than MinerU-
Diffusion (2.5B) and 18x faster than Chandra (~3B).
On a laptop GPU. With 26% GPU utilization,
meaning it wasn’t even trying hard.
Oh!
But speed means nothing if the output is garbage.
Let’s look at what each model actually produced.


---
*Page 18*


The Quality Verdict Nobody Expected
Here’s where LightOnOCR went from “interesting”
to “wait, are you serious?”
LightOnOCR output:
### Reason for Appointment
1. MVA: 10/11/2025
2. Follow up: Cervical, Lumbar
3. Patient is being treated today at [Redacted] Medic
### Current Medications
**Taking**
- Cyclobenzaprine HCl 10 MG Tablet 1 tablet at bedtim
- Metaxalone 800 MG Tablet 1 tablet Orally Three time
- Gabapentin 400 MG Capsule 1 capsule Orally Once a d
Clean markdown. Proper headings. Bullet lists. No
duplicates. Every medication name spelled
correctly. Redacted fields cleanly marked as
[REDACTED]. Even the clinic name and tagline were
captured:
MinerU-Diffusion output (same page):


---
*Page 19*


Current Medications
Taking
- Cyclobenzaprine HCI 10 MG Tablet 1 tablet at bedtim
• Metaxalone 800 MG Tablet 1 tablet Orally Three time
...
• Nab nonprofitsone 750 MG Tablet as directed Orally
Two problems jump out immediately. First, “Nab
nonprofitsone” instead of “Nabumetone.” That’s a
hallucination. The 2.5B diffusion model looked at
the scanned text, got confused by the font
rendering, and invented a word that doesn’t exist.
In a medical record. Where drug names matter.
Second, the entire medication list appears twice.
The model detected the same content region as
two separate layout blocks and extracted it
independently.
LiteParse output (same page):
+ Cyclobenzaprine HCI 10 MG Tablet 1 tablet at bedtim
800 MG Tablet 1 tablet Orally Three times a d
+ Gabapentin 400 MG Capsule 1 capsule Orally Once a d


---
*Page 20*


Raw spatial text. The + symbols instead of bullet
points. "Metaxalone" is missing entirely because
the text extraction failed on that line. The
indentation preserves the physical layout of the
page, which is faithful but unusable without post-
processing.
Chandra output:
Captured a completely different section of the page
(vitals, exam findings, assessments with ICD
codes) while missing the entire top half. At 66
seconds per page, it’s not just slow; it’s unreliable
about what it reads.
Given DataLab’s Chandra and Surya reputation I
think I might have broken something here but I
was not about to go in another rabit hole to fix it.
So I left it there. If it does not work out of the box
settings then I am moving on.


---
*Page 21*


Radio Buttons and the 1B Advantage
This is the finding that genuinely surprised me. On
a page of medical records is an intake form with a
checklist: “Past Medical History” followed by 25+
conditions, each with a filled or unfilled radio
button indicating Yes or No.
LightOnOCR nailed it:
<tr><td>asthma</td></tr>
<tr><td>● Yes ○ No</td></tr>
<tr><td>chronic cough</td></tr>
<tr><td>○ Yes ● No</td></tr>
It correctly distinguished filled circles (●) from
empty circles (○) on a scanned, redacted medical
form. The model understood that this was a form,
represented it as a table, and preserved the
semantic meaning of each checkbox state.
Not really something you’d expect from a 1B
model. But here we are.


---
*Page 22*


The Table Test
Academic papers have tables. Complex ones with
merged cells, subscripts, superscripts, and
footnotes. A page of the arxiv paper has a 14-row
comparison table with rowspan cells spanning
multiple method categories.
LightOnOCR produced a full HTML table with
proper <thead>, <tbody>, <tr>, <td rowspan="2">,
and every single number correct. The table
rendered perfectly in a browser. Every column
aligned. Every decimal point in place.
MinerU-Diffusion, by contrast, outputs tables in
OTSL (Open Table Structure Language): <fcel>,
<ecel>, <lcel> tokens that require post-processing
to become usable HTML. It's technically correct
but requires a conversion step that LightOnOCR
doesn't need.


---
*Page 23*


What About Layout Coordinates?
Here’s the one area where MinerU-Diffusion
genuinely excels and LightOnOCR falls short.
MinerU-Diffusion runs a two-stage pipeline:
first, layout detection that produces bounding
boxes for every block on the page (text, table,
equation, header, footer, image). Then, content
extraction for each detected block. You get
coordinates for everything.
LightOnOCR’s bbox
The Bbox ariant only outputs coordinates for
embedded images and figures. Text blocks, tables,
headings? No coordinates. The text is beautifully
extracted but you don’t know where on the page it
came from.


---
*Page 24*


If your downstream pipeline needs to link
extracted text back to specific page regions (for
document understanding, spatial reasoning, or
visual grounding), MinerU-Diffusion’s layout
detection is unmatched among these four
methods. If you just need the text, LightOnOCR
wins.
The vLLM Adventure
Getting LightOnOCR running via vLLM was its own
saga. The model is so new that the stable vLLM
Docker image (0.11.0) had never heard of
LightOnOCRForConditionalGeneration. Not in its
model registry. Not even through the generic


---
*Page 25*


TransformersForMultimodalLM fallback. But I think
that was my bad. using an outdated vLLM (that was
working for my rest of the workflows in last 2
years, was still running because “If aint broken,
dont fix it” mentality).
The fix: pull the latest Docker image (0.18.0), build
a custom Dockerfile that force-upgrades
transformers to 5.4.0, and then it just works. One
Dockerfile, three lines:
FROM vllm/vllm-openai:latest
RUN pip install --no-cache-dir --force-reinstall "tra
MinerU-Diffusion, on the other hand, can never
use standard vLLM. Its diffusion decoding requires
the custom nano_dvlm engine. Period. This isn’t a
temporary limitation; it’s architectural. As long as
the model uses block-wise masked denoising
instead of autoregressive token generation,
standard vLLM will never support it.


---
*Page 26*


Throughput at Scale
Single-page benchmarks are useful for latency
comparisons. But what about processing 30+
pages? I decided to compare only 2 main
contenders going forward. The LightOnOCR and
Miner-U-diffusion bbox
LightOnOCR on 30 pages of scanned medical
records:
203 seconds total (6.8s/page average). Most pages
took 3–5 seconds. Four pages with dense tables
spiked to 23–25 seconds each, likely hitting the
max token limit.
LightOnOCR on 33 pages of an academic paper:


---
*Page 27*


143 seconds total (4.3s/page average). Cleaner
layouts with fewer visual artifacts meant faster
processing across the board.
For context, MinerU-Diffusion (batched) averaged
10.5s/page on the same medical records; roughly
2x slower. And this is with batch optimization
enabled. Without it, you’re looking at 15.6s/page.
The Quirks
Every model has them. Here’s the highlight reel:
MinerU-Diffusion hallucinated Russian text on one
page. The string “St эксперт” appeared in the
output where “Stabbing” should have been. The
model’s training data apparently included Russian
medical documents, and when the visual signal
was ambiguous (tiny scanned text), it reached for
the wrong language model prior.


---
*Page 28*


LightOnOCR faithfully transcribed a
file:///C:/Users/ path that was embedded in the
footer of a page printed from an EHR system. This
is correct behavior for an OCR tool: transcribe
what you see. But it means you'll need post-
processing to filter watermarks and print artifacts.
LiteParse requires Node.js. In 2026. For a Python
project. The Python wrapper calls the Node.js CLI
via subprocess. I had to install fnm (a Node version
manager), install Node 22, install the npm package
globally, and then configure PATH detection in the
script so Python could find the lit binary. It
worked as a prototype; then all went down!
(Actually it worked fine, but the setup was painful.)
Chandra loaded a ~3B model into GPU memory,
ran inference for 66 seconds on a single page, and
only captured half the page content. The
HuggingFace local backend is clearly not the
intended deployment path; they expect you to use
their vLLM server. But on a single 16GB GPU, you


---
*Page 29*


can’t run their vLLM server and get decent
throughput anyway.
It’s Not the Size, It’s the Training Data
The real story isn’t that a 1B model beat a 2.5B
model. That happens all the time. The real story is
how it beat it.
LightOnOCR didn’t just extract text faster. It
produced structurally superior output: proper
markdown hierarchy, clean heading levels, table
structures that render correctly, form elements
preserved with semantic meaning. A 1B model
shouldn’t know that ● means "selected" and ○
means "unselected" on a scanned intake form. But
it does, because the training data and the post-
training RLVR (reinforcement learning with
verifiable rewards) were focused on exactly these
document understanding tasks.


---
*Page 30*


MinerU-Diffusion’s parallel diffusion decoding is
genuinely innovative. Architecturally, it’s more
interesting than anything else in this comparison.
But innovation in the decoder doesn’t help if the
model hallucinates drug names on scanned
medical records. The decoder is not the
bottleneck; the visual encoder and the training
data are.
The code is in this repo
https://github.com/mandar-karhade/OCR-tools
So What Should You Actually Use?
This is my perspective. You should do what you are
comfortable with.
If you need fast, accurate text extraction from
documents and don’t care about layout
coordinates: LightOnOCR. It’s the smallest
model, the fastest model, and produces the


---
*Page 31*


cleanest output. Serve it via vLLM in a Docker
container and move on with your life.
If you need layout coordinates for every block on
the page (text, tables, figures, equations):
MinerU-Diffusion for the layout detection step,
then pipe the cropped blocks to LightOnOCR for
the actual text extraction. Best of both worlds.
If you’re processing native-text PDFs (not
scanned images) and need sub-second latency:
LiteParse. It’s not doing OCR in the traditional
sense; it’s reading the PDF’s embedded text.
When the text is there, nothing is faster.
If you’re looking at Chandra: wait for their vLLM
server deployment to mature, or use a bigger
GPU. The model has potential (full layout
detection with bounding boxes for every chunk),
but the HuggingFace local inference path is not
production-ready at 66 seconds per page.
If you’re about to integrate any of these into a
product, check the license first. Half the OCR


---
*Page 32*


ecosystem is GPL-3.0. The other half is actually
usable.
If you have read it until this point, Thank you! You
are a hero (and a Nerd ❤)! I try to keep my readers
up to date with “interesting happenings in the AI
🔔 🔔
world,” so please clap | follow | Subscribe
AI Agent LLM Generative Ai Tools
Generative Ai Use Cases Artificial Intelligence
Written by Mandar Karhade, MD.
Following
PhD.
4.9K followers · 146 following
Life Sciences AI/ML/GenAI advisor


---
*Page 33*


Responses (1)
To respond to this story,
get the free Medium app.
Keith Bowden
3 days ago
PaddleOCR: Did you give PPStructure and PaddleVL a try? The v3
version is a rewrite of the API.
More from Mandar Karhade, MD. PhD.
In by In by
Activated … Mandar Karhad… Towar… Mandar Karhade, …
200,000 Devices. One Anthropic Leaked Its
Ad i P d H O N l O ti


---
*Page 34*


Stryker Corporation’s The company that warns
b it b t “ d t d
Mar 16 6d ago
In by In by
Towar… Mandar Karhade, … Towar… Mandar Karhade, …
Five Days, Four The .claude Folder Is
C i d th I t t A d Y ’
OpenAI ships the kitchen sink. A Beginner-to-Advanced
G l ’ AI l th G id t C fi i Cl d
Mar 8 Mar 22
See all from Mandar Karhade, MD. PhD.
Recommended from Medium


---
*Page 35*


Manava Agarwal In by
ILLUMINATI… Mohab A.Kar…
Corrective RAG
How to Safely Publish
(CRAG) Fi i th
AI A i t d C t t
Large Language Models
A practical guide to publishing
(LLM ) f l b t th
AI i t d t t f l
Mar 21 5d ago
In by In by
AI Exploration Jo… Florian J… AI Adva… Mandar Karhade,…
dots.ocr: Turning TurboQuant: Google
D t P i i t R d All O h
At first glance, document The math is real. Two stage KV
i i ht l k lik OCR i l di t 2 5bi
Mar 25 5d ago


---
*Page 36*


In by In by
Activated… Adi Insights and… Google Cloud … Dazbo (Dar…
I Ignored 40+ Documentation as
O F Alt ti C t t A Skill t
Everyone is building agent Supercharge your AI agents
f k M t P th ith th j t
Mar 21 5d ago
See more recommendations