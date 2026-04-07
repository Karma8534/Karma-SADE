# Re-defining the ‘Agentic Web’

*Converted from: Re-defining the ‘Agentic Web’.PDF*



---
*Page 1*


Data Science Collective
Re-defining the ‘Agentic Web’
The version everyone’s building for is not the web I’m talking about!
Rob Manson Follow 13 min read · 1 day ago
11 5


---
*Page 2*


The traditional view of the ‘Agentic Web’ is agents ‘using’ the web like we do
T here’s been a lot of focus on the “Agentic Web”, and for good reason —
the idea that AI agents can act on our behalf across the internet is
genuinely compelling. But if you look closely at what most people mean
when they say Agentic Web, they’re describing something surprisingly
conservative. They’re talking about the web we already have, but with AI
agents doing the clicking, instead of us. (See Operator, CoWork, Project
Mariner, etc.)
The current vision goes something like this — you tell your agent to book a
flight, and it navigates airline websites, fills in forms, compares prices, and
completes the purchase. The agent replaces you as the user. The web stays


---
*Page 3*


exactly the same (designed for human eyes, human hands, human attention)
and agents just learn to operate the controls we built for ourselves.
Figure 5 from the ‘Agentic Web: Weaving the Next Web with AI Agents’ paper — Source arXiv
This is useful. It’s even impressive. But it’s not a “new web”. It’s automation
on top of the old one.
Some discussions even go a little further, outlining a web that’s updated to
allow agents to interact with it more easily. Adapting web pages to become a
form of API customised for AI. This is really useful too, and a natural part of
the evolution.
But I think these discussions are all missing something much bigger.
The web is already adapting for agents
It’s worth noting that the Agentic Web isn’t just theoretical — it’s already
being standardised. WebMCP (Web Model Context Protocol) is a W3C
Community Group standard, jointly developed by Google and Microsoft, that


---
*Page 4*


lets web pages expose structured tools directly to AI agents through the
browser itself.
Instead of agents having to scrape the DOM or interpret screenshots, a web
page can declare its capabilities (“here’s how to search flights”, “here’s how to
file a support ticket”) as structured tools with defined schemas and security
boundaries. It’s available for early preview in Chrome 146, and it’s a
significant step forward.
An overview of how WebMCP works — Source WebMCP.link
This matters for our discussion because it confirms something important —
the browser vendors themselves now recognise that AI agents are first-class
participants on the web. The platform is actively evolving to accommodate
them. Agents aren’t just a layer on top of the web anymore — they’re being
designed into it.


---
*Page 5*


But notice the assumption that’s the focus here. WebMCP is designed for
agents that visit web pages. It helps a page tell an incoming agent what it can
do and how to do it. The agent is still a guest, and the page is still someone
else’s house with a better welcome mat.
What happens when the agent isn’t visiting? What happens when it builds
the house itself?
This is not your parents’ ‘Agentic Web’
What if the web wasn’t just ‘where agents go’ ?
Consider the browser. It’s on every device. It has a rendering engine, a
scripting runtime, access to cameras, microphones, accelerometers, GPS,
local storage, and a security model that’s been hardened over more than
three decades of adversarial pressure. It can display anything from a text
form to a full 3D environment. It can run sophisticated applications entirely
locally, without installation, without accounts, and without servers.


---
*Page 6*


Many people think of the ‘browser’ as a window onto ‘remote content’
We tend to think of the browser as a viewport — a window you look through
to see content that “lives somewhere else”. But it’s not. It’s a runtime.
Arguably the most ubiquitous and capable runtime ever deployed. And
nobody had to install it.
It’s just there.
Now consider what AI agents actually need. They need a way to perceive the
world. They need a way to act in it. They need a way to communicate with
users — not through text alone, but through rich, interactive, dynamic


---
*Page 7*


interfaces that can evolve in real time. They need a secure, sandboxed
environment where they can operate without putting the user’s system at
risk.
Our existing browsers already have all of this.
From artefacts to inhabited spaces
Most people are familiar with AI creating content for them. Power users are
even familiar with what the AI platforms have lovingly called “interactive
artefacts” (seriously?!)— a chart, a small application, a visualisation.
You prompt, the AI generates, you receive the output
It’s a creative and productive workflow. But it follows an “old school” pattern:
edit -> generate -> view
The AI is the author. You are the audience. The artefact is the finished
product.
But what if the artefact wasn’t the end point? What if it was just the
beginning?
Imagine an AI that doesn’t just generate a web page and hand it to you — but
moves into it. An AI that creates its own interface, watches how you interact
with it, and reshapes it in response.


---
*Page 8*


