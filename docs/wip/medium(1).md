# medium(1)

*Converted from: medium(1).PDF*



---
*Page 1*


Open in app
Search Write
Pub Crawl is coming back, March 11–12! Register Now!
Vibe Coding
Image I created using Midjourney then edited with Figma
Member-only story
Every Developer Using
AI Needs This Tool (But


---
*Page 2*


99% Don’t Know It
Exists)
Specification framework that helps prevent AI
building crap code
Alex Dunlop Follow 4 min read · Sep 12, 2025
752 25
Recently, I’ve been wanting a solution to one of the
biggest problems in AI coding. Every project
requires manually writing detailed specification
files just to get AI tools to work properly, breaking
work into bite-sized chunks instead of an
unmanageable code mess.
I’ve been wasting time having to create these
markdown files for every new project, having to
create context documents that should be
automatic. This is frustrating because I constantly


---
*Page 3*


have to remember and add the same best practices
over and over again.
Not a Medium member? Keep reading for free by
clicking here.
Then GitHub quietly released SpecKit, I realised
they had solved one of the most frustrating parts of
AI development, this back and forth of trying to get
tools to build the way you want.
The great thing about SpecKit is it forces AI to
work in the structured way that tools like Claude
Code and Cursor recommend. It helps break things
into chunks and creates a tracking system.
Think of it like a Jira board, but for AI to track what
it’s working on. The AI creates its own little tasks,
manages and identifies what it’s doing, and
updates itself throughout the process. It’s like
having a little agile system that keeps the AI
focused.


---
*Page 4*


SpecKit GitHub repo explaination
This completely transforms how AI approaches
development. Instead of a mess, you get thought
out code.
How SpecKit Actually Works (The Four
Phases)
SpecKit splits development into four phases, each
with checkpoints. No more second guessing
whether you are using the right prompt.


---
*Page 5*


specify init project
Phase 1: Specify — You describe what you want
to build and your reasons. SpecKit generates a
detailed document with user stories and
acceptance criteria.
Phase 2: Plan — Time to define the tech stack
and some constraints. SpecKit will then create
an architectural plan.
Phase 3: Tasks — Everything will get broken into
numbered tasks. Creating a clear development
plan (like Jira).


---
*Page 6*


Phase 4: Implement — Now time to execute the
tasks one at a time. You can then review each
piece before moving onto the next.
SpecKit with Claude Code
I personally love using SpecKit inside of Claude Code!
Why This Helps Teams
I’ve seen what happens when AI tools lack clear
specifications. You get unclear results.
unclear prompts equal unclear results


---
*Page 7*


Features may get built, but we all know the failure
rate and quality isn’t viable. Technical debt is
becoming a bigger problem than we can seem to
handle, code is getting generated so fast that code
reviewing is becoming a much harder and more
important task.
SpecKit allows you to have a better system for
generating code in the first place, not just code but
the higher level of the project too.
I’m excited to try this one out on my next super
complicated project, but so far it’s been great on
the projects I have used so far.
Getting Started
First, install SpecKit:
uvx --from git+https://github.com/github/spec-kit.git


---
*Page 8*


Now choose your AI agent: SpecKit works with
Claude Code, GitHub Copilot, or Gemini CLI.
# For Claude Code
specify init my-project --ai claude
# For GitHub Copilot
specify init my-project --ai copilot
# For Gemini CLI
specify init my-project --ai gemini
# Or initialize in current directory
specify init --here --ai claude
Start building: Once you have run init, you now
have access to three commands:
/specify — describe what you want to build.
/plan — describe your tech stack.
/tasks — makes a list of tasks.
You Should Try It Out


---
*Page 9*


30 minutes: Take a feature idea and run it through
SpecKit. Notice the difference with these new
prompts.
2 hours: Build something using all four phases,
really thought out, try out a complex feature you
have been avoiding.
Weekend project: Have an open-source idea you
want to try out, use SpecKit to help you build (it’s
helped me so far).
At The End Of The Day
Vibe coding is great for MVP’s and getting results
fast, but production systems need to use
specifications.
SpecKit gives you a really good structured
prompting tool, instead of manually figuring it out
yourself and managing everything.
The cognitive load it takes off you is amazing and I
personally love the way it goes about this, GitHub


---
*Page 10*


really thought up a tool that I wanted.
This isn’t about removing developers, instead it’s
about being able to use AI CLI tools effectively. You
still need to instruct it and understand at the end
of the day.
SpecKit GitHub repo home banner
Try SpecKit:
SpecKit GitHub.
SpecKit walkthrough.


---
*Page 11*


What’s your biggest AI coding annoyance, how
have you gone about solving that issue?
Have you tried specification driven development
before, I would love to hear your feedback!
I’m not affiliated with GitHub, SpecKit, or any of the
tools mentioned. All opinions are based on my
experience as a senior engineer building AI products.
Programming Technology Software Engineering
Artificial Intelligence Data Science
Published in Vibe Coding
Following
3.6K followers · Last published Jan 29, 2026
Vibe Coders is where we share ideas that help shape
the future.
Written by Alex Dunlop
Follow
2.8K followers · 5 following


---
*Page 12*


Senior Engineer at Popp AI. Co-Founder at Cub.
Passionate about learning/collaborating. Trying to
leave a positive contribution for the dev community.
Responses (25)
To respond to this story,
get the free Medium app.
krishnareddy nandyala
Sep 17, 2025
code is getting generated so fast that code reviewing
is becoming a much harder and more important task.
Exactly! Recently one of my project related ASTM communication server
code generated by AI in 20 min, but I am reviewing, testing and bug fixing
since last 3 weeks. At one point I felt better to write my own step by step,
but even though there are… more
33
Bhojanapuharinanda
Sep 12, 2025
Great Tool at right time as per my requirements. I am struggling with you
kind of situation. Can you take up any work for you it may take hours. I


---
*Page 13*


have good experience with other things not python interpretations, I
don't know why I am not… more
24
MarketTrendz they/them/he
Sep 13, 2025
Good explanation. Need to try.
11 1 reply
See all responses
More from Alex Dunlop and Vibe Coding
In by In by
Vibe Coding Alex Dunlop Vibe Coding Alex Dunlop
Claude Code’s Creator, This Tool Gained 30K
100 PR W k Hi GitH b St i O
Simple principles most I kept putting off OpenCode.
d l l k 70K d l did ’t


---
*Page 14*


Jan 15 Jan 16
In by In by
Vibe Coding Alex Dunlop Vibe Coding Alex Dunlop
Our JetBrains Devs Cursor Changed How
S it h d t VSC d W C d Thi T l
They’re still complaining, How developers can become
h th h ’t d i
Jan 12 Jan 24
See all from Alex Dunlop See all from Vibe Coding
Recommended from Medium


---
*Page 15*


Reza Rezvani In by
AI Software Engi… Joe Nje…
I Tested Every Major
Anthropic Just
Cl d O 4 6
R l d Cl d C d
After 24 hours of real testing
Anthropic just launched their
d il kfl
Cl d C d i A ti
Feb 6 Jan 21
In by Agent Native
Product Not… Mohit Aggar…
Local LLMs That Can
The 2026 AI Agent
R l Cl d C d
R l ti 7 T l
Small team of engineers can
Forget chatbots. The real
il b >$2K/
l ti i AI t th t
Feb 3 Jan 20
In by In by
Women in Tech… Alina Kovt… Vibe Coding Alex Dunlop
Stop Memorizing Cursor Changed How
D i P tt U W C d Thi T l
Choose design patterns based How developers can become
i i t l th i h d i


---
*Page 16*


Jan 29 Jan 24
See more recommendations