# UsingAIRight

*Converted from: UsingAIRight.PDF*



---
*Page 1*


Open in app
2
Search Write
Artificial Corner
Member-only story Featured
You’re Using AI Wrong!
Here’s How to Be Ahead
of 99% of Users
The 3 levels of using AI in 2026.
The PyCoach Follow 8 min read · Feb 23, 2026
530 12


---
*Page 2*


Image made with ChatGPT
Read this article for free here
I’ve been using Claude, Claude Cowork, and Claude
Code a lot lately.
It’s the best AI I tried so far.
If it weren’t for the short daily usage limit (the $20
plan isn’t enough), I would’ve cancelled ChatGPT a
long time ago.


---
*Page 3*


Most people can’t get the most out of Claude
because they’ve been using ChatGPT for a long
time, so they:
Use Claude like ChatGPT. Like it’s 2023!
Think of prompt crafting, rather than systems
Have a big catalog of prompts that they rarely use
I’ve been there. You’re probably there too, and
there’s nothing wrong with that.
ChatGPT was our introduction to AI, so we learned
the ChatGPT mindset. In 2026, we need to shift this
mindset. In this guide, we’ll do that.
We’ll learn when and how to go from:
Prompts → .md files
Prompt libraries → Skills for repeatable
workflows
Chat windows → AI that executes


---
*Page 4*


I’ll break this into levels. Not everyone needs to
reach the final level, but I want to give you a sense
of what’s possible with a mindset shift.
Level 1: Prompts → .md files
Since ChatGPT’s release, we’ve been obsessed with
prompt engineering.
I wrote many guides teaching the best prompt
engineering techniques. They’re still relevant. But
here’s the thing.
Your best prompts saved on Notion are at the
“what to do” level.
Since 2023, the context window and agentic
capabilities evolved. Now we can go deep into the
“exactly how to do it” level.
This means we can go far beyond ‘Act as a writer
with 10 years of experience. Write about XYZ ’


---
*Page 5*


We can teach the AI how to create the article end-
to-end: our writing voice, how to structure each
section, which words to avoid, the format, etc. The
entire workflow becomes instructable, not just the
final ask.
All this info goes into an .md file (aka markdown
file).
An .md file is simply a text file.
The difference? A .txt file is flat. Markdown gives
you headings, code blocks, bold/italic text, and
organized lists. This structure helps AI (and us)
quickly find sections without having to read the
entire file top to bottom.
Here’s what a simplified .md file looks like for
capturing your writing voice:
# Blog Post Instructions
## Structure
- Start with a personal story (1-2 sentences max)


---
*Page 6*


