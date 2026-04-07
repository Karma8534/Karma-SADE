# How GSD turns Claude into a self-steering developer - The New Stack

*Converted from: How GSD turns Claude into a self-steering developer - The New Stack.PDF*



---
*Page 1*


Platform Engineering Playbook
AI / AI AGENTS / OPERATIONS
How GSD turns Claude into a self-steering
developer
OpenClaw may be flawed, but it does show how limited the available and entrenched
digital assistants are compared to what agents can do.
Feb 7th, 2026 9:00am by David Eastman
Sara Oliveira for Unsplash+


---
*Page 2*


The speed at which ClawdBot MoltBot OpenClaw climbed in popularity was quite
phenomenal, and for good reason: It has an audience beyond the developer space,
especially those who just want to experiment with digital assistance. Todays post
continues my journey with GSD, but the LLM agent landscape is changing rapidly and
this shooting star caught everyone’s eye.
Instant Multi-CDN Visibility
At its core, OpenClaw is a locally hosted, open-source AI assistant that runs on your
computer or server. You talk to it through apps you probably already use, like
WhatsApp, Telegram, Discord, Slack, Signal, or even iMessage. And it really “does
stuff” — sometimes too well. It is a gateway service that maintains WebSocket
connections and includes a smart orchestration layer for working with LLM agents.
OpenClaw shows a strong technical focus on LLM agents; however, its significant and
varied security issues mean we must think more carefully about agent vulnerabilities
before experimenting with them. But keep watching, even the odd sidetrack of the AI
church is genuinely intriguing. OpenClaw may be flawed, but it does show how
laughably limited the available and entrenched digital assistants are compared to
what agents can do. Now back to our scheduled program.
OpenClaw may be flawed, but it does show how laughably limited the
available and entrenched digital assistants are compared to what
agents can do.
In my first article on the popular Claude extension GSD, I set up a project to create a
JSON viewer. GSD then asked many questions to create concrete plans before finally
crunching a version 1 on its chosen platform, SwiftUI.
It had just presented its work when we stopped:


---
*Page 3*


Zoom
So first of all, let’s run the actual thing. I am following the advice carefully, as I am not
a SwiftUI developer and I don’t use Xcode. Indeed, I had to get the update to 26.2 just
to use it. I run it, and indeed it does what is described:
TRENDING STORIES
1. Beyond automation: Dynatrace unveils agentic AI that fixes problems
on its own
2. OpenAI's Codex desktop app is all about managing agents
3. Why enterprise businesses should adopt immutable Linux for the
desktop
4. Unlocking AI's full potential: Why context is everything


---
*Page 4*


5. Chainguard admitted Factory 1.0 was "brittle." Here’s how 2.0 fixes it.
Zoom
So I approve the checkpoint. Yes, it’s just a titled window, but it tells me that all the
assumptions are correct. It spends some time updating the roadmap and
requirements.
And then we were ready for a second planning phase:
Zoom


---
*Page 5*


Well, that percentage progress is creeping up. At the time, I thought it represented
how close the project was to finishing.
I am running GSD within a Warp shell, but one downside of running in a single
continuous session is that I can’t use Warp’s distinctive command-and-response
blocks, which would give me the times of all the responses.
The phase goals and success criteria now roll into SwiftUI specifics, which I like.
While I’m not a Mac developer, I can see that it is pulling in the common components it
needs to operate:
Zoom
Despite my managerial role in this process, my developer head can follow the steps it
is working through. After creating the plan, it executes it.
The human (that is, me) is now required again for verification – this time to check I
can load a JSON file through the app:


---
*Page 6*


Zoom
I do indeed load a JSON file from my project with the expected Mac user interface,
and it does count up all the objects within the file – and no more. I approve its
progress in order to continue. Just before I do, I ask a quick question regarding token
usage:
Zoom
Again, GSD wants my approval before continuing. I give it.
And finally, we hit my plan limit:
Zoom
So I clear the context window and attempt phase 3 again. Note the scary skull as the
progress bar goes red.


---
*Page 7*


Zoom
Anyway, now I know what that progress bar means! It resets when the window is clear.
I also check my billing on the website. I am also warned that I am approaching my
limit until the periodic reset:
Zoom
This is on the Pro plan, by the way. So I execute phase 3. For the record, here is the
planning section:


---
*Page 8*


