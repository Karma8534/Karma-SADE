# 350M-LocalLlm

*Converted from: 350M-LocalLlm.PDF*



---
*Page 1*


Open in app
11
Search Write
Member-only story
LFM2.5-350M: Agentic
Loops at 350M
Parameters
Agent Native Following 12 min read · 2 days ago
72 1
This model easily runs on a phone, car, laptop,
browser, industrial edge device, embedded
workflow or offline field system.
It unlocks tool use, structured output, instruction
following, and data extraction with just 350M
parameters.


---
*Page 2*


LFM2.5–350M is optimized around the boring,
expensive, operationally painful parts of AI
systems that engineering teams actually need to
make reliable.
This changes the question from:


---
*Page 3*


“What is the smartest model I can afford?”
to:
“What is the smallest model I can trust inside a
loop?”
LFM2.5–350M keeps the footprint small enough for
constrained deployments, ships in formats meant
for real deployment paths, and improves sharply
over the earlier 350M release specifically on
instruction following, extraction, and tool use.
The model is recommended for data extraction,
structured outputs, and tool use, and not
recommended for knowledge-heavy tasks,
programming, or creative writing.
That honesty is also part of why this release is
compelling.
LFM2.5–350M is a specialized control-plane model
for the edge of your system: the component that


---
*Page 4*


turns messy user intent into validated structure,
safe tool invocations, and local low-latency
execution.
In this article, I will cover the important aspects,
show how to run it, how to wire it into a tool loop,
where it fits architecturally, and why the most


---
*Page 5*


important takeaway is not “350M is enough for
everything,” but rather:
350M is suddenly enough for more of the agent
stack than many teams assumed.
The Real Signal in This Release
LFM2.5–350M is more interesting because the
release is framed around capabilities that matter
in production:
instruction following
structured outputs
data extraction
function calling / tool use
low memory footprint
low-latency deployment across CPUs, GPUs,
NPUs, and mobile
consistent behavior under constrained
environments


---
*Page 6*


That changes how you should evaluate it.
If you are building an agent, the expensive failures
are rarely “the answer sounded slightly less
eloquent.” but they are:
the model emits invalid JSON
the wrong field is extracted
the wrong tool is selected
the right tool is selected with the wrong
arguments
a loop goes off-script
latency kills the UX
inference costs force you into batching, caching,
or product compromises
privacy requirements prevent you from shipping
the workflow you actually want
So the question is “Can this model sit inside an
operational loop without becoming the weakest


---
*Page 7*


reliability link?”
The model was extended from 10T to 28T tokens of
pre-training and post-trained with large-scale
reinforcement learning.
I would not reduce the story to “just more tokens,”
but the outcome is clear: the 350M class is being
pushed toward operational competence.
Why You Should Care
The context around this release includes two
separate tuning stories that point in the same
direction:
Liquid AI’s collaboration with Distil Labs reports
that task-specific fine-tuning pushed multi-turn
tool calling into the 95%+ range on smart home,
banking, and terminal-style workflows.
A separate hands-on report showed that a LoRA
fine-tune on 390 examples turned a base model
with complete parse failure into a tuned model


---
*Page 8*


with 0 parse errors, then rose further to roughly
93% precision / recall after adding targeted
examples and checkpoint selection.
And this particular model appears unusually
receptive to small-data adaptation for structured
tasks.
That is gold for product teams.
Because once a model becomes tunable in the way
your workflow demands, you start thinking in
terms of small specialist models embedded into
specific product paths.
That is how real systems get cheaper, faster, and
more reliable.
Move the Model Closer to the Action
For years, a lot of AI products have defaulted to
this pattern:
1. collect user input on-device


---
*Page 9*


2. send to cloud model
3. interpret intent in the cloud
4. maybe call tools in the cloud
5. maybe return a result to a local app
That pattern is fine when the cloud is the only
place inference is practical.
But for high-frequency agentic loops, it is often the
wrong shape.
If a model can run locally and cheaply, then you
can move the first-pass intelligence much closer to
where the state is:
the phone
the car
the laptop
the browser
the industrial edge device


---
*Page 10*


the embedded workflow
the offline field system
That has real consequences.
1. Lower latency changes what workflows feel
possible
The official benchmarks are exactly the kind that I
care about because they are attached to actual
devices:
313 tok/s decode on AMD Ryzen AI Max 395+
with llama.cpp Q4
62 tok/s decode on a Snapdragon 8 Elite For
Galaxy GPU with RunAnywhere Q4
564 tok/s decode on Apple M5 Max with Mirai
bf16
operation on low-memory devices including
iPhone 13 Mini, Pixel 6a, and Raspberry Pi 5


