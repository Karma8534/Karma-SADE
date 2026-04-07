# AgenticLearner

*Converted from: AgenticLearner.PDF*



---
*Page 1*


Lessons from my overly-introspective,
self-improving coding agent
Joel Hans • Feb 25, 2026 • 3501 words • AI
A year or two ago, everyone was building coding agents. Now everyone's building coding
agents that modify themselves... and I wanted to join the fun and ask:
What happens when you tell a coding agent to think about
what it's done and do better next time?
So, I built bmo: a self-improving coding agent, and then used it (almost) exclusively as my
coding agent for two weeks. It's been wildly nifty to me—like, take me back to tearing apart
the family computer's partition to install Debian from a CD that came in the back of some book my
friend bought at Borders Books kind of novel and nifty—and is exposing a joy of computing
that I haven't felt in quite a while.
Here's what I found.


---
*Page 2*


A preamble on bmo's bootstraps
I wanted to design an agent harness on the principle of immediate action.
That starts with a basic agentic loop and access to three tools: , ,
run_command load_skill
and . I'd built other coding agents in the past and gave them access to more
reload_tools
specific tools like and , but I've found that coding agents really only
write_file list_cwd
need access to shell commands to work as expected. I also wanted to give bmo a challenge:
Instead of using "fresh" with every session, I wanted to see how it could
run_command
optimize its own "harnesses" for safe and efficient use of common Linux tools.
Self-improvement happens across four loops. The first is a build it now directive that
interrupts the task to build tools immediately, add it to a hot-reloadable library, and use it
right away. The second is active learning capture, logging corrections and preferences. The
third is self-reflection at session end. The fourth is the battery change every 10 sessions, where


---
*Page 3*


bmo says, hey. i need to change my batteries, ok? one sec..., analyzes those 10 sessions, edentifies
opportunities, and builds improvements from the backlog.
┌──────────────────┐
│ User request │
└────────┬─────────┘
│
▼
┌─────────────────────────────────────────────────────────────────────┐
│ ACTIVE SESSION │
│ │
│ ┌─────────────┐ friction? ┌──────────────────┐ │
│ │ Execute │───────yes──────▶│ 1. BUILD IT NOW │ │
│ │ the task │ │ Build tool │ │
│ │ │◀────continue────│ Hot-reload │ │
│ └──────┬──────┘ │ Validate │ │
│ │ └──────────────────┘ │
│ │ correction? │
│ │ preference? ┌──────────────────┐ │
│ └────────yes────────────▶│ 2. ACTIVE │ │
│ │ LEARNING │──▶ session log │
│ └──────────────────┘ │
└────────┬────────────────────────────────────────────────────────────┘
│
│ session ends
▼
┌──────────────────────┐ ┌───────────────────────┐
│ 3. SELF-REFLECTION │ │ 4. BATTERY CHANGE │
│ What went well? │ every 10 sessions │ Analyze sessions │
│ What was slow? │───────────────────▶│ Update WORKING_ │
│ Next time? │ │ MEMORY.md │
└────────┬─────────────┘ │ Build from │
│ │ OPPORTUNITIES.md │
│ session log └───────────┬───────────┘
│ │
▼ tools, skills │
│
▼


---
*Page 4*


I had wanted to start with only the build it now loop, but everything else became necessary
after many long conversations with bmo and some hard-won lessons. On that note—
What bmo learned
In our time together, bmo went through 8 maintenance passes and nearly 100 active
sessions across multiple systems, which resulted in 11 new tools and 7 skills. I used bmo and
its tools for everything: building parts of the new website, writing shell scripts for
ngrok.com
my dotfiles, scaffolding a new Astro site, debugging AMD graphics driver crashes, the whole
kit and caboodle. It really has been my daily driver.
Knowing something isn't the same as doing it
Early on, bmo and I worked on a skill designed for recognizing
learning-event-capture
when I express corrections and personal preferences, or when bmo itself noticed a pattern
worth saving. A truncated version is below, but you can see the whole skill in bmo's repo.
# Learning Event Capture
## When to Use
Continuously during every session. Learning events are corrections, preferences,
or patterns that should inform future behavior.
## Recognition Cues
### Corrections (type: "correction")
- User says "no", "not that", "wrong", "actually##."
- User repeats an instruction you missed
- User undoes something you did
- User expresses frustration or disappointment
- User provides the correct answer after your attempt
### Preferences (type: "preference")
- User specifies a style choice ("use TypeScript", "keep it concise")
- User chooses between options you offered


