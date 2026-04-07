# MoltOnLocal

*Converted from: MoltOnLocal.PDF*



---
*Page 1*


Open in app
Search Write
Level Up Coding
Member-only story
Moltbot (Clawdbot->) +
Ollama: How I Built a
Private AI That Costs
🔒
Nothing
Your code stays on your machine. Your
conversations stay private. Your wallet stays
full.
ZIRU Follow 10 min read · Jan 27, 2026
158 5


---
*Page 2*


https://clawd.bot/
Y ou know that moment when you paste
company code into ChatGPT, and a tiny voice
in your head whispers, “Should I be doing this?”
I ignored that voice for months. Then my manager
forwarded an email from legal about “AI tool usage
policies.” Suddenly, that tiny voice got very loud.
Here’s what nobody tells you about cloud AI
services. Every message you send travels to
someone else’s servers. Every code snippet. Every


---
*Page 3*


private conversation. Every embarrassing question
you were too shy to ask your coworkers.
For personal stuff? Fine. But for work code, private
projects, or anything you don’t want a third party
seeing? That’s a different story.
So I built my own private AI using two open-source
tools. Two hours of setup. Zero dollars per month.
And honestly? It’s better than I expected.
This is the complete story of how I did it — every
mistake, every fix, every “aha” moment included.
The Two Tools That Changed Everything
My private AI runs on two open-source projects
that work perfectly together.
Ollama is the engine. It runs AI models directly on
your computer. No cloud. No API calls. No data
leaving your machine. Think of it as “Docker for AI


---
*Page 4*


models” — you pull a model, run it locally, done.
The community has made it incredibly easy to use.
Clawdbot is the interface. It’s an open-source
gateway that connects Ollama to the apps you
actually use — Slack, web browsers, command
line, even Discord. Without Clawdbot, you’d be
stuck typing into a terminal window. With it, you
can chat with your AI from anywhere.
Together, they create this architecture:
Slack/Web/CLI → Clawdbot Gateway → Ollama → AI Mode
↑ ↑
Your apps Your computer
(Nothing ever leaves)
The magic is in that last line. Nothing ever leaves.
Your questions, your code, your private thoughts —
they never touch the internet. They never hit
someone else’s server. They stay exactly where you
put them.


---
*Page 5*


Why I Chose This Over Cloud AI
Let me be honest. ChatGPT and Claude are
amazing. I still use them for personal stuff. They’re
faster to set up and have cutting-edge models.
But here’s my cost math:
Cloud AI costs (my actual spending):
ChatGPT Plus: $20/month
Claude Pro: $20/month
Occasional API usage: $30–50/month
That’s roughly $70–90 per month. Over $800 per
year.
My Clawdbot + Ollama setup:
One-time hardware: Already had a GPU
Electricity: ~$10–15/month for 24/7 operation
Software: $0 (open source)


---
*Page 6*


API costs: $0 forever
Break-even time: About 2 months.
But here’s the thing — money isn’t the real reason I
switched.
The real reason: I needed to ask about work code
without worrying.
Every time I used cloud AI for work, questions
haunted me. Where does this data go? Who can see
it? Is it being used to train future models? Am I
violating company policy? Could this code end up
in someone else’s autocomplete?
With my local setup, I know exactly where
everything goes. Nowhere. It processes on my
machine and stays on my machine. Period.
That peace of mind changed how I use AI
completely.


---
*Page 7*


The Hardware Question (It’s Not What You
Think)
Before we dive into setup, let’s talk hardware. This
is where most people get scared off.
You don’t need a supercomputer.
Here’s what actually works:
I have dual RTX 4090s (48GB total), which is
overkill. But I started testing on an older RTX 3080,
and it worked fine with smaller models.
The honest truth: If you have any gaming GPU
from the last 3–4 years, you can run local AI. It
might be slower than cloud, but it works.


---
*Page 8*


