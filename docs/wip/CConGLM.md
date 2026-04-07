# CConGLM

*Converted from: CConGLM.PDF*



---
*Page 1*


Open in app
Search Write
Dev Genius
Claude Code, but
cheaper: GLM-4.7 on
Z.ai with a tiny wrapper
Keen to try out Claude Code extensively but
don’t want to fork substantial money just yet?
This guide is for you!
JP Caparas Follow 5 min read · Dec 22, 2025
35 2


---
*Page 2*


GLM 4.7 just released today, and it claims a superior uplift against 4.6
If you like Claude Code’s workflow but the pricing
makes you wince, Z.ai’s Anthropic-compatible
endpoint is worth another look. This is an updated
version of my earlier write-up with GLM-4.7, new
model mappings, and a safer, lighter wrapper.
The setup in one sentence: point Claude Code at
Z.ai’s API, map Claude’s internal
Haiku/Sonnet/Opus slots to GLM models, and keep
your key out of shell history by loading it from a
local config file.


---
*Page 3*


What’s new in GLM-4.7 (vendor-reported)
Z.ai’s GLM-4.7 release post focuses on coding, tool
use, reasoning, and UI output. The benchmarks
below are Z.ai’s own reported numbers, so treat
them as directional and validate on your own
workload:
SWE-bench Verified: 73.8% (Z.ai says +5.8 over
GLM-4.6).
SWE-bench Multilingual: 66.7% (Z.ai says +12.9).
Terminal Bench 2.0: 41% (Z.ai says +16.5).
HLE with tools: 42.8% (Z.ai says +12.4).
The release also calls out better “vibe coding”
output (cleaner HTML and slide layouts) and
stronger tool-using benchmarks. Those are vendor
numbers too, but they’re a helpful signal if you’re
already using Claude Code for web UI tasks.
Quick setup (config + wrapper, about 5
minutes)


---
*Page 4*


This keeps the same structure as the original post:
a local config file plus a tiny wrapper that injects
the right environment variables for Claude Code.
0) Make sure “zc” is free
command -v zc
If that prints a path, pick another name (for
example zai-c) and use it everywhere below. I use
zc because it's short and currently unused on my
machine.
1) Create a config file
Create ~/.zai.json:
{
"apiUrl": "https://api.z.ai/api/anthropic",
"apiKey": "REPLACE_WITH_YOUR_ZAI_API_KEY",
"yolo": false,
"haikuModel": "glm-4.5-air",
"sonnetModel": "glm-4.7",


---
*Page 5*


"opusModel": "glm-4.7"
}
Lock it down so your key is not world-readable:
chmod 600 ~/.zai.json
If you want everything to use one model, just set
all three fields to the same value.
2) Add the wrapper function
Drop this into ~/.zshrc or ~/.bashrc:
zc() {
local config="$HOME/.zai.json"
if ! command -v jq >/dev/null 2>&1; then
echo "zc: jq is required (brew install jq | apt-g
return 1
fi
if ! command -v claude >/dev/null 2>&1; then
echo "zc: Claude Code not found. Install: npm ins
return 1
fi


---
*Page 6*


if [ ! -f "$config" ]; then
echo "zc: missing $config" >&2
return 1
fi
local api_url api_key yolo haiku_model sonnet_model
IFS=$'\t' read -r api_url api_key yolo haiku_model
jq -r '[.apiUrl // "", .apiKey // "", .yolo // fa
)
if [ -z "$api_url" ] || [ -z "$api_key" ]; then
echo "zc: apiUrl/apiKey missing in $config" >&2
return 1
fi
[ -z "$haiku_model" ] && haiku_model="glm-4.5-air"
[ -z "$sonnet_model" ] && sonnet_model="glm-4.7"
[ -z "$opus_model" ] && opus_model="glm-4.7"
local yolo_flag=""
if [ "$yolo" = "true" ]; then
yolo_flag="--dangerously-skip-permissions"
fi
local key_hint="${api_key:0:4}...${api_key: -4}"
echo "zc: endpoint=$api_url | haiku=$haiku_model |
ANTHROPIC_BASE_URL="$api_url" \
ANTHROPIC_AUTH_TOKEN="$api_key" \
ANTHROPIC_DEFAULT_HAIKU_MODEL="$haiku_model" \
ANTHROPIC_DEFAULT_SONNET_MODEL="$sonnet_model" \
ANTHROPIC_DEFAULT_OPUS_MODEL="$opus_model" \
claude $yolo_flag "$@"
}


---
*Page 7*


3) Reload your shell and smoke test
source ~/.zshrc # or ~/.bashrc
Then:
zc
# Inside Claude Code, run:
# /status
You should see the GLM model mapping in the
status output.
How the model mapping works (and how
to change it)
Claude Code internally thinks in
Haiku/Sonnet/Opus. Z.ai’s docs explain that you
can map those internal slots to GLM models by
setting:


---
*Page 8*


ANTHROPIC_DEFAULT_HAIKU_MODEL
ANTHROPIC_DEFAULT_SONNET_MODEL
ANTHROPIC_DEFAULT_OPUS_MODEL
The wrapper above sets all three every time you
run zc, so you can keep your environment clean
and avoid exporting secrets in your shell profile.
If you prefer to configure Claude Code directly, you
can add the same mapping to
~/.claude/settings.json instead:
{
"env": {
"ANTHROPIC_AUTH_TOKEN": "REPLACE_WITH_YOUR_ZAI_AP
"ANTHROPIC_BASE_URL": "https://api.z.ai/api/anthr
"ANTHROPIC_DEFAULT_HAIKU_MODEL": "glm-4.5-air",
"ANTHROPIC_DEFAULT_SONNET_MODEL": "glm-4.7",
"ANTHROPIC_DEFAULT_OPUS_MODEL": "glm-4.7"
}
}
Have you tried it yourself?


