# ClaudeStudioPlujgin

*Converted from: ClaudeStudioPlujgin.PDF*



---
*Page 1*


Open in app
2
Search Write
From Terminal to
Dashboard: How
Claude Code Studio
Changes AI-Assisted
Development
Tiberiy Follow 7 min read · 2 days ago
3
What if your AI coding assistant had a visual
interface designed for real workflows?


---
*Page 2*


If you’ve been using Claude Code in a terminal,
you already know how powerful it is. Type a
prompt, watch it think, and see code appear. But as
your tasks grow more complex — multiple parallel
projects, long-running operations, team
coordination — the terminal starts to feel limiting.
That’s exactly the problem Claude Code Studio
solves. It’s an open-source web workspace that
wraps Claude Code in a visual interface designed
for real development workflows: Kanban boards
for task management, multi-agent orchestration,
project isolation, and SSH remote execution.


---
*Page 3*


Let me walk you through what it offers and why it
might change how you work with AI.
The Problem with Terminal-Only AI
There’s nothing wrong with the terminal. It’s fast,
lightweight, and gets out of your way. But when
you’re working with an AI assistant day in and day
out, certain friction points emerge:
Context management — Each terminal session is
isolated. Switch between projects, and you lose


---
*Page 4*


your place. Resume tomorrow, and you’re scrolling
through history to remember what Claude was
doing.
Parallel tasks — Want Claude working on three
things at once? Open three terminal tabs, manage
three separate sessions, manually coordinate what
goes where.
Task visibility — You queue up five tasks and walk
away. Two hours later, which ones finished? Which
ones failed? You’re reading scrollback to find out.


---
*Page 5*


Remote work — SSH into a server, run Claude
there, copy results back. Or forward ports, manage
sessions, hope the connection doesn’t drop.
Screenshots and files — “Look at this error” means
uploading an image somewhere, getting a URL,
pasting it. It works, but it’s not seamless.
Claude Code Studio doesn’t replace the terminal —
it extends it. You still get Claude’s full capabilities,
but now with infrastructure designed for sustained
work.
What Claude Code Studio Actually Does


---
*Page 6*


At its core, Claude Code Studio is a web interface
that spawns and manages Claude Code processes.
But the key is what it adds around that core:
Real-Time Chat Interface
Same Claude Code you know, but in a browser.
Type prompts, see responses stream in as Claude
thinks and works. Supports markdown, syntax-
highlighted code blocks, image pasting from
clipboard, file attachments via @filename`. Switch
between Claude models (Opus, Sonnet, Haiku)
depending on the task complexity.


---
*Page 7*


Kanban Board for AI Tasks
This is where it gets interesting. You create task
cards describing what you want done. Move a card
to “To Do,” and Claude automatically picks it up
and starts working. You watch progress in real-
time, see when it’s done, and the card moves to
“Done” on its own.
Cards can run in parallel (independent tasks, fresh
Claude sessions) or sequentially (linked to the
same session, so Claude remembers previous
work). This transforms how you think about


---
*Page 8*


delegating to AI — instead of one-off prompts,
you’re managing a queue of work.
Multi-Agent Mode
For complex tasks, Claude can spawn specialized
agents and coordinate them. One agent analyzes
the codebase, another writes tests, a third handles
documentation. You see all agents working in
parallel, each with its own output stream.
Project Isolation
Create separate projects, each with its own
working directory and chat history. Switch
between them without losing context. Your
frontend project doesn’t bleed into your backend
project.
Remote SSH Projects


---
*Page 9*


This one’s significant for system administrators.
You add remote hosts (servers you manage), create
projects pointing to directories on those servers,
and Claude Code runs *on the remote machine*.
All commands execute there, not locally.
For developers, this means working with code on
powerful build servers or staging environments.
For sysadmins, it means managing your entire
server fleet from one browser tab.


---
*Page 10*


A Practical Example: Managing Multiple
Servers
Let’s say you manage five production servers and
need to update nginx on all of them, verify the
config, and reload.
Traditional approach:
ssh user@prod-eu-01
sudo apt update && apt upgrade nginx
sudo nginx -t
sudo systemctl reload nginx
exit
ssh user@prod-eu-02
# repeat for all five servers…
With Claude Code Studio:
1. Add each server as an SSH host (one-time setup)
2. Create a Remote Project for each server
3. Create five Kanban cards: *”Update nginx to


---
*Page 11*


latest, test config, reload, verify health check”*
4. All five execute in parallel, you watch progress
in real-time
Three minutes later, all servers are updated. Zero
manual SSH, full audit trail.
Another Example: Parallel Feature
Development
You’re working on a web app and want Claude to
tackle three independent features:
1. Add a user settings page
2. Implement rate limiting on the API
3. Write documentation for the authentication flow
In a terminal: You’d run these sequentially, or
juggle three terminal windows.
In Claude Code Studio: Create three Kanban cards,
set each to “New session,” drag all to “To Do.”
Claude spawns three parallel processes, each


---
*Page 12*


working independently. You check back in an hour
and all three are done.
For dependent tasks — like “implement feature X,
then write tests for it” — you link cards to the same
session. The second card waits for the first to
complete, then continues with full context.
Built-In Safety: File Locks
If you’ve ever had two AI processes try to edit the
same file simultaneously, you know the result:
corruption, lost changes, frustration.
Claude Code Studio includes automatic file
locking. Before Claude touches a file, it checks
whether another process is already editing it. If
yes, it waits. After editing, it releases the lock.
Crashed processes don’t leave stale locks — they’re
detected and cleared automatically.


---
*Page 13*


This means you can safely run multiple Claude
agents on the same codebase without worrying
about conflicts.
The SSH Security Model
Remote execution raises obvious security
questions. Claude Code Studio addresses them:
- SSH passwords are encrypted at rest using AES-
256-GCM. The encryption key lives in
`data/hosts.key`, never committed to git.
- SSH keys stay on your machine, used only for
establishing connections.


---
*Page 14*


- No key forwarding — keys aren’t copied or
transmitted.
- Connection testing — verify connectivity before
creating projects.
Your credentials don’t leave your machine. The
remote server sees only the SSH connection and
Claude Code commands.
Installation: Remarkably Simple
The easiest way to try it:
npx github:Lexus2016/claude-code-studio
That’s it. No global install, no config files. Open
`http://localhost:3000`, set a password, and start
chatting.
For a more permanent setup:
npm install -g github:Lexus2016/claude-code-studio
claude-code-studio


