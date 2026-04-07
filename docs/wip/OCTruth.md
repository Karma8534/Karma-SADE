# OCTruth

*Converted from: OCTruth.PDF*



---
*Page 1*


Open in app
Search Write
Member-only story
I Tried Running
Openclaw (ex
Clawdbot) with a Free
LLM. Here’s What
Happened.
“Run your own AI assistant locally! No API
costs! Privacy! Freedom!”
Phil | Rentier Digital 3 min · Jan 25,
Following
Automation read 2026
291 15
Sounds great. I have a headless server. I have
Ollama. I have dreams.


---
*Page 2*


Here’s how reality crushed them — and how I
eventually won.
⚡
Update (Feb 20, 2026): The free LLM landscape
moved fast since January. Three things changed:
1. Anthropic banned Claude Max tokens in
OpenClaw. If you were running on your Max
subscription, that’s over. I rebuilt mine for
$15/month using Kimi K2.5 + MiniMax M2.5
fallback.
2. New models entered the ring. Qwen 3.5
(Alibaba) — native agentic capabilities, $0.40/M
input tokens. DeepSeek V3.2 “Speciale” — 88.7% on
LiveCodeBench, MIT license, $0.28/M input. Both
OpenRouter-compatible, plug straight into
OpenClaw.
3. NVIDIA published an official guide for running
OpenClaw locally on RTX GPUs with Ollama. If you
have an RTX card, LM Studio + 7B model = truly $0.


---
*Page 3*


My current pick: Kimi K2.5 via OpenRouter for
near-Claude quality at pennies. Ollama + Qwen 3.5
locally for $0.
Act 1: The Config Wilderness
The official docs said:
{
"api": "openai"
}
My server said:


---
*Page 4*


Invalid input
Turns out the actual magic words are:
{
"api": "openai-completions"
}
One hyphen. Three hours of my life.
Act 2: The Model That Could(n’t)
First attempt: qwen2.5:7b — a respectable 7 billion
parameters.
Time to respond to “Say OK”: 7 minutes.
My mass-produced Chinese rice cooker has better
inference speed.


---
*Page 5*


Act 3: The Context Window Betrayal
“Fine,” I said. “I’ll use TinyLlama. It’s tiny. It’s a
llama. What could go wrong?”
FailoverError: Model context window too small (2048 t
Clawdbot requires a PhD-level attention span.
TinyLlama has the memory of a goldfish.
Act 4: The Goldilocks Model
Finally: qwen2.5:1.5b
Size: 986 MB (not too big)
Context: 32k tokens (not too small)
Speed: Actually responds before my coffee gets
cold
Quality: Hallucinates a bit, but who doesn’t?


---
*Page 6*


The Working Config
{
"models": {
"mode": "merge",
"providers": {
"ollama": {
"baseUrl": "http://127.0.0.1:11434/v1",
"apiKey": "ollama-local",
"api": "openai-completions",
"models": [{
"id": "qwen2.5:1.5b",
"name": "Qwen 2.5 1.5B",
"reasoning": false,
"input": ["text"],
"contextWindow": 32768,
"maxTokens": 8192,
"cost": { "input": 0, "output": 0, "cacheRe
}]
}
}
},
"agents": {
"defaults": {
"model": { "primary": "ollama/qwen2.5:1.5b" }
}
}
}


---
*Page 7*


Save to: ~/.clawdbot/clawdbot.json AND
~/.clawdbot/agents/main/agent/models.json
Yes, both. Don’t ask.
The Commands That Actually Work
# Install the model
ollama pull qwen2.5:1.5b
# Test directly (bypass gateway complexity)
clawdbot agent --agent main --local --message
"Hello"
# Or with gateway
clawdbot gateway &
clawdbot agent --agent main --message "Hello"
# Interactive TUI
clawdbot tui
The Honest Truth
What they promised vs. what you get:


---
*Page 8*


“Free AI” → Free if your time is worthless
“Local privacy” → Actually true ✓
“Fast responses” → Depends on your definition
of “fast”
“Easy setup” → api: "openai-completions" (not
"openai")
Should You Do This?
Yes, if:
You have a GPU (even a modest one)
You enjoy debugging configs at 2 AM
You value privacy over speed
You find corporate AI pricing offensive
No, if:
You have a CPU-only potato server
You expect ChatGPT-level responses


---
*Page 9*


You value your sanity
The Real Minimum Specs
RAM: 8 GB minimum, 16 GB recommended
Model: qwen2.5:1.5b minimum, qwen2.5:7b +
GPU recommended
Context window: 16k+ required
Patience: Infinite
Need a VPS That Can Actually Handle
This?
If you’re tired of running AI on a potato, a proper
VPS makes all the difference. I recommend
starting with at least 8GB RAM and some decent
CPU cores.
👉
Get a VPS with extra bonus here


---
*Page 10*


Written by someone who mass-retry’d configs until
something worked. You’re welcome.
Local Llm Free Llm Local Ai Clawd Bot
Written by Phil | Rentier Digital
Following
Automation
1.5K followers · 1 following
Claude Code in production. What works, what
breaks, what ships.
Responses (15)
To respond to this story,
get the free Medium app.
Alex E he/him
Feb 2 (edited)


---
*Page 11*


I tried this with OpenClaw, Ollama and UTM on a MacMini running a lot of
other stuff (postgresql, n8n, Sim, mongo) and it ran, just.
However, switching to Ollama cloud sorted this out. Looking for speed, I
tried Ministral 3-3b, way too thick. GTP… more
108 1 reply
David Watkin
Feb 1
Normally I would leave this alone but I just can’t.
No one promised you anything. The docs explicitly state that trying it with
a local model is probably not going to go well unless you want to throw a
huge pile of money at getting a beefy enough… more
17 2 replies
Tac Tacelosky
Feb 4
thanks for making this humorous!
54
See all responses
More from Phil | Rentier Digital Automation


---
*Page 12*


Phil | Rentier Digital Automation Phil | Rentier Digital Automation
33 OpenClaw Y Combinator Just Told
A t ti Y C Y E tl H t
While you were reading this Your agency is about to
titl ’ l b t b ft
Feb 1 Feb 5
Phil | Rentier Digital Automation Phil | Rentier Digital Automation
Why CLIs Beat MCP for I Gave Claude Code a
AI A t A d H M d N It
“mcp were a mistake. bash is Claude Code has the memory
b tt ” f d d b t
Feb 17 Jan 15
See all from Phil | Rentier Digital Automation


---
*Page 13*


Recommended from Medium
In by In by
CodeX MayhemCode AI Advanc… Jose Crespo, P…
Why Thousands Are Anthropic is Killing
B i M Mi i t Bit i
Something strange happened The AI-native currency
i l 2026 A l t l d i t hidi i
Feb 15 Feb 17


---
*Page 14*


Max Petrusenko In by
Activated Thin… Shane Coll…
OpenClaw: I Let This AI
Stop Watching
C t l M M f 3
O Cl I t ll
Everyone can run npm install.
O l f k h t t
Jan 30 Feb 1
In by In by
Towards Deep L… Sumit Pa… Predict Nov Tech
Andrej Karpathy Just I’m Skeptical of AI hype
B ilt E ti GPT i b t h t h d
No PyTorch. No TensorFlow. When Anthropic, Google
J t P th d b i D Mi d d O AI ll
Feb 15 Feb 2
See more recommendations