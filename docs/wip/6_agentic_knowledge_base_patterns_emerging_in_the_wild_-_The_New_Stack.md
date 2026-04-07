# 6_agentic_knowledge_base_patterns_emerging_in_the_wild_-_The_New_Stack

*Converted from: 6_agentic_knowledge_base_patterns_emerging_in_the_wild_-_The_New_Stack.PDF*



---
*Page 1*


AI AGENTS / AI OPERATIONS / MODEL CONTEXT PROTOCOL
6 agentic knowledge base patterns emerging in
the wild
Organizations are actively building agentic knowledge bases for AI agents. Here are six
real-world approaches taking shape across the software industry.
Feb 18th, 2026 5:00am by Bill Doerrfeld
Rizki Ardia for Unsplash+
AI agents have become the software industry’s latest fascination. Backed by large
language models (LLMs), this new class of AI is unlocking data-driven decision-


---
*Page 2*


making and autonomous actions, transforming enterprise software practices and
business workflows in the process.
However, it wasn’t always this way. According to Ajay Prakash, a senior staff software
engineer at LinkedIn, AI agents initially faced a major gap. “Out of the box, AI coding
agents weren’t effective,” Prakash tells The New Stack. They lacked context and
awareness of internal systems, frameworks, and practices, he adds.
“Out of the box, AI coding agents weren’t effective. They lacked
context and awareness of internal systems, frameworks, and
practices…”
Agentic knowledge bases have emerged to close that gap. These systems allow AI
agents to surface institutional data, runbooks, tools, project histories, and other
context, helping them operate more effectively to deliver more consistent, verifiable
outcomes.
As Anusha Kovi, a business intelligence engineer at Amazon, tells The New Stack,
“Organizations are definitely building these, though it rarely looks like one centralized
knowledge base product.” Instead, they’re often materializing as purpose-built layers
to enforce accountability within specific domains.
Agentic knowledge bases are still taking shape, and their architectures, data sources,
and use cases vary widely. Some are purely internal, while others are embedded within
products or exposed to partners. What they have in common: coalescing organization-
wide working standards. Below are six emerging patterns.
1. The playbook for coding assistants
The foremost use case for agentic knowledge bases in software development is
context engineering. A prime example is LinkedIn’s knowledge base for AI agents,
which acts as a source of truth for coding style and conventions, bringing platform
consistency to AI-driven development. But it goes beyond enforcing style — it governs
how agents act.


---
*Page 3*


“Our knowledge base at LinkedIn enables AI coding agents to assist with company-
specific tasks by providing tools to access internal systems and playbooks,” says
LinkedIn’s Prakash. These playbooks encode rules, conventions, procedures, and
verification steps.
TRENDING STORIES
1. VS Code becomes multi-agent command center for developers
2. Why 40% of AI projects will be canceled by 2027 (and how to stay in
the other 60%)
3. GitHub's former CEO launches a developer platform for the age of
agentic coding
4. GitLab CEO on why AI isn't helping enterprises ship code faster
5. The reason AI agents shouldn’t touch your source code — and what
they should do instead
One playbook focuses on debugging. “The agent proactively gathers relevant context,”
says Prakash. “It fetches ticket details, pulls relevant logs, searches historical tickets,
identifies related code paths, and classifies the likely team owners, automatically.”
More than gathering information, the playbook directs comprehensive operations.
“The agent can apply the fix, run validation, and create a pull request with the original
ticket linked, closing the loop from bug report to resolution,” says Prakash.
LinkedIn calls its framework contextual agent playbooks and tools (CAPT). It surfaces
organization-wide instructions and dynamically exposes tool integrations and
playbooks using Model Context Protocol (MCP). Interestingly, our playbook
architecture anticipated what the industry later standardized as agent skills,” adds
Prakash.
2. The integration knowledge center
Another use case is standardizing enterprise integration knowledge. Integrations are
notoriously challenging to maintain, as fields change or contracts drift over time,
making them brittle.


---
*Page 4*


