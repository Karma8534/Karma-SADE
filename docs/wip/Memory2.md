# Memory2

*Converted from: Memory2.PDF*



---
*Page 1*


Open in app
11
Search Write
UX Planet
Member-only story
Claude Code Memory
2.0
Exploring the Claude Code Auto-dream
Nick Babich Following 5 min read · Mar 25, 2026
154


---
*Page 2*


Claude Code Memory is one of the most important,
yet often overlooked, parts of Claude’s
performance. Why? Because bad memory → bad
outputs (yes, just like in real life).
In this article, I want to explain what memory
means conceptually in Claude Code, how to
configure it for your project, and what recent
change the Anthropic team has made to improve
memory functionality.
What is Memory
Claude Code memory is the mechanism that lets
Claude understand your project, preferences, and
workflows across interactions, so you don’t have to
repeat context every time you try to solve a
particular task.
Claude Code memory = persistent
context the AI uses to make better
decisions.


---
*Page 3*


You can configure project memory settings with
the following command
/memory
This will show you details about the memory:
Memory modes (Auto-memory and Auto-dream)


---
*Page 4*


Memory types (User memory and Project
memory)
Memory modes
Auto memory
Auto memory is notes that Claude leaves for itself
while working with your project. These notes help
Claude better perform tasks in this project.
For example, if you ask Claude, “always annotate
functions in source code,” Claude will remember this
and save the instruction to its memory.
When Auto memory is ON, Claude automatically
saves useful context
When OFF → nothing is stored unless you
explicitly tell Claude to store
When Auto memory is ON, Claude Code will
analyze conversations and store the following:


---
*Page 5*


Your preferences (e.g., coding style,
frameworks)
Reusable instructions
Patterns in how you work
As a result, it will feel like Claude learns about you
over time without you repeating yourself.
Auto-dream
Auto memory is a great feature, but it has one
important downside: it can bloat memory with
many duplicate instructions over time, especially
when you work on a project for a long time.
Bloated memory files will slow Claude Code down
and can potentially lead to system bias.
To prevent that from happening, you need to
periodically review and “clean” the project
memory. Before Auto-dream, you typically did it
manually. But Auto-dream changed the way we
“clean” memory.


---
*Page 6*


Auto-dream is what I call Claude Code Memory
2.0. It’s a more advanced, experimental feature
that simulates human memory behavior.
When Auto-dream is ON → Claude periodically
reorganizes & refines memory
When OFF → memory stays exactly as saved
While Auto memory is Claude’s
adaptation to your behavior &
preferences, “dreaming” is memory
optimization.
From a technical point of view, when Claude
“dreams,” it runs an AI sub-agent that analyzes
Claude’s memory files in the background to
optimize project context. The agent deduplicates
memory and merges similar instructions, which
leads to more structured instructions.


---
*Page 7*


To enable Auto-dream, you need to type /memory,
select Auto-dream, and toggle it ON by hitting
Enter.
Once you do that, you will see a new status
indicator below your prompt input field.


---
*Page 8*


When Claude Code is dreaming, you will see “dreaming” in the status line.
Quick notes about Auto-dream
You can prompt Claude to describe what it’s
dreaming about in real time, and the tool will show
you a summary of its recent dreams:
/btw what are you dreaming about?
For example, in my case, it’s trying to optimize the
design for the sign-out page that it generated


---
*Page 9*


previously.
When Claude finishes dreaming, it will provide a
quick summary of the improvements it introduced
in the .md files for the current project.


---
*Page 10*


Auto-dream changes only memory .md files (like
MEMORY.md). It won't modify the source code; it only
changes instructions in the .md files.
Memory files location
User memory
User memory is a global memory that Claude
relies on when working with all your projects.
It’s located in your machine’s home directory:


---
*Page 11*


~/.claude/CLAUDE.md
It typically features:
Your personal preferences
Your workflows
Your habits
Example of an instruction you might want to add to
your user memory:
When explaining functional design decisions, explain
Project memory
Project memory is stored in:
~/CLAUDE.md


---
*Page 12*


CLAUDE.md is a file Claude constantly looks at when
working with your project. This file features
project-specific context, such as:
Architecture decisions
Folder structure
Design system rules
API patterns
CLAUDE.md Best Practices
10 Sections to Include in your CLAUDE.md
uxplanet.org
This memory is a set of instructions that helps
guide Claude when it works with your project. If
you have Auto memory set to ON, Claude will
refine CLAUDE.md as it works: it can append, refine,
or update the file based on what it decides is worth
remembering.


---
*Page 13*


As a result, CLAUDE.md evolves alongside your
project.
Best Approach to Working with Claude
Code Memory
Try to treat memory like code
Review it
Refactor it
Keep it clean
I follow a 3-step approach:
1. Start every project with a strong CLAUDE.md. Don’t
rely on Auto-memory at the beginning. Instead,
I run /init and manually refine CLAUDE.md
generated by Claude.
2. Turn ON Auto-memory once I finish refining
CLAUDE.md (I don’t trust Auto-memory blindly). I
try to review CLAUDE.md periodically to make sure
its relevant to my project.


---
*Page 14*


3. Use Auto-dream as your “cleanup engine”
(recently started using this feature to get rid of
temporary instructions)
Want to master Claude Code?
Check out my complete guide to Claude Code,
packed with highly practical insights on how you
can integrate it into your design process.
Claude Code: Practical Guide for Product
D i
Practical guide for product designers who
t t t Cl d C d It th
babich.gumroad.com
AI Design Artificial Intelligence Coding
Web Development
Published in UX Planet
Follow


---
*Page 15*


357K followers · Last published 4 hours ago
UX Planet is a one-stop resource for everything
related to user experience.
Written by Nick Babich
Following
142K followers · 60 following
Product designer & editor-in-chief of UX Planet.
Twitter https://twitter.com/101babich
No responses yet
To respond to this story,
get the free Medium app.
More from Nick Babich and UX Planet


---
*Page 16*


In by In by
UX Planet Nick Babich UX Planet Nick Babich
Top 7 Claude Code Top 10 Claude Skills
Pl i Y Sh ld T i
Claude Plugins are nice ways Claude, Anthropic’s AI
t t d h t Cl d d i t t h b f
Mar 9 Feb 19
In by In by
UX Planet Nick Babich UX Planet Nick Babich
Google Stitch for UI Claude Code Cheat
D i Sh t
“From idea to app” is the Complete set of commands to
l G l f it AI t li d il k
Dec 23, 2025 Mar 24
See all from Nick Babich See all from UX Planet
Recommended from Medium


---
*Page 17*


In by In by
UX Planet Nick Babich Bootcamp Michael Szeto
How to Prevent Claude I tried designing with
C d f C ti Cl d d Fi f
If you ask Claude to generate a A summary on my key take-
b f th i h t I h l d i
Mar 18 Mar 11
Michal Malewicz In by
Level Up Co… Sanjay Nelag…
My Complete Web
Claude Code Skills 2.0:
d i & b ild
Th W kfl U d
25 years of experience
A while back, I wrote about
d d i t th b t
Cl d C d Skill th
Mar 12 Mar 16


---
*Page 18*


In by In by
Data Science … Gao Dalie… Stackademic Usman Writes
How to build Claude The One Color Decision
Skill 2 0 B tt th Th t M k UI L k
If you don’t have a Medium Open any product that reads
b i ti thi li k t " i " Li St i
Mar 14 Mar 9
See more recommendations