---
*Page 15*


Or clone the repo for development:
git clone https://github.com/Lexus2016/claude-code-
studio.git
cd claude-code-studio
npm install
node server.js
Docker is also supported, with a ready-to-use
`docker-compose.yml`.
Requirements: Node.js 18+ and the `claude` CLI
installed and authenticated. If you’re already using
Claude Code, you’re ready.
What the Architecture Looks Like


---
*Page 16*


Under the hood, it’s straightforward:
- Backend: Express.js server with WebSocket for
real-time communication
- Frontend: Single HTML file — no React, no build
step, just vanilla JS
- Database: SQLite for session persistence and auth
- Process management: Spawns `claude`
subprocesses, parses the output stream
- SSH: Uses `ssh2` library with encrypted password
storage
The codebase is intentionally simple. If you want
to understand how it works or modify it, you can


---
*Page 17*


read through in an afternoon. No TypeScript, no
complex bundling, no abstraction layers.
Use Cases That Make Sense
For individual developers:
- Manage multiple projects with isolated contexts
- Queue up tasks and let Claude work through them
- Resume sessions days later without losing context
For teams:
- Shared Claude Code Studio instance with project
visibility
- Kanban board shows what’s being worked on
- Session history provides an audit trail
For system administrators:
- Manage server fleet from one interface
- Delegate routine tasks to Claude (“check disk
usage and clean logs”)
- Parallel operations across multiple servers
For ML/AI engineers:


---
*Page 18*


- Run Claude on powerful remote GPU servers
- Queue training jobs, preprocessing tasks,
evaluation runs
- Check results from your laptop
What It Doesn’t Do
To be clear about the scope:
It doesn’t add capabilities to Claude Code — it
provides an interface for them
- It doesn’t replace your IDE — it manages Claude
sessions
- It doesn’t host code — your files stay on your
machine or your servers
- It’s not a SaaS — you run it locally, your data
stays with you
The Development Philosophy
One thing that stands out in the codebase: it’s built
for developers to understand and modify. Single-
file frontend, straightforward Express routes, clear
separation of concerns. If you want to add a


---
*Page 19*


feature or integrate with your existing tools, the
path is obvious.
This isn’t a product trying to lock you in. It’s
infrastructure you can own.
Getting Started
If you’re already using Claude Code, trying Claude
Code Studio is low-risk:
npx github:Lexus2016/claude-code-studio
Open your browser, create a project, and see if the
visual workflow fits how you work. The terminal
will always be there for quick questions. But for
sustained work — projects that span days, tasks
that run in parallel, servers that need management
— a dashboard might be exactly what you need.
Claude Code Studio is open-source under the MIT
license. You can find it at


---
*Page 20*


github.com/Lexus2016/claude-code-studio
AI Open Source Developer Tools Claude Code
Written by Tiberiy
Follow
5 followers · 6 following
No responses yet
To respond to this story,
get the free Medium app.
More from Tiberiy


---
*Page 21*


Tiberiy Tiberiy
Claude Code Studio: Smart Money strategy:
В б ф й
A l t
Как проект
open-source
б
Cl d
3d ago May 12, 2024
Tiberiy Tiberiy
Revealed: Scalping Exposure: ChatGPT 4
St t f $500 T di St t M d
🚨
The Truth About the Most
P l Y T b St t
May 3, 2024 May 23, 2024
See all from Tiberiy


---
*Page 22*


Recommended from Medium
kumaran srinivasan Marco Kotrotsos
3 Ways to Run Claude Anthropic Just Made
C d CLI D kt Cl d C k 10
How I switch between three Adding scheduling to an
i t f l f ll l d i l t
6d ago 4d ago


---
*Page 23*


In by In by
UX Planet Nick Babich Obsidian Obser… Theo Sto…
Gemini 3.1 for UI & Web My Claude Code Now
D i H It O S d
Google recently released its How I turned it into a personal
AI d l G i i 31 Thi i t t th t li i
Feb 23 Feb 19
Reza Rezvani In by
Spillwave Solu… Rick Hight…
30 OpenClaw
What Is GSD? Spec-
A t ti P t
D i D l t
SOUL.md templates, cron
How AI agents forget what
h d l it d il
th ’ b ildi d h t
5d ago Feb 22
See more recommendations