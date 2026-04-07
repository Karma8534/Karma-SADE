# pub.towardsai

*Converted from: pub.towardsai.PDF*



---
*Page 1*


Open in app
Search Write
Pub Crawl is coming back, March 11–12! Register Now!
Towards AI
Member-only story
OpenClaw + Ollama +
Security Guide: The
ULTIMATE LOCAL AI
Assistant Agent has
ARRIVED!
⾼達烈
Gao Dalie ( ) Follow 16 min read · 3 days ago
193 1


---
*Page 2*


At the end of 2025, an open source project
suddenly appeared, gathering stars at the fastest
pace in GitHub history. Its name was Clawdbot. It
was not just an AI that could chat, but an AI agent
that could actually operate a computer and
complete tasks, shocking the tech world.
But the road has been anything but smooth: in just
two months, the company has faced a dramatic
turn of events, including three name changes, a
cryptocurrency scam, serious security issues, and
a trademark dispute with Anthropic.


---
*Page 3*


In this “Year of AI,” great tools like ChatGPT,
Claude, and Gemini are appearing one after
another. However, as you use them every day, do
you ever feel like something is missing?
“They write great sentences, but they never click
the send button on the email.” “They write the
code, but when an error occurs, you have to debug
it yourself.” “When I close the browser tab, all the
conversation and context from that moment is
reset.”
Yes, existing AI is merely an “advisor in your
browser,” not a “partner” that acts as your hands
and feet.
That’s where Clawdbot comes in.
Clawdbot is more than just a chatbot — it’s an
autonomous personal AI agent that runs on your
local machine (PC or server) and performs the
actual tasks for you while protecting your data.


---
*Page 4*


It’s an open-source personal AI assistant that lets
you interact with Claude Code across multiple
messaging platforms, including WhatsApp,
Telegram, Discord, and Slack.
Meanwhile, Ollama is a runtime that lets you easily
install open-source LLMs, such as Meta Llama and
Mistral, locally and access them via an API.
Combining these two platforms lets you build an
AI assistant environment with no API fees, full
functionality on your own PC, and the ability to
swap out your preferred models.
So, let me give you a quick demo of a live chatbot
to show you what I mean.


---
*Page 5*


I will ask the chatbot two questions:” generate a
small app using html, css and javescripts”, If you
take a look at how the chatbot generates the
output, you’ll see that the agent works as a layered,
self-governing agent system rather than a single
prompt-response model: when a user sends an
input (via the Gateway from Slack, WhatsApp, UI,
or API), applied first (hard constraints enforced by
infrastructure and hooks, such as tool permissions
and safety rules).
Next, Agent loads its prompts in a fixed, deliberate
order defined in AGENTS.md: it anchors behavior


---
*Page 6*


using SOUL.md (personality, values, tone), then
applies IDENTITY.md (name, role, persona),
incorporates USER.md (user preferences and
relationship context), and finally references
relevant persistent memory from the memory
logs.
With this structured context assembled, the agent
evaluates whether it already has the skills required
to fulfil the request; if not, it autonomously
searches ClawHub for missing capabilities or uses
Workspace Skills, if available, installing or
prioritising them as needed.
The request is then executed using available tools
and skills, while the LLM generates a response
guided by soft constraints (prompt hierarchy, role
definitions) and hard constraints (system
enforcement).
After producing the output, Agent records relevant
outcomes into persistent memory, updates its


---
*Page 7*


workspace if new skills or behaviors were learned,
and — because the workspace is Git-managed —
these changes remain transparent, reversible, and
controllable by the user.
󰬾
Before we start!
If you like this topic and you want to support me:
1. Clap my article 50 times; that will really help me
👏
out.
2. Follow me on Medium and subscribe to get my
🫶
latest article for Free
3. Join the family — Subscribe to the YouTube
channel
Why OpenClaw is attracting attention
1. The meaning of “personal” has changed
ChatGPT and Claude are also useful, but they are
not “personal.” Conversation history is stored in
the cloud, and customisation is limited. OpenClaw


---
*Page 8*


is literally “your own AI running on your own
machine.”
2. Fits into your existing workflow
There’s no need to open a new app. You can talk to
the AI directly through your usual apps like Slack
or WhatsApp. This is a subtle but significant
feature.
Self-replication: the heart of OpenClaw
The most distinctive feature of OpenClaw is self-
evolution, which is not just customisation but also
refers to the mechanism by which agents can
expand themselves.


