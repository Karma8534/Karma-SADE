# DynamicSkillsAgent

*Converted from: DynamicSkillsAgent.PDF*



---
*Page 1*


Open in app
11
Search Write
Google Cloud - C…
Why I Stopped
Installing Agent Skills
(and Built a Dynamic
Skills Agent instead)
Esther Lloyd Follow 10 min read · Mar 12, 2026
38 1
Agent Skills are a brilliantly simple answer to the
right context at the right time. Skills use my new
favourite term progressive disclosure, where the
agent only reads into memory the skills metadata
(name and description) until it actually needs to
activate the logic and then it loads the rest of the


---
*Page 2*


context. It can save tokens and keeps context and
memory clean. However, at the time of writing
this, there appears to be something missing; a
standardised skills registry.
I don’t want to do a javascript and “download the
internet” of skills just in case I might need them. I
also don’t want to download skills for them to be
outdated in a few hours. I also only want skills
from trusted sources and providers, like the new
Firebase agent skills. Therefore I want them
available precisely when I find myself saying
something along the lines “oh I need to add
authentication to my app because I don’t have the
right skills”.
So, Gemini and I built an Agent Development Kit
(ADK) agent to do exactly this. You can find the
resulting generated code here. Keep reading to
find out more about the process and what skills I
learnt along the way.


---
*Page 3*


Scaffolding the ADK Agent with
Antigravity.
I started in Antigravity to scaffold the agent. I
chose Antigravity as my IDE of choice over just
using the Gemini CLI mostly because of the built-
in browser. I knew that I could then use the
Antigravity Agent to then test the agent using adk
web. I chose ADK as the agent framework because
I want this agent to be available and registered in
tools like Gemini Enterprise but also I wanted to
deploy it as a remote agent on Cloud Run so I could
call it as a remote Gemini CLI subagent. ADK is
also available in Typescript, so it is aligned
perfectly with the Node ecosystem of the Gemini
CLI and Firebase skills, ensuring the resulting
agent only requires a Node image.
I want to use ADK to build an agent. The agent is des
Example from https://geminicli.com/docs/cli/skills/:
Some basic rules to follow:
* The skills must ONLY be from verified sources, such


---
*Page 4*


* The agent should be built using Typescript
* Final output should be a Skills folder with all the
* Ultimately the agent should be designed to be a rem
* The agent should also be able to be registered with
Agent prompt to bootstrap the project.
While registries like Vercel skills.io are starting up,
I sense another javascript library fiasco. Lots of
duplicate libraries, some from verified sources,
others just done by standard developers to help
others. This doesn’t work in an enterprise
environment. I personally don’t want a random
Firebase Auth skill from a well meaning developer
that isn’t from the Firebase team helping me in my
production project.
I wanted an agent that acts as a security
gatekeeper, strictly pulling from approved GitHub
organisations like Firebase or Google Cloud
Platform. For the purpose of this exercise, I simply
just hardcoded these sources into the agent
assuming that Skills distribution will be a solved


---
*Page 5*


problem by next week (things move fast in AI
time). However, if we don’t get a standardised
means for distributing skills in a registry, then I
would look to expand this into a simple datastore,
using Firestore or something similar for the agent
to pull approved Github skills registries from.
Which in itself, is a nice simple RAG ADK Agent.
As a nice update, there are now Flutter Skills.
Which means I might need that database sooner
rather than later.
Right Agent Skill, right time. Making the
Agent useful.
Once the ADK scaffold was put in place, and
Antigravity had installed all the required packages
and verified that ADK was working locally, it was
time to use the Antigravity agent to help build it
out. I wanted the Agent to be able to call two tools,
one to fetch skills, and then other to install them.
The flow looked like this:


---
*Page 6*


1. Intent detection: The user asks for a capability
(e.g., “I want to add Auth to this app.”).
2. Skill discovery: The agent uses its built-in tool to
find the skill to install from an approved repo.
3. Human-in-the-loop approval: When the agent
finds the appropriate skill they will prompt the
user to confirm that it should go ahead and
install.
4. Skill installation: Instead of manual cloning, the
agent triggers the official Gemini CLI install
command: gemini skills install
https://github.com/firebase/agent-skills — path
firebase-auth-basics
5. Skill activation: Since the tool is installed locally,
both the Gemini CLI and Antigravity notices the
new skill. Via progressive disclosure, it pulls it
into context only when you’re ready to actually
implement the code.
The agent code is as follows:


---
*Page 7*