Zoom
After waiting for my tokens to refill from the magic fountain Pro plan usage, we plough
onwards. Now, GSD was working out how to implement a browsable list, bound to my
JSON data.
Finally, GSD crunched a much more significant version, with much of the viewing
capabilities apparently in place:
Zoom
And after firing up the app in Xcode, I can select objects at will from the JSON file I
selected:


---
*Page 9*


Zoom
For completion, here is the functional layout of the generated project within Xcode.
The structure looks fine — and I’ve no problem continuing with this project. But we’ve
gone far enough to prove GSD has what it takes to steer a development project
without issue.
Zoom
Conclusion
While the GSD workflow uses a blizzard of organizational terminology — plans,
requirements, phases, waves, checkpoints (they really didn’t leave any agile jargon


---
*Page 10*


behind) — I understand this is meant to tie everything together, retain “focus,” and put
less pressure on the context window.
Zoom
And I was able to continue after running out of the window, running out of tokens, and
the Mac having to restart. As I mentioned in the previous article, these restrictions are
of their time — given the amount of global resources apparently now going towards AI
infrastructure, I expect token costs to come down and the average context window to
expand until it presents no restrictions. If I wanted to avoid the break between token
refills, then I would have needed to upgrade my plan.
For a developer, seeing the project develop requirement by requirement is perfectly
natural — but this might be slower than some imagined. For me, the value lies in
pursuing a project whose language (SwiftUI) I can learn after seeing a working


---
*Page 11*


prototype. I feel GSD is a sensible route forward that I expect Anthropic will quietly
absorb.
David has been a London-based professional software developer with Oracle Corp. and British
Telecom, and a consultant helping teams work in a more agile fashion. He wrote a book on UI
design and has been writing technical articles ever since....
Read more from David Eastman
TNS owner Insight Partners is an investor in: Anthropic.
SHARE THIS STORY
TRENDING STORIES
1. Beyond automation: Dynatrace unveils agentic AI that fixes problems on its own
2. OpenAI's Codex desktop app is all about managing agents
3. Why enterprise businesses should adopt immutable Linux for the desktop
4. Unlocking AI's full potential: Why context is everything
5. Chainguard admitted Factory 1.0 was "brittle." Here’s how 2.0 fixes it.
INSIGHTS FROM OUR SPONSORS
Building trust in agentic AI: An observability‑led 90‑day
action plan
5 February 2026


---
*Page 12*


Smarter vulnerability remediation with Dynatrace and
Atlassian Rovo Dev
3 February 2026
Adriana Villela of Dynatrace takes on OpenTelemetry
community manager role
2 February 2026
Continuous Testing for AI-Generated Code: Building
Trust at AI Velocity
30 January 2026
Why AI Coding Velocity Requires Continuous Testing
22 January 2026
Why Continuous Testing Is the Missing Link in AI
Development
15 January 2026
How to choose your LLM without ruining your Java code
26 January 2026
Announcing SonarQube Server 2026.1 LTA
26 January 2026
The AI trust gap: Why code verification matters
22 January 2026
TNS DAILY NEWSLETTER


---
*Page 13*


Receive a free roundup of the
most recent TNS articles in your
inbox each day.
rae.steele76@gmail.com
SUBSCRIBE
The New Stack does not sell your information or share it with unaffiliated third parties. By
continuing, you agree to our Terms of Use and Privacy Policy.
ARCHITECTURE ENGINEERING
Cloud Native Ecosystem AI
Containers AI Engineering
Databases API Management
Edge Computing Backend development
Infrastructure as Code Data
Linux Frontend Development
Microservices Large Language Models
Open Source Security
Networking Software Development
Storage WebAssembly
OPERATIONS CHANNELS
AI Operations Podcasts
CI/CD Ebooks


---
*Page 14*


Cloud Services Events
DevOps Webinars
Kubernetes Newsletter
Observability TNS RSS Feeds
Operations
Platform Engineering
THE NEW STACK roadmap.sh
About / Contact Community created roadmaps, articles,
resources and journeys for developers to
Sponsors
help you choose your path and grow in
Advertise With Us
your career.
Contributions
Frontend Developer Roadmap
Backend Developer Roadmap
Devops Roadmap
FOLLOW TNS
© The New Stack 2026
Disclosures
Terms of Use
Advertising Terms & Conditions
Privacy Policy
Cookie Policy