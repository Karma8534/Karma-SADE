# CaludeFreeModel

*Converted from: CaludeFreeModel.pdf*



---
*Page 1*


2/27/26, 11:59 AM I Didn’t Pay a Single Dollar to Use Claude Code — Here’s Exactly How | by Ayesha Mughal | Feb, 2026 | Artificial Intelligence in Pl…
Artificial Intelligence in Pla…
Open in app
Search Write
I Didn’t Pay a Single Dollar to Use
Claude Code — Here’s Exactly How
Ayesha Mughal Following 6 min read · 6 days ago
138 3
Everyone assumes Claude Code needs an Anthropic subscription.
https://medium.com/ai-in-plain-english/i-didnt-pay-a-single-dollar-to-use-claude-code-here-s-exactly-how-979b40132b02 1/15


---
*Page 2*


2/27/26, 11:59 AM I Didn’t Pay a Single Dollar to Use Claude Code — Here’s Exactly How | by Ayesha Mughal | Feb, 2026 | Artificial Intelligence in Pl…
It doesn’t.
I found this out after spending 20 minutes trying to justify the $20/month
plan to myself. Then I went down a rabbit hole, found the actual setup in the
Panaversity AI Agent Factory docs, and had it running free in under 10
minutes.
Here’s what nobody tells you upfront: Claude Code doesn’t care what model
is actually behind the API. It just talks to whatever URL you point it at. So if
you point it at a free model — Gemini, DeepSeek, or any of 30+ models on
OpenRouter — it works identically. Same Skills, same MCP servers, same
subagents, same everything.
Let me show you exactly how.
⚡
But First — Pick Your Weapon
You have 3 options. They’re not equal. Know before you choose:
OpenRouter Gemini DeepSeek Cost Free (daily limits) Free (daily limits)
~$0.028/M tokens Models 30+ (Qwen, Llama, Gemini) Gemini 2.5 Flash
DeepSeek Chat + Reasoner Best for Flexibility, experimenting Simplest setup
⚠
Consistent quality Gotcha Models rotate, quality varies Limits dropped
50–80% Dec 2025 Not truly free
⚠
The thing people don’t know: Google quietly slashed Gemini’s free tier in
December 2025 — daily request limits dropped 50–80% across most models.
It still works, but if you’re coding heavily, you’ll hit the wall. OpenRouter
gives you more breathing room because you can switch models when one
runs out.
https://medium.com/ai-in-plain-english/i-didnt-pay-a-single-dollar-to-use-claude-code-here-s-exactly-how-979b40132b02 2/15


---
*Page 3*


2/27/26, 11:59 AM I Didn’t Pay a Single Dollar to Use Claude Code — Here’s Exactly How | by Ayesha Mughal | Feb, 2026 | Artificial Intelligence in Pl…
I’ll walk through OpenRouter — it’s the most flexible and the one I actually
use daily. The Gemini and DeepSeek setups follow the exact same pattern,
just different config files.
🧱
What’s Actually Happening Under the Hood
Before we touch a terminal, understand the architecture. This will save you
from confusion later.
You → ccr code → Claude Code Router (local) → OpenRouter API → Free Model
Claude Code talks to a local router running on port 3456. The router
translates Claude’s requests into whatever format the backend model
expects. That’s it. No hacks, no jailbreaks — this is literally the documented
setup from Anthropic’s own ecosystem.
The tool is called claude-code-router (ccr). It's open source.
🛠
Setup: OpenRouter + Claude Code
Step 1: Get Your Free OpenRouter Key
1. Go to openrouter.ai/keys
2. Click “Create Key” — name it anything
3. Copy it (starts with sk-or-v1-...)
Free account gets you access to 30+ models with daily limits. No credit card
needed.
https://medium.com/ai-in-plain-english/i-didnt-pay-a-single-dollar-to-use-claude-code-here-s-exactly-how-979b40132b02 3/15


---
*Page 4*