- 3 tips only. No fluff. Each tip should have a real
- End with one clear takeaway the reader can apply to
## Writing Style
- Short paragraphs (2-3 sentences max)
- Use "you" more than "I"
- No corporate jargon. Write like you're texting a sm
- Never use: "In today's world", "Let's dive in", "Ga
## Formatting
- No bullet points inside the body (use them only for
- Bold only the first sentence of each tip
- Total length: 800-1000 words
Not all your prompts should be turned into an .md
file, though.
Think of .md files as recipes: write the instructions
once, and the AI follows them every time it runs
the task.
There are different ways to create an .md file:
You can create one manually from scratch (like
drafting a brief)
You can have AI interview you and generate it
from your answers


---
*Page 7*


You can generate them with Claude skills
I spent over an hour answering a 100-question
interview designed to capture my writing voice in
an .md file. The result is a detailed instruction set
for how I write guides. Now, anyone on my team
can upload that file and rewrite any draft in my
voice.


---
*Page 8*


Image by author
Writing an .md file takes time, but you only do it
once. And here’s the thing — you only need to write
a few manually (the ones that capture something
personal, like your voice or your process).
The rest? Claude skills can generate them in
seconds
Level 2: Prompt libraries → Skills
Skills are Claude’s cheat code.
They’re powerful when you have repeatable
workflows.
Instead of re-explaining your preferences and
processes in every conversation, skills let you
teach Claude once and benefit every time
Let’s take the “brand-guidelines” skill as an
example. With this skill, we can generate slides


---
*Page 9*


that copy Anthropic brand guidelines in one shot
(colors, design, etc):
Image by author
Skills produce outputs that are more consistent
and aligned with our standards
The best part? You don’t have to save skills in your
Notion database. No more copy-pasting. Claude
triggers a skill automatically when needed.
Here’s how to use skills in Claude
To work with Skills, enable it in settings.


---
*Page 10*


Go to Settings → Capabilities → Turn on Skills
Image by author
Go to “example skills“ to browse skills created by
Anthropic. Turn on any skill you want. Just make
sure “skill-creator“ is always enabled (that’s what
lets you build your own skill)
Image by author


---
*Page 11*


To create your own skill, just describe what you
need in plain English. Claude takes care of the rest.
Here’s a prompt you can try:
Help me create a skill that applies Google’s official
brand colors and typography to any sort of artifact
that may benefit from having Google’s look-and-
feel. It should be used when brand colors or style
guidelines, visual formatting, or company design
standards apply
Claude will generate a zip file (that’s the skill). To
add your new skill to Claude, do this:
Settings → Capabilities → Skills → Upload the zip file
Once a skill is added, you can either click on “try
on chat“ or let Claude trigger the skill when
necessary.
📚
Learn more about Claude skills:
artificialcorner.com/p/claude


---
*Page 12*


Level 3: Chat windows → AI that executes
Using ChatGPT is like being stuck in a chat bubble.
You type, ChatGPT responds. You upload a file,
ChatGPT processes it. Back and forth.
But what if AI could actually do things on your
computer? Not just generate text and code, but
read your files, run scripts, and build things end-
to-end.
That’s what Claude Code does.
Claude Code is a command-line tool where Claude
doesn’t just answer. It executes!
Claude Code allows us to structure our most
valuable tasks into well-defined projects. This
means you stop repeating the same instructions
over and over again. Here’s Claude Code’s high-
level structure to turn raw input into meaningful
output.


---
*Page 13*


Image by author
This might look intimidating, but it’s a
combination of many elements we’ve seen so far:
Remember the .md files from Level 1? Claude
Code uses a CLAUDE.md to store your project
structure, preferences, and past decisions. It
gives Claude context before a session starts
(without it, every interaction resets to zero, like
opening a fresh ChatGPT conversation)


---
*Page 14*


Remember the skills from Level 2? Claude Code
uses those too. Skills tell Claude how to execute
specific tasks.
With Claude Code, we build systems that give us
more control over what Claude produces. We
create pipelines that work the same way every
time.
Many non-technical users are afraid of Claude
Code because of the “code“ in its name.
You shouldn’t.
I have a series of Claude Code guides for non-
coders. Check it out here.
I know many of you aren’t technical, so I’ll show
you what Claude Code can do using Claude Cowork
as an example. Cowork is a simplified version of
Claude Code. It was built for non-technical people
who are afraid of working with the terminal.


---
*Page 15*


While ChatGPT requires you to be the middleman
who gathers and uploads context, Claude Cowork
does it itself.
Point Cowork at a folder on your machine and it
gets to work. If that folder has your reusable
instructions from Level 1, even better. Claude
reads them at the start of every session, so you’re
never starting from scratch. From there, Cowork
can:
Sort your downloads
Extract data from screenshots into spreadsheets
Draft reports from scattered notes
Execute multi-step workflows on its own
Here’s an example:


---
*Page 16*


This is just one example. For more, check out this
guide I wrote.
Here’s how to use Claude Cowork
Download Claude for desktop, install it, and open
the app.
At the top, you’ll see 3 options: Chat, Cowork,
Code. Choose Cowork. Choose Cowork


---
*Page 17*


Image by author
Try this prompt:
Click on “Organize files” (from the prompt
templates) and select a folder. You’ll get a prompt
like this:
Help me organize my Downloads folder. Scan the
contents and propose a plan:


---
*Page 18*


- Categories/folders to create
- How files should be sorted
- Any naming conventions to apply
- Files to flag for review or deletion
Show me the plan before making changes. Only
proceed after I approve.
After approving the plan, my downloads folder was
quickly organized.
Note: If you’re working with important files, back
up first. Just like any other AI, Claude Cowork can
make mistakes.


---
*Page 19*


Image by author
📚
My complete guide to Cowork:
artificialcorner.com/p/cowork
Note: Sooner or later, you might hit a wall with
Cowork. Cowork is a simplified version. Claude
Code is the full, unrestricted experience.
So, how to use Claude better than 99% of
people?
Adopt the new AI mindset
Explore each level. Without realizing it, you’ll
build the foundation for level 3
Instead of crafting the perfect prompt, build
systems that give you consistent, high-quality
results
Subscribe so you don’t miss my upcoming
Claude guides
Join my newsletter with 50K+ people to get weekly
guides like this


---
*Page 20*


Artificial Intelligence Technology Productivity
Data Science ChatGPT
Published in Artificial Corner
Follow
13.1K followers · Last published Feb 23, 2026
A Medium publication about AI, tech, programming,
data science and everything in between (We’re
currently not accepting new writers)
Written by The PyCoach
Follow
147K followers · 14 following
FREE AI Guides -> https://bit.ly/free-ai-guide
Responses (12)
To respond to this story,
get the free Medium app.


---
*Page 21*


Deborah Rosen
Feb 23
Really appreciate this encouragement and examples. I’ve used Claude
and have just started with the desktop version and now I’m excited to
dive in. I run a small business and need all the automation I can get. Keep
the examples coming!
18 1 reply
Axons Mobility
5 days ago
Really enjoyed this excellent breakdown of how most people use AI
reactively instead of strategically. The point about thinking in systems
rather than inputs resonates strongly. Insightful read!
2
Theo James
6 days ago
I love Claude and really enjoy Projects. I just put in the instructions and
most of the time it follows them pretty well. Claude Code seems pretty
complicated for me though.
1
See all responses


---
*Page 22*


More from The PyCoach and Artificial
Corner
In by In by
Artificial Corn… The PyCoa… Artificial Corn… The PyCoa…
The Best AI Tools for The Best ChatGPT
2026 P t f 2026
If you’re going to learn a new Here’s what actually helped
AI t l k it’ f t b tt ( ft
Dec 1, 2025 Jan 1
In by In by
Artificial Corn… The PyCoa… Artificial Corn… The PyCoa…
Forget AI Tools. These Clawdbot Is Taking The
3 AI A t Will AI C it b
Turn days of work in minutes Clawdbot will quietly run your
ith AI t di it l lif


---
*Page 23*


Jan 26 Jan 27
See all from The PyCoach See all from Artificial Corner
Recommended from Medium
In by In by
Personal Gr… Thomas Op… Data Science Col… Marina …
Careers Are Collapsing. Should You Still Learn
J b A D i Th t C d i 2026?
“Earn with your mind, not your The answer isn’t as obvious as
ti ” N l I d t b li
Feb 22 Feb 22


---
*Page 24*


In by Marco Kotrotsos
Artificial Intelligen… Tanma…
Coding Is Solved.
Everyone Is “Learning
AI” B t N b d R ll This Is How Programming Will
Prompting teaches you the
Ch
i t f AI lit
Jan 21 Feb 21
Will Lockett In by
Artificial Corn… The PyCoa…
OpenAI Is Totally
The Best AI Tools for
C k d
2026
What a s**tshow.
If you’re going to learn a new
AI t l k it’ f
Feb 23 Dec 1, 2025
See more recommendations