---
*Page 9*


Well in fact, I did! I used Conductor to load up the
new models and it was able to perform a quick UI
change for me.
It KNOWS!
Following confirmation that we’re running GLM
4.7, I asked it to make some changes to the footer.


---
*Page 10*


It was pretty quick at coding that up.
Proof of the pudding.
Daily use tips
Use zc exactly the way you'd use claude.


---
*Page 11*


Check /status to confirm the mapping before a
long session.
If you set "yolo": true in the config, the
wrapper passes --dangerously-skip-permissions.
Treat that as a sharp tool.
Costs, benchmarks, and expectations
Z.ai markets its GLM Coding Plan as roughly 1/7
the cost with 3x the usage compared with Claude
tiers, and positions GLM-4.7 as a top-end coding
model. Those are Z.ai’s claims; I still run two quick
checks before I fully switch a project:
1. A small refactor on a real repo (tests passing,
diffs sensible).
2. A single “hard” task I already know Claude
handles well.
If both feel good, I move the rest of the project
over.
Security notes


---
*Page 12*


Keep ~/.zai.json out of git and locked down
(chmod 600).
Rotate your Z.ai API key if it ever leaks.
Only enable yolo when you're comfortable with
the workspace permissions.
Uninstall / revert
Remove the zc function from your shell profile.
Delete ~/.zai.json.
Use claude directly again (or remove the Z.ai env
mapping from ~/.claude/settings.json if you
added it).
Appendix: example configs
Balanced (default):
{
"apiUrl": "https://api.z.ai/api/anthropic",
"apiKey": "REPLACE_WITH_YOUR_ZAI_API_KEY",
"yolo": false,
"haikuModel": "glm-4.5-air",
"sonnetModel": "glm-4.7",


---
*Page 13*


"opusModel": "glm-4.7"
}
Lower cost / lower latency (map everything to
GLM-4.5-Air) (but honestly, no need for this unless
you’re truly penny-pinching):
{
"apiUrl": "https://api.z.ai/api/anthropic",
"apiKey": "REPLACE_WITH_YOUR_ZAI_API_KEY",
"yolo": false,
"haikuModel": "glm-4.5-air",
"sonnetModel": "glm-4.5-air",
"opusModel": "glm-4.5-air"
}
All-in on GLM-4.7:
{
"apiUrl": "https://api.z.ai/api/anthropic",
"apiKey": "REPLACE_WITH_YOUR_ZAI_API_KEY",
"yolo": false,
"haikuModel": "glm-4.7",
"sonnetModel": "glm-4.7",
"opusModel": "glm-4.7"
}


---
*Page 14*


References
GLM-4.7: Advancing the Coding Capability
(release post with benchmark table):
https://z.ai/blog/glm-4.7
Claude Code on Z.ai (Anthropic-compatible
endpoint and model mapping):
https://docs.z.ai/devpack/tool/claude
GLM-4.7 model overview:
https://docs.z.ai/guides/llm/glm-4.7
Original article this update builds on:
https://jpcaparas.medium.com/make-claude-
code-use-the-z-ai-api-and-save-a-tiny-zai-
wrapper-low-cost-high-usage-tiers-bc26be23bbfb
Thanks for reading
If you liked this article and haven’t subscribed to
the GLM coding plan yet, do yourself a favour and
subscribe now and grab a limited-time deal at
https://z.ai/subscribe?ic=IIJ5RBCVWO


---
*Page 15*


Claude Code Glm Vibe Coding Tui Wrapper
Published in Dev Genius
Following
30K followers · Last published 7 hours ago
Coding, Tutorials, News, UX, UI and much more
related to development
Written by JP Caparas
Follow
1.95K followers · 103 following
I bring fact-based and trending updates on AI,
automation, dev, and tech trends. A hint of humour
and a dash of cynicism. Subscribe now for daily
updates.
Responses (2)
To respond to this story,
get the free Medium app.
Charles
Jan 15


---
*Page 16*


The cost savings on Z.ai are legit. I tried this exact setup and honestly
GLM-4.7 gets you 80% of the way there for like 1/10th the price. Perfect if
you're still experimenting or burning through tokens daily.
Andy Eadie
Jan 5
Can you do one of these but for deepseek? Its API is really cheap!
More from JP Caparas and Dev Genius


---
*Page 17*


In by In by
Reading.sh JP Caparas Dev Genius JP Caparas
The Claude Code team Qwen3-Coder-Next just
j t l d th i l h d
Boris’ workflow is excellent.
Hi ll d it diff tl
Jan 31 Feb 3
In by In by
Dev Genius Ezekiel Njuguna Reading.sh JP Caparas
Just Found the Math The definitive guide to
Th t G t P f O C d f fi t
I am lost for words after what I
di d b t P l k
Feb 1 Feb 1
See all from JP Caparas See all from Dev Genius


---
*Page 18*


Recommended from Medium
In by In by
Towards Dev Bill WANG Activated Thin… Shane Coll…
Running OpenClaw Stop Watching
ith L l LLM O Cl I t ll
Everyone can run npm install.
O l f k h t t
Feb 15 Feb 1


---
*Page 19*


In by In by
CodeToD… Manjunath Jan… ITNEXT Jacob Ferus
Open Claw on Cursor Is Dying
R b Pi B ildi
Cursor is a great product. It
How I set up OpenClaw as a
f th fi t t
h dl l AI
Feb 4 Feb 11
Steve Yegge In by
GitBit John Gruber
The Anthropic Hive
Websites Are Dead. Go
Mi d
H I t d
As you’ve probably noticed,
I finally did it. I launched a
thi i h i
bl Th I li d th h d
Feb 6 Feb 10
See more recommendations