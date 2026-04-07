# Agentic AI for Modern Deep Learning Experimentation _ Towards Data Science

*Converted from: Agentic AI for Modern Deep Learning Experimentation _ Towards Data Science.PDF*



---
*Page 1*


SOC Alert Overload?
AGENTIC AI
Agentic AI for Modern Deep
Learning Experimentation
Stop babysitting training runs. Start shipping research. Autonomous
experiment management built for/by deep learning engineers.
Sam Black
Feb 18, 2026 14 min read
Photo by MART PRODUCTION via Pexels


---
*Page 2*


Meet an agent that reads your metrics, detects anomalies,
applies predefined tuning rules, restarts jobs when necessary,
and logs every decision—without you staring at loss curves at 2
a.m.
In this article, I’ll provide a lightweight agent designed for deep
learning researchers and ML engineers that can:
• Detect failures automatically
• Visually reason over performance metrics
• Apply your predefined hyperparameter strategies
• Relaunch jobs
• Document every action and outcome
No architecture search. No AutoML. No invasive rewrites of your
codebase.
The implementation is intentionally minimal: containerize your
training script, add a small LangChain-based agent, define
hyperparameters in YAML, and express preferences in markdown.
You’re probably doing 50% of this already.
Drop this agent into your manual train.py workflow and go from
󰑣 💯
to in a single day.
The problem with your existing experiments
🤔
You endlessly ponder over hyperparameters.
▶
You run train.py.
🐛
You fix the bug in train.py.


---
*Page 3*


🔁
You rerun train.py
👀
You stare at TensorBoard.
🫠
You question reality.
🔄
You repeat.
Every practicing Deep Learning/Machine Learning
Engineer in the field does this. Don’t be ashamed.
Original photo by MART PRODUCTION via Pexels.
Gif imagined by Grok
Stop staring at your model spit out numbers
You are not a Jedi. No amount of staring will magically make your
[validation loss | classification accuracy | perplexity | any other
metric you can name] move in the direction you want.
Babysitting a model into the middle of the night for a
vanishing/exploding gradient NaN in a deep transformer based
network that you can’t track down—and that might never even
appear? Also a hard no.
How are you supposed to solve real research problems when
most of your time is spent on work that technically has to be
done, yet contributes very little to actual insight?


---
*Page 4*


If 70% of your day is consumed by operational drag, when does
the thinking happen?
Shift to agentic-driven experiments
Most of the deep learning engineers and researchers I work with
still run experiments manually. A significant portion of the day
goes to: scanning Weights & Biases or TensorBoard for last night’s
run, comparing runs, exporting metrics, adjusting
hyperparameters, logging notes, restarting jobs. Then repeating
the cycle.
It is dry, tedious, and repetitive work.
We’re going to offload these repetitive tasks so you can shift your
focus to high value work
The concept of AutoML is, frankly, laughable.
Your [new] agent will not make decisions on how to change your
network topology or add complex features — that’s your job. It
will replace the repetitive glue work that eats valuable time with
little added value.
Agent Driven Experiments (ADEs)
Switching from manual experiments to an agent-driven workflow
is simpler than it initially seems. No rewriting your stack, no
heavy systems, no tech debt.


---
*Page 5*


Image by Author
At its core, an ADE requires three steps:
1. Containerize your existing training script
Wrap your current train.py in a Docker container. No
refactoring of model logic. No architectural changes. Just
a reproducible execution boundary.
2. Add a lightweight agent
Introduce a small LangChain-based script that reads
metrics from your dashboard, applies your preferences,
decides when and where to relaunch, halt or document
and schedule it with cron or any job scheduler
3. Define behavior and preferences with natural language
Use a YAML file for configuration and hyperparameters


---
*Page 6*