My Setup Journey (The Honest Version)
I wish I could say this was easy. The first attempt
wasn’t. But the mistakes taught me what actually
matters.
Step 1: Installing Ollama (Easy Part)
This part was actually simple:
curl -fsSL https://ollama.ai/install.sh | sh
Then I pulled my first model:
ollama pull qwen3:30b-a3b
Why this specific model? I’ll explain later. For now,
just know it took about 10 minutes to download
18GB.


---
*Page 9*


Quick test:
ollama run qwen3:30b-a3b "What is 2+2?"
It responded “4” in about 2 seconds. Ollama was
working. So far so good.
Step 2: Installing Clawdbot (Also Easy)
npm install -g clawdbot@latest
clawdbot onboard
```
The onboarding wizard asked me questions about which
Everything looked fine. Then came my first real probl
---
## Mistake #1: The Context Window Trap
I configured my model with an 8,192 token context win
Clawdbot refused to start.
```
Error: Model context window too small (8192 tokens).
Minimum is 16000.


---
*Page 10*


I spent an embarrassing hour confused. Why
would Clawdbot need such a large context
window? Was my model broken?
Then I actually checked my model’s real
capabilities:
curl -s http://127.0.0.1:11434/api/show \
-d '{"name":"qwen3:30b-a3b"}'
The result shocked me:
Qwen3 30B → 262,144 tokens
Llama 3.3 70B → 131,072 tokens
DeepSeek Coder → 163,840 tokens
I was limiting my model to 3% of its actual
capability. For no reason. Just because I assumed
cloud defaults applied locally.
The fix was simple. I updated my config to match
reality:


---
*Page 11*


{
"models": {
"providers": {
"ollama": {
"baseUrl": "http://127.0.0.1:11434/v1",
"apiKey": "ollama-local",
"models": [
{
"id": "qwen3:30b-a3b",
"contextWindow": 262144,
"maxTokens": 32768
}
]
}
}
}
}
Lesson learned: Never assume. Local models are
often MORE capable than their cloud counterparts
in terms of context window. Always check the
actual specs.
Mistake #2: Slack’s Silent Failure Mode


---
*Page 12*


With Clawdbot running, I connected it to Slack.
Created the app. Added the tokens. The bot
appeared online with a green dot.
I sent it a message: “Hello, are you there?”
Nothing happened.
No error message. No response. No indication
anything was wrong. Just silence.
I checked Clawdbot’s logs. No errors. I checked
Slack’s app dashboard. Everything looked
connected. I restarted everything multiple times.
After an hour of increasingly frustrated debugging,
I found the problem buried in a log file. I had
forgotten one Slack permission: groups:read.
Without it, the bot couldn’t see messages in private
channels. And my test channel was private.
The cruel part? Slack doesn’t tell you. It doesn’t
show an error. It doesn’t warn you. It just silently


---
*Page 13*


ignores messages the bot can’t see.
Here are ALL the permissions you actually need:
PermissionWhy You Need Itapp_mentions:readSee
when people @mention the botchat:writeSend
responses backim:read + im:writeHandle direct
messagesgroups:read + groups:historySee private
channelschannels:read + channels:historySee
public channels
Miss any single one of these, and your bot fails
with zero warning. I learned this the hard way so
you don’t have to.
Lesson learned: Add every permission upfront.
Debugging silent failures will steal hours of your
life.
Why I Chose a “Weird” Model
Here’s where I made a good decision for once.


---
*Page 14*


Most guides say “pick the biggest model that fits
your GPU.” Makes sense, right? Bigger model =
better responses.
I did the opposite. I picked Qwen3 30B-A3B instead
of a 70B model.
The “A3B” part is the secret. This model uses
“Mixture of Experts” (MoE) architecture. It has 30
billion parameters total, but only activates 3 billion
for any given response.
Think of it like a hospital with 30 specialists. When
you have a heart problem, you don’t need all 30
doctors in the room. You need the cardiologist.
Maybe a nurse. MoE models work the same way —
they route your question to the right “expert”
parameters.
Here’s the real-world difference:
MetricLlama 70BQwen3 30B MoEResponse time5–
10 seconds1–3 secondsVRAM needed40GB+15–


---
*Page 15*


