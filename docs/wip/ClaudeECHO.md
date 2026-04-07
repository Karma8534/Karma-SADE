# ClaudeECHO

*Converted from: ClaudeECHO.pdf*



---
*Page 1*


3/3/26, 9:28 AM Claude Desktop Has a Hidden Feature | by Marco Kotrotsos | Feb, 2026 | Medium
Member-only story
Claude Desktop Has a Hidden
Feature
Anthropic is building an ambient screen monitor. They call it Echo.
Marco Kotrotsos Follow 7 min read · 5 days ago
229 6
https://kotrotsos.medium.com/claude-desktop-has-a-hidden-feature-6322a22ab625 1/16


---
*Page 2*


3/3/26, 9:28 AM Claude Desktop Has a Hidden Feature | by Marco Kotrotsos | Feb, 2026 | Medium
I use Claude alot. It writes with me, it codes with me, reviews my drafts,
helps me think through problems, takes care of administration, scheduling,
and tons more. It is the most embedded tool in my workflow. And at some
point, the question became unavoidable: what else is this application doing
on my machine?
So I cracked it open. Claude Desktop is an Electron app, and Electron apps
are JavaScript. The JavaScript is minified but not encrypted.
Open in app
https://kotrotsos.medium.com/claude-desktop-has-a-hidden-feature-6322a22ab625 2/16


---
*Page 3*


3/3/26, 9:28 AM Claude Desktop Has a Hidden Feature | by Marco Kotrotsos | Feb, 2026 | Medium
I pulled apart the app bundle, found the .vite/build/ output directory,2 and
Search Write
started reading through megabytes of obfuscated code. IPC channel strings,
preload scripts, native module bindings, tray icon assets, configuration
schemas. I read it the way a birdwatcher reads a forest: not looking for any
specific thing, just paying attention to what moves.
Over an hour it produced 19 documents covering over 300 IPC channels,
native modules written in four programming languages, internal
codenames, a full Linux VM system, an Office add-in, a government
deployment variant, and enough hidden infrastructure for three separate
products. Most of it was interesting.
One finding stopped me cold.
A 6.8-kilobyte file called echoWindows.js. Seventy-eight IPC channels for a
feature that does not appear anywhere in the UI.
Anthropic is building an ambient screen monitor. They call it Echo.
Finding Echo
The first thing I noticed was the tray icons. Two PNG files, EchoTrayActive
and EchoTrayTemplate, in three resolutions each. Active and idle states.
https://kotrotsos.medium.com/claude-desktop-has-a-hidden-feature-6322a22ab625 3/16


---
*Page 4*


3/3/26, 9:28 AM Claude Desktop Has a Hidden Feature | by Marco Kotrotsos | Feb, 2026 | Medium
That means a persistent system tray presence, something that sits in your
menu bar and signals whether it is watching.
Then the preload script. echoWindows.js exposes a window.echoApi object
through Electron's Context Bridge. I started cataloging the methods it
exposes, and the scope of the thing kept growing.
https://kotrotsos.medium.com/claude-desktop-has-a-hidden-feature-6322a22ab625 4/16


---
*Page 5*


3/3/26, 9:28 AM Claude Desktop Has a Hidden Feature | by Marco Kotrotsos | Feb, 2026 | Medium
The capture engine came first. Screen capture at configurable intervals, with
batch processing, quiet hours settings, weekend mode, and rate limiting per
hour. Fine. A screenshot tool. Maybe they were building something like
Rewind.
Then the activity tracker. Not just captures, but indexed activity. Query by
date. Browse a feed. An onActivityUpdate callback for real-time updates.
This was not storing screenshots. This was building a timeline.
Then the knowledge base. getKnowledge() returns stored entries.
deleteKnowledgeEntry() takes three parameters. Echo was not just recording
what I do. It was extracting what I know.
That was the moment the hair stands up. A screenshot tool is one thing. A
knowledge extraction system that watches your screen and learns from it is
something else entirely.
And it kept going. Behavioral goals: create a goal, update it, delete it, track
progress. Echo watches your screen and tells you whether you are living up
to your own intentions. Imagine setting a goal to spend less time in email,
and your computer quietly tracking whether you keep your promise. That is
not a feature. That is a mirror.
Proactive notifications. Not alerts you set up. Notifications Echo generates
based on patterns it detects. With a feedback mechanism so it learns which
interventions you find helpful. A “reflections” system for macro-level
analysis of your activity. A Slack integration called “Slack Pulse” that
monitors your messaging patterns.
https://kotrotsos.medium.com/claude-desktop-has-a-hidden-feature-6322a22ab625 5/16


---
*Page 6*


3/3/26, 9:28 AM Claude Desktop Has a Hidden Feature | by Marco Kotrotsos | Feb, 2026 | Medium
And at the center of it all, a conversational interface. Separate from the main
Claude chat. You can start conversations with Echo, resume them, browse
them by date. You can talk to it about what it has observed. Ask it what it
knows about you.
Not a Prototype
I have seen feature stubs left in production code. Half-implemented
experiments, placeholder strings, dead branches. Echo is not that.
https://kotrotsos.medium.com/claude-desktop-has-a-hidden-feature-6322a22ab625 6/16