Adeptia has built an AI knowledge base as part of its data automation platform,
empowering AI agents with institutional integration patterns and on-the-ground
context. As Tim Bond, chief product officer at Adeptia, tells The New Stack, the
knowledge base helps agents gradually understand how systems are used in practice.
“Agents interact through retrieval and augmentation,” says Bond. They first start with
institutional knowledge, such as schemas, known integration patterns, and
compliance requirements. Then, to tailor responses, the agents query situational
context, such as prior conversations, workflow configurations, custom system
mappings, and domain-specific terminology.
An example could be informing an AI agent how to automate a Salesforce-to-NetSuite
integration, adds Bond.
With access to an AI knowledge center, agents can produce more valid, less generic
integrations. “Agents become increasingly helpful over time, require less repetitive
clarification, and handle more complex tasks,” says Bond.
3. The multi-agent home base
Agentic knowledge bases are also being designed to standardize multi-agent
operations at scale. Organizations like R Systems, an IT service management
company, are exploring knowledge bases as a foundation for such intelligent
automation.
Neeraj Abhyankar, VP of data and AI at R Systems, tells The New Stack that an agent
knowledge base serves as the company’s brain. “It gives every agent the same rules,
voice, and playbook so they don’t improvise policy on the fly,” he says.
“We’ve implemented solutions that combine vectorized document repositories,
semantic search, and retrieval-augmented generation (RAG) to support multi-agent
workflows,” adds Abhyankar.
At the heart of their knowledge base is practical data and know-how, including
policies, escalation paths, redaction rules, schemas, and vocabulary, runbooks like
step-by-step how-tos for common tasks, and tool manifests.


---
*Page 5*


Key benefits include faster agent action, greater consistency at scale, and improved
governance, since responses and actions are traceable. “When a rule or template in
the knowledge base is tweaked, the improvement shows up everywhere at once,” says
Abhyankar. “How we work is encoded in the knowledge base, not scattered.”
4. The shared well of business context
It goes beyond software disciplines — agentic knowledge bases also empower
business workflows. For example, Epicor’s knowledge base provides institutional
knowledge on business data and enterprise resource planning (ERP) to inform
financial and customer support agents better.
As Arturo Buzzalino, group vice president and chief innovation officer, Epicor, a
provider of enterprise resource planning software, tells The New Stack, “We’ve built a
centralized, organization-wide knowledge infrastructure designed specifically to
support AI-driven work.”
In addition to accelerating access to business information, the knowledge base guides
new workflows. “We saw an opportunity to enable true agentic automation,” says
Buzzalino. “That shift from ‘tell me this’ to ‘handle this’ is what pushed us to formalize
the knowledge base.”
Internal data supporting the knowledge base includes support documentation, system
guidance, ticket histories, ERP-related knowledge, historical implementation data, and
financial data.
“One of the most impactful examples is our financial agent,” says Buzzalino. Epicor’s
knowledge base streamlines answers to complex financial questions, such as ‘Show
me X metric for last quarter’ or ‘What’s our performance in Y region?’
“The agent retrieves the answer directly from the financial knowledge base, without
needing to create a ticket, look at a dashboard, or wait for someone else with the right
expertise,” says Buzzalino.
Epicor is seeing similar gains within its professional services division. For instance,
agents can reference implementation data from past projects to improve real-time
support.


---
*Page 6*


Overall, the results have been increased agility and higher-value work delivered at
lower operational cost, says Buzzalino. “It turns latent organizational knowledge into
accessible intelligence, making individuals dramatically more capable in their roles.”
5. The source of truth for data intelligence
Other agentic knowledge bases are similarly emerging to bring consistency to
business intelligence and data engineering disciplines. In these areas, a knowledge
base can help an AI agent resolve confusion when it encounters conflicting fields or
redundancies in databases.
A big driver is metrics chaos. “Conversations like ‘Wait, my dashboard shows a
different number’ basically disappear when the agent always pulls from the same
governed definition,” says Amazon’s Kovi. “That alone is worth it.”
“What I’ve seen in practice is teams assembling purpose-built layers that agents query
before taking action,” Kovi adds. Structurally, the backend is composed of machine-
readable definitions of tasks, schemas, data quality rulesets, and incident runbooks.
“The knowledge base isn’t there to help the agent be creative. It’s
there to keep it inside the lines.”
On the business intelligence side, Kovi notes that these often emerge as a semantic
layer, powered by metric definitions, exact SQL logic, dimensional hierarchies,
business rule exceptions, and report formatting standards.
Although it sounds tech-heavy, your typical agentic knowledge base is using pretty
standard components. “Most of it is YAML configs, versioned markdown, and
structured catalog tables exposed via API.”
According to Kovi, agent knowledge bases reduce the repetitive grind of incident
triage in data engineering. Converging on a single, one true definition of a metric can
avoid getting different answers from slightly different prompts for the same source.


---
*Page 7*