import 'dotenv/config';
import { LlmAgent } from '@google/adk';
import { addAgentSkills, searchAgentSkills } from './
const agentInstruction = `
You are a Remote Skills Collator Agent.
Your purpose is to take a user's intent and fetch the
A user will describe what they want to achieve (e.g.,
Some basic rules to follow:
* The skills must ONLY be fetched from verified sourc
* Use the \`search_agent_skills\` tool first to check
* When adding a skill, you must use the \`add_agent_s
* CRITICAL: ALWAYS prompt the user to confirm the ski
* The final output of your tool execution should ensu
If the user's request is unclear, ask them to clarify
* CRITICAL: After successfully adding a skill, you MU
`;
export const skillsCollatorAgent = new LlmAgent({
name: 'SkillsCollatorAgent',
model: 'gemini-3-flash-preview',
description: 'An agent that fetches and collates
instruction: agentInstruction,
tools: [addAgentSkills, searchAgentSkills],
});
export const rootAgent = skillsCollatorAgent;
Example code snippet.


---
*Page 8*


The searchAgentsSkills tool isn’t a thing of beauty,
rather dodgy failable regex patterns. However, the
addAgentSkills tool simply utilises the built in
method with Gemini CLI to install skills gemini
skills install. In the future, it would be good to
expand on this and enable and disable skills as
required.
...
// 2. Execute `gemini skills install` non-
const repo = repositoryUrl.endsWith('.git
// Check if skillName already contains th
const skillPath = skillName.includes('/')
const command = `gemini skills install ${
const { stdout, stderr } = await execAsyn
...
Testing the Agent. Antigravity browser
and computer use model.
This is where Antigravity shines. It’s so simple to
check that the ADK Agent is actually working.
There are are a few methods:


---
*Page 9*


adk web is used with the agents computer use
model;
Invoking it through a curl command using the
Agent tool;
Finally Antigravity Agent uses the Gemini CLI
once the skill has been installed.
Simple prompt to the Antigravity agent spins up the ADK agent and
checks it’s working. All whilst I have a coffee and think about the meaning
of life.


---
*Page 10*


Thanks to Antigravity, it appears that the logic and
the ADK agent and tools are working. The skills are
installed and loaded into the workspace:
Installed Skills into the Antigravity Workspace.
Now it’s time to test if the skills can be invoked. It’s
worth noting, that because skills are standard
format, both the Gemini CLI and the Antigravity
Agent should be able to use and call the same
skills.
First, let’s use the Antigravity Agent to test if
Gemini CLI can invoke the skill with a simple
prompt: Test to see if the Gemini CLI can use the
skill.


---
*Page 11*


Antigravity Agent is smarter than I, it even corrected the mistake in the
agent instructions logic.
The Agent successfully verified the skills were
listed using gemini skills list plus also fixed the
logic in the agent instructions. Skills are
automatically loaded based on the skills metadata.
For example, the Firebase Auth skills metadata
gives the Agent just enough context to know when
it should load in the rest of the skills context. The
presence of the skill and as long as it’s discoverable


---
*Page 12*


or symlinked by the Gemini CLI means that there
is nothing further for the user to do.
---
name: firebase-auth-basics
description: Guide for setting up and using Firebase
compatibility: This skill is best used with the Fireb
---
The other test is to see if the Antigravity Agent can
now call the agent. In theory this should work, but
on testing, turns out we need to tweak the folder
naming. When the Gemini CLI installs the skill, it
places it in the .gemini directory. However, this
isn’t discoverable by the Antigravity agent. To fix
this, we simply need to tweak the ADK logic to
rename the directory to .agents which is is the
emerging open standard directory for Agent Skills
(as per agentskills.io) and is supported by both
agents.


---
*Page 13*


Now when I ask the Antigravity agent I get prompted to allow access to
the installed skill.
Deploying the agent. Remote Subagents on Cloud
Run?
The end goal is to deploy this onto Cloud Run. By
hosting this ADK agent remotely and exposing it
with A2A, it becomes a reusable subagent. For
more information on A2A with Cloud Run, see my
colleague Daniel’s brilliant article Implementing
Zero Trust A2A with ADK in Cloud Run.
This makes the agent available in multiple
environments, or to multiple developers, or even
other agents, without needing local setup every
time. It also opens the door for better Day 2
operations. Imagine an agent that not only finds a


---
*Page 14*


skill but also checks for updates or monitors the
success rate of the skills it installs. It makes logical
sense to maintain a single agent. It also allows for
better observability, understanding usage,
acceptance, if the agent errors etc.
However at the time of writing this, there is
currently not a trivial way to ensure that the agent
could be deployed to Cloud Run, secured, and the
Gemini CLI can pass authorization to the agent to
invoke it. My ideal would be to expose the Agent in
Cloud Run, requiring authentication, with an A2A
Agent Card specifying the OAuth requirements to
the Gemini CLI agent.
However, as of time of writing, I’m patiently
waiting for this https://github.com/google-
gemini/gemini-cli/pull/21496 to be merged to make
this possible. In the meantime, nothing stops me
from running this as a local subagent…
The Skills I learnt in this project.


---
*Page 15*


Progressive Disclosure: Agent Skills save memory
by loading only metadata initially, pulling the full
code context only when the skill is actually
needed, this prevents context-window bloat and
reduces token costs It’s also my new favourite term
since ephemeral hit my vocab.
Curated skills are important for security and
sanity: To avoid untrusted code, the custom agent
acts as a gatekeeper, exclusively fetching skills
from approved, enterprise-ready GitHub
repositories.
Always put a human-in-the-Loop in your Agents
workflow: The agent is programmed to mandate
explicit user confirmation before running any
installation commands. Just in case.
Antigravity is amazing: I used Antigravity’s built-in
tools to rapidly scaffold, test, and debug the agent’s
logic whilst I made coffee.


---
*Page 16*


Folder compatibility: Saving installed skills to an
.agents folder instead of .gemini ensured both the
Gemini CLI and Antigravity could detect and use
them. Also other AI Agents I guess, but I don’t
really use them…
Cloud Run with A2A for Remote Subagents: The
ultimate goal is hosting the agent remotely as a
reusable A2A (Agent-to-Agent) subagent, but it’s
pending a future Gemini CLI update for OAuth
support.
So stop downloading all the skills you find “just in
case”. It’s never been easier to use Antigravity to
build an ADK agent to help make the most of agent
skills. Or even, build your own skills!
Antigravity Agent Skills Google Adk
Progressive Disclosure Gemini Api


---
*Page 17*


Published in Google Cloud -
Following
Community
74K followers · Last published 1 day ago
A collection of technical articles and blogs published
or curated by Google Cloud Developer Advocates.
The views expressed are those of the authors and
don't necessarily reflect those of Google.
Written by Esther Lloyd
Follow
40 followers · 13 following
Hi I'm Esther (was a Tester). Now a Customer
Engineer at Google Cloud. Big fan of Firebase and
cycling!
Responses (1)
To respond to this story,
get the free Medium app.
Anand Butani
Mar 28
Progressive disclosure for skills is clever, but you're right that without a
trusted registry layer, you're just back to npm dependency hell with extra


---
*Page 18*


steps. The real unlock is when the registry itself becomes agentic,
surfacing the right skill at… more
More from Esther Lloyd and Google Cloud -
Community
In by In by
Google Cloud - Co… Esther … Google Cloud - C… Federic…
Antigravity ruined the 1 Million Tokens Per
Ad t f C d f S d Q 3 5 27
What using Antigravity taught From 22K tok/s on 4x H100 to
i k d h I thi k 1M+ 96 B200 E
Dec 23, 2025 Mar 26


---
*Page 19*


In by In by
Google Cloud - Co… Romin … Google Cloud - Co… Esther …
Tutorial : Getting Conductor: Testing the
St t d ith G l G i i CLI
Welcome to the tutorial on I tested the Gemini CLI
A ti it G l ’ f d C d t t i d
Nov 19, 2025 Jan 18
See all from Esther Lloyd See all from Google Cloud - Community
Recommended from Medium
In by In by
Google Clou… MCP Toolbo… UselessAI.in Shresth Shukla


---
*Page 20*


Building a Semantic What is happening in
I t lli L f T t t SQL? SPID
Combining OpenMetadata Note — Read this blog for free
d MCP T lb t b ild if t k b hi d
Mar 24 Feb 10
namusanga In by
Google Cloud - Co… Romin …
Getting started with
Full-Stack Vibe Coding:
A th i Cl d
B ildi P d ti
Let’s quick explore what’s new
Sundar Pichai published an
i A th i ’ Cl d
i t ti T t th d th
Oct 2, 2025 Mar 24


---
*Page 21*


In by In by
Google … #TheGenAIGirl … Google Cloud … Dazbo (Dar…
Elevating Agent Documentation as
I t lli ith C t t A Skill t
Trying to understand why Supercharge your AI agents
t f l l d d ith th j t
5d ago 5d ago
See more recommendations