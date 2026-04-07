# ccDream

*Converted from: ccDream.pdf*



---
*Page 1*


3/26/26, 9:47 AM How I’m Using (New) Claude Code /dream & Auto Dream (To Never Lose Memory Again) | by Joe Njenga | Mar, 2026 | Medium
Member-only story
How I’m Using (New) Claude Code
/dream & Auto Dream (To Never
Lose Memory Again)
Joe Njenga Following 9 min read · Just now
3
https://medium.com/@joe.njenga/how-im-using-new-claude-code-dream-auto-dream-to-never-lose-memory-again-ba0575f2881a 1/21


---
*Page 2*


3/26/26, 9:47 AM How I’m Using (New) Claude Code /dream & Auto Dream (To Never Lose Memory Again) | by Joe Njenga | Mar, 2026 | Medium
Claude Code memory sucks at times, but they just shipped a new feature
that resolves your memory problems.
But first, remember last week I shared about Claude Code’s new memory slash
command?
If you missed it, here is the full article where I went into detail and
demonstrated how it works.
Claude Code Memory is great, but you may have come across a problem.
The longer you use it, the more it starts working against you. Contradictions
pile up, stale notes stick around, and Claude starts referencing things that no
longer apply.
https://medium.com/@joe.njenga/how-im-using-new-claude-code-dream-auto-dream-to-never-lose-memory-again-ba0575f2881a 2/21


---
*Page 3*


3/26/26, 9:47 AM How I’m Using (New) Claude Code /dream & Auto Dream (To Never Lose Memory Again) | by Joe Njenga | Mar, 2026 | Medium
The new dream feature is designed to fix this problem.
But when I started researching, I ran into some confusion right away.
There seem to be two things people are calling “Dream” — there is a /dream
slash command, and then there is something called Auto-Dream.
I first tried to see if there was a new command — /dream
When I ran that command, there was no such slash command, but it invoked a
Python resource management skill
https://medium.com/@joe.njenga/how-im-using-new-claude-code-dream-auto-dream-to-never-lose-memory-again-ba0575f2881a 3/21


---
*Page 4*


3/26/26, 9:47 AM How I’m Using (New) Claude Code /dream & Auto Dream (To Never Lose Memory Again) | by Joe Njenga | Mar, 2026 | Medium
(Which is not what we are talking about in this article :) —So, dont get confused)
But,
I kept seeing both (/dream and auto dream) mentioned (on X and blogs), yet
it was not immediately clear whether they are the same feature or two
different things.
It was clear that the /dreamslash command does not exist for the Claude Code
pro account for my current version 2.1.83
I, however, found out how this new dream feature works, and in this article,
I will clear up the confusion and show you how it works.
https://medium.com/@joe.njenga/how-im-using-new-claude-code-dream-auto-dream-to-never-lose-memory-again-ba0575f2881a 4/21


---
*Page 5*


3/26/26, 9:47 AM How I’m Using (New) Claude Code /dream & Auto Dream (To Never Lose Memory Again) | by Joe Njenga | Mar, 2026 | Medium
So, the first thing you should understand is the current state of Claude Code
memory and why it’s inefficient.
Claude Code Memory Problem
Auto-memory is one of Claude Code’s most useful features; it lets Claude
take notes on your project across sessions.
From my experience and testing the first few sessions, it works well. Then it
starts to break down.
The more you use it, the more the memory folder accumulates noise. Here
are some practical examples:
Contradictions — You told Claude to always use React in week one. Three
weeks later, you switched to Vue. Now both instructions exist, and Claude does
not know which one to follow.
Stale information — Debugging notes that reference files you deleted months
ago. Decisions that were reversed but never updated.
Relative dates — Claude saved a note saying “feature due next Friday.” That
note is now six months old and outdated.
Bloated index — The MEMORY.md index file gets loaded at the start of every
session. The bigger it gets, the more context it takes.
The memory that was supposed to make Claude smarter is now making it
slower and less accurate.
https://medium.com/@joe.njenga/how-im-using-new-claude-code-dream-auto-dream-to-never-lose-memory-again-ba0575f2881a 5/21


