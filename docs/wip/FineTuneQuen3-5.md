# FineTuneQuen3-5

*Converted from: FineTuneQuen3-5.PDF*



---
*Page 1*


Open in app
1
Search Write
Coding Nexus
Member-only story
Fine-Tune Qwen3.5 on
Your Own GPU. You
Only Need 5GB VRAM.
Civil Learning Following 6 min read · 2 days ago
11
Fine-tuning used to mean renting cloud GPUs and
spending money you didn’t want to spend. Unsloth
changed that. If you have a GPU sitting in your
machine right now, there’s a real chance you can
train on it locally — for free.
Here’s everything you need to get started.


---
*Page 2*


What Unsloth Actually Does
Unsloth is a training library that makes fine-tuning
faster and dramatically less memory-hungry.
The numbers are real:
2x faster training than standard Hugging Face +
Flash Attention 2
70%+ less VRAM usage
0% accuracy loss — no approximations,
everything is exact
It supports Qwen3.5, Llama, Gemma, DeepSeek,
GPT, and basically anything that runs in


---
*Page 3*


transformers. LoRA, full fine-tuning, 4-bit, 8-bit,
FP8 — all covered.
For Qwen3.5–2B specifically, you need 5GB VRAM.
That’s a GTX 1060 territory. Most people reading
this have enough GPU to run it right now.
Installation
Linux or WSL
Simple:
pip install unsloth
Done.
Windows (No WSL)


---
*Page 6*


This takes a few more steps but it works. Start by
installing Miniconda. Open PowerShell and run:
Invoke-WebRequest -Uri "https://repo.anaconda.com/min
Start-Process -FilePath ".\miniconda.exe" -ArgumentLi
del .\miniconda.exe


---
*Page 7*


After that, open Anaconda PowerShell Prompt
from the Start menu and create your environment:
conda create --name unsloth_env python==3.12 -y
conda activate unsloth_env
Check your CUDA version:
nvidia-smi
Look at the top right — it’ll say something like
“CUDA Version: 13.0”. Use that number to install


---
*Page 8*


PyTorch (change cu130 to match yours):
pip3 install torch torchvision torchaudio --index-url
Verify PyTorch is working before you go further:
import torch
print(torch.cuda.is_available())
A = torch.ones((10, 10), device = "cuda")
B = torch.ones((10, 10), device = "cuda")
A @ B
You should see True and a matrix of 10s. If that
works, install Unsloth:
pip install unsloth
If PyTorch didn’t work, stop here and sort out your
CUDA drivers first. Don’t proceed until that matrix
test passes.


---
*Page 9*