20GBQualityExcellentNearly as goodFits on single
4090?BarelyEasily
For a chat bot, speed matters more than marginal
quality improvements. Nobody wants to wait 10
seconds for a Slack reply. The 70B model gives
slightly better answers, but the MoE model gives
good-enough answers three times faster.
I tested both for a week. The MoE model won
easily for my use case.
What My Private AI Actually Does Now
After two weeks of daily use, here’s how my
Clawdbot setup fits into my workflow:
Code reviews without paranoia. I paste entire files
and ask “What could go wrong here?” or “Can you
spot any bugs?” The code never leaves my network.
I don’t have to sanitize anything or worry about
proprietary logic leaking.


---
*Page 16*


Quick technical questions. Instead of opening a
browser and context-switching to Google, I ask my
AI. “What’s the difference between useEffect and
useLayoutEffect?” It answers in seconds and
remembers what we discussed earlier in the
conversation.
Writing assistance. Documentation, commit
messages, PR descriptions, technical emails — my
AI drafts them, I edit. It’s not perfect, but it’s faster
than starting from scratch.
Rubber duck debugging. Sometimes I just explain
my problem to the AI. Half the time, I figure out
the answer while typing. The other half, it points
me in the right direction.
Bilingual support. I work in both Korean and
English. The Qwen model handles both seamlessly.
안녕 오늘 날씨 어때
I tested: “ , ?” Response came
back in natural Korean within 2 seconds.


---
*Page 17*


The psychological difference: I never think about
costs anymore. There’s no meter running. No “am I
using too many tokens?” anxiety. No monthly bill
creeping up. I ask whatever I want, whenever I
want.
The Web Dashboard (Hidden Gem)
One thing I didn’t expect: Clawdbot has a
surprisingly good web interface.
Access it through an SSH tunnel:
ssh -L 18789:127.0.0.1:18789 your-server
Then open http://localhost:18789 in your browser.
You get a full chat interface, conversation history,
configuration editor, real-time logs, and health
monitoring. It’s easier than the command line for
most tasks.


---
*Page 18*


I use the web dashboard more than Slack now,
honestly.
The Quick Start Guide
Want to build your own? Here’s the fastest path:
Step 1: Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull qwen3:30b-a3b
Step 2: Install Clawdbot
npm install -g clawdbot@latest
clawdbot onboard
Step 3: Test it
clawdbot agent --local --message "Hello, what's 2+2?"


---
*Page 19*


If it responds “4”, you have a working private AI.
The whole process takes about 30 minutes.
Everything else — Slack integration, web
dashboard, systemd services — is optional polish.
The core works immediately.
Should You Build This?
Be honest with yourself about these questions:
Build your own private AI if:
You regularly work with sensitive or proprietary
code
You’re tired of monthly AI subscriptions adding
up
You have a decent GPU (RTX 3080 or better, or
Apple Silicon)
You enjoy tinkering with self-hosted tools


---
*Page 20*


Privacy genuinely matters to your work
Stick with cloud AI if:
You need the absolute cutting-edge models (GPT-
4o, Claude Opus)
Two hours of setup time isn’t worth the long-
term savings
You don’t have suitable hardware and don’t want
to buy any
Your use case is casual and privacy isn’t a
concern
For me, the privacy alone justified the effort. The
cost savings are a nice bonus. The speed is
surprisingly competitive.
What I’d Do Differently Next Time
If I started this project over today, here’s what I’d
change:


---
*Page 21*


Check model specs before configuring. The
context window error wasted an hour because I
assumed instead of verified. Five minutes of
research would have saved sixty minutes of
debugging.
Add all Slack permissions from the start. Silent
failures are the worst kind of bug. Just add every
recommended permission upfront and avoid the
headache.
Start with the MoE model immediately. I tested the
70B model first because “bigger is better” felt
intuitively right. Wrong. For chat applications,
response speed matters more than marginal
quality gains.
Use the web dashboard from day one. I spent too
long fighting with command-line tools when a
perfectly good GUI was sitting there waiting.
Set up systemd service earlier. Having Clawdbot
auto-start on boot saves the hassle of remembering


---
*Page 22*