---
*Page 6*


3/26/26, 9:47 AM How I’m Using (New) Claude Code /dream & Auto Dream (To Never Lose Memory Again) | by Joe Njenga | Mar, 2026 | Medium
This is what happens when notes accumulate without any cleanup process.
The new dream is designed to clean up the memory.
So which works /dreamor auto dream?
Claude Code /dream and Auto-Dream
They are not the same feature, but they are designed to do the same job.
/dream — Manual Command
This is a slash command you run inside a Claude Code session.
When you trigger it, Claude runs a consolidation pass on your memory files —
cleaning up contradictions, merging duplicates, fixing stale dates, and
tightening the index.
You are in control of when it runs.
Auto-Dream — Automated Version
Auto-Dream does the same consolidation work, but in the background
between sessions.
It does not require a manual trigger but runs when two conditions are both
true:
https://medium.com/@joe.njenga/how-im-using-new-claude-code-dream-auto-dream-to-never-lose-memory-again-ba0575f2881a 6/21


---
*Page 7*


3/26/26, 9:47 AM How I’m Using (New) Claude Code /dream & Auto Dream (To Never Lose Memory Again) | by Joe Njenga | Mar, 2026 | Medium
At least 24 hours have passed since the last cycle
At least 5 sessions have been completed since the last cycle
If you open Claude Code right now and run/memory, you will likely see it
listed — Auto-dream: off · never.
It is there in the UI, but it is currently gated behind a feature flag and not yet
live for most users.
The /dream command, on the other hand, is available, though not through a
built-in Anthropic release.
The prompt behind it is public on GitHub, which means you can build it as a
skill and use it right now. More on that in a moment.
https://medium.com/@joe.njenga/how-im-using-new-claude-code-dream-auto-dream-to-never-lose-memory-again-ba0575f2881a 7/21


---
*Page 8*


3/26/26, 9:47 AM How I’m Using (New) Claude Code /dream & Auto Dream (To Never Lose Memory Again) | by Joe Njenga | Mar, 2026 | Medium
Think of it this way: /dream is the manual switch, Auto-Dream is the same
switch set to run on a schedule.
Testing Claude Code /dream
I began by running this prompt :
Create a new skill called dream. Here is the system prompt to use as the basis:
You are performing a dream — a reflective pass over your memory files.
Synthesize what you've learned recently into durable, well-organized memories
so that future sessions can orient quickly.
Run in 4 phases:
Phase 1 — Orient: ls the memory directory, read MEMORY.md, skim existing topic files
Phase 2 — Gather recent signal: check daily logs, look for drifted facts, grep trans
Phase 3 — Consolidate: merge duplicates, convert relative dates to absolute, delete
Phase 4 — Prune and index: rebuild MEMORY.md under 200 lines, remove stale pointers,
Return a summary of what changed.
 
https://medium.com/@joe.njenga/how-im-using-new-claude-code-dream-auto-dream-to-never-lose-memory-again-ba0575f2881a 8/21


---
*Page 9*


3/26/26, 9:47 AM How I’m Using (New) Claude Code /dream & Auto Dream (To Never Lose Memory Again) | by Joe Njenga | Mar, 2026 | Medium
https://medium.com/@joe.njenga/how-im-using-new-claude-code-dream-auto-dream-to-never-lose-memory-again-ba0575f2881a 9/21


---
*Page 10*


