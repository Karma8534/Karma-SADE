# agentfactory.panaversity

*Converted from: agentfactory.panaversity.PDF*



---
*Page 1*


Agent Factory
AI Leaderboard Sign In Sign Up
Part 1: General Agents: Foundations
/ /
Chapter 3: Working with General Agents: Claude Code and Cowork
/
Section A: Claude Code Essentials Free Claude Code Setup
/
13 min read TTeeaacchh MMee Ask
Updated Feb 28, 2026 Version history
Highlight text to Ask questions
Free Claude Code Setup
This lesson provides free alternatives to use Claude Code without a
subscription. You'll choose between Open Router, oGoogle Gemini or
DeepSeek as your backend, learning the same Claude Code CLI interface
and features covered in Lesson 2.
⚠ Important (January 2026): Google significantly reduced Gemini API free
tier limits in December 2025. Daily request limits dropped 50-80% for most
models. OpenRouter free models have daily request limits that vary by
model. OpenRouter offers 30+ free models AI Free API but with daily
request limits. Models rotate and quality varies. DeepSeek is not truly "free"
but offers very low pricing (~$0.028-$0.42 per million tokens). Both
deepseek-chat and deepseek-reasoner follow the same pricing: $0.028 per
million input tokens (cache hit), $0.28 per million input tokens (cache
miss), and $0.42 per million output tokens. Groq has a Free Tier for its API


---
*Page 2*


via GroqCloud. Plan your usage accordingly and have backup options
ready.
All features work identically: Subagents, skills, MCP servers, hooks, and all
other capabilities covered in Lessons 05-15 function the same way with
free backends. The only difference is the backend AI model and API
provider.
FREE ONGOING USAGE
By using Gemini's free tier or DeepSeek's competitive API, you get ongoing
free or low-cost consumption—no subscription required. This setup isn't
just for learning; many developers use it as their daily driver. The free tiers
are generous enough for real development work.
Choose Your Free Backend
Before setup, decide which backend suits you. All three options provide
identical Claude Code functionality:
Factor OpenRouter Gemini DeepSeek
Available Gemini DeepSeek
5+ free options
Models 2.5 Flash Chat/Reasoner
Daily request Daily Token-based
Free Tier limits per request (~$0.028-$0.42/M
model limits tokens)


---
*Page 3*


Factor OpenRouter Gemini DeepSeek
Speed Very Fast Very Fast Fast
Easiest
Setup Manual, most
(few Slightly more involved
Complexity transparent
steps)
Reasoning Available Native
Native support
Models (Qwen, Llama) support
OpenRouter Setup
This section guides you through configuring Claude Code with
OpenRouter's multi-model platform.
OpenRouter aggregates multiple AI models (including Gemini, Qwen,
Llama) under one API. This gives you maximum flexibility to experiment
with different models without re-configuring.
Step 1: Get Your OpenRouter API Key
1. Go to: OpenRouter API Keys
2. Click "Create Key"
3. Name it (e.g., "Claude Code Router")
4. Copy the key (starts with: )
sk-or-v1-...


---
*Page 4*


Step 2: Install and Configure
Select your operating system:
Windows▸ macOS▸ Linux
Verify Node.js
node --version # Should show v18.x.x or higher
If missing, install from nodejs.org
Install Tools
Open PowerShell and run:
npm install -g @anthropic-ai/claude-code
@musistudio/claude-code-router
Create Config Directories


---
*Page 5*


New-Item -ItemType Directory -Force -Path
"$env:USERPROFILE\.claude-code-router"
New-Item -ItemType Directory -Force -Path
"$env:USERPROFILE\.claude"
Create the Config File
1. Open Notepad (search "Notepad" in Windows Start menu)
2. Copy and paste this exactly:
{
"LOG": true,
"LOG_LEVEL": "info",
"HOST": "127.0.0.1",
"PORT": 3456,
"API_TIMEOUT_MS": 600000,
"Providers": [
{
"name": "openrouter",
"api_base_url": "https://openrouter.ai/api/v1",
"api_key": "$OPENROUTER_API_KEY",
"models": [
"qwen/qwen-coder-32b-vision",
"google/gemini-2.0-flash-exp:free",
"meta-llama/llama-3.3-70b-instruct:free",
"qwen/qwen3-14b:free",
"xiaomi/mimo-v2-flash:free"
],


---
*Page 6*


"transformer": {
"use": ["openrouter"]
}
}
],
"Router": {
"default": "openrouter,qwen/qwen-coder-32b-vision",
"background": "openrouter,qwen/qwen-coder-32b-
vision",
"think": "openrouter,meta-llama/llama-3.3-70b-
instruct:free",
"longContext": "openrouter,qwen/qwen-coder-32b-
vision",
"longContextThreshold": 60000
}
}
DO NOT CHANGE $OPENROUTER_API_KEY
Leave exactly as written. The router
"api_key": "$OPENROUTER_API_KEY"
reads your key from the environment variable you'll set in the next step.
1. Click File Save As
→
2. In the "File name" field, type exactly:
%USERPROFILE%\.claude-code-
router\config.json
3. Click Save
Set Your API Key
Run PowerShell as Administrator:


---
*Page 7*


1. Search "PowerShell" in Windows Start menu
2. Right-click on "Windows PowerShell"
3. Click "Run as administrator"
4. Click "Yes" if prompted
Run this command (replace with your key from Step 1):
YOUR_KEY_HERE
[System.Environment]::SetEnvironmentVariable('OPENROUTER_API
'YOUR_KEY_HERE', 'User')
1. Close PowerShell completely (not just the tab—close the whole
window)
2. Open a new regular PowerShell (not as admin)
3. Verify it worked:
echo $env:OPENROUTER_API_KEY
You should see your API key displayed ✅
Verify Setup
claude --version # Should show: Claude Code v2.x.x
ccr version # Should show version number


---
*Page 8*


echo $env:OPENROUTER_API_KEY # Should show your key
✅ Done! Proceed to Step 3: Daily Workflow below.
Step 3: Daily Workflow
Every time you want to code:
Windows▸ macOS▸ Linux
PowerShell 1 - Start router FIRST:
ccr start
Leave this window running. You'll see a warning message—that's normal!
PowerShell 2 - Open a NEW PowerShell window and run:
cd C:\your\project\folder
ccr code
FIRST STARTUP TAKES TIME
Wait 10-20 seconds after running on first startup. The router
ccr code
needs time to initialize.
When done: Press in both windows.
Ctrl+C


---
*Page 9*


Gemini Setup
This section guides you through configuring Claude Code with Google's
Gemini API.
Step 1: Get Your Free Google API Key
1. Go to: Google AI Studio
2. Click "Get API Key"
3. Sign in with Google
4. Click "Create API Key"
5. Copy the key (looks like: )
AIzaSyAaBbCcDd...
Step 2: Install and Configure
Select your operating system:
Windows▸ macOS▸ Linux
Step 0: Install Node.js (Skip if Already
Installed)
Check if you have Node.js:
Open PowerShell (search "PowerShell" in Windows Start menu) and type:


---
*Page 10*


node --version
▸ If you see v18.x.x or higher Skip to Step 1 ✅
→
▸ If you see an error or version lower than v18 Follow these steps:
→
1. Go to: nodejs.org
2. Click the big green button that says "Download Node.js (LTS)"
3. Run the downloaded file (it's called something like
node-v20.x.x-
)
x64.msi
4. Click Next Next Next Install
→ → →
5. Wait for it to finish
6. Close ALL PowerShell windows completely
7. Open a new PowerShell window
8. Type again to confirm it works
node --version
You should now see a version number like ✅
v20.11.0
Step 1: Install Tools
Open PowerShell and run:
npm install -g @anthropic-ai/claude-code
@musistudio/claude-code-router


---
*Page 11*


Step 2: Create Config Directories
Enable running scriptson your system first:
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
Now create directories:
New-Item -ItemType Directory -Force -Path
"$env:USERPROFILE\.claude-code-router"
New-Item -ItemType Directory -Force -Path
"$env:USERPROFILE\.claude"
Step 3: Create the Config File
1. Open Notepad (search "Notepad" in Windows Start menu)
2. Copy and paste this text exactly as-is:
{
"LOG": true,
"LOG_LEVEL": "info",
"HOST": "127.0.0.1",
"PORT": 3456,
"API_TIMEOUT_MS": 600000,
"Providers": [
{


---
*Page 12*


"name": "gemini",
"api_base_url":
"https://generativelanguage.googleapis.com/v1beta/models/",
"api_key": "$GOOGLE_API_KEY",
"models": [
"gemini-2.5-flash-lite",
"gemini-2.0-flash"
],
"transformer": {
"use": ["gemini"]
}
}
],
"Router": {
"default": "gemini,gemini-2.5-flash-lite",
"background": "gemini,gemini-2.5-flash-lite",
"think": "gemini,gemini-2.5-flash-lite",
"longContext": "gemini,gemini-2.5-flash-lite",
"longContextThreshold": 60000
}
}
DO NOT CHANGE $GOOGLE_API_KEY
Leave exactly as written. Do NOT
"api_key": "$GOOGLE_API_KEY"
replace it with your actual key here—the router will automatically read your
key from the environment variable you set in Step 4.
1. Click File Save As
→
2. In the "File name" field, type exactly:
%USERPROFILE%\.claude-code-
router\config.json
3. Click Save


---
*Page 13*


Step 4: Set Your API Key
Run PowerShell as Administrator:
1. Search "PowerShell" in Windows Start menu
2. Right-click on "Windows PowerShell"
3. Click "Run as administrator"
4. Click "Yes" if prompted
Run this command (replace with your actual API key from
YOUR_KEY_HERE
Step 1):
[System.Environment]::SetEnvironmentVariable('GOOGLE_API_KEY
'YOUR_KEY_HERE', 'User')
1. Close PowerShell completely (not just the tab—close the whole
window)
2. Open a new regular PowerShell (not as admin this time)
3. Verify it worked:
echo $env:GOOGLE_API_KEY
You should see your API key displayed ✅