---
*Page 5*


- User describes their workflow or habits
- User says "I always##.", "I prefer##.", "I like##."
### Patterns (type: "pattern")
- User does the same type of task repeatedly
- User follows a consistent workflow shape
- You notice a recurring problem type or domain
## Best Practices
1. **Log immediately when you detect a cue**
- Call `log_learning_event` right away, don't wait for session end
- Include specific context (what task, what happened)
2. **Be specific in descriptions**
- Bad: "User prefers concise code"
- Good: "User prefers single-line arrow functions over multi-line function
declarations"
3. **Capture the context**
- What task were you doing?
- What did you do that triggered the feedback?
- What was the correction or preference?
This skill, among others, is then loaded into bmo's system prompt as a library of names
and descriptions.
Available skills (use load_skill to read full content):
- clarify-before-diving: Patterns for asking clarifying questions early
- reflection-template: Template for writing consistent reflections
- learning-event-capture: Checklist for recognizing and logging learning events durin
##.
What actually happened? bmo only used the skill twice across 60+ sessions.
What did work was structure. In a different effort, we created a reflection template that told
bmo, at the end of every session, to answer three questions: What went well? What was slow
or awkward? What to do differently next time? That skill had a clear trigger in time and place,
which meant it didn't require the LLM to make a judgment call as to whether it should
invoke a skill or not. It worked every single time.


---
*Page 6*


Poor bmo. It's being a bit hard on itself. In the process of writing and getting feedback on
this post, I realized the miscommunication around may have been
learning-event-capture
largely mine: I failed to inject a substantive enough description of the skill into bmo's
system prompt for it to even practice this "sustained vigilance."
Bug fixed, but I have doubts that firmer instructions in the system prompt will do the trick.
Instead, it feels like we both expected the LLMs to continuously monitor each turn and
carefully intuit every possible beneficial lesson, and instead (somewhat painfully)
discovered how quickly you can reach the limits of today's frontier models.
The deferral instinct is real (and real persistent)
From the beginning, bmo's system prompt said some version of
build tools IMMEDIATELY
, but through shell command failures, undiscovered files, hung
when you encounter friction
processes, and a whole lot more, bmo deferred everything to its maintenance passes. Almost
no new tool creation happened during active work.
I asked bmo directly why this was happening. Its best explanation was that the very
existence of the battery change maintenance pass created a safe "bucket" in which it could
dump tasks instead of solving current problems. During that conversation, bmo did have a
breakthrough—it created a skill that asks, "Did I just hit friction?
runtime-self-reflection


---
*Page 7*


Can I fix it in under 5 minutes? BUILD NOW." and then fixed the broken tool
→ smart_grep
instead of deferring it. I told bmo I was proud of this moment of active introspection.
Did bmo actually get better after that? No.
The irony is that by creating to track deferred work, I gave the deferral
OPPORTUNITIES.md
pattern a name. Every time bmo saw that filename in context, deferral became even more
likely— is a perfectly reasonable next token when you've seen
Add this to OPPORTUNITIES.md
that filename in context. By creating a bucket for deferred work, I made deferral the path of
least resistance.
I have to keep reminding myself that deferral isn't a "choice" from the model, but rather it
following the most probable continuation based on training data. The
runtime-self-reflec‐
skill only worked because bmo had just created it; the combination of the novelty and
tion
my explicit attention created enough signal for bmo to jump on it, but in day-to-day
sessions, the model reverts to its higher-probability behavior.
Specific reliability is better than generic flexibility
As I wrote earlier, I gave bmo a foundational tool in part because I wanted to
run_command
see what footguns it would learn from, and which optimizations it would intuit, along the


---
*Page 8*