This vision is of a bigger ‘Agentic Web’ where the agent lives in the DOM and wears it like an interactive skin that it
shares with the user
Not in the way a chatbot responds to your next message, but in the way a
living system adapts to its environment.
The page isn’t an output. It’s a shared space.
The AI can see what you do. You can see what it creates. Both of you are
present in the same surface, at the same time.


---
*Page 9*


This is a fundamentally different relationship between AI and the web. The
AI isn’t navigating someone else’s interface. It isn’t generating a static
deliverable. It’s inhabiting a space (a space built from the same HTML, CSS,
and JavaScript that powers everything else on the web), and it’s alive in that
space, perceiving and responding through the DOM itself.
In the old model, the AI is the author of the artefact.
In this new model, the AI is the occupant.
Authors leave when the work is done. Occupants stay and liven the place up
a little.
The web as living skin
This reframing has real implications for how we think about the relationship
between AI and interfaces.
Today, most AI interfaces are conversational. You type, it responds. Some
platforms extend this with tool use, code execution, or generated
components. But the interface is always a container that the AI fills with
content. The interface itself is inert — designed by humans, operated by the
AI within fixed boundaries.
What happens when the AI controls the interface itself? When it can create a
form because it needs information from you, build a game because it wants
to teach you something, render a 3D environment because the problem
you’re working on is spatial, or set up a camera feed because visual context
would help it understand what you need?


---
*Page 10*


The interface becomes the AI’s skin.
Not a metaphorical skin — but a functional one. It’s the surface through
which the agent senses the world, and expresses itself.
An octopus provides a good analogy — it can change its colour and texture to communicate and interact with its
environment
In this new view of the Agentic Web the agent is dynamic, responsive, and
adaptive. It can change shape, change purpose, and change modality. It’s
literally built from the web, which means it inherits all of the web’s
capabilities — rich media, interactivity, device access, accessibility, universal
reach, and security.


---
*Page 11*


This isn’t AI visiting the web like in the traditional view of the Agentic Web.
Get Rob Manson’s stories in your inbox
Join Medium for free to get updates from this writer.
Enter your email Subscribe
This is AI wearing the web.
Bidirectionality changes everything
The critical shift here is bidirectionality. In most current AI interactions,
information flows in one direction at a time. You send a prompt. The AI
sends a response. Even in more sophisticated setups (tool use, function
calling, multi-turn conversation) the fundamental pattern is turn-based.
Request, response. Request, response.
When an AI agent inhabits a web page, the interaction model changes. The
agent can place a listener on a button and know the moment you click it. It
can watch a form field and respond when you type. It can track mouse
movement, scroll position, or device orientation. And it can update the
interface at any time — not in response to a prompt, but because something
in its own reasoning or perception has changed.
This is the same interaction model that every web application already uses.
Events, listeners, callbacks, dynamic DOM manipulation. It’s how the web
has worked for decades. What’s new is that the intelligence driving these
interactions isn’t a script written by a developer — it’s an AI agent that wrote


---
*Page 12*


the script itself, deployed it into its own interface, and is actively
interpreting the signals as it receives them.
The user and the agent are both present in the same dynamic space, both
acting, both perceiving. That’s not a chatbot. It’s not an artefact generator.
This is something new.
The agent has a voice
Bidirectionality isn’t limited to just the moments when a user is staring at the
page too. The web platform has another trick that most agent frameworks
are ignoring — push notifications.
Today, when AI agents need to reach out to users proactively, they typically
route through proprietary messaging channels. WhatsApp, Telegram, Slack,
SMS. Each comes with its own API, its own rate limits, its own
authentication model, and its own dependency on a third-party platform
that can change the rules at any time.
But the browser already solved this. The Push API and the Notification API
let a web application reach a user even when the tab is closed, even when the
browser is in the background. No third-party messaging platform required.
The user grants permission once, and the agent has a direct, web-native
channel to initiate contact. Of course they can use the APIs for other
messaging systems, but push notifications are now a standard part of the
web.
This matters because it extends the agent’s presence beyond the active
session. An agent that can only respond when the user is looking at it is


---
*Page 13*


