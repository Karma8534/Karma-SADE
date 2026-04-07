# Stitch

*Converted from: Stitch.PDF*



---
*Page 1*


Open in app
11
Search Write
AI Software Engi…
Member-only story
I Tested The New
Google Stitch (And
Discovered The End of
Figma Is Near)
Joe Njenga Following 8 min read · Mar 26, 2026
102 2


---
*Page 2*


Not so long ago, I discovered Google Stitch and saw
the end of UI/UX design as we know it. Now, a few
days ago, the updated Google Stitch gave Figma’s
stock a ‘wake-up shock’ and 12% drop in value.


---
*Page 3*


This drop started the ‘end of Figma
trend’
Figma shares fell 8% the day after Google’s
announcement, then dropped another 4% the
following day. The stock is now down roughly 35%
this year and sitting nearly 80% below its post-IPO
high.
So,


---
*Page 4*


I set out to research, test, and show you what has
changed since our first Google Stitch review, when I
‘blindly’ designed a car dealership mobile app, habit
tracking app and more with zero design skills — it
was impressive.
If you missed that article, check it out here:
I Tested Google Stitch AI and Discovered (The End of
UI Designers)
Back then, Stitch was a simple text-to-UI experiment
that Google quietly launched at I/O 2025 while


---
*Page 5*


everyone was busy talking about Gemini 2.5.
It could generate screens from prompts, export to
Figma, and spit out HTML/CSS code that actually
worked.
It was a good prototyping tool.
Fast forward — Google has completely redesigned
Stitch from the ground up, and it now threatens the
existence of Figma in UI/UX design.


---
*Page 6*


They added :


---
*Page 7*


Infinite AI canvas
Design agent that reasons across your entire
project
Voice-powered design through Gemini Live
Instant prototyping, and a portable design system
format called DESIGN.md that lets you carry your
brand rules anywhere
Google is calling this “vibe design” — where you
describe what your product should feel like instead of
starting with wireframes.
And a quote from one of the most popular UI/UX
designers —
Gary Simon, a UI/UX designer with
over 20 years of experience and a
million subscribers on YouTube,
tested the new Stitch and found it
generating production-ready


---
*Page 8*


wireframes in minutes. The same
work that used to take designers
hours.
I wanted to test it and share with you what works,
what surprised me, and whether this update
signals the end of Figma — or if it’s just hype.
Google Stitch New Updates
When Google first launched Stitch at I/O 2025, it
was a single-purpose tool — type a prompt, get a UI
screen.


---
*Page 9*


Google Stitch Version 1.0
Google has turned Stitch into what they call an “AI-
native software design canvas,” and they shipped
five major features.
Here is a quick homepage UI tour :


---
*Page 10*


So what are the features in the new update?
1. Infinite AI Canvas
The new version introduces an infinite canvas
where you can drag in images, text, code snippets,


---
*Page 11*


competitor screenshots, and reference URLs — all as
context for the AI.
It's like a digital whiteboard that understands
everything you put on it.
If you already have a website you like the look of,
you can paste the URL into the canvas, and Stitch
will pull the colors, fonts, and styling from that site
to use in your designs.
For my first test, I gave it my website URL:


---
*Page 13*


It quickly built this clone on the canvas:


---
*Page 15*


This alone changes the workflow because you’re
no longer starting from a blank prompt — you’re
building context visually.
2. Design Agent + Agent Manager
Stitch now has a dedicated design agent that can
reason across your entire project’s history, screens,
iterations, and decisions you’ve made.
It doesn’t just generate one screen at a time anymore.
It understands the relationship between your screens
and maintains consistency across the full project.
Google also added an Agent Manager that lets you
explore multiple design directions in parallel
without losing track of any branch.
For my second test, I span multiple agents designing
different pages of my portfolio website :


---
*Page 17*


You can spin up different variations — say, a dark
theme version and a light theme version — and the
Agent Manager keeps them organized side by side.
This was completed very fast, and I could see the
practical use of the infinite canvas:


---
*Page 19*


For anyone who has ever lost a good design idea
because they iterated too far in one direction, this
is a big deal.
3. Voice-Powered Design with Gemini Live
You can now talk to Stitch using Gemini Live.
You speak to the canvas and the AI responds in real
time — making design changes, offering critiques,
and suggesting alternatives as you talk through your
ideas.


---
*Page 21*


It’s still in preview and slightly rough around the
edges, but the concept is clear: Google wants
designing to feel like a conversation with a colleague.
You can say things like “show me three different
menu layouts” or “change the color palette to
something warmer” and watch it happen live.
4. Instant Prototyping
In the old version, your designs were static — you’d
export them to Figma or code and handle the
interactivity.
Now, Stitch can take your static screens and stitch
them together (pun intended) into clickable,
interactive prototypes with a single click.


---
*Page 23*


Hit the “Play” button, and you can preview the full
app flow — on desktop, tablet, or phone — right
inside the tool.


---
*Page 25*


It can also auto-generate the next logical screen
based on what a user would tap, mapping out user
journeys without you having to plan every step
manually.
For rapid prototyping and stakeholder demos, this
cuts hours of work down to seconds.
5. DESIGN.md — The Portable Design
System
This feature might not sound exciting at first, but
for developers and teams working across multiple
projects, it could be the most impactful one.
DESIGN.md is an agent-friendly markdown file that
captures your entire design system — colors, fonts,
spacing, button styles, everything.