3/26/26, 9:47 AM How I’m Using (New) Claude Code /dream & Auto Dream (To Never Lose Memory Again) | by Joe Njenga | Mar, 2026 | Medium
It crafts this dream skill that you can copy manually into your skills folder:
# Dream Skill
## Purpose
A reflective memory consolidation pass. Synthesizes recent learnings into durable, w
## When to Use
Activate this skill when the user says:
- "dream"
- "/dream"
- "consolidate my memories"
- "clean up memory"
- "organize memories"
## Instructions
You are performing a dream — a reflective pass over your memory files. Synthesize wh
Run in four phases:
### Phase 1 — Orient
- `ls` the memory directory (`~/.claude/projects/*/memory/`)
- Read `MEMORY.md`
- Skim existing topic files to understand current state
### Phase 2 — Gather recent signal
- Check for drifted facts — stale dates, references to files that no longer exist
- Grep transcripts or logs narrowly, only when needed to resolve ambiguity
- Look for contradictions between memory files and current codebase state
### Phase 3 — Consolidate
- Merge duplicate memories covering the same topic
- Convert relative dates to absolute dates (e.g., "last Thursday" → "2026-03-20")
- Delete facts contradicted by newer information
- Update stale file paths, function names, or flags that no longer exist
### Phase 4 — Prune and index
- Rebuild `MEMORY.md` to under 200 lines
- Remove pointers to deleted or merged files
- Add pointers for any new memory files created
- Keep each `MEMORY.md` entry to one line under 150 characters
Return a brief summary of what changed: files merged, facts updated, stale entries r
 
https://medium.com/@joe.njenga/how-im-using-new-claude-code-dream-auto-dream-to-never-lose-memory-again-ba0575f2881a 10/21


---
*Page 11*


3/26/26, 9:47 AM How I’m Using (New) Claude Code /dream & Auto Dream (To Never Lose Memory Again) | by Joe Njenga | Mar, 2026 | Medium
https://medium.com/@joe.njenga/how-im-using-new-claude-code-dream-auto-dream-to-never-lose-memory-again-ba0575f2881a 11/21


---
*Page 12*


3/26/26, 9:47 AM How I’m Using (New) Claude Code /dream & Auto Dream (To Never Lose Memory Again) | by Joe Njenga | Mar, 2026 | Medium
Once the skill is created, run /dream in your session
How Claude Code Dream Works
It works in four phases:
Phase 1 — Orient
Dream starts by surveying what already exists. It reads your MEMORY.md index,
lists the memory directory, and skims existing topic files.
This prevents it from creating duplicates of things that are already there.
https://medium.com/@joe.njenga/how-im-using-new-claude-code-dream-auto-dream-to-never-lose-memory-again-ba0575f2881a 12/21


---
*Page 13*


3/26/26, 9:47 AM How I’m Using (New) Claude Code /dream & Auto Dream (To Never Lose Memory Again) | by Joe Njenga | Mar, 2026 | Medium
Phase 2 — Gather Recent Signal
Dream does not read all your session transcripts — that would be slow and
expensive.
Instead, it looks at your daily logs first, then checks for any facts in your
existing memories that might have drifted from what is in your codebase
now.
If it needs specific context, it uses targeted grep searches on your JSONL
transcript files rather than reading them in full.
Phase 3 — Consolidate
This is where the cleanup happens:
Merges new information into existing topic files rather than creating near-
duplicates
Converts relative dates like “yesterday” or “next Friday” to absolute
timestamps
Deletes facts that have been contradicted
Updates anything that has drifted from the current state of the project
https://medium.com/@joe.njenga/how-im-using-new-claude-code-dream-auto-dream-to-never-lose-memory-again-ba0575f2881a 13/21


---
*Page 14*