2/27/26, 11:59 AM I Didn’t Pay a Single Dollar to Use Claude Code — Here’s Exactly How | by Ayesha Mughal | Feb, 2026 | Artificial Intelligence in Pl…
Step 2: Install Both Tools
npm install -g @anthropic-ai/claude-code @musistudio/claude-code-router
🧾
What just happened: You installed Claude Code (the agent) AND the
router (the translator). Both are needed. Without the router, Claude Code
tries to hit Anthropic’s paid API directly.
Verify they’re both there:
claude --version # Claude Code v2.x.x
ccr version # shows version number
Step 3: Create the Config File
Mac/Linux — paste this entire block:
mkdir -p ~/.claude-code-router ~/.claude
cat > ~/.claude-code-router/config.json << 'EOF'
{
"LOG": true,
"LOG_LEVEL": "info",
"HOST": "127.0.0.1",
"PORT": 3456,
"API_TIMEOUT_MS": 600000,
"Providers": [
{
https://medium.com/ai-in-plain-english/i-didnt-pay-a-single-dollar-to-use-claude-code-here-s-exactly-how-979b40132b02 4/15


---
*Page 5*


2/27/26, 11:59 AM I Didn’t Pay a Single Dollar to Use Claude Code — Here’s Exactly How | by Ayesha Mughal | Feb, 2026 | Artificial Intelligence in Pl…
"name": "openrouter",
"api_base_url": "https://openrouter.ai/api/v1",
"api_key": "$OPENROUTER_API_KEY",
"models": [
"qwen/qwen-coder-32b-vision",
"google/gemini-2.0-flash-exp:free",
"meta-llama/llama-3.3-70b-instruct:free",
"qwen/qwen3-14b:free"
],
"transformer": {
"use": ["openrouter"]
}
}
],
"Router": {
"default": "openrouter,qwen/qwen-coder-32b-vision",
"background": "openrouter,qwen/qwen-coder-32b-vision",
"think": "openrouter,meta-llama/llama-3.3-70b-instruct:free",
"longContext": "openrouter,qwen/qwen-coder-32b-vision",
"longContextThreshold": 60000
}
}
EOF
Windows — open Notepad and save the same JSON to:
%USERPROFILE%\.claude-code-router\config.json
🧾
What just happened: You told the router which models to use and for
what purpose. default is your everyday coding model, think is for complex
reasoning tasks, longContext handles big files. The router switches between
them automatically — you never think about it.
🚨
Do NOT replace $OPENROUTER_API_KEY in the config file. Leave it exactly as
$OPENROUTER_API_KEY. The router reads it from your environment variable
(next step). If you paste your key directly into the file, it won't work and
you'll spend 30 minutes confused.
Step 4: Set Your API Key Permanently
https://medium.com/ai-in-plain-english/i-didnt-pay-a-single-dollar-to-use-claude-code-here-s-exactly-how-979b40132b02 5/15


---
*Page 6*