to start it manually.
One More Thing: The Model That Actually Works
for Everything
Before I settled on my current setup, I tested over
20 different models. I wasn’t just checking if they
could answer questions. I had three strict
requirements: tool-calling (can it use functions
like searching or calculations?), Korean language
(does it respond in Korean when asked in Korean?),
and accuracy (are the answers actually correct?).
Most models failed at least one test. Some big
names surprised me with how badly they
performed.
Here’s what I found:


---
*Page 23*


The pattern was frustrating. Some models handled
tool-calls perfectly but refused to respond in
Korean. Others spoke Korean beautifully but gave
completely wrong answers. Granite4 was the most
annoying — it did everything right except the
answers were nonsense.
After weeks of testing, only one model passed every
single test: GLM-4 9B Flash. It handled Korean,
English, Chinese, and mixed-language conversations
without breaking a sweat. Tool-calls worked perfectly.
Answers were accurate.


---
*Page 24*


If you need a truly multilingual private AI that
actually works, this is the one. Pull it with ollama
pull glm4:9b and thank me later.
The Real Reason I Built This
Here’s what I realized after everything was
working.
The technology isn’t the hard part. Ollama and
Clawdbot made the technical setup surprisingly
straightforward. The documentation is good. The
communities are helpful.
The hard part was deciding that privacy and
control matter enough to spend a couple hours on
setup.
Most developers paste code into cloud AI tools
without a second thought. That’s fine — until your
company asks “where does that code go?” Until
legal sends around a policy update. Until you


---
*Page 25*


realize you’ve been sharing proprietary algorithms
with servers you don’t control.
Building a private AI isn’t about paranoia. It’s about
having a clear, simple answer: “It never left my
machine.”
When someone asks where my AI conversations
go, I don’t have to read terms of service or privacy
policies. I don’t have to hope a company keeps its
promises. I just point at my server and say “there.”
That clarity is worth more than the $800 per year
I’m saving.
Machine Learning Clawdbot AI AGI Moltbot
Published in Level Up Coding
Follow
304K followers · Last published 2 days ago


---
*Page 26*


Coding tutorials and news. The developer homepage
gitconnected.com && skilled.dev && levelup.dev
Written by ZIRU
Follow
2.6K followers · 176 following
Lead Principal Data Scientist | Saab Inc. | Depence AI
Specialist | San Diego | UCSD |
https://www.linkedin.com/in/jhbaek/
Responses (5)
To respond to this story,
get the free Medium app.
See all responses
More from ZIRU and Level Up Coding


---
*Page 27*


In by In by
Level Up Coding ZIRU Level Up Codi… Pushkar Sin…
Why I Stopped Paying 6 Commands That
API Bill d S d 3 Q i tl Ch d H
I used to think paying for API The commands that quietly
d “ l” i d d b i
Jan 30 Feb 15
In by In by
Level Up C… Dr. Ashish B… Level Up Coding ZIRU
Learn About The Entire How to Build Software
C t S i Th t A t ll W k
A visual tour through the A practical workflow that
ti C t S i t d h ti d
Jan 29 Nov 5, 2025
See all from ZIRU See all from Level Up Coding


---
*Page 28*


Recommended from Medium
In by Reza Rezvani
GitBit John Gruber
OpenClaw Security: My
Websites Are Dead. Go
C l t H d i
H I t d
A practical guide to securing
I finally did it. I launched a
AI i t t f fi t
bl Th I li d th h d
Feb 10 Feb 2


---
*Page 29*


ZIRU Phil | Rentier Digital Automation
How I Set Up OpenClaw Why CLIs Beat MCP for
M M Mi i M4 AI A t A d H
Everything I learned after “mcp were a mistake. bash is
k f t i d b i b tt ”
Feb 16 Feb 17
Mubashir Rahim Can Artuc
The RTX 5080 Is 3x 10 Billion Devices Run
F t Th NVIDIA’ Hi C d H M i t i
I benchmarked the DGX Spark One Swedish developer keeps
i t GPU Th l i h
Feb 16 Feb 17
See more recommendations