3/26/26, 9:47 AM How I’m Using (New) Claude Code /dream & Auto Dream (To Never Lose Memory Again) | by Joe Njenga | Mar, 2026 | Medium
Phase 4 — Prune and Index
Dream rebuilds your MEMORY.md index with one rule: keep it under 200 lines.
The index is meant to be a lightweight pointer file, not a content dump.
Detailed information lives in the individual topic files.
At the end, Dream returns a summary of what it changed, merged, or removed.
If your memory was already clean, it says so and exits.
Final Thoughts
Auto-Dream is not live for most users yet, but you can start using it because
the Dream prompt is publicly available on GitHub.
You can build it as a Claude Code skill and run it manually as I demonstrated
above.
Building the Dream Skill
For a quick start, open Claude Code in any project and run:
Create a new skill called dream using the Dream memory consolidation prompt
from https://github.com/Piebald-AI/claude-code-system-prompts
https://medium.com/@joe.njenga/how-im-using-new-claude-code-dream-auto-dream-to-never-lose-memory-again-ba0575f2881a 14/21


---
*Page 15*


3/26/26, 9:47 AM How I’m Using (New) Claude Code /dream & Auto Dream (To Never Lose Memory Again) | by Joe Njenga | Mar, 2026 | Medium
Claude will pull the prompt, create the skill file, and you can trigger it
/dream
Running It
Once the skill is in place, you have three options depending on what you
want to consolidate:
/dream — runs consolidation on the current project's memory only
/dream user — runs it on your user-level memory, which applies across all
projects
/dream all — runs both at once
Start with /dream on a project that has several previous sessions. The more
history there is, the more it will find to clean up.
A reasonable approach is to run it after a long or complex session, or any
time you notice Claude referencing something outdated or contradicting
itself.
Once Auto-Dream is fully rolled out, this will likely become automatic.
Have you tried Claude Code /dream what is your experience? Let me know in
the comments below.
Claude Code Masterclass Course
https://medium.com/@joe.njenga/how-im-using-new-claude-code-dream-auto-dream-to-never-lose-memory-again-ba0575f2881a 15/21


---
*Page 16*


3/26/26, 9:47 AM How I’m Using (New) Claude Code /dream & Auto Dream (To Never Lose Memory Again) | by Joe Njenga | Mar, 2026 | Medium
Every day, I’m working hard to build the ultimate Claude Code course, which
demonstrates how to create workflows that coordinate multiple agents for
complex development tasks. It’s due for release soon.
It will take what you have learned from this article to the next level of
complete automation.
New features are added to Claude Code daily, and keeping up is tough.
The course explores Agents, Hooks, advanced workflows, and productivity
techniques that many developers may not be aware of.
Once you join, you’ll receive all the updates as new features are rolled out.
This course will cover:
Advanced subagent patterns and workflows
Production-ready hook configurations
MCP server integrations for external tools
Team collaboration strategies
Enterprise deployment patterns
Real-world case studies from my consulting work
https://medium.com/@joe.njenga/how-im-using-new-claude-code-dream-auto-dream-to-never-lose-memory-again-ba0575f2881a 16/21


---
*Page 17*


3/26/26, 9:47 AM How I’m Using (New) Claude Code /dream & Auto Dream (To Never Lose Memory Again) | by Joe Njenga | Mar, 2026 | Medium
If you’re interested in getting notified when the Claude Code course
launches, click here to join the early access list →
( Currently, I have 35,000+ already signed-up developers)
I’ll share exclusive previews, early access pricing, and bonus materials with
Open in app
people on the list.
Search Write
Let’s Connect!
If you are new to my content, my name is Joe Njenga
Join thousands of other software engineers, AI engineers, and solopreneurs who
read my content daily on Medium and on YouTube where I review the latest AI
engineering tools and trends. If you are more curious about my projects and
want to receive detailed guides and tutorials, join thousands of other AI
enthusiasts in my weekly AI Software engineer newsletter
If you would like to connect directly, you can reach out here:
AI Integration Software Engineer (10+ Years Experience )
Software Engineer specializing in AI integration and automation.
Expert in building AI agents, MCP servers, RAG…
njengah.com
Follow me on Medium | YouTube Channel | X | LinkedIn
https://medium.com/@joe.njenga/how-im-using-new-claude-code-dream-auto-dream-to-never-lose-memory-again-ba0575f2881a 17/21