---
*Page 9*


Self-renewal flow: Automatically acquires skills in
response to user requests and accumulates learning
results
Layer 1: ClawHub (skill auto-discovery)
ClawHub is a skills registry (marketplace). When a
user requests “do something,” if the required skill
is not available, OpenClaw itself will search
ClawHub and install the required skill.
There is no need for humans to give instructions
such as “Add this skill.” The agent will make its
own decisions and expand its capabilities.
Layer 2: Self-hackable
OpenClaw can fix itself. This is not a metaphor; it
has actually happened.
“my @openclaw added Antigravity auth to
@zeddotdev based on how it itself authenticates
with Antigravity.”


---
*Page 10*


One user, OpenClaw, added his own
authentication feature for the Zed editor, inspired
by how he authenticates with Antigravity.
This ability to “augment itself” is what sets it apart
from other AI assistants. As one user commented:
“The fact that it’s hackable (and more importantly,
self-hackable) and hostable on-prem will make
sure tech like this DOMINATES.”
Layer 3: Workspace Skills (User-specific skills)
There are three layers of skills:
1. Bundled Skills — Core functions built into
OpenClaw
2. Managed Skills — Public skills curated by
ClawHub
3. Workspace Skills — User-created skills
Workspace Skills can be added by simply placing a
Markdown file
~/.openclaw/workspace/skills/<skill>/SKILL.mdin. If


---
*Page 11*


there is a skill with the same name, Workspace
Skills will take priority.
Layer 4: Persistent Memory and Git Management
OpenClaw records your daily conversations
memory/YYYY-MM-DD.mdin a persistent memory.
More importantly, the entire Agent Workspace can
be a Git repository.
cd ~/.openclaw/workspace
git init
git add AGENTS.md SOUL.md TOOLS.md IDENTITY.md USER.m
git commit -m "Add agent workspace"
If the agent makes a mistake in its learning, git
revertit can be rolled back. This is groundbreaking
in that it allows humans to control the "learning" of
AI.
How it works as an Agent
Having used OpenClaw this time, I felt that it was
extremely well-made. Also, one of the things I


---
*Page 12*


want to create is a “human-like AI agent,” so I was
very interested in how it works.
Gateway
OpenClaw has a mechanism called Gateway. It has
a built-in API server function that accepts requests
from external apps. For example, you can have the
AI pick up comments made on your smartphone
via Slack or Discord while you’re out and about and
automatically perform tasks.
Sending requests to a locally running Clawdbot
requires the use of another tool, such as ngrok,
which is a bit of a hassle, but it turns out to be
quite useful.
What I personally found interesting was how it
behaves as an autonomous assistant.
Here are some excerpts from the slides explained
using Google NotebookML.


---
*Page 13*


As the image shows, OpenClaw has a hierarchical
prompt structure, as follows:
1. System rules: Top-level rules. Rules that must be
followed.
2. Operational rules: Behavioral policies (prompt
loading standards, etc.)
3. Personality core: Values, personality, etc., the
part that corresponds to the “heart” in humans
4. Identity: Name, catchphrases, personality, etc.
Information about a person that has different


---
*Page 14*


aspects depending on who they interact with.
5. User information: information about the people
you interact with (i.e. you)
Its unique feature is that it does not consolidate all
information in one place, but divides it into
multiple parts and organises them into layers.
Also, as I understand it, one of the problems with
AI is that “prompts are not 100% guaranteed.”
I was curious about this too, so I asked the AI about
it, and it gave me the following explanation:
As you pointed out, prompts for LLMs (large-scale
language models) are merely “probabilistic
weights” and do not function as “absolute
prohibitions” like program code.
OpenClaw recognizes this limitation and makes its
hierarchical rules effective by combining
“enforcing context through prompts (soft
constraints)” with “physical blocking by the
system infrastructure (hard constraints) .”


---
*Page 15*


System-enforced constraints are also realised
through Claude Code’s hooks. Another interesting
part was the following explanation:
Fixing Context through “Loading Order” and
“Role Definition” (Soft Constraints)
OpenClaw does not simply pass all information to
the AI at once, but instead provides a structured
understanding of information priority.
• Absolute High-Level Conventions (System
Prompt): According to the explanatory materials,
the system fixes “safety, tool operation, and
expression rules” at the top level
(System/Developer layer). These are treated as
instructions with stronger authority than user-
defined prompts, motivating the AI to adhere to
this framework.
• Explicit “Rules for Reading Rules” (AGENTS.md):
The file AGENTS.md functions as the “operational
rules,” specifying what to load and in what order


