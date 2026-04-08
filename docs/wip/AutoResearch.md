# AutoResearch

*Converted from: AutoResearch.PDF*



---
*Page 1*


Open in app
1
Search Write
Member-only story
How to 10x Your Claude
Skills Using Karpathy’s
Autoresearch Method
Code Coup Following 5 min read · Mar 18, 2026
25
Your Claude skills probably fail 30% of the time. You
just don’t notice. I used to think my Claude skills
were solid. Then I ran a simple test. Turned out my
landing page copy skills were passing their own
quality checks only 56% of the time.
Half the outputs were poor. Vague headlines.
Buzzword clutter. Weak CTAs. I was accepting


---
*Page 2*


mediocre results because I had nothing to
compare them against.
Then I discovered a method that automated this
process. No manual adjustments needed. No
prompt engineering sessions. I started it and
returned to a skill that improved from 56% to 92%
pass rate.
Here’s exactly how it works.
Where this idea came from


---
*Page 3*


Andrej Karpathy — co-founder of OpenAI, former
head of AI at Tesla, the guy who coined “vibe
coding” — released a method called autoresearch.
The concept is dead simple. Instead of you
manually improving something, an AI agent does
it in a loop:
1. Try a small change
2. Check if the result got better
3. Keep it if yes. Toss it if no
4. Repeat
He used it on machine learning code. But the
method works on anything you can measure.
Including Claude skills.
I took his method and turned it into a skill that
runs in Claude Code and Cowork. You say “run
autoresearch on my landing page skill” and it handles
everything else.


---
*Page 4*


Think of it like improving a recipe
You have a recipe that works great 7 out of 10
times. The other 3 times, something’s off.
Instead of rewriting the whole thing from scratch,
you change one ingredient. Cook it 10 times. Did it
get better? Keep the change. Worse? Put it back.
Change the next thing. Cook 10 more times. Better
or worse?
After 50 rounds, your recipe works 9.5 out of 10
times.
That’s autoresearch. Except:
The “recipe” is your skill prompt
The “cooking” is running the skill
The “tasting” is scoring the output


---
*Page 5*


The only thing you need to provide: a scoring
checklist
The agent needs to know what “good” looks like.
That’s your only job.
You give it a checklist of yes/no questions. Each
one checks a single specific thing about the output.
Think of it like a teacher grading papers — but
instead of “rate the writing 1–10” (vague,
inconsistent), you get:
Did the student include a thesis statement? Yes
or no.
Is every source cited? Yes or no.
Is it under 5 pages? Yes or no.
For a landing page copy skill, your checklist might
look like this:


---
*Page 6*