---
*Page 18*


3/26/26, 9:47 AM How I’m Using (New) Claude Code /dream & Auto Dream (To Never Lose Memory Again) | by Joe Njenga | Mar, 2026 | Medium
Claude Code Claude Anthropic Claude Agent Memory Claude Ai
Written by Joe Njenga
Following
19.8K followers · 97 following
Software & AI Automation Engineer, Tech Writer & Educator. Vision:
Enlighten, Educate, Entertain. One story at a time. Work with me:
mail.njengah@gmail.com
No responses yet
Rae Steele
What are your thoughts?
More from Joe Njenga
https://medium.com/@joe.njenga/how-im-using-new-claude-code-dream-auto-dream-to-never-lose-memory-again-ba0575f2881a 18/21


---
*Page 19*


3/26/26, 9:47 AM How I’m Using (New) Claude Code /dream & Auto Dream (To Never Lose Memory Again) | by Joe Njenga | Mar, 2026 | Medium
InAI Software Engineer by Joe Njenga Joe Njenga
Why Claude Weekly Limits Are I Finally Tested Claude Code /voice
Making Everyone Angry (And… — It’s Faster than Typing (Don’t…
Yesterday, I finally hit my weekly Claude limit, Anthropic has now rolled out Claude Code
and I wasn't surprised, since I see dozens of… /voice to all users, and I have just tested it for …
Oct 19, 2025 706 62 Mar 13 217 4
Joe Njenga Joe Njenga
Everything Claude Code: The Repo 12 Little-Known Claude Code
That Won Anthropic Hackathon… Commands That Make You a Whiz
If you slept through this or missed out, What if I told you there are some Claude Code
Everything Claude Code hit 900,000 views o… commands that, although not very popular,…
Jan 22 526 4 Sep 21, 2025 379 6
See all from Joe Njenga
https://medium.com/@joe.njenga/how-im-using-new-claude-code-dream-auto-dream-to-never-lose-memory-again-ba0575f2881a 19/21


---
*Page 20*


3/26/26, 9:47 AM How I’m Using (New) Claude Code /dream & Auto Dream (To Never Lose Memory Again) | by Joe Njenga | Mar, 2026 | Medium
Recommended from Medium
Reza Rezvani huizhou92
Claude Code Channels: The Native Which Programming Language
OpenClaw Replacement. Here Ar… Should You Use with Claude Code?
A complete setup guide for Telegram and A benchmark across 13 languages reveals
Discord — with an honest comparison to… surprising patterns — and what it means for…
5d ago 26 7 Mar 11 782 46
InStackademic by Usman Writes InRealworld AI Use Casesby Chris Dunlop
Your AI Is Useless Without These 8 I Charge by the Hour in an Industry
MCP Servers — Most Developers… That’s Compressing Hours. Here’s…
Two engineers. The same AI model. One AI has compressed software development
copy-pastes files all day. The other connects… timelines, here is how I think about the world…
https://medium.com/@joe.njenga/how-im-using-new-claude-code-dream-auto-dream-to-never-lose-memory-again-ba0575f2881a 20/21


---
*Page 21*


3/26/26, 9:47 AM How I’m Using (New) Claude Code /dream & Auto Dream (To Never Lose Memory Again) | by Joe Njenga | Mar, 2026 | Medium
Feb 26 502 13 5d ago 200 6
Marco Kotrotsos InLevel Up Coding by Youssef Hosni
Claude Cowork Superpower Claude Code — MEMORY.md:
Unlock: Dispatch. Everything you need to know & ho…
OpenClawd returns :) Read the full article for free through this friend
link.
Mar 18 247 5 Mar 18 258 2
See more recommendations
https://medium.com/@joe.njenga/how-im-using-new-claude-code-dream-auto-dream-to-never-lose-memory-again-ba0575f2881a 21/21