2/27/26, 11:59 AM I Didn’t Pay a Single Dollar to Use Claude Code — Here’s Exactly How | by Ayesha Mughal | Feb, 2026 | Artificial Intelligence in Pl…
Mac (zsh):
echo 'export OPENROUTER_API_KEY="YOUR_KEY_HERE"' >> ~/.zshrc
source ~/.zshrc
Mac (bash):
echo 'export OPENROUTER_API_KEY="YOUR_KEY_HERE"' >> ~/.bashrc
source ~/.bashrc
Windows (PowerShell — run as Administrator):
[System.Environment]::SetEnvironmentVariable('OPENROUTER_API_KEY', 'YOUR_KEY_HERE',
 
Then close ALL PowerShell windows and open a fresh one.
Verify it worked:
echo $OPENROUTER_API_KEY # Should print your key
https://medium.com/ai-in-plain-english/i-didnt-pay-a-single-dollar-to-use-claude-code-here-s-exactly-how-979b40132b02 6/15


---
*Page 7*


2/27/26, 11:59 AM I Didn’t Pay a Single Dollar to Use Claude Code — Here’s Exactly How | by Ayesha Mughal | Feb, 2026 | Artificial Intelligence in Pl…
🧾
What just happened: You stored the key in your shell so it loads
automatically every session. Without this, you’d need to export it manually
every time you open a terminal — which everyone forgets and then wonders
why nothing works.
Step 5: The Daily Workflow (Two Terminals)
This is the part that trips people up. You need two terminals.
Terminal 1 — Start the router:
ccr start
Wait until you see ✅ Service started successfully. Leave this window
open.
Terminal 2 — Start coding:
cd your-project-folder
ccr code
🧾
Why two terminals? The router is a local server that has to keep running.
ccr code is Claude Code pointed at that server. If you kill Terminal 1, your
coding session dies. Think of Terminal 1 as the engine and Terminal 2 as the
driver's seat.
https://medium.com/ai-in-plain-english/i-didnt-pay-a-single-dollar-to-use-claude-code-here-s-exactly-how-979b40132b02 7/15


---
*Page 8*


2/27/26, 11:59 AM I Didn’t Pay a Single Dollar to Use Claude Code — Here’s Exactly How | by Ayesha Mughal | Feb, 2026 | Artificial Intelligence in Pl…
⏳
First startup takes 10–20 seconds. Don’t panic if ccr code seems stuck.
The router is initializing. Just wait.
✅
Verify It’s Working
Once you’re in Claude Code, type:
hi
If it responds, you’re live. For a deeper check:
Explain what files are in this directory and what this project does
Claude should read your actual files and respond. If it does — you have a
fully working agentic coding environment running on free models.
🔄
What If I Want Gemini or DeepSeek Instead?
Same exact steps. Just swap the config file content.
For Gemini, get your key from aistudio.google.com/api-keys and use:
"Providers": [{
"name": "gemini",
"api_base_url": "https://generativelanguage.googleapis.com/v1beta/models/",
"api_key": "$GOOGLE_API_KEY",
"models": ["gemini-2.5-flash-lite", "gemini-2.0-flash"],
https://medium.com/ai-in-plain-english/i-didnt-pay-a-single-dollar-to-use-claude-code-here-s-exactly-how-979b40132b02 8/15


---
*Page 9*


2/27/26, 11:59 AM I Didn’t Pay a Single Dollar to Use Claude Code — Here’s Exactly How | by Ayesha Mughal | Feb, 2026 | Artificial Intelligence in Pl…
"transformer": { "use": ["gemini"] }
}]
Environment variable: GOOGLE_API_KEY
For DeepSeek, get your key from platform.deepseek.com and use:
"Providers": [{
"name": "deepseek",
"api_base_url": "https://api.deepseek.com/v1",
"api_key": "$DEEPSEEK_API_KEY",
"models": ["deepseek-chat", "deepseek-reasoner"],
"transformer": { "use": ["openai"] }
}]
Environment variable: DEEPSEEK_API_KEY
🚨
Troubleshooting (The Errors You Will Actually Hit)
“command not found: ccr” The npm global bin directory isn’t in your PATH.
Run:
npm config get prefix
# Add the output + /bin to your PATH in ~/.zshrc or ~/.bashrc
Router starts but Claude hangs You ran ccr code before ccr start finished.
Kill both, restart Terminal 1 first, wait for the success message, then
Terminal 2.
https://medium.com/ai-in-plain-english/i-didnt-pay-a-single-dollar-to-use-claude-code-here-s-exactly-how-979b40132b02 9/15


---
*Page 10*


2/27/26, 11:59 AM I Didn’t Pay a Single Dollar to Use Claude Code — Here’s Exactly How | by Ayesha Mughal | Feb, 2026 | Artificial Intelligence in Pl…
“API key not found” You set the variable in one terminal session and it didn’t
persist. Add the export to your ~/.zshrc or ~/.bashrc as shown in Step 4 and
source it.
Hitting rate limits mid-session Switch your default model in the config to a
different free model on OpenRouter. You have 30+ options — rotate through
them.
💡
The Honest Take
Does free mean same quality as Claude Sonnet or Opus? No. For complex
multi-step reasoning, the paid Claude models are better.
But here’s what I’ve found: for most real development work ,reading
codebases, generating boilerplate, explaining errors, writing tests ,the free
models on OpenRouter are genuinely good enough. Qwen-Coder-32B in
particular is surprisingly strong for code tasks.
The people paying $20/month for Claude Pro to use Claude Code are mostly
paying for convenience and peak performance. If you’re learning,
experimenting, or building side projects — free gets you 90% of the way
there.
Start free. Upgrade when you actually hit the ceiling.
📌
Quick Summary
What How Install both tools npm install -g @anthropic-ai/claude-code
@musistudio/claude-code-router Config location ~/.claude-code-
router/config.json Set API key Export in ~/.zshrc or ~/.bashrc Start router
https://medium.com/ai-in-plain-english/i-didnt-pay-a-single-dollar-to-use-claude-code-here-s-exactly-how-979b40132b02 10/15


---
*Page 11*


2/27/26, 11:59 AM I Didn’t Pay a Single Dollar to Use Claude Code — Here’s Exactly How | by Ayesha Mughal | Feb, 2026 | Artificial Intelligence in Pl…
ccr start (Terminal 1) Start coding ccr code (Terminal 2) Best free option
OpenRouter — most models, most flexibility
This setup is based on the official free setup guide from the AI Agent Factory by
Panaversity — the same curriculum used across AI agent hackathons. All Claude
Code features (Skills, MCP servers, subagents, hooks) work identically on free
backends.
Next up: What is a SKILL.md file and how does Claude Code actually use it?
Claude Code Artificial Intelligence Programming Developer Tools LLM
Published in Artificial Intelligence in Plain English
Follow
39K followers · Last published 17 hours ago
New AI, ML and Data Science articles every day. Follow to join our 3.5M+ monthly
readers.
Written by Ayesha Mughal
Following
18 followers · 3 following
Coding with a Spark of ChaosIT student 💡 | Code lover 💻 | Tea addict ☕|
Dreaming in dark mode 🌒Building logic, chasing stars ✨ — one line of code at
a time.
Responses (3)
https://medium.com/ai-in-plain-english/i-didnt-pay-a-single-dollar-to-use-claude-code-here-s-exactly-how-979b40132b02 11/15


---
*Page 12*


2/27/26, 11:59 AM I Didn’t Pay a Single Dollar to Use Claude Code — Here’s Exactly How | by Ayesha Mughal | Feb, 2026 | Artificial Intelligence in Pl…
Rae Steele
What are your thoughts?
KASHIF JILANI
16 mins ago
Amazing will definitely give a try. Thanks for sharing.
Reply
Swalk
5 hours ago
Nice
1 reply Reply
NTTP
2 days ago
Brilliant!
1 reply Reply
More from Ayesha Mughal and Artificial Intelligence in Plain
English
https://medium.com/ai-in-plain-english/i-didnt-pay-a-single-dollar-to-use-claude-code-here-s-exactly-how-979b40132b02 12/15


---
*Page 13*


2/27/26, 11:59 AM I Didn’t Pay a Single Dollar to Use Claude Code — Here’s Exactly How | by Ayesha Mughal | Feb, 2026 | Artificial Intelligence in Pl…
InArtificial Intelligence in Plain E… by Ayesha Mu… InArtificial Intelligence in Plain En… by Claudio L…
Claude Code Has a Secret Weapon DeepSeek V4 Is Coming — And
Most Developers Never Use Your AI Strategy Might Be Obsolet…
You set up Claude Code. You’re running it on The Chinese AI lab that crashed $600 billion
free Gemini or OpenRouter. off NVIDIA’s market cap is about to drop a…
2d ago 9 Jan 19 1K 24
InArtificial Intelligence in Plain Englishby Shashwat InArtificial Intelligence in Plain E… by Ayesha Mu…
Is Antigravity Dead Already? The Unlocking AI Potential: Exploring 3
Day the Free Lunch Ended Essential Prompting Techniques f…
Google just patched the infinite money Claude In the rapidly evolving world of artificial
glitch. Here is what 0.00% quota looks like. intelligence, large language models (LLMs)…
Jan 29 531 28 Oct 16, 2025
See all from Ayesha Mughal See all from Artificial Intelligence in Plain English
https://medium.com/ai-in-plain-english/i-didnt-pay-a-single-dollar-to-use-claude-code-here-s-exactly-how-979b40132b02 13/15


---
*Page 14*


2/27/26, 11:59 AM I Didn’t Pay a Single Dollar to Use Claude Code — Here’s Exactly How | by Ayesha Mughal | Feb, 2026 | Artificial Intelligence in Pl…
Recommended from Medium
Agent Native InGitBitby John Gruber
OpenClaw Memory Systems That Websites Are Dead. Go Here
Don’t Forget: QMD, Mem0, Cogne… Instead.
If your agent has ever randomly ignored a I finally did it. I launched a blog. Then I realized
decision you know you told it… it’s not random. the hard truth.
6d ago 89 1 Feb 10 5K 204
InActivated Thinker by Shane Collins InInvestor’s Handbook by Sanjeev P.
The $830 Billion Wake-Up Call: How A New Financial Era Has Begun —
Claude Just “Murdered” the Old… 5 Years to Position Yourself
In one week, Anthropic didn’t just release an The Strategic Moves Smart Earners are
update — they dismantled the three pillars of… Making Now
https://medium.com/ai-in-plain-english/i-didnt-pay-a-single-dollar-to-use-claude-code-here-s-exactly-how-979b40132b02 14/15


---
*Page 15*


2/27/26, 11:59 AM I Didn’t Pay a Single Dollar to Use Claude Code — Here’s Exactly How | by Ayesha Mughal | Feb, 2026 | Artificial Intelligence in Pl…
Feb 17 2K 74 Feb 17 1.2K 56
InLevel Up Coding by Pushkar Singh Can Artuc
6 Commands That Quietly Changed 10 Billion Devices Run His Code. He
How I Use Git Maintains It Alone. Now AI is…
The commands that quietly improved my One Swedish developer keeps curl running on
debugging process, commit discipline, and… every phone, car, and console on Earth. 47 ca…
Feb 15 481 3 Feb 17 6.6K 55
See more recommendations
https://medium.com/ai-in-plain-english/i-didnt-pay-a-single-dollar-to-use-claude-code-here-s-exactly-how-979b40132b02 15/15