---
*Page 26*


You can extract a design system from any website
URL with one click, export it as a DESIGN.md file,


---
*Page 27*


and import it into any other Stitch project or
coding tool.
This means you build your brand’s design rules once
and carry them everywhere — into Cursor, Claude
Code, Gemini CLI, or any other coding agent that
supports it.
For teams and freelancers working on multiple
client projects, this is a serious time saver.
From Design to Code
Stitch now gives you multiple ways to get your
designs out of the tool and into production.
You can export to Figma with editable layers and
auto-layout intact. This means designers on your
team can still refine things
You can export to Google AI Studio, which takes
your Stitch designs and lets you add
authentication, databases, and backend logic


---
*Page 28*


You can download raw HTML and CSS code that
runs immediately in any browser.


---
*Page 29*


And you can export a full ZIP with all assets and
code bundled together.


---
*Page 30*


Google Stitch MCP Server
Google released a Stitch MCP server and SDK that
lets you plug Stitch into your coding workflow.
If you’re using Cursor, Claude Code, Gemini CLI, or
Antigravity, you can connect Stitch as an MCP
server, and your coding agent gets direct access to
your designs.
You add the Stitch MCP config to your coding
agent:
{
"mcpServers": {
"stitch": {
"command": "npx",
"args": ["@_davideast/stitch-mcp", "proxy"]
}
}
}


---
*Page 31*


Once connected, your coding agent can pull design
screens, extract HTML, and even build an entire site
by mapping your Stitch screens to routes.
The MCP server exposes tools like build_site,
get_screen_code, and get_screen_image
This is a very useful feature that
deserves a complete tutorial.
Final Thoughts
In this article, I have just scratched the surface;
there are tons of features, tips, and tricks that will
make Google Stitch your daily design-to-code tool.
So, Is This Really The End of
Figma?
After spending days researching, testing, and
building with the new Google Stitch, here are my


---
*Page 32*


thoughts:
Figma is not dead today. But it's definitely going to
feel the change, and in the future, it might as well
keep only the royal fans.
For developers, founders, and non-designers who
need to go from idea to working prototype fast, Stitch
is now a new, better option.
The combination of the infinite canvas, the design
agent, instant prototyping, and the MCP pipeline to
coding agent creates a workflow that Figma will
find hard to compete with.
Try it at stitch.withgoogle.com and let me know
what you build, and in the next tutorial, we will
cover a complete workflow comparison — Google
Stitch vs Figma side by side.
Let’s Connect!


---
*Page 33*


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
AI Integration Software Engineer (10+
Y E i )
Software Engineer specializing in AI
i t ti d t ti E t i
njengah.com
Follow me on Medium | YouTube Channel | X |
LinkedIn


---
*Page 34*


Figma Google Stitch UI Design Ui Ux Design
UX Design
Published in AI Software Engineer
Follow
3.3K followers · Last published 6 hours ago
Sharing ideas about using AI for software
development and integrating AI systems into existing
software workflows. We explores practical
approaches for developers and teams who want to
use AI tools in their coding process.
Written by Joe Njenga
Following
20K followers · 98 following
Software & AI Automation Engineer, Tech Writer
& Educator. Vision: Enlighten, Educate, Entertain.
One story at a time. Work with me:
mail.njengah@gmail.com
Responses (2)


---
*Page 35*


To respond to this story,
get the free Medium app.
Octavio Ortega
3 days ago
This only generates generic garbage
1
Parham Davari
5 days ago
As a software engineer, I strongly believe the latest update of Stitch is a
real game changer, when used in combination with Superpowers.
2
More from Joe Njenga and AI Software
Engineer


---
*Page 36*


Joe Njenga In by
AI Software Engi… Joe Nje…
Everything Claude
I Tested Cursor vs
C d Th R Th t
A ti it (I D ’t
If you slept through this or
After a week of rigorous
i d t E thi Cl d
t ti G l A ti it i
Jan 22 Dec 9, 2025
In by Joe Njenga
AI Software Engi… Joe Nje…
12 Little-Known Claude
Gemini CLI Skills Are
C d C d Th
H W k With Y
What if I told you there are
Yes, Gemini CLI now supports
Cl d C d
Skill b t d ’t k th
Jan 12 Sep 21, 2025
See all from Joe Njenga See all from AI Software Engineer
Recommended from Medium


---
*Page 37*


In by In by
UX Planet Nick Babich Bootcamp Michael Szeto
How to Prevent Claude I tried designing with
C d f C ti Cl d d Fi f
If you ask Claude to generate a A summary on my key take-
b f th i h t I h l d i
Mar 18 Mar 11
Reza Rezvani In by
Stackademic Usman Writes
Top 10 Claude Code
The One Color Decision
Q ti B i
Th t M k UI L k
The same three clusters keep
Open any product that reads
f i t ti
" i " Li St i
4d ago Mar 9


---
*Page 38*


In by UX Movement
Write A Catal… 𝐍𝐀𝐉𝐄𝐄𝐁…
The Best Mobile Layout
AI Business Ideas That
f C l D t
S ll N Will B
Fit any size table on a mobile
Why the next wave of AI
i f
Mar 23 Mar 24
See more recommendations