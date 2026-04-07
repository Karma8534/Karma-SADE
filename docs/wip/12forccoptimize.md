# 12forccoptimize

*Converted from: 12forccoptimize.PDF*



---
*Page 1*


Open in app
11
Search Write
Member-only story
12 Little-Known Claude
Code Commands That
Make You a Whiz
Joe Njenga Following 8 min read · Sep 21, 2025
379 6


---
*Page 2*


What if I told you there are some Claude Code
commands that, although not very popular, could
be your gateway to becoming a Claude Code whiz?
However, to make the most of them, you need to
understand how they work, or they may become
your nightmare.
A quick example that comes to mind is --
dangerously-skip-permissions.
While it's incredibly useful for streamlining your
workflow, you need to be very careful with it. Use it
wrong, and you could find yourself in serious
problems.
But these commands are what separate the casual
Claude Code users from the power users.
They’re the difference between copy-pasting AI
suggestions and having an AI teammate that gets
your workflow.


---
*Page 3*


If you are completely new to Claude Code, you can
start here, where I shared the most basic starting kit,
but if you are already using Claude Code, you may
benefit from my other Claude Code tutorials here.
Now, let’s explore these 12 commands that’ll make
you better at using Claude Code in your Workflow.
1.
--dangerously-skip-permissions
What it does: Bypasses all permission prompts,
letting Claude work autonomously without asking


---
*Page 4*


for approval on every file edit or command
execution.
The magic: Imagine telling Claude to “refactor this
entire module” and actually being able to grab
coffee while it works, instead of coming back to
find it stuck on “Can I edit this file?” for the 47th
time.
The danger: As the name suggests, this is
dangerous. Claude could run destructive
commands or make unwanted changes across your
entire codebase without your oversight.
Use it when: You’re working on non-critical
projects, have good git hygiene, and trust Claude’s
judgment. Never use this on production code or
when you’re unsure about Claude’s proposed
changes.
Pro tip: Start your session with Command+C then run
claude --dangerously-skip-permissions for that
sweet, sweet autonomous coding experience.


---
*Page 5*


2. : The Token Detective
/context
What it does: Provides a detailed token breakdown
across MCP tools, Custom Agents, and memory
files to optimize your Claude Code performance.
The magic: Ever wondered why Claude seems slow
or gives shorter responses? This command reveals
exactly where your tokens are going — whether it’s


---
*Page 6*


bloated CLAUDE.md files, excessive conversation
history, or memory-hungry sub-agents.
The danger: Information overload — You might
spend more time optimizing token usage than
coding.
Use it when: Claude feels sluggish, you’re hitting
token limits, or you want to optimize your setup for
maximum efficiency.
3. : Your Personal AI Army
/agents


---
*Page 7*


What it does: Creates specialized sub-agents with
their own instructions, context windows, and tool
permissions for specific tasks like code review,
testing, and documentation.
The magic: Instead of one Claude trying to do
everything, you get a specialized team. Your Code
Reviewer agent focuses purely on quality, your Test
Engineer agent thinks only about edge cases, and
your Documentation Writer agent makes your code
readable.


---
*Page 8*


The danger: Agent sprawl — too many specialized
agents can lead to conflicting advice and context
fragmentation.
Use it when: Working on complex projects where
you need different perspectives, or when you want
to maintain separation of concerns in your AI
workflow.
Pro tip: Start with just 2–3 agents max. Quality over
quantity always wins.
4. : Your Automated PR
/install-github-app
Reviewer


---
*Page 9*


What it does: Sets up Claude to automatically
review your pull requests.
The magic: As you use more AI tools, your PR
volume increases dramatically. This command
ensures every PR gets a consistent, thorough
review without burning out your human reviewers.
The danger: Over-reliance on AI reviews might
cause you to miss subtle issues that require human
intuition.


---
*Page 10*