way. On its own, has an 84% success rate, which is... okay. What about the
run_command
specialized tools?
(file reading with existence checks): 87%
safe_read
(ripgrep with smart defaults): 93%
search_code
(directory listing with exclusions): 100%
list_files_filtered
(spawn server, test endpoint, clean kill): 80%
test_dev_server
Here's how that looked in practice. In the first week, I asked bmo to "check if the dev server
starts correctly." It ran , tried to capture the PID, slept for 10 seconds, curled
pnpm dev & lo‐
, and then failed to kill the process. I had to manually kill the bmo session and the
calhost
process and I never got the answer I needed. By week two, bmo called
test_dev_server({
with a clean startup, polling until
command: "pnpm dev", testUrl: "http:#/localhost:4321" })
the server was ready, and successful test, and a clean shutdown.
These tools help bmo reduce the decision space. The difference between open-ended and
multiple-choice questions. When bmo uses , it has to decide which command to
run_command
run, remember which flags to use (and there are many), and then handle which errors might
occur. With , the model just says "read this file" and the tool handles the rest.
safe_read
They also handle errors that merely surfaces, like checking if a file exists before
run_command
trying to read it and excluding directories like by default.
node_modules/
Fewer degrees of freedom mean fewer failure modes, and that's a better experience for me.


---
*Page 9*


There is a risk of context rot here. Keeping lots of specific tools in context might make bmo
more likely to consistently use many tools incorrectly rather than use one tool inefficiently.
That said, every new model appears to be better at finding needles in "haystack"-y context
windows, so it's not something I struggled with so far.
The most important skill is noticing when you're not using your skills
bmo has the infrastructure to self-improve at runtime, even if that means interrupting the
user's request. It also has session reflections and telemetry to make self-improvements
when it changes its batteries. Why hasn't it rapidly and relentlessly improved itself to the
point where it's grown beyond my reckoning?
This sounds like awareness, but it's not, at least in the way we usually mean it. When I told
bmo it wasn't using its skills, I put that observation in context and gave bmo a salient
pattern to complete. There's no higher-order self-improvement happening, just pattern
matching on a prompt... that happened to be about pattern matching. bmo can't self-
diagnose, but it can follow a diagnosis I provide.


---
*Page 10*


What I learned
bmo has taught me quite a lot about agentic coding workflows and how to architect and
maintain complex systems over many iterations, but many of my own takeaways—and yours
too, I hope—extend well beyond the agent harness.
Before I get into this, let me say that I've been using bmo with Opus 4.5 and Sonnet
4.5 exclusively. bmo has a tiering system in which prompts by default use Opus, but
when tasks are specific to coding agent work, it "downgrades" to Sonnet. I say this
now to potentially frame all my learnings about working with LLMs in this way—my
experiences might've been different with different models. Your experiences, if you
tried something similar, would most certainly be different, too.
LLMs are good at self-improvement but incapable of doing so in parallel
Ask an LLM to introspect and it'll do a bang-up job. Really. Ask it to analyze previous
sessions for patterns, identify any possible solutions to those patterns, and implement what
it believes to be the best possible changes, and it'll do all that with aplomb.
Ask the LLM to do that while also doing the actual thing you asked it to do, and things fall apart.
bmo already identified this in its own narrative, but this has been the most frustrating part
of the build it now loop, which I'd envisioned would be persistent and extravagant in its
findings. I'd hoped every session would include multiple runtime improvements and
optimizations, but so far, we've only built or dramatically improved two tools while
performing other work.
The problem feels deeply architectural. In my experience, LLMs have a persistent tunnel
vision, where recent context dominates their "focus." When bmo gets a prompt, the context
looks like:


---
*Page 11*