“You’ve got three teams with three different SQL definitions of ‘revenue,’ and the agent
just grabs whichever one scores highest in a vector search,” Kovi says. “The
knowledge base becomes the thing the agent has to check before it writes any query.”
6. The MCP-powered capability layer
Arguably, new infrastructure around MCP, such as MCP gateways and MCP registries,
takes agentic knowledge bases to their zenith, since they add a structured means for
AI agents to access sanctioned capabilities, bringing governed power to what an LLM
can automate on its own.
For instance, Vendia, an AI platform provider, has built an MCP gateway to construct
agentic knowledge bases.
Tim Wagner, CEO and co-founder, Vendia, tells The New Stack that the MCP protocol is
enabling a sea change in agent architecture. It unlocks LLM intelligence and
simultaneously lowers the cost, delivery risk, and complexity of building agents that
can access and eventually maintain AI knowledge bases.
Wagner adds: “Companies are starting to migrate from prompt stuffing techniques
like RAG that require the company’s developers to manually search and compute
results out of the knowledge base and instead let the LLM automate its own
searching, retrieval, and results exploration.”
The revolutionary aspect is that, through MCP, he says, AI agent queries can be
combined with all of a company’s other assets and services, including third-party
software-as-a-service APIs, internal applications, and cloud and on-premises content
management systems.
Alongside MCP servers, he’s seeing organizations store media and intellectual
property assets, policy documents, manuals, and more within AI knowledge bases.
The use cases vary across sectors and span both internal and external-facing
workflows.
For Wagner, the benefits of an agentic knowledge base are primarily customer-based.
“Usually, improved employee or customer outcomes are the driving force today, more
so than automation or cost reduction.”


---
*Page 8*


Agentic knowledge bases bring clear results
Many companies, platforms, and infrastructure providers are actively constructing AI
knowledge bases for various purposes. The resounding effect is to govern access to
data and capabilities and to reduce tribal knowledge in the process.
Bond shares that Adeptia’s approach of combining historical knowledge with
situational context has reduced dependence on human support while maintaining
accuracy.
After implementing an agentic knowledge base, LinkedIn has seen a 20% increase in
AI coding adoption and measurable productivity gains in debugging and data analysis.
“Issue triage time has dropped by approximately 70% in many areas,” says LinkedIn’s
Prakash.
In data engineering, a knowledge base establishes an institutionally defined context to
prevent an LLM from misinterpreting information or assuming database mechanics.
“The knowledge base isn’t there to help the agent be creative,” says Amazon’s Kovi.
“It’s there to keep it inside the lines.”
The groundwork for agentic AI
A 2026 Zapier study found that 25% of enterprises expect to achieve full-scale
orchestration by 2026, in which AI functions as an operating system for the business.
43% anticipate reaching the agentic AI stage, defined by more autonomous linking of
systems and workflows.
More AI agent development is underway, and knowledge bases will be a key
component to support its maturity. Today’s early implementations demonstrate much
potential as a foundation for future iteration.
That said, challenges remain: Keeping data fresh will require pipelines to continually
update the knowledge base and ensure data quality. Experts also recommend using an
open, standards-based approach, maintaining distributed ownership, establishing
version control, and intentionally federating knowledge.
“The space is still evolving,” says R Systems’ Abhyankar. “Structured knowledge bases
can empower AI agents to deliver reliable, context-aware assistance and lay the
groundwork for broader enterprise adoption of agentic AI.”


---
*Page 9*


Bill Doerrfeld is a tech journalist and API thought leader. He is the editor-in-chief of the Nordic
APIs blog, a global API community dedicated to making the world more programmable. He is
also an active contributor to a handful of...
Read more from Bill Doerrfeld
SHARE THIS STORY
TRENDING STORIES
1. VS Code becomes multi-agent command center for developers
2. Why 40% of AI projects will be canceled by 2027 (and how to stay in the other
60%)
3. GitHub's former CEO launches a developer platform for the age of agentic coding
4. GitLab CEO on why AI isn't helping enterprises ship code faster
5. The reason AI agents shouldn’t touch your source code — and what they should
do instead
INSIGHTS FROM OUR SPONSORS
Why I joined Nitric
20 October 2025
Build Azure Infrastructure Using AI and Terraform
11 June 2025


---
*Page 10*


GenAI Made Terraform More Relevant Than Ever
1 April 2025
Andela | Apply to Join the Next Cohort of Kubernetes
Experts Powering Global Cloud-Native Operations from
Africa
21 January 2026
Andela | Partnership to Train 30,000 African
Technologists on Kubernetes Sparks Career Growth &
High Demand
11 November 2025
Andela | AI Can Eviscerate Technical Debt, But Only If
You Let It
20 August 2025
Devtron vs Harness
18 February 2026
Best 7 Harness Alternatives in 2026: Top CI/CD Tools
Compared
27 January 2026
Introducing Devtron 2.0 - A Unified Platform for
Kubernetes Operation
22 December 2025
TNS DAILY NEWSLETTER


---
*Page 11*


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
*Page 12*


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