Checklist:
1. Does the headline include a specific number or res
(catches vague headlines like "Grow Your Business"
2. Is the copy free of buzzwords like "revolutionary,
"cutting-edge," "next-level"?
3. Does the CTA use a specific verb phrase?
(catches weak CTAs like "Learn More" or "Click Her
4. Does the first line call out a specific pain point
(catches generic openers like "In today's fast-pac
5. Is the total copy under 150 words?
(catches bloated pages that lose the reader)
3–6 questions is the sweet spot. More than that and
the skill starts gaming the checklist, like a student
who memorizes answers without understanding
the material.
When you start autoresearch, the agent walks you
through building this checklist. It asks what good
looks like, helps you turn vague feelings into
specific yes/no questions, and can even pull from
style guides you already have.


---
*Page 7*


How to run it
Step 1: Download the skill
Grab it here and drop it into your skills folder in
Claude Code or Cowork:
https://www.dropbox.com/scl/fi/57v11vtj9gzqz10yb
v7or/autoresearch.zip
Step 2: Pick the skill that annoys you most
The one where you get a great output half the time
and garbage the other half.
"Run autoresearch on my landing page copy skill."
Step 3: Answer 3 questions
The agent asks:
Which skill to optimize


---
*Page 8*


What test inputs to use (e.g., “write landing page
copy for an AI productivity tool”)
What your checklist questions are
Step 4: See your baseline score
The agent runs your skill and shows you where
you’re starting. Mine was 56%.
Step 5: A live dashboard opens in your browser
Score chart going up over time
Pass/fail breakdown per checklist question
A log of every change tried
Auto-refreshes every 10 seconds
Step 6: Walk away
The agent enters the loop. It analyzes what’s
failing, makes one small change to the skill
prompt, tests again, keeps or reverts the change,
then does it again.


---
*Page 9*


It stops when it hits 95%+ three times in a row — or
when you stop it manually.
Your original skill stays untouched. The improved
version saves as a separate file.
What actually happened to my landing page skill
56% → 92%. Four rounds of changes. Three kept,
one undone.
Here’s what the agent actually changed in my
prompt:
ADDED:
"Your headline must include a specific number or resu
Never use vague promises like 'Transform Your Busines
ADDED (banned words list):
"NEVER use: revolutionary, cutting-edge, synergy, nex
game-changing, leverage, unlock, transform."
ADDED:
A worked example showing a strong pain point opener
and a specific CTA - so the skill sees what good
looks like instead of guessing.


---
*Page 10*


TRIED (then undid):
Tighter word count - copy got too thin,
CTA quality dropped. Reverted.
That last one is important. The system catches
changes that seem like improvements in isolation
but hurt the overall output. It’s not just optimizing
one metric. It’s scoring the whole thing.
When it finished, I got:
The improved skill (saved separately)
A results log showing every round’s score
A changelog explaining every change — what
was tried, why, and whether it helped
A backup of my original skill
That changelog is the most valuable part. It’s a
complete record of what works and what doesn’t
for that specific skill. When smarter models come
out, you hand them that changelog and they pick
up right where the last agent left off.


---
*Page 11*


This works on way more than Claude skills
The method works on anything you can score:
Website speed One person ran this on page load
time. Changed one thing, measured the speed,
kept or reverted. Went from 1100ms to 67ms in 67
rounds.
Cold outreach Checklist: “Does it mention the
prospect’s company? Is it under 75 words? Does it end
with a specific question?” Let the agent run 50
variations.
Newsletter intros “Does the opener include a personal
detail?” and “Is it free of cliche phrases?” — let the
agent tighten your writing on autopilot.
If you can score it, you can autoresearch it.


---
*Page 12*


Go run it
Pick your worst-performing skill. Start
autoresearch. Come back to something that
actually works.
Download here:
https://www.dropbox.com/scl/fi/57v11vtj9gzqz10yb
v7or/autoresearch.zip
Claude Claude Code Anthropic Claude Claude Skills
AI
Written by Code Coup
Following
3.9K followers · 1 following
Code Coup: Seize the Code, Stage a Coup!


---
*Page 13*


No responses yet
To respond to this story,
get the free Medium app.
More from Code Coup
In by In by
Coding Nexus Code Coup Coding Nexus Tattva Tarang
I Trained an LLM on How to Run Qwen3.5
A l ’ N l E i L ll With Cl d
Every Apple Silicon Mac has You can run a full agentic
th t it th CP di t
Mar 10 Mar 10


---
*Page 14*


In by In by
Coding Nexus CodeBun Coding Nexus Code Coup
I’ve Been Daily Driving Most People Use
Q 3 5 27B Th Cl d Lik S h
Things are moving faster than I’ve spent the last few months
I t t th I h d ’t t hi l Cl d
Mar 8 Mar 12
See all from Code Coup
Recommended from Medium
Balu Kosuri Mihailo Zoin
I Turned Andrej 7 NotebookLM
K th ’ St t i t V if AI
By Balasubramanyam Kosuri Don’t just train AI conductors
t i l h h h
Mar 21 6d ago


---
*Page 15*


Marco Kotrotsos In by
AI Exploration Jo… Florian J…
Claude Code Dreams
dots.ocr: Turning
Claude’s hidden memory D t P i i t
At first glance, document
t b d t ld
i i ht l k lik OCR
Mar 27 Mar 25
Reliable Data Engineering Vikas Sah
Data Engineering After Build Your First Claude
AI Skill i 5 Mi t
I was few weeks into using
Cl d ’ C k d h
Mar 19 Mar 7
See more recommendations