Docker (Easiest Option for Windows)
No dependency headaches at all. Install Docker
and NVIDIA Container Toolkit:
export NVIDIA_CONTAINER_TOOLKIT_VERSION=1.17.8-1
sudo apt-get update && sudo apt-get install -y \
nvidia-container-toolkit=${NVIDIA_CONTAINER_TOOLKIT
nvidia-container-toolkit-base=${NVIDIA_CONTAINER_TO
libnvidia-container-tools=${NVIDIA_CONTAINER_TOOLKI
libnvidia-container1=${NVIDIA_CONTAINER_TOOLKIT_VER
Then run the container:
docker run -d -e JUPYTER_PASSWORD="mypassword" \
-p 8888:8888 -p 2222:22 \
-v $(pwd)/work:/workspace/work \
--gpus all \
unsloth/unsloth
Go to http://localhost:8888 and you're in. Jupyter
Lab with Unsloth notebooks ready to go.


---
*Page 10*


Verify Everything Works
Run this script to confirm Unsloth is working end-
to-end:
from unsloth import FastLanguageModel, FastModel
import torch
from trl import SFTTrainer, SFTConfig
from datasets import load_dataset
max_seq_length = 512
url = "https://huggingface.co/datasets/laion/OIG/reso
dataset = load_dataset("json", data_files = {"train"
model, tokenizer = FastLanguageModel.from_pretrained(
model_name = "unsloth/gemma-3-270m-it",
max_seq_length = max_seq_length,
load_in_4bit = True,
load_in_8bit = False,
load_in_16bit = False,
full_finetuning = False,
trust_remote_code = False,
)
model = FastLanguageModel.get_peft_model(
model,
r = 16,
target_modules = ["q_proj", "k_proj", "v_proj", "
"gate_proj", "up_proj", "down_p
lora_alpha = 16,
lora_dropout = 0,
bias = "none",
use_gradient_checkpointing = "unsloth",
random_state = 3407,


---
*Page 11*


max_seq_length = max_seq_length,
use_rslora = False,
loftq_config = None,
)
trainer = SFTTrainer(
model = model,
train_dataset = dataset,
tokenizer = tokenizer,
args = SFTConfig(
max_seq_length = max_seq_length,
per_device_train_batch_size = 2,
gradient_accumulation_steps = 4,
warmup_steps = 10,
max_steps = 60,
logging_steps = 1,
output_dir = "outputs",
optim = "adamw_8bit",
seed = 3407,
dataset_num_proc = 1,
),
)
trainer.train()
If it’s working you’ll see the Unsloth banner and
training steps logging out. That means your setup
is good.
Fine-Tuning a Bigger Model (gpt-oss-20B)


---
*Page 12*


Same pattern, different model name. Here’s a full
training script for gpt-oss-20B:
from unsloth import FastLanguageModel, FastModel, Fas
import torch
from trl import SFTTrainer, SFTConfig
from datasets import load_dataset
max_seq_length = 2048
url = "https://huggingface.co/datasets/laion/OIG/reso
dataset = load_dataset("json", data_files = {"train"
fourbit_models = [
"unsloth/gpt-oss-20b-unsloth-bnb-4bit",
]
model, tokenizer = FastLanguageModel.from_pretrained(
model_name = "unsloth/gpt-oss-20b",
max_seq_length = max_seq_length,
load_in_4bit = True,
load_in_8bit = False,
load_in_16bit = False,
full_finetuning = False,
trust_remote_code = False,
)
model = FastLanguageModel.get_peft_model(
model,
r = 16,
target_modules = ["q_proj", "k_proj", "v_proj", "
"gate_proj", "up_proj", "down_p
lora_alpha = 16,
lora_dropout = 0,
bias = "none",
use_gradient_checkpointing = "unsloth",
random_state = 3407,


---
*Page 13*


max_seq_length = max_seq_length,
use_rslora = False,
loftq_config = None,
)
trainer = SFTTrainer(
model = model,
train_dataset = dataset,
tokenizer = tokenizer,
args = SFTConfig(
max_seq_length = max_seq_length,
per_device_train_batch_size = 2,
gradient_accumulation_steps = 4,
warmup_steps = 10,
max_steps = 60,
logging_steps = 1,
output_dir = "outputs",
optim = "adamw_8bit",
seed = 3407,
),
)
trainer.train()
The structure is identical. The only meaningful
change is the model name and sequence length.
The Context Length Numbers Are Worth
Understanding


---
*Page 14*


This is the part that surprised me most. Here’s
what Unsloth allows on a 24GB GPU for Llama 3.1
8B vs standard Hugging Face:
| GPU VRAM | Unsloth Context | HF + FA2 Context |
| -------- | --------------- | ---------------- |
| 8 GB | 2,972 | OOM |
| 12 GB | 21,848 | 9,321 |
| 16 GB | 40,724 | 2,551 |
| 24 GB | 78,475 | 5,789 |
| 80 GB | 342,733 | 28,454 |
On 8GB VRAM, standard Hugging Face crashes.
Unsloth trains at nearly 3K context. On 24GB,
Unsloth handles 78K context while HF maxes out
at 5.7K.
That’s not a marginal improvement. That’s a
different category of what’s possible on the same
hardware.


---
*Page 15*


Advanced Install (If You Need a Specific
Torch/CUDA Combo)
If the basic pip install unsloth doesn't work, you
might need to match your exact PyTorch and
CUDA versions. Let the auto-installer figure it out:
wget -qO- https://raw.githubusercontent.com/unslothai
Or manually, for example torch 2.4 + CUDA 12.1:
pip install --upgrade pip
pip install "unsloth[cu121-torch240] @ git+https://gi
For Ampere GPUs (A100, H100, RTX 3090) add -
ampere:
pip install "unsloth[cu121-ampere-torch240] @ git+htt
To update Unsloth later:


---
*Page 16*


pip install --upgrade --force-reinstall --no-cache-di
What You Can Do With It
Once training finishes, you can export to GGUF for
llama.cpp, deploy with vLLM or SGLang, push to
Hugging Face, or keep training from a saved LoRA
adapter. The docs at unsloth.ai cover all of that.
The short version: you train locally, export in
whatever format you need, and run it wherever
you want.
No cloud bill. No rate limits. Your model, your
hardware, your data.
Qwen AI AI Agent LLM Fine Tuning


---
*Page 17*


Published in Coding Nexus
Following
18.7K followers · Last published 2 days ago
Coding Nexus is a community of developers, tech
enthusiasts, and aspiring coders. Whether you’re
exploring the depths of Python, diving into data
science, mastering web development, or staying
updated on the latest trends in AI, Coding Nexus has
something for you.
Written by Civil Learning
Following
6.3K followers · 6 following
We share what you need to know. Shared only for
information.
No responses yet
To respond to this story,
get the free Medium app.
More from Civil Learning and Coding Nexus


---
*Page 18*


In by In by
Coding Nexus Civil Learning Coding Nexus Emma Kirsten
Daggr: Code-First Why the Kalman Filter
P th Lib Th t B t M i A
Daggr is a code-first Python How an old aerospace
lib th t t AI kfl l ith t th h k
Jan 30 Dec 18, 2025
In by In by
Coding Nexus Civil Learning Coding Nexus Civil Learning
Search 40M The Ralph Loop
d t i d Ch d H I B ild
Search 40M documents in Using the Ralph Wiggum loop
d 200 CPU i ill t h d f 98% f
Jan 8 Jan 28
See all from Civil Learning See all from Coding Nexus


---
*Page 19*


Recommended from Medium
In by Alain Airom (Ayrom)
AI Exploration Jo… Florian J…
The Architecture of
NVIDIA Nemotron-
U d t di M
P 1 1 A Li ht i
Beyond the Text: Wiring Up My
If you’re the person in your
Fi t D li G h
ibl f
Feb 24 Feb 22


---
*Page 20*


In by In by
Towar… Mandar Karhade, … Level Up Codi… Richard Qui…
OpenClaw’s Victim: Hidden States on a Mac
M t R h ’ Mi i U i MLX f
“Director of Alignment” and Most machine learning
th i li d t! Wh t it h h NVIDIA
Feb 25 Feb 24
Phil | Rentier Digital Automation Rost Glukhov
Spotify Built “Honk” to Best LLMs for Ollama
R l C di I B il 16GB VRAM GPU
Last week, Spotify’s co-CEO Running large language
t ld W ll St t th t hi b t d l l ll i
Feb 20 Feb 21
See more recommendations