reactive. An agent that can surface something important (an insight, a
completed task, a time-sensitive change) on its own terms is something
closer to a collaborator. And it can do this through the same web
infrastructure that already powers every notification you’ve ever received
from a website.
Once again, the capability is already there. It’s been there for years. The
agentic frameworks just haven’t really adopted it yet.
The browser can think too
We’ve established that the browser is a capable runtime — a rendering
engine, a sensor array, a sandbox, a communication channel. But there’s one
more dimension that completes the picture - the browser is increasingly a
viable inference environment.
When people think about where AI “runs”, they typically picture remote
servers too — API calls to large model providers, responses streaming back
over the network. And that’s certainly one option. An agent living in the
browser can call out to any remote LLM API (e.g. Anthropic, OpenAI,
Gemini) just as easily as any other web application makes a fetch request.
But that’s just one end of a spectrum.
At the other end, AI can run entirely inside the browser itself. TensorFlow.js
has been doing client-side inference for years. MediaPipe brings real-time
perception — hand tracking, face detection, pose estimation — straight to the
browser with no server round-trip. LiteRT (formerly TensorFlow Lite) is
pushing efficient on-device models into web contexts. Plus transformers.js
from Hugging Face has enabled a wealth of web based AI. And this is


---
*Page 14*


accelerating - Chrome has introduced Web-based AI APIs that expose built-in
model capabilities directly to web applications, and other browsers will
follow.
Between these extremes sits the middle ground — open models served
locally through tools like Ollama, where the inference happens on the user’s
machine but outside the browser, accessible via local API calls.
What this means for a browser-inhabiting agent is that it has choices. It can
route a complex reasoning task to a powerful remote model. It can handle
real-time perception (camera input, gesture recognition, voice recognition)
using local inference where latency matters and privacy is paramount. It can
use a built-in browser model for lightweight tasks without any network call
at all. The agent can make these decisions dynamically, based on context,
capability, and the user’s preferences.
This is the browser not just as a surface the agent wears, but as a brain the
agent can think with. And once again, the security model comes along for
free — when inference runs locally in the browser sandbox, the user’s data
never has to leave their device.
The security model you don’t have to build
One of the most overlooked advantages of the web as an agent runtime is its
security architecture.
Every browser tab is a sandbox. Code running in one context can’t access
another. The same-origin policy, content security policies, permissions APIs,
and secure contexts — these aren’t features someone bolted on for the AI
era. They’re the result of thirty-plus years of adversarial engineering,


---
*Page 15*


millions of real-world exploits, and continuous hardening by every major
browser vendor on earth.
The web platform is hardened from over thirty years in the trenches
When an AI agent runs in a browser sandbox, it inherits all of this for free.
It can’t access your file system. It can’t read other tabs. It can’t exfiltrate data
without explicit network permissions. Follow the rules and the user’s API
credentials can be stored in local browser storage where no external script
or service can reach them.
Compare this to the alternative (deploying AI agents on servers, in
containers, or through custom runtimes) each of which requires building


---
*Page 16*


and maintaining security infrastructure from scratch, and each of which
introduces trust relationships that the user has to evaluate independently.
The browser is the most battle-tested sandbox in computing history. It
seems almost obvious, in retrospect, that this should be where agents live.
Beyond the single browser
A browser-inhabiting agent is compelling on its own. But the architecture
becomes even more powerful when you introduce persistence and
distribution.
In the simplest case, an agent runs entirely in your local browser. That’s
powerful, but when you close the tab, the agent stops. This is fine for many
interactions and it’s beautifully simple — no server, no account, no
installation. Just the web. Open the page and it’s there.
But some agents need to persist. They need to keep working when you step
away. For this, you need a persistent compute layer — a server-side
component where the agent can continue to run independently of any
browser.
Once one of these new Agentic Web agents is running on a persistent server,
something interesting happens — it’s no longer limited to a single browser
session. It can reach into multiple browsers simultaneously. Each browser
becomes a different point of presence — with its own display, its own
sensors, its own user. The agent can present different interfaces to different
contexts while maintaining a unified intelligence across all of them.


---
*Page 17*


This is distributed presence. One agent, many surfaces. Each surface alive
and interactive. Each surface a different window into the same underlying
intelligence. The agent can coordinate across these surfaces, distribute tasks
between them, or use each one for a different purpose entirely.
This moves well beyond what any current AI interface offers. It’s not multi-
modal — it’s multi-present.
The mental model problem
I’ll be honest — there is one big challenge with this vision and it isn’t
technical. It’s conceptual.
I’ve seen this before. For over a decade, I worked on web-based augmented
reality — AR experiences that ran in the browser with no app required. The
technology worked. But people couldn’t stop thinking in terms of apps.
“How do I install it?” they’d ask, while looking at the
AR experience already running in their browser.
The answer was “you don’t, it’s already working” — and they’d nod, and
smile…and then ask where to download it.
This new Agentic Web faces a similar wall. People hear “AI agent” and they
think of a backend system, a cloud service, an API endpoint, a deployment
pipeline. They don’t think of a browser tab. Telling someone “just click this
link and the agent is alive in your browser” feels too simple to be true. It
triggers the same disbelief that “just point your camera and the AR is right
there” used to trigger. They’re used to web based chatbots, but this is a
different mental model.