---
*Page 16*


(SOUL → USER → memory). Rather than simply
passing a file, the instruction (prompt) specifies
the thought process itself — “first refer to the
personality (SOUL), then apply the settings
(IDENTITY)” — to prevent misinterpretation of
rule priorities (such as settings overriding the
personality).
By combining various constraints in this way, it
appears possible to achieve a human-like
behaviour as an assistant.
I personally find this very interesting, so I’m going
to dig deeper and look into it further. I might even
write another article about what I learn in the
process.
Agent Workspace structure


---
*Page 17*


Agent Workspace directory structure: each file defines
an agent’s personality, memories, and abilities
The workspace ~/.openclaw/workspace/is located in
and consists of the following files:
fileroleAGENTS.mdAgent operation rules and
memory usage guidelinesSOUL.mdPersonality, tone,
and dialogue boundariesUSER.mdUser information,
naming preferencesTOOLS.mdA note about local
toolsIDENTITY.mdAgent name, character,
emojimemory/Daily Memory Logskills/Custom
Skills


---
*Page 18*


In particular SOUL.mdThis is a file that defines the
agent's "personality," and by editing this, you can
fundamentally change OpenClaw's behavior.
security risks
After using it this time, I felt that there were some
risks that were higher than with previous AI
agents.
I feel that with the increase in integration with
various chat tools and touch points with these
tools, there is a possibility that instructions may be
sent unintentionally from outside. In particular,
there are likely to be problems if someone without
such knowledge sets it up carelessly.
If AI were used alone, the only issue would be cost,
but since it acts as an assistant, the problem is that
it can access your private information.
If the assistant were human, it would be able to
determine who is giving instructions and handle
them appropriately, but with AI, communication is


---
*Page 19*


limited to text, so in some cases, it is entirely
possible that the processing could progress and
information could be leaked.
Currently, possible measures include narrowing
the range of access or running it in a secondary
environment.
However, convenience and risk are always two
sides of the same coin, so I think it’s a good idea to
get started on it now for verification purposes and
to explore the future of agents.
If you are actually planning to build an
environment, please be sure to keep these things
in mind when you try it out.
There is also official documentation on security,
which I recommend reading as well. The
documentation includes a security check
command that OpenClaw provides as standard,
and recommends that you always run it when
updating your settings.


---
*Page 20*


Security Check
$ openclaw security audit --deep
Five measures to ensure safe use
For those who want to use OpenClaw, we have
summarized the minimum security measures that
should be observed.
1. Ensure Gateway Authentication is enabled
Gateway authentication is now mandatory in the
latest version, but you must set a token, password,
or Tailscale Server ID. The “none” mode has been
removed.
# Check for any security warnings.
openclaw doctor # Verify there are no security warni
2. Don’t publish directly to the internet
Trust boundary issues behind reverse proxies are
the cause of many of the problems. Only use it


---
*Page 21*


within your local network or access it via VPN.
3. Don’t install third-party skills easily
Research has shown that 26% of 31,000 agent skills
contain vulnerabilities. Use skills only when
necessary and review the code before installing
them.
4. Running in a Virtual Machine
It is recommended to run sandboxed in a VM or
container rather than running directly on the host
OS.
5. Don’t trust default settings
~/.openclaw/Configuration files and memory in
the directory are stored in plain text. Consider
using encryption tools in combination. If you are
operating with default settings, security experts
recommend assuming that you have been
compromised.
OpenClaw Settings
First, let me show you how to install Clawdbot.


---
*Page 22*


It only takes one command; it’s actually not
difficult, very simple.
The following commands apply to Mac, Windows,
and Linux. I have chosen to deploy and test on
Mac.
PS: I want to make a serious statement here. This is
a test laptop that I keep at the company. I would
like to remind everyone to pay attention to security
issues. If it is not necessary, do not install it on
your main machine. You must use a backup
machine. I must give you this warning in advance.
This thing has high privileges, so be careful.
If you run it directly on your main machine, and
the AI happens to execute `rm -rf /`, all your
privacy and learning materials on your computer
will be lost.
Please don’t blame me when your important files
get deleted = =


---
*Page 23*