---
*Page 14*


Verify Setup
claude --version # Should show: Claude Code v2.x.x
ccr version # Should show version number
echo $env:GOOGLE_API_KEY # Should show your key
✅ Done! Proceed to Step 3: Daily Workflow below.
Step 3: Daily Workflow
Every time you want to code:
Windows▸ macOS▸ Linux
PowerShell 1 - Start router FIRST:
ccr start
Leave this window running. You'll see a warning message—that's normal!
PowerShell 2 - Open a NEW PowerShell window and run:
cd C:\your\project\folder
ccr code
FIRST STARTUP TAKES TIME


---
*Page 15*


Wait 10-20 seconds after running on first startup. The router
ccr code
needs time to initialize. If it seems stuck, just wait—it's working!
When done: Press in both windows.
Ctrl+C
DeepSeek Setup
This section guides you through configuring Claude Code with DeepSeek's
API.
If you already completed the Gemini Setup above, you already have Node.js
and the Claude Code Router installed. You only need to create the
DeepSeek configuration and set your API key.
Step 1: Get Your DeepSeek API Key
1. Go to: DeepSeek API Platform
2. Sign up or log in with your account
3. Navigate to API Keys section
4. Click "Create API Key"
5. Copy the key (looks like: )
sk-...
Step 2: Configure DeepSeek
Windows▸ macOS▸ Linux


---
*Page 16*


Create the config file: Open Notepad and paste:
{
"LOG": true,
"LOG_LEVEL": "info",
"HOST": "127.0.0.1",
"PORT": 3456,
"API_TIMEOUT_MS": 600000,
"Providers": [
{
"name": "deepseek",
"api_base_url": "https://api.deepseek.com/v1",
"api_key": "$DEEPSEEK_API_KEY",
"models": [
"deepseek-chat",
"deepseek-reasoner"
],
"transformer": {
"use": ["openai"]
}
}
],
"Router": {
"default": "deepseek,deepseek-chat",
"background": "deepseek,deepseek-chat",
"think": "deepseek,deepseek-reasoner",
"longContext": "deepseek,deepseek-chat",
"longContextThreshold": 60000
}
}


---
*Page 17*


DO NOT CHANGE $DEEPSEEK_API_KEY
Leave exactly as written.
"api_key": "$DEEPSEEK_API_KEY"
Save as:
%USERPROFILE%\.claude-code-router\config.json
Set your API key (Run PowerShell as Administrator):
[System.Environment]::SetEnvironmentVariable('DEEPSEEK_API_K
'YOUR_KEY_HERE', 'User')
Close and reopen PowerShell, then verify:
echo $env:DEEPSEEK_API_KEY
Verification
Both Gemini and DeepSeek use the same daily workflow and verification
process.
Start a Claude session and say hi:
hi
Expected: Claude responds with a greeting confirming it's working! ✅
Success!


---
*Page 18*


Troubleshooting
Windows▸ macOS▸ Linux
"command not found" or "not recognized"
Close and reopen PowerShell completely. If still failing, the npm global bin
directory isn't in your PATH.
"API key not found" or empty variable
1. Make sure you ran the command as
SetEnvironmentVariable
Administrator
2. Close ALL PowerShell windows and open a fresh one
3. Check with
echo $env:GOOGLE_API_KEY
Stuck at "starting service"
Wait 20-30 seconds on first run. This is normal.
Router starts but Claude hangs
Make sure is running in PowerShell 1 before running
ccr start ccr
in PowerShell 2.
code
Try With AI


---
*Page 19*


Once your free setup is working, try these prompts to verify everything
works:
Verify Basic Functionality:
"Hello! Confirm you're working by telling me: (1) what model you're using,
(2) can you see files in this directory? List them if so."
Test File Operations:
"Create a simple test file called with the text 'Free Claude
hello.txt
Code setup works!' Then read it back to confirm."
Understand the Architecture:
"Explain the architecture of my current setup: I'm using Claude Code CLI
with a router pointing to a free backend. What's happening when I send
you a message? Walk me through the request flow."
That's it. Proceed to Lesson 05 to learn about teaching Claude your way of
working.
Flashcards Study Aid
⎘


---
*Page 20*


⎘
What is the three-layer
architecture that enables
‹ ›
Claude Code to work with any
AI backend?
Click to flip
1 / 10 cards
⤢ Fullscreen ⇅ Shuffle ⓘ Guide ↧ Download
Last updated on Feb 28, 2026
The AI Agent LEARN COMPANY
Factory Start Reading About Us
Curriculum Our Mission
Specification Contact
Projects Privacy
Authors


---
*Page 21*


PANAVERSITY
© 2026 Panaversity. Open Source Education.