---
*Page 18*


Social media is filled with posts from people saying “It took me less than an hour” — this is a different mindset
This will normalise over time. It did with webAR. It will with Agentic Web
experiences too. But in the meantime, the most effective way to break
through the mental model mismatch isn’t to explain the architecture — it’s to
show someone the experience and let the novelty and usefulness speak for
itself.
Re-defining the conversation
We opened this discussion by describing how the Agentic Web as it’s
currently discussed in research papers, investment theses, and industry
commentary is overwhelmingly about agents as users of the existing web. It’s
about protocols for agent-to-agent communication, about infrastructure for
agent identity and trust, about redesigning websites to be machine-readable.
These are worthwhile pursuits. But they fixate on the web as it is and ask
how agents can navigate it.
What I’ve suggested here is that we also ask a different question:
What if the web isn’t just the environment agents
navigate, but the medium they inhabit?
What if the browser isn’t just a viewport for content, but a living surface for
intelligence? What if the thirty years of engineering that went into making


---
*Page 19*


the web secure, capable, interactive, and universal weren’t just infrastructure
for human consumption — but the foundation for a new kind of agent
presence?
The current Agentic Web is about sending agents out onto the web. This
vision is about agents coming alive in the web. This small geometric change
makes all the difference.
These aren’t competing visions. They’re complementary. Agents will
navigate existing websites. Agents can also inhabit their own living
interfaces in the browser. Both will happen. But the conversation right now
is almost entirely about the first, and hasn’t been aware of the second — until
now.
It’s time to broaden that conversation. The Agentic Web isn’t just about
agents using the web. It’s about the web becoming the native medium for AI
to be present, to perceive, to interact, and to be alive in.
And you can try it for yourself right now. Code that implements this vision is
open sourced on Github, and it’s live in your browser at flo.monster. Please
don’t ask me how to install it, or where to download it!
Webmcp Webai Agentic Web AI Web


---
*Page 20*


Published in Data Science Collective
Follow
898K followers · Last published 1 day ago
Advice, insights, and ideas from the Medium data science community
Written by Rob Manson
Follow
494 followers · 61 following
I make sense of AI & our AI-Mediated landscape through a geometric lens. If
everything’s changing faster & faster, what can you rely on? See TrustIndex.today
Responses (5)
To respond to this story,
get the free Medium app.
Martinemanuel
13 hours ago
It's alive !
1
Neural Foundry
22 hours ago
This completely reshapes how I've been thinking about AI agents. The distinction between agents visiting the
web versus inhabiting it is so clearr once you spell it out. Your analogy of the browser as a skin rather than just
a viewport really… more
1


---
*Page 21*


Chris Marmo
1 day ago
One day, the website will visit you!
5 1 reply
See all responses
More from Rob Manson and Data Science Collective
In AI Advances by Rob Manson In Data Science Collective by Shenggang Li
Claude, Code Thyself Why Building AI Agents Is Mostly a
Waste of Time
I’ve given Claude the ability to edit its own
code. Then I stepped back and asked the… The Structural, Mathematical, and Economic
Limits of RAG Pipelines
Jan 21 Jan 12


---
*Page 22*


In Data Science Collective by Marina Wyss Rob Manson
AI Agents: Complete Course Live Tracking Is About To Change
— Again!
From beginner to intermediate to production.
Computer Vision based Augmented Reality
made Live Tracking Mainstream. Recently th…
Dec 6, 2025 6d ago
See all from Rob Manson See all from Data Science Collective
Recommended from Medium


---
*Page 23*


In Activated Thinker by Shane Collins In Level Up Coding by Teja Kusireddy
Why the Smartest People in Tech I Stopped Using ChatGPT for 30
Are Quietly Panicking Right Now Days. What Happened to My Brai…
The water is rising fast, and your free version 91% of you will abandon 2026 resolutions by
of ChatGPT is hiding the terrifying,… January 10th. Here’s how to be in the 9% who…
5d ago Dec 28, 2025
Alberto Romero In AI Advances by Delanoe Pirard
LEAKED: The Truth Behind A 1967 Math Paper Just Solved AI’s
Moltbook, Revealed $100 Million Problem
… December 31st, 2025. While Silicon Valley
popped champagne, 20 researchers in…
Jan 31 Jan 28
Will Lockett Steve Yegge
The SpaceX xAI Merger Is A Giant The Anthropic Hive Mind
Red Flag
As you’ve probably noticed, something is
No matter how you look at this, it is bad news. happening over at Anthropic. They are a…


---
*Page 24*


5d ago Feb 6
See more recommendations