---
*Page 11*


2. Privacy becomes a deployment decision, not a
product compromise
The cookbook examples are full of local-first
workflows: invoice parsing, desktop agents, on-
device search, voice interactions, browser-based
tool calling.
3. You can split the agent stack by difficulty


---
*Page 12*


Once a small local model can handle the repetitive
structured parts, your larger remote model
becomes an escalation path rather than the default
runtime.
That is a far better cost structure.
Quick Start: The Simplest Way to Run
LFM2.5–350M
At minimum, you want a recent Transformers
build.
Install:
pip install "transformers>=4.55.0" torch accelera
Basic inference with Transformers:
from transformers import AutoModelForCausalLM, AutoTo
model_id = "LiquidAI/LFM2.5-350M"
model = AutoModelForCausalLM.from_pretrained(
model_id,


---
*Page 13*


device_map="auto",
dtype="bfloat16",
# attn_implementation="flash_attention_2" <- uncomm
)
tokenizer = AutoTokenizer.from_pretrained(model_id)
streamer = TextStreamer(tokenizer, skip_prompt=True,
prompt = "What is C. elegans?"
input_ids = tokenizer.apply_chat_template(
[{"role": "user", "content": prompt}],
add_generation_prompt=True,
return_tensors="pt",
tokenize=True,
).to(model.device)
output = model.generate(
input_ids,
do_sample=True,
temperature=0.1,
top_k=50,
repetition_penalty=1.05,
max_new_tokens=512,
streamer=streamer,
)
That gives you the minimum viable setup.
A few practical notes:
The model uses a ChatML-like template.


---
*Page 14*


Context length is 32,768 tokens.
The published generation defaults emphasize
low-temperature, more deterministic use.
For operational workflows, that is exactly what
you usually want.
If your goal is extraction or tool routing, resist the
temptation to make the model “more creative.”
Determinism is usually your friend.
Quick Start for Local CPU Inference
If your goal is local deployment, the model library
and model card both emphasize multiple
deployment formats:
GGUF for llama.cpp / LM Studio / local CPU-GPU
workflows
MLX for Apple Silicon
ONNX for cross-platform and edge deployment
native checkpoint for Transformers and vLLM


---
*Page 15*


For local CPU-first setups, GGUF is the obvious
entry point.
The docs recommend Q4_K_M as the best balance
of size and quality for GGUF deployments.
Example llama.cpp run


---
*Page 16*


llama-cli -hf LiquidAI/LFM2.5-350M-GGUF -c 4096 --col
--temp 0.1 --top-k 50 --repeat-penalty 1.05
If inference is slower than expected, check the
usual levers:
use the right thread count
compile with GPU support where available
try a smaller quantization level
prefer GGUF for CPU inference
prefer MLX on Apple Silicon
prefer vLLM for high-throughput serving
That may sound obvious, but with small models it
matters even more because the entire value
proposition is tied to deployment efficiency.
The First Real Pattern: Structured Output
If you are evaluating LFM2.5–350M, start with this:
extract this form


---
*Page 17*


normalize this request
map this sentence to schema
emit valid JSON
omit missing values
do not invent fields
Start the assistant response with the opening
structure you want so the model continues in the
right format.
Here is a practical extraction pattern for agent
inputs.
Structured extraction pattern
from transformers import AutoModelForCausalLM, AutoTo
import torch
model_id = "LiquidAI/LFM2.5-350M"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
model_id,
device_map="auto",
dtype="bfloat16",


---
*Page 18*


)
messages = [
{
"role": "system",
"content": (
"Extract intent into JSON.\n"
"Return only a JSON object with these optional
"- action\n"
"- entity\n"
"- priority\n"
"- destination\n"
"- notes\n"
"Omit missing keys. Do not hallucinate."
),
},
{
"role": "user",
"content": (
"The shipment for order 48372 is urgent. "
"Please reroute it to Rotterdam and let ops kno
),
},
{
"role": "assistant",
"content": "{\n",
},
]
inputs = tokenizer.apply_chat_template(
messages,
add_generation_prompt=False,
return_tensors="pt",
tokenize=True,
).to(model.device)


---
*Page 19*