This command is very simple:
# Windows
iwr -useb https://molt.bot/install.ps1 | iex
# macOS / Linux / Ubuntu / Debian
curl -fsSL https://molt.bot/install.sh | bash -s -- -
Remember to install Node.js before running this
command; it must be version 22 or higher,
otherwise you will get an error.
Then you’ll see him start installing.
During onboarding, you can interactively set the
Gateway’s port, workspace, channel, skills, etc.,


---
*Page 24*


and the configuration file created here will serve
as the foundation for later adjusting the details of
the model and agent.
After completing the wizard, the Gateway will
reside as a user service, so Clawdbot will start
automatically when your PC starts up, creating
your own personal AI central centre that can be
called up via chat at any time.
npm install -g openclaw@latest
openclaw onboard --install-daemo
The gist of this sentence is: I understand that this
lobster is very capable, but the risks are extremely
high. Are you sure you want to continue?
He will only let you proceed to the next step if you
select “yes”.
If you choose “No,” and the process is shut down
directly, that’s a very unfair and arbitrary clause.


---
*Page 25*


After you say yes, you will see an option.
The first option is to start quickly and then
configure the information using clawdbot
configure. The second option is to configure
manually first.
will tell you to configure a model.


---
*Page 26*


We will skip the model because we are going use
Ollama, but I would like to tell you never use your
Claude Max credit limit to link to Clawdbot.
Anthropic, that scoundrel, now only allows that
credit limit to be used on Claude Code. If you use
Clawdbot to authorise it, your account will likely
be banned immediately. There have been many
cases like this on X.


---
*Page 27*


When you select QuickStart, you will be asked to
select the model you want to use.
Since I want to use Ollama this time, I select Skip
for now and select All providers. But feel free to
select any model you want


---
*Page 29*


Then I will enter the model manually
and the model I will be given is ollama/gpt-oss:20
b. I tried to use this method as all the developers
did, but it doesn’t work, as you can see in the
screen couldn’t find the model. But later, I will
show you how to fix it


---
*Page 30*


After onboarding, Clawdbot generates an internal
JSON-based configuration file that manages the
“list of models,” “default model,” “connection
information for each model,” and more.
The GitHub documentation explains how to
configure models from the CLI and the OAuth/API
key rotation feature in the Models section. When
using Ollama, this is written as a “local model via
HTTP.”
Carefully designing this model definition allows
you to intelligently switch between models
depending on the purpose, such as a “lightweight
model for everyday conversation,” a “larger model
for code reviews,” and a “longer context model for
summaries.”


---
*Page 31*


This section is all from overseas, and normal
people don’t use this stuff, so you can choose the
last one and skip it. We can teach you how to use
Lark to launch this later.
Then, he will ask you if you want to configure the
skills he provides; just say “Yes” without hesitation.


---
*Page 32*


Then you’ll be asked to choose which manager to
use for installation. I personally prefer npm, which
is automatically included if you’ve installed
Node.js.
Then, you’ll be given a bunch of skills…


---
*Page 33*


Each one has a description, so you can choose
whichever you like to equip. If you’re too lazy to
choose, you can just skip it, since you can equip it
later by talking to him.


---
*Page 34*


That’s it — now run the gateway server. It will then
ask the final questions, like whether you want to
run this bot in a UI. Of course, you should choose
“hatch in UI,” which is the UI for you — a
dashboard in OpenClaw where you can see how
things are going. You can access the OpenClaw
cloud that you have installed in your browser to


---
*Page 35*


start chatting with OpenClaw, which is quite
amazing.
Look at this — there are some issues, so we’ll just
go to the overview. You can see that the status of
this OpenClaw instance is currently Disconnected.
To make this connected, we’re going to run this
command to fix that, because it’s currently
disconnected. We’re going to copy this command
exactly as I am doing it, stop the terminal, paste it
into the terminal and hit Enter. The moment I do
that, you can see that the red screen is gone and
the health status is now okay.


---
*Page 36*


If I go to the overview, you can see that it is now
connected, which means my OpenClaw is
connected and ready to accept chats and
commands. If I try to chat here, I’ll tell you exactly
what happens.
For example, if I say “hi” here, you can see that it
shows it is running, but nothing actually happens
because it doesn’t respond with any answers. This
is happening because we haven’t set up Ollama yet.


---
*Page 37*


Next, we’re going to set up the Ollama settings.
Make sure that you’ve downloaded Ollama. Then
click on Settings and adjust the context length to
64,000 tokens, because OpenClaw requires a larger
context window to work properly with models
If you have not installed the model yet, we will use
this command to install the model. Once installed,


---
*Page 38*