Use it when: You’re pushing multiple PRs daily and
need consistent review coverage, especially for
personal projects or small teams.
5. : The Automation
--output-format json
Gateway
What it does: Makes Claude’s responses machine-
readable for scripting and automation workflows.


---
*Page 11*


The magic: Chain Claude Code with other tools in
your pipeline. Parse responses, feed them into
other systems, or build complex automation
workflows.
The danger: You might get lost in over-engineering
automation instead of focusing on core
development tasks.
Use it when: Building CI/CD integrations, creating
custom tooling, or when you need to process
Claude’s output.
6. : For the Modal Warriors
/vim


---
*Page 12*


What it does: Enables vim-style editing within
Claude Code.
The magic: Brings the power and efficiency of
modal editing to your AI conversations. Navigate
and edit with vim keybindings.
The danger: Vim learning curve applies here too. If
you’re not already a vim user, this might slow you
down rather than speed you up.
Use it when: You’re a vim power user who can’t
function without modal editing, even in AI tools.


---
*Page 13*


7. : The Integration Whisperer
--mcp-debug
What it does: Reveals detailed debugging
information for MCP (Model Context Protocol)
configuration issues.
The magic: When your external integrations aren’t
working and you can’t figure out why, this flag
shows you what’s happening behind the scenes.


---
*Page 14*


The danger: Debug output can be overwhelming
and might expose sensitive configuration details in
logs.
Use it when: Setting up complex MCP integrations
with tools like Jira, Google Drive, or custom APIs.
8. Command Prefix: The Token Saver
!
What it does: Bypasses Claude’s conversational
mode for direct shell command execution.


---
*Page 15*


The magic: Instead of Claude interpreting and
explaining every command, it just runs it. Saves
tokens and gets faster results.
The danger: Less context about what commands
are doing, which might lead to confusion or
unexpected results.
Use it when: You know exactly what commands
you want to run and don’t need Claude’s
interpretation or explanation.
Example: !git status instead of "Can you check
the git status?"
9. vs : Strategic Memory
/compact /clear
Management


---
*Page 16*


What it does: /compact summarizes conversation
history while /clear gives you a completely fresh
start.
The magic: Strategic context management lets you
maintain relevant information while pruning
unnecessary details. Think of it as Marie Kondo for
your AI conversations.
The danger: Compacting might lose important
nuances, while clearing loses all context.


---
*Page 17*


Use it when: Your conversation is getting unwieldy,
but you don’t want to lose all context (/compact), or
when starting a completely different task (/clear).
10. Custom Hooks with
: The Automation Ninja
$CLAUDE_PROJECT_DIR
What it does: Automatically runs commands
before/after tool execution, with access to the
project directory environment variable.


---
*Page 18*


The magic: Set up workflows that automatically
format code, run tests, update documentation, or
perform security checks whenever Claude makes
changes.
The danger: Hooks can slow down Claude’s
workflow or fail unexpectedly, breaking your
development flow.
Use it when you have consistent post-processing
needs, such as code formatting, linting, or
automated testing.
Example: Auto-format Python files after Claude
modifies them.
11. Shift+Drag File References: The
Context Master


---
*Page 19*


What it does: Hold Shift while dragging files to
properly reference them in Claude instead of
opening them in new tabs.
The magic: Seamlessly add file context to your
conversations without cluttering your workspace
with open tabs.
The danger: Easy to forget the Shift key and end up
with a workspace full of unwanted open files.
Use it when: You need to reference multiple files in
your conversation with Claude.


---
*Page 20*


12. Double Escape Message Navigation:
The Time Traveler
What it does: Press Escape twice to show a list of
all previous messages you can jump back to in the
conversation.
The magic: Quickly navigate to any point in your
conversation history without scrolling through
everything.


---
*Page 21*


The danger: It can be distracting and pull you away
from your current task.
Use it when: You need to reference something
Claude said earlier or want to fork your
conversation from a previous point.
The Real Magic: Combining These
Commands
The true power isn’t in using these commands
individually but in strategic combinations.
Here’s a real-world workflow that showcases their
synergy:
1. Start with --dangerously-skip-permissions for
autonomous work
2. Use /agents to set up specialized reviewers
3. Leverage custom hooks for automatic formatting
4. Use /context to monitor token usage