outputs = model.generate(
inputs,
do_sample=False,
max_new_tokens=128,
)
text = tokenizer.decode(outputs[0], skip_special_toke
print(text)
Why this matters:
it narrows the output manifold
it reduces parse errors
it gives you a cleaner post-processing path
it is much closer to how production systems
actually use small models
This is also why the anecdotal fine-tuning results
in the context are so important: once parse errors
drop to zero and field placement gets more stable,
a tiny model becomes dramatically more valuable.
The Second Real Pattern: Tool Use with a
Constrained Tool Set


---
*Page 20*


Liquid’s tool-use docs are refreshingly concrete.
The workflow is simple:
1. define tools as JSON in the system prompt or via
apply_chat_template
2. generate a response that may include a function
call
3. execute the tool outside the model
4. append the tool result as a tool role
5. generate again so the model can interpret the
result
That is the agent loop in its cleanest form.
Here is a minimal example adapted for LFM2.5–
350M.
Minimal tool-calling example
import json
from transformers import AutoModelForCausalLM, AutoTo


---
*Page 21*


model_id = "LiquidAI/LFM2.5-350M"
model = AutoModelForCausalLM.from_pretrained(
model_id,
dtype="bfloat16",
device_map="auto",
)
tokenizer = AutoTokenizer.from_pretrained(model_id)
tools = [{
"name": "get_candidate_status",
"description": "Retrieves the current status of a c
"parameters": {
"type": "object",
"properties": {
"candidate_id": {
"type": "string",
"description": "Unique identifier for the candidate
}
},
"required": ["candidate_id"]
}
}]
messages = [
{"role": "system", "content": f"List of tools: {jso
{"role": "user", "content": "What is the current st
]
inputs = tokenizer.apply_chat_template(
messages,
add_generation_prompt=True,
return_dict=True,
return_tensors="pt"


---
*Page 22*


).to(model.device)
outputs = model.generate(**inputs, max_new_tokens=256
response = tokenizer.decode(
outputs[0][len(inputs["input_ids"][0]):],
skip_special_tokens=False
)
print("MODEL RESPONSE:")
print(response)
A typical output includes a function call wrapped
in the model’s tool-call tokens:
<|tool_call_start|>[get_candidate_status(candidate_id
Checking the current status of candidate ID 12345.
Then you execute the tool yourself:
def get_candidate_status(candidate_id: str):
return [{
"candidate_id": candidate_id,
"status": "Interview Scheduled",
"position": "Clinical Research Associate",
"date": "2023-11-20",
}]


---
*Page 23*


messages.append({"role": "assistant", "content": resp
messages.append({"role": "tool", "content": json.dump
And regenerate:
inputs = tokenizer.apply_chat_template(
messages,
add_generation_prompt=True,
return_dict=True,
return_tensors="pt"
).to(model.device)
outputs = model.generate(**inputs, max_new_tokens=256
final = tokenizer.decode(
outputs[0][len(inputs["input_ids"][0]):],
skip_special_tokens=True
)
print("FINAL ANSWER:")
print(final)
This matters because it shows the real opportunity
for LFM2.5–350M:
don’t ask it to be the database


---
*Page 24*


don’t ask it to be the world model
ask it to select and parameterize the right tool
That is the correct small-model mindset.
Generate, Execute and Regenerate
Here’s the core loop:
generate a response, possibly with tool calls
execute the tool calls
regenerate the response
You need to know whether it can do this loop
cleanly.
Here is a minimal version you can adapt.
Minimal agent loop skeleton
import json
import re
from transformers import AutoModelForCausalLM, AutoTo
TOOL_CALL_RE = re.compile(r"<\|tool_call_start\|>(.*?


---
*Page 25*


def search_orders(order_id: str):
return [{"order_id": order_id, "status": "delayed",
def reroute_order(order_id: str, destination: str):
return [{"order_id": order_id, "status": "rerouted"
tool_registry = {
"search_orders": search_orders,
"reroute_order": reroute_order,
}
tools = [
{
"name": "search_orders",
"description": "Lookup the latest order record",
"parameters": {
"type": "object",
"properties": {"order_id": {"type": "string"}},
"required": ["order_id"],
},
},
{
"name": "reroute_order",
"description": "Reroute an order to a new destinati
"parameters": {
"type": "object",
"properties": {
"order_id": {"type": "string"},
"destination": {"type": "string"},
},
"required": ["order_id", "destination"],
},
},
]


---
*Page 26*


model_id = "LiquidAI/LFM2.5-350M"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
model_id,
device_map="auto",
dtype="bfloat16",
)
messages = [
{"role": "system", "content": f"List of tools: {jso
{"role": "user", "content": "Check order 48372 and
]
for step in range(4):
inputs = tokenizer.apply_chat_template(
messages,
add_generation_prompt=True,
return_dict=True,
return_tensors="pt"
).to(model.device)
outputs = model.generate(**inputs, max_new_tokens=256
response = tokenizer.decode(
outputs[0][len(inputs["input_ids"][0]):],
skip_special_tokens=False
)
print(f"\nSTEP {step} RESPONSE:\n{response}")
messages.append({"role": "assistant", "content": resp
match = TOOL_CALL_RE.search(response)
if not match:
break


---
*Page 27*


# Extremely minimal parser for demo purposes only.
call_text = match.group(1).strip()
if call_text.startswith("[") and call_text.endswith("
call_text = call_text[1:-1]
if call_text.startswith('search_orders('):
order_id = call_text.split('order_id="')[1].split('
tool_result = tool_registry["search_orders"](order_
elif call_text.startswith('reroute_order('):
order_id = call_text.split('order_id="')[1].split('
destination = call_text.split('destination="')[1].s
tool_result = tool_registry["reroute_order"](order_
else:
tool_result = [{"error": "Unsupported tool call"}]
messages.append({"role": "tool", "content": json.dump
This demonstrates the right evaluation question:
Can the model reliably stay inside this loop with
your tools, your schemas, and your domain
prompts?
If yes, you are in business.
Fine-Tuning Is Not Optional If Reliability
Actually Matters


---
*Page 28*


The base scores are promising but if your system
has real correctness requirements, you should
assume that fine-tuning is part of the
productization path.
It supports:
SFT with LoRA using TRL
SFT with LoRA using Unsloth
DPO
GRPO
continued pre-training
And some practical knobs you usually need:
start around 2e-4 for LoRA
consider QLoRA for memory efficiency
reduce batch size and use gradient accumulation
enable gradient checkpointing


---
*Page 29*


verify dataset formatting against the chat
template
That lines up almost perfectly with:
base model: total parse collapse on the task
LoRA fine-tune on a tiny dataset: parse errors
drop to zero
targeted error-driven examples: precision/recall
move into the low 90s
training time: measured in seconds on a laptop
That suggests a very actionable development loop:
1. start with the base or instruct checkpoint
2. run a small eval harness against your real
schema or tool set
3. collect exact failure modes
4. add targeted examples for argument mapping,
boundary conditions, and empty-output cases
5. re-run


---
*Page 30*


6. only then decide whether you need a larger
model
That order matters.
Too many teams escalate model size before they
have tested how far task shaping can take them.
Small Specialist First, Bigger Model Only
on Escalation
Here is the architecture I think this release most
strongly suggests.
Tier 1: LFM2.5–350M as the fast local specialist
Use it for:
request normalization
intent classification
structured extraction
tool selection
argument construction
deterministic summary of tool results


---
*Page 31*


offline or low-connectivity modes
Tier 2: escalate only when needed
Escalate to a larger model when:
the task is planning-heavy
the tool loop breaks confidence thresholds
the user asks open-ended knowledge questions
the answer requires coding, math, or richer
prose
ambiguity remains after one local pass
This gives you three wins at once:
1. Cost: Your high-frequency requests stop hitting
the expensive path.
2. Latency: The short operational loop gets
dramatically faster.
3. Privacy: Sensitive text can remain local unless
escalation is necessary.


---
*Page 32*


Deployment Choices: Pick the Format
That Matches the Job
Liquid’s model library is nicely explicit about
formats, and developers should take that seriously.
Use native checkpoint when:
you want easiest access in Transformers
you are experimenting with prompts
you plan to fine-tune
you want to serve with vLLM
Use GGUF when:
you want local inference through llama.cpp or
LM Studio
you are targeting CPU-heavy environments
you want quantized deployment with tight
memory control
Use MLX when:
you are on Apple Silicon


---
*Page 33*


you want local performance with unified
memory
Use ONNX when:
you want cross-platform runtime portability
you care about deployment across
heterogeneous accelerators
you are building a product around embedded or
edge serving constraints
As for quantization, the model library’s guidance is
practical:
Q4_K_M is the recommended GGUF balance
8-bit is the recommended MLX balance
Q4 is the default ONNX recommendation for
most deployments
This is exactly how small models become
deployable products.
Concluding Thoughts


---
*Page 34*


LFM2.5–350M is interesting not because it proves
that tiny models are secretly AGI.
It is interesting because it helps formalize a better
way to build agents.
The better pattern is:
use small models for the repetitive operational
work
keep them close to the edge
shape them toward structure
fine-tune them on real failure cases
escalate only when the task truly needs broader
intelligence
That is a software architecture insight disguised as
a model launch.
And that is why this release matters.


---
*Page 35*


For developers building agentic systems, the
question is no longer whether a 350M model can
produce fluent chat. That is the wrong bar.
The right bar is this:
Can it reliably turn intent into action inside a
constrained loop, under real deployment
constraints, at a cost and latency profile that
changes the product?
LFM2.5–350M does not answer “yes” for every
agentic problem.
But for extraction-heavy, tool-driven, structure-
first workflows, it moves that answer much closer
to yes than the parameter count would suggest.
That is the real story.
And if the tuning results in the surrounding
ecosystem are any indication, the most exciting


---
*Page 36*


part may not be what this model does out of the
box.
It may be what it becomes after you teach it your
exact workflow.
Bonus Articles
7 Local LLM Families To Replace
Cl d /C d (f d t k )
Open-source model families you can run
l ll th t d li i l ld
agentnativedev.medium.com
Qwen 3.5 35B-A3B: Why Your $800 GPU
J t B F ti Cl AI
I have been running local models for a while
d I th ht I h d tt d
agentnativedev.medium.com
I Ignored 30+ OpenClaw Alternatives Until
O F
Fully open-source Agent Operating System,
itt ti l i R t hi i i l
agentnativedev.medium.com
MiroFish: Swarm-Intelligence with 1M
A t Th t C P di t E thi
Spawning thousands of autonomous agents
ith i liti i d


---
*Page 37*


agentnativedev.medium.com
MiniMax M2.7 Shouldn’t Be This Close to
O 4 6
How can a 203-person company match
O 4 6 l l f d t
agentnativedev.medium.com
KubeClaw: OpenClaw for Adults
Secure defaults, pinned images, predictable
d b bilit d li bilit f
agentnativedev.medium.com
TurboQuant: Local Agent Swarms with 4M-
T k C t t $5K D kt
Multi-agent system that previously required
th t API b i ti i t
agentnativedev.medium.com
GSD-Browser: Playwright Is Not Good
E h f A t
Fast, native browser automation CLI powered
b Ch D T l P t l ith
agentnativedev.medium.com
AI Agent Local Ai Open Source Ai Agentic Ai


---
*Page 38*


Edge Computing
Written by Agent Native
Following
9K followers · 0 following
Hyperscalers, open-source developments, startup
activity and the emerging enterprise patterns
shaping agentic AI.
Responses (1)
To respond to this story,
get the free Medium app.
Sebastian Buzdugan
2 days ago
unpopular opinion but "agentic loops" on a 350m model sound great until
you hit real-world edge cases and realize your eval + monitoring stack is
doing all the actual reliability work


---
*Page 39*


More from Agent Native
Agent Native Agent Native
qlaude: Queue-based GLM-5V-Turbo Beats
Cl d C d O 4 6 M lti d
Claude Code has operational GLM-5V-Turbo is Z.AI’s first
b t f l ff lti d l di f d ti
5d ago 1d ago
Agent Native Agent Native
Why LLMs Break When Agentic Identity in
Y Add V i AWS A GCP d
Voice layer is a first-class Biggest blind spot in most
hit t l d it t ’ ti hit t i
Mar 20 Mar 6


---
*Page 40*


See all from Agent Native
Recommended from Medium
Will Lockett Alvis Ng
Musk’s Orbital Data Nobody Wants to Learn
C t Id I G tti AI
How does anyone believe The “lifelong learner” identity
thi ? i ’t i ti It’
6d ago Mar 24
In by Roberta Micore
Predict Tasmia Sharmin


---
*Page 41*


Palantir CEO Says Only The First 5 Apps I
T T Will S i I t ll E N
Alex Karp told Gen Z there are The short version: I set up a
“b i ll t t k M t k l t th
Mar 26
Mar 25
In by In by
CodeX MayhemCode Towards Deep L… Sumit Pa…
Mini PC vs Desktop PC Anthropic Accidentally
f L l LLM i 2026 L k d It O S
Most people buying hardware The company that talks about
f l l AI i 2026 k th AI f t th t j t l ft it
Mar 26 5d ago
See more recommendations