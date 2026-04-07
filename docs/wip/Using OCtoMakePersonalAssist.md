New: Claude in MS Foundry
AGENTIC AI
Use OpenClaw to Make a Personal
AI Assistant
Learn how to set up OpenClaw as a personalized AI agent
Eivind Kjosbakken
Feb 17, 2026 10 min read
Learn how to set up OpenClaw to become your AI assistant, making you far more productive. Image by
ChatGPT
New: Claude in MS Foundry
OpenClaw has quickly become a well-known open source system
for running Claude Code. OpenClaw is essentially a system that
runs Claude Code indefinitely, allowing you to set it up as your
personal AI assistant.
You can set up OpenClaw to perform all kinds of tasks for you,
such as:
Reviewing GitHub pull requests
Analyzing emails
Browsing the internet.
I’ve spent the last week setting up many different OpenClaw
systems to act as my bots, specialized in different application
areas. In this article, I’ll take you through how I’ve set up
OpenClaw on my own system, ensuring the implementation is
both secure and makes me more effective as an engineer.
I’ll cover the specifics of where you should set up OpenClaw, how
you can set it up, the recommended way to run your OpenClaw
instances, and how to get the most out of OpenClaw.
This infographic highlights the main contents of this article. I’ll go through exactly how I set up OpenClaw to
become my personal assistant, saving me massive amounts of time. Image by Gemini
Why set up an OpenClaw Assistant?
The number one reason you should set up OpenCline on your
computer is simply that it makes you more effective. You can set
up OpenClaw to automate all kinds of different tasks and help
you organize all of your work.
For example, instead of manually scouring through your emails
looking for relevant emails and coming up with answers, you can
simply tell OpenClo to analyze all of your emails daily, teach it
which emails you think are relevant and which are not, and have
it come up with example responses you can allow it to send.
You can also give OpenClaw access to your GitHub profile, have it
notify you whenever you’re tagged in a relevant pull request.
Analyze the pull request as if it were you and suggest a pull
review comment.
The best part of OpenClaw is that it can be personalized:
How to implement OpenClaw
In this section, I’ll go through how I implemented OpenClaw.
There are a lot of different ways to do it, and a lot of different
applications you can set up. To keep it simple and specific, I’ll tell
you how I did it specifically and which apps I connected it to, to
give you inspiration for how to do it yourself. However, there is no
one true way to do this, and the optimal way for you depends on
your workflow.
Access to Claude Code
The first thing you need is access to Claude Code. Claude Code
offers three different subscription tiers, which give you a set
amount of usage per month. This is correspondingly $20, $100,
and $200 per month.
I utilize Claude Code for my other programming as well and have
the max subscription. I can then use this same subscription for
my OpenClaude assistance and still be well within my usage
limitations per month.
You can also do Pay Per Use through an API pricing, though I do
not recommend this because it will quickly get more expensive
You can tell it exactly how to behave and you can teach it over
time so it can become better and better. This is exactly what
you need in a personal assistant. It’s very capable right off the
bat and becomes even more capable the more you teach it.
than the equivalent usage you could get through one of the
subscriptions I described in the section above.
Once you have access to Claude Code, you can run the command
below to set up a token, which you can provide to open Claude
when setting it up. Remember not to share this token with
anyone, as it gives access to your Claude Code subscription.
claude setup-token
Docker images on a separate computer
You can install OpenClaw through this link. Exactly how you
install it will depend on your operating system so I’ll avoid
providing specific commands here. However, another way of
setting it up, which might be the simplest way, is to simply tell
Claude Code to set it up for you. Provide Claude Code the token
we described above, and it can set up your assistant for you. I
have done this three different times, and it’s worked every time
to fully set up my assistant exactly how I want it.
When you set up your assistant, I recommend telling Claude
Code to set it up as different Docker images on your computer.
This has multiple advantages.
The agent will run in an isolated environment and not get
access to things it shouldn’t have access to. This is super
important for security concerns.
Running it as a Docker image makes it easy to move and
create backups of your agent. You can simply download the
Docker image and use it on a different computer, and store
the image on Docker Hub to have a backup of your agent.
You can simply tell Claude Code to set everything up in Docker,
and it will do it for you. You don’t have to do anything yourself
there.
Personalizing OpenClaw
After you’ve set up OpenClaw with Claude Code, you should
personalize it. Tell Claude Code to open the OpenClaw dashboard
in your desired web browser and start chatting with your agent. It
will ask… The agent will ask for your name and what the agent
should be called, and you can give it a personality.
I’ve set up multiple different bots. For example, I set up a
personal assistant that has my personality and tries to be super
rational and just gives me concise summaries of everything I
need to do and things I need to be aware of.
I’ve also set up a sales bot which has a bit of a different attitude,
very positively minded, and which I’ve given access to relevant
sales material and so on.
In general, you can simply chat with your agent and tell it to
remember things. Open Claw will then proceed to store
important information in memory and remember it for later.
Access
After you’ve set up OpenClaw with its personality, you should
start by giving it access to stuff. When giving access to your
agents, you should follow the principle of giving the least amount
of access necessary to perform actions. For my personal bot, I
have given the following access.
Slack (where we communicate)
My emails and calendar so it can read emails and book
meetings
Linear, so I can check the different tasks I have to do.
GitHub, so it can perform actions on my behalf on GitHub.
I’ve also set up a different agent that acts as a sales bot. This bot
has been given access to the CRM system ,where it can get all its
relevant material regarding sales. I’ve also given him Slack access
where we communicate.
Overall, the access you give your agent is crucial for what it can
do. If you want to perform an action, you need to give it access
and permissions to do so. However, you should also be careful
with the access you give it, as your agent will act fully
autonomously within these systems.
Skills
Another incredibly important part of setting up OpenClaw is the
skills you provided. If you want OpenClaw to remember things for
later or act in a specific way, you need to provide it with skills. To
provide the OpenClaw skill, you can simply tell it “store this as a
skill” after you provide some information.
I’ll give a few examples of the skills I’ve created:
GitHub skill: this tells the agent how it should act on GitHub
on behalf of me. It, for example, tells him how I do pull
request reviews (I made my agent look at all my different
reviews from previous to analyze my preferences.)
Gmail skill: tells the agent which emails it should set to red
automatically, which I don’t care about, and which emails it
should inform me about in my daily briefing.
Slack skill: tells the agent how to interact on Slack, for
example to always respond in threads and not as new
messages.
Calendar skill: tells the agent exactly how to read my
calendar, informs me of meetings, and how to book meetings
with others, and how to interact with the Google API for
Google Calendar.
In general, I try to provide the agent with a relevant skill every
time I want it to perform an action.
The skill will then be loaded dynamically whenever the agent is
asked to do something related to a given skill. For example, if
asked to read Gmails or emails, it will read the Gmail skill.
What doesn’t work with OpenClaw
I’ve experimented a lot with OpenClaw in the last week. I’ve
noticed situations where it works incredibly well out of the box,
and I also noticed scenarios where it doesn’t work as well. There
are two main things you should be aware of that don’t work very
well.
Being vague
Simply telling the agent to remember stuff for later.
Being vague doesn’t work because OpenClaw doesn’t plan in the
same way as you do and doesn’t have access to all the contacts
it needs. You should thus make sure to have a very specific plan
and avoid ambiguity whenever setting up things for OpenClaw to
do.
To achieve this, I recommend discussing with an LLM beforehand
before trying to implement something, and then being super
specific once you try to implement it. It’s not a problem to
change your plan later on as OpenClaw will adapt, if you provide
a very vague plan, OpenClaw will struggle a lot and will likely not
be able to implement the thing you intend to make.
Furthermore, simply telling the agent to remember stuff for later
doesn’t work as well. In general, you should make sure to store
all important information in skills. Whenever you teach the agent
something specific, tell it to either add it to a previously created
relevant skill or make a new skill with the information. These
skills will then be loaded whenever the agent is performing
actions.
For example, if you provide the agent with an email reading skill,
this skill will be loaded whenever the agent interacts with emails.
So if you want the agent to perform in a specific way when
reading emails or sending emails, you should store it in a
separate skill.
I thus highly recommend making sure the agent stores all
relevant information in explicit skills and that you keep track of
these skills and continually update them as you get more and
more information.
Conclusion
In this article, I’ve gone through how to set up OpenClaw. You can
simply set up OpenClaw for free,e given that you already have a
Claude Code subscription. When setting up OpenClaw, you should
set it up on a separate Docker container,s isolating each
environment and making sure different agents don’t have access
to each other’s information and keys. Creating an OpenClaw
assistance has been incredibly powerful for me, and in less than
a week after setting them up, I’ve already noticed massive
efficiency gains. However, I’ll also notice scenarios where the
agent doesn’t work as well, which you have to take into account
when setting up your assistance. The overall key, however, is to
be as specific as possible and make the agent store everything
relevant as skills that can be loaded dynamically on demand.
👉 My free eBook and Webinar:
🚀 10x Your Engineering with LLMs (Free 3-Day Email Course)
📚 Get my free Vision Language Models ebook
💻 My webinar on Vision Language Models
👉 Find me on socials:
💌 Substack
🔗 LinkedIn
🐦 X / Twitter
· · ·
Towards Data Science is a community publication. Submit your
insights to reach our global audience and earn through the TDS
Author Payment Program.
Write for TDS
WRITTEN BY
Eivind Kjosbakken
Ai Assistant Claude Code Llm Machine Learning
OpenClaw
Share This Article
See all from Eivind Kjosbakken
Related Articles
ARTIFICIAL INTELLIGENCE
Talk to my Agent
The exciting new world of designing
conversation driven APIs for LLMs.
Roni Dover
July 28, 2025
AGENTIC AI
Smarter Model Tuning: An AI
Agent with LangGraph +
Streamlit That Boosts ML
Performance
Automating model tuning in Python with
Gemini, LangGraph, and Streamlit for
regression and classification
improvements
Gustavo Santos
August 20, 2025
MACHINE LEARNING
Using LangGraph and MCP
Servers to Create My Own Voice
Assistant
AGENTIC AI
Preventing Context Overload:
Controlled Neo4j MCP Cypher
Responses for LLMs
9 min read
12 min read
Built over 14 days, all locally run, no API
keys, cloud services, or subscription
fees.
Benjamin Lee
September 4, 2025
How timeouts, truncation, and result
sanitization keep Cypher outputs LLMready
Tomaz Bratanic
September 7, 2025
AGENTIC AI
How to Build Effective AI Agents
to Process Millions of Requests
Learn how to build production ready
systems using AI agents
Eivind Kjosbakken
September 9, 2025
AUTHOR SPOTLIGHTS
Generalists Can Also Dig Deep
Ida Silfverskiöld on AI agents, RAG, evals,
and what design choice ended up
mattering more…
TDS Editors
September 12, 2025
AGENTIC AI
Building Research Agents for
Tech Insights
Using a controlled workflow, unique data
& prompt chaining
Ida Silfverskiöld
September 13, 2025
30 min read 4 min read
9 min read 6 min read
10 min read
Your home for data science and Al. The world’s leading publication for data science, data
analytics, data engineering, machine learning, and artificial intelligence professionals.
© Insight Media Group, LLC 2026
Subscribe to Our Newsletter
WRITE FOR TDS • ABOUT • ADVERTISE • PRIVACY POLICY • TERMS OF USE