ollama pull gpt-oss:20b
we copy this command ‘ollama launch’, and this
configures OpenClaw to use Ollama and starts the
gateway. If the gateway is already running, no
changes need to be made as the gateway will auto-
reload the changes.
ollama launch openclaw
Then we're going to tell OpenClaw to enter the
configuration wizard for the “web” section of its
settings. This is specifically where you set up web-
related tools, such as web search (and optionally
web fetch), so the agent can browse or search the
internet
OpenClaw doesn’t automatically know how to do
web search or web fetch out of the box — those
features require API keys or settings


---
*Page 39*


openclaw configufe - section web
Thoughts


---
*Page 40*


I’m still not sure if we really need an AI agent. I’m
an engineer, so I’m fine with Claude Code.
Above all, this is a local program, so if I take down
the terminal, no one else can use it. That’s why it’s
so popular to buy a cheap and powerful machine
like a Mac mini and run it on it.
However, by providing an environment where I
can use the AI agent, I think it will be a huge
benefit that non-engineer team members and
managers who do not use ClaudeCode will also be
able to use the AI agent.
It’s very appealing to be able to casually ask
questions like, “What happened back then?” or
“How’s the current project going?”
that don’t take up anyone’s time.
I sincerely hope this article will be helpful to
someone.


---
*Page 41*


If you find any errors or unclear points in the
article, please feel free to leave a comment.
󰩃
I am an AI Generative expert! If you want to
collaborate on a project, drop an inquiry here or
book a 1-on-1 Consulting Call With Me.
RLM + Graph: The Ultimate Evolution of AI?
R i L M d l G h
Not long ago, I shared a video about
R i L M d l d f
pub.towardsai.net
RLM: The Ultimate Evolution of AI?
R i L M d l
During the weekend, I scrolled through
T itt t h t h i i th AI
pub.towardsai.net
Gemini 3.0 Flash + MistralOCR 3 + RAG Just
R l ti i d A t OCR F
Not long ago, I shared a video about
D S k OCR d P ddl OCR d
medium.com
Data Science Machine Learning Artificial Intelligence


---
*Page 42*


Programming Technology
Published in Towards AI
Following
108K followers · Last published 3 hours ago
We build Enterprise AI. We teach what we learn. Join
100K+ practitioners on Towards AI Academy. Free:
Get our 2026 AI Agents Cheat Sheet + Webinar.
Download Now:
https://tinyurl.com/agentarchitecturecheatsheet
⾼達烈
Written by Gao Dalie ( )
Follow
9.2K followers · 1 following
NC State Uni (Research Assistant), Learn AI Agent,
LLMs, RAG & Generative AI. See everything I have to
offer at the link below: https://linktr.ee/GaoDalie_AI
Responses (1)
To respond to this story,
get the free Medium app.


---
*Page 43*


FUZAIL UR REHMAN KHAN
12 hours ago
Good article
⾼達烈
More from Gao Dalie ( ) and Towards
AI
In by ⾼達 In by
Towards … Gao Dalie ( … Towards AI Soultntoure
RLM: The Ultimate The NotebookLM
E l ti f AI? W kfl Th t
During the weekend, I scrolled A practical system for
th h T itt t h t i d
Jan 10 Dec 23, 2025


---
*Page 44*


In by In by ⾼達
Towar… Adi Insights and In… Towards … Gao Dalie ( …
I Let an Autonomous RAG is Not Dead! No
A t R f t M Ch ki N V t
We spent 3 years afraid to Over the past two years, I have
t h til fi l 2 j S I itt ti l
Jan 19 Oct 17, 2025
⾼達烈
See all from Gao Dalie ( ) See all from Towards AI
Recommended from Medium
Reza Rezvani Balazs Kocsis


---
*Page 45*


I Tested Every Major 10 OpenClaw Use
Cl d O 4 6 C f P l
After 24 hours of real testing How are people actually using
d il kfl O Cl d h th
6d ago Jan 27
Will Lockett In by
Activated Thin… Shane Coll…
OpenAI Is In A Far
Stop Watching
W P iti Th I
O Cl I t ll
This is beyond reckless…
Everyone can run npm install.
O l f k h t t
6d ago Feb 1


---
*Page 46*


Alberto Romero Joe Njenga
LEAKED: The Truth I Tried (New) Claude
B hi d M ltb k C d A t T
… Forget single-agent
kfl Cl d C d A
Jan 31 5d ago
See more recommendations