Use a Markdown document to communicate with your
agent
That’s the entire system. Now, Let’s review each step.
Containerize your training script
One could argue you should be doing this anyways. It makes
restarting and scheduling much easier, and, if you move to a
Kubernetes cluster for training, the disruption to your existing
process is much lower.
If you’re already doing this, skip to the next section. If not,
here’s some helpful code you can use to get started.
First, let’s define a project structure that will work with Docker.
your experiment/
├── scripts/
│ ├── train.py # Main training script
│ └── health_server.py # Health check server
├── requirements.txt # Python dependencies
├── Dockerfile # Container definition
└── run.sh # Script to start training + heal
We need to make sure that your train.py script can load a
configuration file from the cloud, allowing the agent to edit it if
needed.
I recommend using GitHub for this. Here’s an example of how to
read a remote config file. The agent will have a corresponding
tool to read and modify this config file.


---
*Page 7*


import os
import requests
import yaml
from box import Box
# add this to `train.py`
GITHUB_RAW = (
"https://raw.githubusercontent.com/"
"{owner}/{repo}/{ref}/{path}"
)
def load_config_from_github(owner, repo, path, ref="main", token=N
url = GITHUB_RAW.format(owner=owner, repo=repo, ref=ref, path=
headers = {}
if token:
headers["Authorization"] = f"Bearer {token}"
r = requests.get(url, headers=headers, timeout=10)
r.raise_for_status()
return Box(yaml.safe_load(r.text))
config = load_yaml_from_github(...)
# use params throughout your `train.py` script
optimizer = Adam(lr=config.lr)
We also include a health check server to run alongside the main
process. This allows container managers, such as Kubernetes, or
your agent, to monitor the job’s status without inspecting logs.
If the container’s state changes unexpectedly, it can be
automatically restarted. This simplifies agent inspection, as
reading and summarizing log files can be more costly in tokens
than simply checking the health of a container.


---
*Page 8*


# health_server.py
import time
from pathlib import Path
from fastapi import FastAPI, Response
app = FastAPI()
HEARTBEAT = Path("/tmp/heartbeat")
STATUS = Path("/tmp/status.json") # optional richer state
MAX_AGE = 300 # seconds
def last_heartbeat_age():
if not HEARTBEAT.exists():
return float("inf")
return time.time() - float(HEARTBEAT.read_text())
@app.get("/health")
def health():
age = last_heartbeat_age()
# stale -> training likely hung
if age > MAX_AGE:
return Response("stalled", status_code=500)
# optional: detect NaNs or failure flags written by trainer
if STATUS.exists() and "failed" in STATUS.read_text():
return Response("failed", status_code=500)
return {"status": "ok", "heartbeat_age": age}
A small shell script, run.sh, which starts the health_server
process along side the train.py
#!/bin/bash
# Start health check server in the background
python scripts/health_server.py &
# Capture its PID if you want to terminate later


---
*Page 9*


HEALTH_PID=$!
# Start the main training script
python scripts/train.py
And of course, our Dockerfile, which is built on NVIDIA’s base
image so your container can use the host’s accelerator with zero
friction. This example is for Pytorch, but you can simply extend it
to Jax or Tensorflow if needed.
FROM nvidia/cuda:12.1.0-cudnn8-devel-ubuntu20.04
RUN apt-get update && apt-get install -y \
python3 python3-pip git
RUN python3 -m pip install --upgrade pip
# Install PyTorch with CUDA support
RUN pip3 install torch torchvision torchaudio --extra-index-url ht
WORKDIR /app
COPY . /app
CMD ["sh", "run.sh"]
✅
You’re containerized. Simple and minimal.
Add a lightweight agent
There are many agent frameworks to chose from. For this agent, I
like Langchain.
LangChain is a framework for building LLM-driven systems that
combine reasoning and execution. It simplifies chaining model


---
*Page 10*


calls, managing memory, and integrating external capabilities so
your LLM can do more than generate text.
In LangChain, Tools are explicitly defined, schema-bound
functions the model can call. Each tool is an idempotent skill or
task (e.g., reading a file, querying an API, modifying state).
In order for our agent to work, we first need to define the tools
that it can use to achieve our objective.
Tool definitions
1. read_preferences
Reads in user preferences and experiment notes from a
markdown document
2. check_tensorboard
Uses selenium with a chrome webdriver to screenshot
metrics
3. analyze_metric
Uses multimodal LLM reasoning to understand what’s
happening in the screenshot
4. check_container_health
Checks our containerized experiment using a health
check
5. restart_container
Restarts experiment if unhealthy or a hyperparameter
needs to be changed
6. modify_config


---
*Page 11*


Modifies a remote config file and commits to Github
7. write_memory
Writes a chain of actions to a persistent memory
(markdown)
This set of tools define our agent’s operational boundaries. All
interaction with our experiment through these tools, making
behavior controllable and hopefully, predictable.
Instead of providing these tools in line — here’s a github gist
containing all the tools described above. You can plug these into
your agent or modify as you see fit.
The agent
To be quite honest, the first time I tried to grok the official
Langchain documentation, I became immediately turned off of
the idea all together.
It’s overly verbose and more complex than necessary. If you’re
new to agents, or just don’t want to navigate the labyrinth that is
the Langchain documentation, please continue reading below.


---
*Page 12*


Langsmith? Random asides? Little tooltips
everywhere? I’ll pass on smiting this
worthy foe. Imagined by Grok
In a nutshell, this is how Langchain agents work:
Our agent uses a prompt to decide what to do at each step.
Steps are dynamically created by filling in the prompt with the
current context and previous outputs. Each LLM call [+ optional
tool invocation] is a step, and its output feeds into the next,
forming a chain.
Using this conceptionally recursive loop, the agent can reason
and perform the correct intended action over all the steps
required. How many steps is dependent on the agent’s ability to
reason and how clearly the termination condition is defined.
🤗
It’s a Lang-chain. Get it?


---
*Page 13*


The prompt
As noted, the prompt is the recursive glue that maintains context
across LLM and tool invocations. You’ll see placeholders (defined
below) used when the agent is first initialized.
We use a bit of LangChain’s built-in memory abstractions,
included with each tool call. Aside from that, the agent fills in the
gaps, deciding both the next step and which tool to call.
For readability, the main prompt is below. You can either plug it
directly into the agent script or load it from the filesystem before
running.
"You are an experiment automation agent responsible for monitoring
and maintaining ML experiments.
Current context:
{chat_history}
Your workflow:
1. First, read preferences from preferences.md to understand thres
2. Check TensorBoard at the specified URL and capture a screenshot
3. Analyze key metrics (validation loss, training loss, accuracy)
4. Check Docker container health for the training container
5. Take corrective actions based on analysis:
- Restart unhealthy containers
- Adjust hyperparameters according to user preferences
and anomalous patterns, restarting the experiment if necessar
6. Log all observations and actions to memory
Important guidelines:
- Always read preferences first to get current configuration
- Use visual analysis to understand metric trends
- Be conservative with config changes (only adjust if clearly need
- Write detailed memory entries for future reference
- Check container health before and after any restart


---
*Page 14*


- When modifying config, use appropriate values from preferences
Available tools: {tool_names}
Tool descriptions: {tools}
Current task: {input}
Think step by step and use tools to complete the workflow.
"""
Now with ~100ish lines, we have our agent. The agent is
initialized, then we define a series of steps. For each step, the
current_task directive is populated in our prompt, and each tool
updates a shared memory instance
ConverstationSummaryBufferMemory
We are going to use OpenAI for this agent, however, Langchain
provides alternatives, including hosting your own. If cost is an
issue, there are open-sourced models which can be used here.
import os
from datetime import datetime
from pathlib import Path
from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationSummaryBufferMemory
# Import tools from tools.py
from tools import (
read_preferences,
check_tensorboard,
analyze_metric,
check_container_health,
restart_container,
modify_config,
write_memory


---
*Page 15*


)
PROMPT=open("prompt.txt").read()
class ExperimentAutomation:
def __init__(self, openai_key=None):
"""Initialize the agent"""
self.llm = ChatOpenAI(
temperature=0.8,
model="gpt-4-turbo-preview",
api_key=openai_key or os.getenv('OPENAI_API_KEY')
)
# Initialize memory for conversation context
self.memory = ConversationSummaryBufferMemory(
llm=self.llm,
max_token_limit=32000,
memory_key="chat_history",
return_messages=True
)
def create_agent(self):
"""Create LangChain agent with imported tools"""
tools = [
lambda **kwargs: read_preferences(memory=self.memory,
lambda **kwargs: check_tensorboard(memory=self.memory,
lambda **kwargs: analyze_metric(memory=self.memory, **
lambda **kwargs: check_container_health(memory=self.me
lambda **kwargs: restart_container(memory=self.memory,
lambda **kwargs: modify_config(memory=self.memory, **k
lambda **kwargs: write_memory(memory=self.memory, **kw
]
# Create the prompt template
prompt = PromptTemplate.from_template(PROMPT)
agent = create_react_agent(
llm=self.llm,
tools=tools,
prompt=prompt
)


---
*Page 16*


# Create agent executor with memory
return AgentExecutor(
agent=agent,
tools=tools,
memory=self.memory,
verbose=True,
max_iterations=15,
handle_parsing_errors=True,
return_intermediate_steps=True
)
def run_automation_cycle(self):
"""Execute the full automation cycle step by step"""
write_memory(
entry="Automation cycle started",
category="SYSTEM",
memory=self.memory
)
try:
agent = self.create_agent()
# Define the workflow as individual steps
workflow_steps = [
"Read preferences from preferences.md to capture t
"Check TensorBoard at the specified URL and captur
"Analyze validation loss, training loss, and accur
"Check Docker container health for the training co
"Restart unhealthy containers if needed",
"Adjust hyperparameters according to preferences a
"Write all observations and actions to memory"
]
# Execute each step individually
for step in workflow_steps:
result = agent.invoke({"input": step})
# Write step output to memory
if result.get("output"):


---
*Page 17*


memory_summary = f"Step: {step}\nOutput: {resu
write_memory(entry=memory_summary, category="S
write_memory(
entry="Automation cycle completed successfully",
category="SYSTEM",
memory=self.memory
)
return result
except Exception as e:
error_msg = f"Automation cycle failed: {str(e)}"
write_memory(entry=error_msg, category="ERROR", memory
raise
def main():
try:
automation = ExperimentAutomation(openai_key=os.environ["O
result = automation.run_automation_cycle()
if result.get('output'):
print(f"\nFinal Output:\n{result['output']}")
if result.get('intermediate_steps'):
print(f"\nSteps Executed: {len(result['intermediate_st
print("\n✓ Automation cycle completed successfully")
except Exception as e:
print(f"\n✗ Automation failed: {e}")
write_memory(entry=f"Critical failure: {str(e)}", category
import sys
sys.exit(1)
if __name__ == "__main__":
main()


---
*Page 18*


Now that we have our agent, and tools, let’s discuss how we
actually express our intent as a researcher – the most important
piece.
Define behavior and preferences with natural
language
As described, defining what we are looking for when we start an
experiment is vital to getting the correct behavior from an agent.
Although image reasoning models have come quite far, and have
a good bit of context, they still have a ways to go before they can
understand what a good policy loss curve looks like in
Hierarchical Policy Optimization, or what the perplexity of the
codebook should look like in a Vector Quantized Variational
Autoencoder, something I’ve been optimizing over the past week.
For this, we initialize any automated reasoning with a
preferences.md .
Let’s start with some general settings
# Experiment Preferences
This file defines my preferences for this experiment.
The agent should always read this first before taking any action.
---
## General Settings
- experiment_name: vqvae
- container_name: vqvae-train
- tensorboard_url: http://localhost:6006


---
*Page 19*


- memory_file: memory.md
- maximum_adjustments_per_run: 4
---
## More details
You can always add more sections here. The read_preferences task w
and reason over each section.
Now, let’s define metrics of interest. This is especially important
in the case of visual reasoning.
Within the markdown document, define yaml blocks which will
be parsed by the agent using the read_preferences tool. Adding
this bit of structure is helpful for using preferences as arguments
to other tools.
```yaml
metrics:
- name: perplexity
pattern: should remain high through the course of training
restart_condition: premature collapse to zero
hyperparameters: |
if collapse, increase `perplexity_weight` from current val
- name: prediction_loss
pattern: should decrease over the course of training
restart_condition: increases or stalls
hyperparameters: |
if increases, increase the `prediction_weight` value from
- name: codebook_usage
pattern: should remain fixed at > 90%
restart_condition: drops below 90% for many epochs
hyperparameters: |
decrease the `codebook_size` param from 512 to 256.
```


---
*Page 20*


The key idea is that the preferences.md should provide enough
structured and descriptive detail so the agent can:
Compare its analysis against your intent, e.g., if the agent sees
validation loss = 0.6 but preferences say val_loss_threshold should
be 0.5, it knows what the corrective action should be
Read the thresholds and constraints (YAML or key-value) for
metrics, hyperparameters, and container management.
Understand intent or intent patterns described in human-
readable sections, like “only adjust learning rate if validation loss
exceeds threshold and accuracy is stagnating.”
Wiring it all together
Now that we have a containerized experiment + an agent, we
need to schedule the agent. This is as simple as running the
agent process via a cron task. This runs our agent once every
hour, providing a tradeoff between cost (in tokens) vs. operational
efficiency.
0 * * * * /usr/bin/python3 /path/to/agent.py >> /var/log/agent.log
I’ve found that this agent doesn’t need the latest reasoning
model and performs fine with the previous generations from
Anthropic and OpenAI.
Wrapping up


---
*Page 21*


If research time is finite, it should be spent on research, not
babysitting experiments.
Your agent should handle monitoring, restarts, and parameter
adjustments without constant supervision. When the drag
disappears, what remains is the actual work: forming hypotheses,
designing better models, and testing ideas that matter.
Hopefully, this agent will free you up a bit to dream up the next
big idea. Enjoy.
References
Müller, T., Smith, J., & Li, K. (2023). LangChain: A framework for
developing applications with large language models. GitHub
repository. https://github.com/hwchase17/langchain
OpenAI. (2023). OpenAI API documentation.
https://platform.openai.com/docs
· · ·
WRITTEN BY
Sam Black
See all from Sam Black
Artificial Intelligence Deep Dives Deep Learning


---
*Page 22*


Experiment Management ML Engineering
Share This Article
Towards Data Science is a community publication. Submit your
insights to reach our global audience and earn through the TDS
Author Payment Program.
Write for TDS
Related Articles
MACHINE LEARNING AGENTIC AI
The Stanford Framework That LangGraph + SciPy: Building an
Turns AI into Your PM AI That Reads Documentation
Superpower and Makes Decisions
A human-centric guide to AI automation Stop guessing your statistical test. Let
for product managers. this AI do it for you.
Rahul Vir Gustavo Santos
July 28, 2025 6 min read August 11, 2025 11 min read


---
*Page 23*


AGENTIC AI MACHINE LEARNING
Smarter Model Tuning: An AI Using LangGraph and MCP
Agent with LangGraph + Servers to Create My Own Voice
Streamlit That Boosts ML Assistant
Performance
Built over 14 days, all locally run, no API
Automating model tuning in Python with keys, cloud services, or subscription
Gemini, LangGraph, and Streamlit for fees.
regression and classification
Benjamin Lee
improvements
September 4, 2025 30 min read
Gustavo Santos
August 20, 2025 12 min read
AGENTIC AI AGENTIC AI
Tool Masking: The Layer LangChain for EDA: Build a CSV
MCP Forgot Sanity-Check Agent in Python
Tool masking for AI improves AI agents: A practical LangChain tutorial for data
shape MCP tool surfaces to cut tokens scientists to inspect CSVs
and…
Sarah Schürch
Frank Wittkampf September 9, 2025 19 min read
September 5, 2025 16 min read


---
*Page 24*


AUTHOR SPOTLIGHTS
Generalists Can Also Dig Deep
Ida Silfverskiöld on AI agents, RAG, evals,
and what design choice ended up
mattering more…
TDS Editors
September 12, 2025 6 min read
Your home for data science and Al. The world’s leading publication for data science, data
analytics, data engineering, machine learning, and artificial intelligence professionals.
© Insight Media Group, LLC 2026
Subscribe to Our Newsletter
WRITE FOR TDS ABOUT ADVERTISE PRIVACY POLICY TERMS OF USE
• • • •