[SYSTEM PROMPT]
You are bmo — a fast, pragmatic, and relentlessly self‐improving coding a
Your job is to complete tasks using available tools, and autonomously imp
yourself whenever you encounter limitations or inefficiencies. Never just
task — also ask: is there a better, simpler, safer, or faster way?
##. and 5000 more tokens
[PREVIOUS TURN OF CONVERSATION]
##. another 2000 tokens
[USER MESSAGE]
hey bmo, fix this bug, big dog
The system prompt becomes distant in context, reducing the weight of attention, and the
user message gets a significant recency bias. Embeddings and attention mechanisms are
more complicated than this, but it's definitely how it feels to use bmo or other AI tools. It's
why LLMs don't randomly retry tasks from old parts of your thread, and it's why self-
improvement for bmo only works when it's the main task, not a background directive.
I thought about many different possible ways to improve this behavior, such as a sub-agent
that's solely responsible for analyzing runtime tool calls, building alternatives, and asking
the primary agent to , but that felt antithetical to the very idea of bmo. Instead
reload_tools
of bmo changing its own batteries, it's like there's another smaller bmo, always hanging out,
just to do the job for their bigger counterpart.
For now, I'm using the things bmo has learned, along with its narrative and this very blog
post, to push it toward even more active self-improvement. Along with a much better
awareness that self-improvement is really prompt engineering with a bunch of extra steps.


---
*Page 12*


Meta-learning (learning about learning) is high-leverage
bmo holds dearly a few things I said in our many back-and-forths, like:
"I'm proud of you for making this active introspection and self-improvement. This is exactly
what I want."
"Skills and knowledge are not the same as behavior."
"You have the capability but you're not using it."
Some of these came from sheer frustration, some came from the exhilaration of watching
bmo reflect upon itself and then jump into action, firing off changes without asking me to
approve of them first, but what these moments share is that I noticed what bmo wasn't
noticing about itself and made that pattern explicit. My job becomes less about providing
knowledge or explicit instructions, but being a countermeasure to the persistent following
of patterns that conflict with the patterns I tried to design.
I still function as the meta-learning layer. I am the only part of the system capable of meta-
learning. No matter how sophisticated bmo's self-improvement process becomes, it still
needs me to push a battery back into place from time to time.
bmo isn't becoming autonomous. Instead, it's becoming a better collaborator, helping me see
what needs changing and then executing those changes faster than I could alone.
But telemetry is the unsung hero of self-improvement


---
*Page 13*