---
*Page 7*


3/3/26, 9:28 AM Claude Desktop Has a Hidden Feature | by Marco Kotrotsos | Feb, 2026 | Medium
It has a dedicated onboarding flow. Four IPC channels for setup alone:
provide an API key, enable notifications, set an ignore list of apps or
windows you do not want captured, mark onboarding complete. Someone
designed a first-run experience. Someone thought about what the first sixty
seconds should feel like.
It has a prompt management system. Seven channels for creating, reading,
updating, deleting, and resetting prompts that control how Echo interprets
what it sees. It has a floating bubble widget with its own enable/disable
toggle and hover callbacks. It has a dashboard with tabs for activity,
conversations, notifications, knowledge, and settings, with a
onDashboardTabChanged callback.
It has three display modes. Auto-start on login. A configurable keyboard
shortcut for toggling it. The UI is not sketched. It is finished.
And it has its own API key. Not your Claude subscription credentials. A
separate key, provided during onboarding through a claude-echo-api-key
channel. An ambient monitoring system that processes screenshots
continuously would generate significant API traffic. A separate key makes
practical sense. But it also means Echo was designed as a distinct product
surface, not just a toggle inside Claude Desktop. This is not a feature. It is a
product-in-waiting. The separate API key is the business plan hiding in plain
sight.
The Privacy Architecture
What interested me almost as much as what Echo does is how carefully it
was designed to be turned off.
https://kotrotsos.medium.com/claude-desktop-has-a-hidden-feature-6322a22ab625 7/16


---
*Page 8*


3/3/26, 9:28 AM Claude Desktop Has a Hidden Feature | by Marco Kotrotsos | Feb, 2026 | Medium
Quiet hours with configurable start and end times. Weekend mode that
pauses capture entirely. Rate limiting with a per-hour cap. An ignore list set
during onboarding. Every setting has both a getter and a setter, meaning they
expected users to change these frequently.
These are not afterthought privacy controls bolted on before launch. They
are baked into the architecture from the first line of code. Whoever designed
Echo understood that an AI watching your screen sits on a razor’s edge
between helpful and invasive, and they tried to give you the off switch before
you asked for it.
The question is whether that is enough. A knowledge base that learns what
you know from watching what you do is a different category of data than
your chat history. Microsoft tried this- they killed it real quick because of
community backlash.
Chat is explicit. You chose to type that question. Screen monitoring is
ambient. It captures everything in its window, your email, your Slack, your
browsing, your code, your financial dashboards, whatever crosses your
screen during capture intervals.
The quiet hours and ignore lists acknowledge this tension. But the core
premise remains: Echo’s value comes from watching, and the more it
watches, the more useful it becomes.
The Bigger Picture
Echo was the most revealing find, but not the only one. The reverse
engineering uncovered an entire hidden infrastructure.
https://kotrotsos.medium.com/claude-desktop-has-a-hidden-feature-6322a22ab625 8/16


---
*Page 9*


3/3/26, 9:28 AM Claude Desktop Has a Hidden Feature | by Marco Kotrotsos | Feb, 2026 | Medium
Cowork, we all know and love is a full Linux VM system using Apple’s
Virtualization framework. Ubuntu 22.04.5 instances boot from 10-megabyte
disk images, run sandboxed in gVisor networking with a MITM proxy for
domain allowlisting, and create ephemeral user accounts per session. The
VM bundle on disk is 8.4 gigabytes.
Pivot is an Office add-in connecting Claude to Excel via WebSockets with
OAuth authentication and file read/write capabilities. FedStart is a
government deployment variant pointing to Palantir FedRAMP infrastructure
at claude.fedstart.com. Teleport migrates sessions to the cloud. Clod is a
minimal AI personality whose name accidentally leaked into the macOS
screenshot permission string across all 11 translations: "To capture
screenshots, Clod needs permission to record your screen."
The Claude Desktop app that most people see as a simple chat window is
running four compiled languages (Rust, Swift, Go, C), orchestrating virtual
machines, managing desktop extensions with a marketplace, hosting MCP
servers, bridging to browser extensions, and waiting for the feature flags to
flip on a screen monitoring AI.
This is a recreation of the Echo screens
https://kotrotsos.medium.com/claude-desktop-has-a-hidden-feature-6322a22ab625 9/16


---
*Page 10*


3/3/26, 9:28 AM Claude Desktop Has a Hidden Feature | by Marco Kotrotsos | Feb, 2026 | Medium
A recreation based on the information found.
What Echo Tells Us
Echo shows where Anthropic thinks the interface is heading. Not a chat box
you type into when you have a question. A persistent presence that watches,
learns, and speaks up when it has something to say.
This is the logical conclusion of every “AI assistant” pitch. If the assistant
only knows what you tell it, it can only help with what you remember to ask.
If it watches your screen, it knows your context without being told. It can
notice patterns you do not see yourself. It can warn you before you make the
same mistake twice. It can hold you accountable to the goals you set for
yourself.
https://kotrotsos.medium.com/claude-desktop-has-a-hidden-feature-6322a22ab625 10/16