---
*Page 22*


5. Apply ! prefix for direct command execution
6. Use /compact strategically to maintain context
Final Thoughts
These commands can transform your Claude Code
experience, but they require knowledge to use
effectively.
First, understand each command’s implications, and
gradually incorporate them into your workflow. The
goal isn’t to use every command, but to use the
proper commands for your specific needs.
Master the basics first, then selectively add these
power features as they solve real problems in your
workflow.
Your journey to Claude Code mastery starts with
understanding not just what these commands do,
but when and why to use them.


---
*Page 23*


Pick one command from this list, experiment with it
on a non-critical project, and gradually make it part
of your workflow.
Before you know it, you’ll be a Claude Code whiz.
Let’s Connect!
If you are new to my content, my name is Joe
Njenga
Join thousands of other software engineers, AI
engineers, and solopreneurs who read my content
daily on Medium and on YouTube where I review the
latest AI engineering tools and trends. If you are
more curious about my projects and want to receive
detailed guides and tutorials, join thousands of other
AI enthusiasts in my weekly AI Software engineer
newsletter
If you would like to connect directly, you can reach
out here:


---
*Page 24*


AI Integration Software Engineer (10+
Y E i )
Software Engineer specializing in AI
i t ti d t ti E t i
njengah.com
Follow me on Medium | YouTube Channel | X |
LinkedIn
Claude Code Claude Agentic Workflow
Anthropic Claude Agentic Ai
Written by Joe Njenga
Following
20K followers · 98 following
Software & AI Automation Engineer, Tech Writer
& Educator. Vision: Enlighten, Educate, Entertain.
One story at a time. Work with me:
mail.njengah@gmail.com
Responses (6)


---
*Page 25*


To respond to this story,
get the free Medium app.
John Wong
Sep 24, 2025
Well written article. Great work. Your tips will help my coding working.
1
Sebastian Buzdugan
Mar 14
love the idea of power-user flags, but i wish tools like claude code had a
built-in “safety dry run” mode before something like `--dangerously-
skip-permissions` actually executes
Mahrukh Aleem
Mar 1
Really helpful - Thanks
See all responses


---
*Page 26*


More from Joe Njenga
In by Joe Njenga
AI Software Engi… Joe Nje…
Everything Claude
Why Claude Weekly
C d Th R Th t
Li it A M ki
If you slept through this or
Yesterday, I finally hit my
i d t E thi Cl d
kl Cl d li it d I
Oct 19, 2025 Jan 22


---
*Page 27*


In by In by
AI Software Engi… Joe Nje… AI Software Engi… Joe Nje…
Anthropic Just Solved Claude Can Now Create
AI A t Bl t 150K C l Di
Anthropic just released We have come along with
t t t b ild l bl C b t Cl d '
Nov 6, 2025 Mar 12
See all from Joe Njenga
Recommended from Medium
In by Reza Rezvani
Bootcamp nardaimonia


---
*Page 28*


What Claude Cowork AI Agent Skills at Scale:
t ll d Wh t B ildi 170
The complete breakdown of The AI skills ecosystem is
h t it h dl h t t it i i th d
Mar 7
Mar 13
Madhuranga Rathnayaka Alex Rozdolskyi
Massive Upgrade by 5 OpenClaw
Cl d C d A t ti Th t G
It upgraded your computer We don’t have bandwidth” is
l C b t ll d b i td t d
Mar 26 Feb 16


---
*Page 29*


Vishal Mysore Marco Kotrotsos
Spec-Driven The Biggest Job
D l t M t C ti E t Si
Most software specifications 92 Million Jobs Will Disappear.
itt f h Th t’ B t 170 Milli Will R l
Mar 11 Mar 11
See more recommendations