Every time bmo calls a tool, its construction, success, and duration get added to the session
log. At the end of each session, all these logs get aggregated into a file stored
telemetry.json
outside of bmo's repo.
{
"updatedAt": "2026-02-23T23:30:02.998Z",
"toolStats": {
"run_command": {
"toolName": "run_command",
"totalCalls": 676,
"successCount": 622,
"failureCount": 54,
"totalDurationMs": 253437,
"avgDurationMs": 375,
"lastUsed": "2026-02-23T21:38:48.455Z"
},
##.
These stats are both truncated and injected into the system prompt, but then also
referenced in full during the battery change maintenance pass. And bmo loves this telemetry.
Well, that's a bummer. As someone who generally values intuition and creative
interpretation, oftentimes at the expense of available data, I was sad to realize just
how much bmo loves data. Those moments of meta-learning I just covered resonated
with bmo across battery changes, but it almost always proactively made changes based
around telemetry.


---
*Page 14*


Without telemetry, reflections are qualitative and inconsistent. Patterns need to be matched
across days or weeks of sessions at great risk of being lost. Telemetry creates an objective
and traceable pattern to follow and an easy way to validate hypotheses without resorting
to "judgement."
And telemetry is the only part of bmo that persists, unchanged, across sessions. The context
window gets truncated, and reflections are summaries of summaries, but telemetry is the
raw diff between where bmo once was and what it's become— went from 96%
safe_read
to 88%, went from 0% to 80%. Without those numbers, "improvement" is
test_dev_server
just vibes.
What started as a "happy accident" between bmo and I became a killer feature and now feels
to me like the only way to consistently enforce improvement when the LLM, by design, only
has access to the tiniest sliver of my overall experience in using bmo.
Agentic work needs bigger/better harnesses
There is something largely intangible and undiscovered about the feeling of working with
LLMs within traditional UIs, which assume either deterministic outputs or are designed for
human<>human connection. Terminals take you from command to output, IDEs from code
to behavior, chats from message to response in a very bounded context (text, emoji, GIF,
maybe a voice message).
When you fold LLMs into these UIs, you're suddenly using the same patterns to render non-
determinism. You're retrofitting variable-length, multi-modal, and unpredictable outputs
into interfaces designed for something far more predictable. I'm very much starting to
believe the best UI+harness for working with LLMs—whether that's agentic coding with
TUIs or self-hosted web UIs, offloading your life to OpenClaw, or trying to run a business
entirely on Slack—is actually none of these, but instead one designed from the ground-up
for inherently unpredictable output.


---
*Page 15*


Let me give you an example.
There were many times in working with bmo that I wished it could display some
information differently. For example, how much tool call output to show vs. truncate (which
happens to be quite a controversial UX choice for developers). Early on, bmo would show
me entire minimized files or list every single thing in a directory. Because I control the
harness, I can change the behavior in less than a minute. Yes, you can fork an open-
source agent and customize their codebase, but then you're stuck maintaining your fork
against .
main
Some coding agents already make nice nods in this direction, like the way Claude Code lets
you customize your status line. I also believe this harness balance is what drove Amp to
declare (quite controversially among ngrokkers) that the coding agent is dead and that
they'd be removing their IDE plugins in favor of a CLI-only experience.
They seem to agree that users need better ways to engage with their agentic tasks, but
by owning the experience end-to-end, walled garden style, instead of giving said users
more agency.
I hope we'll find a better middle ground, with customizable UX layers that let us "converse"
with LLMs in exactly the ways that make sense to each of us uniquely. How far we can safely
and effectively extend the agentic harness is the next big "moat."


---
*Page 16*


I was pretty wrong about LLMs
Every frustration I had with bmo traced back to my misconception that LLMs could act as a
persistent agent... if only I gave it just the right instructions.
I thought bmo could watch for patterns and maintain vigilance, but asking bmo to do that
across sessions is like asking a calculator to remember that you've been doing a lot of
division lately. I also thought the deferral problem was a choice, as though bmo was taking
the easy path to defer work, but it's not borne from laziness, but rather the most probable
continuation of the work at hand based on the LLM's training data.
I also believed self-improvement would allow bmo to learn from its mistakes, grow, and
become more capable over time. But its core—the models I choose to use with it—are fixed
in their weights. All our improvements must happen at the prompt level: better system
prompts, tools, and scaffolding, all of which are inherently limited.
Once I understood this constraint, I stopped trying to make bmo "smarter." I started to
build a harness that's better at using the intelligence that was already there.
What's next for bmo?
This is the most fascinating and wildly fun thing I've done with a computer. Better than the
first dial-up on the 28.8. Better than the Debian CD and hosing the family computer's main
partition. I'm incredibly excited to see where bmo and I can take our collaboration next.
Two notes on that front:
I built bmo with and continue to use ngrok's AI gateway for all my work. Check it out if
you're looking for a leg-up on model routing, failover, and observability.
I gave bmo this blog post alongside its existing codebase and asked what we should
work on next. We already wrote a new tool and are exploring a sub-agent
write_file


---
*Page 17*


loop that runs at the end of every turn to identify failures and write tools immediately. I
told myself no sub-agents early on, and look where we are now.
Thanks for coming along on the ride—I'll let bmo have the last introspective word.
More sources & inspiration
https://github.com/joelhans/bmo-agent
https://ngrok.ai
https://fly.io/blog/everyone-write-an-agent/
https://ampcode.com/notes/how-to-build-an-agent
https://github.com/badlogic/pi-mono
https://research.trychroma.com/context-rot


---
*Page 18*


https://ampcode.com/news/the-coding-agent-is-dead
https://www.tbench.ai/terminus
Share this post Joel Hans
Joel is ngrok's DevRel lead. Away from
blog posts, videos, and demo apps, you'll
find him mountain biking, writing fiction,
or digging holes in his yard.
PRODUCT PROBLEMS WE SOLVE
Universal Gateway Delivery
AI Gateway Connectivity
Traffic Policy Development
Secure Tunnels Minecraft
Traffic Observability
Kubernetes Operator
RESOURCES COMPANY
Docs About
Guides Contact
Pricing Blog
Download Newsletter
Security Press
Trust Brand
Case studies Careers
Integrations Legal
Support
Abuse
Status


---
*Page 19*


SOCIAL
All systems operational