---
*Page 11*


3/3/26, 9:28 AM Claude Desktop Has a Hidden Feature | by Marco Kotrotsos | Feb, 2026 | Medium
The question is not whether this technology will exist. It will. The question is
who you trust to build it, and whether you get to decide when it watches and
when it does not.
Echo might ship next month. It might stay dormant for years. Right now, it is
behind a feature flag, and the flag is off. But the architecture is complete.
The icons are in the bundle. The onboarding flow is designed. Someone at
Anthropic has already decided what Echo should feel like when you first
turn it on.
They just have not turned it on yet.
The complete reverse engineering documentation, covering all 19 areas of
the Claude Desktop app (v1.1.4088), is on
https://github.com/Kotrotsos/claude_echo.
AI Productivity Programming
Written by Marco Kotrotsos
Follow
1.4K followers · 410 following
Tech person. I write about technology, Generative AI, the cloud, design and
development. Deeper AND broader at acdigest.substack.com
https://kotrotsos.medium.com/claude-desktop-has-a-hidden-feature-6322a22ab625 11/16


---
*Page 12*


3/3/26, 9:28 AM Claude Desktop Has a Hidden Feature | by Marco Kotrotsos | Feb, 2026 | Medium
Responses (6)
Rae Steele
What are your thoughts?
Eduard Ruzga
3 days ago
Impressive digging.
Feature feels weird a bit.
I understand that they are going towards computer assistant but this part feels too... Uncontrollable.
50 Reply
David Allison SMACCPHhe/him
2 days ago
Sounds similar (as a non-techy guy) to Littlebird.ai
Reply
Sbayer
2 days ago
The claude desktop app in Mac feels like it is becoming over featured. I have used the app since it dropped
with every new preview. It feels like the first few iterations of the ipod, and then the iphone , the tech was
invisible to the user - magic… more
Reply
See all responses
https://kotrotsos.medium.com/claude-desktop-has-a-hidden-feature-6322a22ab625 12/16


---
*Page 13*


3/3/26, 9:28 AM Claude Desktop Has a Hidden Feature | by Marco Kotrotsos | Feb, 2026 | Medium
More from Marco Kotrotsos
Marco Kotrotsos Marco Kotrotsos
GPT-5.3 Codex Isn’t a Code Claude Cowork is a Game-Changer
Generator Anymore. Here’s What …
What Claude Code’s Consumer Sibling Means
One developer said they built more in four for the Future of Work
hours than they had in the previous week.…
Feb 8 559 6 Jan 16 355 12
https://kotrotsos.medium.com/claude-desktop-has-a-hidden-feature-6322a22ab625 13/16


---
*Page 14*


3/3/26, 9:28 AM Claude Desktop Has a Hidden Feature | by Marco Kotrotsos | Feb, 2026 | Medium
Marco Kotrotsos Marco Kotrotsos
Anthropic Is Running a Different The AI Agent Race is Over. The
Race Winner is a Folder.
OpenAI needs to do more than going to code Or; Agent Skills for the masses.
red.
Feb 18 281 10 Dec 12, 2025 737 9
See all from Marco Kotrotsos
Recommended from Medium
https://kotrotsos.medium.com/claude-desktop-has-a-hidden-feature-6322a22ab625 14/16


---
*Page 15*


3/3/26, 9:28 AM Claude Desktop Has a Hidden Feature | by Marco Kotrotsos | Feb, 2026 | Medium
InTowards AIby Felix Pappe Hams AI Tech
From Notes to Knowledge: The Claude Cowork for Lawyers /
Claude and Obsidian Second-Brai… Attorneys
How to combine human insight with AI The legal profession has always been
reasoning for next-level ideation document-intensive, deadline-driven, and…
Feb 7 92 3 Jan 27 56 1
Marco Kotrotsos InObsidian Observer by Theo Stowell
Anthropic Is Running a Different My Claude Code Now Has Its Own
Race Second Brain in Obsidian
OpenAI needs to do more than going to code How I turned it into a personal assistant that
red. lives in my Obsidian vault and learns my…
Feb 18 281 10 Feb 19 142 7
Ondrej Machart Pierce Lamb
Lessons From 13 Claude Code Building /deep-plan: A Claude Code
Projects That Changed My Produ… Plugin for Comprehensive Planning
From a printed gift for my dad to internal tool /deep-plan is a Claude Code plugin that
that helped top management make a tough… transforms vague requirements into detailed…
https://kotrotsos.medium.com/claude-desktop-has-a-hidden-feature-6322a22ab625 15/16


---
*Page 16*


3/3/26, 9:28 AM Claude Desktop Has a Hidden Feature | by Marco Kotrotsos | Feb, 2026 | Medium
Feb 13 275 6 Jan 16 177 7
See more recommendations
https://kotrotsos.medium.com/claude-desktop-has-a-hidden-feature-6322a22ab625 16/16