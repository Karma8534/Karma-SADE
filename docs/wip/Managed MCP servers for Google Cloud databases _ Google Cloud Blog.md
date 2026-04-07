# Managed MCP servers for Google Cloud databases _ Google Cloud Blog

*Converted from: Managed MCP servers for Google Cloud databases _ Google Cloud Blog.PDF*



---
*Page 1*


Cloud Blog Contact sales Get started for free
Databases
Powering the next
generation of agents with
Google Cloud databases
February 18, 2026
Amit Ganesh Rahul Deshmukh
Vice President, AI & Sr. Product Manager, AI
Databases for Databases
For developers building AI applications, including
custom agents and chatbots, the open-source


---
*Page 2*


Model Context Protocol (MCP) standard enables
Cloud Blog Contact sales Get started for free
your innovations to access data and tools
consistently and securely. At the end of 2025, we
introduced managed and remote MCP support for
services like Google Maps and BigQuery,
establishing a standard method for AI to connect
with tools, and effectively creating a universal
interface for applications. Today, we are expanding
this offering to include PostgreSQL with AlloyDB,
Spanner and Cloud SQL, as well as Firestore and
Bigtable for high-performance NoSQL workloads,
and introducing a new Developer Knowledge MCP
server, which presents an API to connect IDEs to
Google’s documentation. These servers run in
Google Cloud, providing a secure interface for
Gemini and other MCP-compliant clients to easily
interact with data and infrastructure.
With the launch of Gemini 3, developers gained
advanced reasoning capabilities to plan, build, and
solve complex problems. But for an AI model to
function as a useful "agent," it must reliably interact
with its environment. Today’s announcement
extends these capabilities more broadly to the
database tools our customers leverage daily as the
backbone of their work environment.
To connect your agents to these servers, you don’t
need to deploy infrastructure. Just configure the
MCP server endpoint in the agent configuration and
immediately gain access to your operational data,
backed by enterprise-grade auditing, observability
and governance. With no infrastructure
management, you can scale your agentic workloads
without incurring operational overhead.


---
*Page 3*


Bringing operational data to
Cloud Blog Contact sales Get started for free
agents
These new managed servers enable agents to
access specific capabilities across our portfolio:
AlloyDB for PostgreSQL: Agents can interact
with PostgreSQL workloads, enabling tasks such
as schema creation, diagnosing complex
queries for slowness and performing vector
similarity search.
Spanner: With unified multi-model capabilities
in Spanner such as Spanner Graph, agents can
model and query complex relationships directly
alongside relational and semantic data using
standard (SQL and GQL) queries. This allows
agents to quickly uncover deep insights (like
identifying fraud rings or generating product
recommendations) using the MCP tools at its
disposal.
Cloud SQL for PostgreSQL, MySQL and SQL
Server: Developers and database
administrators can use the Cloud SQL MCP
Server across MySQL, PostgreSQL, and SQL
Server fleets for natural language interactions
with the database, AI-assisted app
development, query performance optimization
and database troubleshooting via agents.
Bigtable: Bigtable’s flexible schema and high-
throughput ingestion capabilities are commonly
used for building digital integration hubs and
managing time series data. MCP simplifies
automating operational workflows and


---
*Page 4*


developing agentic customer support, CRM,
Cloud Blog Contact sales Get started for free
human resources, IT operations, supply chain
and logistics applications with this data.
Firestore: Focused on mobile and web
development, the Firestore MCP server enables
agents to sync with live document collections.
This supports dynamic interactions such as
checking user session states or verifying order
statuses via natural language prompts.
Managing applications and
infrastructure
Beyond data retrieval, we are enabling agents to
help build and manage applications. The Developer
Knowledge MCP server connects IDEs to Google’s
documentation, allowing agents to answer technical
questions and troubleshoot code with relevant
context.
Security and governance
Connecting an agent to a database requires robust
security and governance. These servers are built on
Google Cloud's standard identity and observability
frameworks:
Identity-first security: Authentication is
handled entirely through Identity and Access
Management (IAM) rather than shared keys.
This ensures agents can only access the


---
*Page 5*


specific tables or views explicitly authorized by
Cloud Blog Contact sales Get started for free
the user.
Full observability: To track agent activity, every
query and action taken via these MCP servers is
logged in Cloud Audit Logs. This provides
security teams with a record of every database
interaction, maintaining visibility alongside ease
of access.
Demo: From local code to
managed data
Let’s see these new MCP servers in action.
Imagine an agent designed to automate the
migration of a full-stack event management
platform for fitness communities. Through a series
of natural language instructions in the Gemini CLI,
the agent utilizes the Cloud SQL remote MCP
server to provision a managed PostgreSQL
instance, apply the correct schema, and securely
migrate your local data. You don't need to master
complex gcloud commands or become a Cloud
SQL expert; the agent handles the heavy lifting. This
transition is architected in real-time by the
Developer Knowledge MCP server, which
references official documentation to guide the
agent through best practices — easily upgrading
your application's backbone from local storage to a
fully managed enterprise database.


---
*Page 6*


Cloud Blog Contact sales Get started for free
Support for third-party
agents
Because these servers follow the open MCP
standard, they also work with your favorite AI
agents. You can easily connect clients like
Anthropic’s Claude by adding a Custom Connector
in the settings. Simply point it to your Google Cloud
database MCP endpoint, and you are ready to start
building — no complex configuration files required.


---
*Page 7*


What’s next
Cloud Blog Contact sales Get started for free
We’ll continue to expand this ecosystem in the
coming months with managed MCP support for
Looker, Database Migration Service (DMS),
BigQuery Migration Service, Memorystore,
Database Center, Pub/Sub, Kafka and more.
To start building secure, data-driven agents, explore
our guides for AlloyDB, Spanner, Cloud SQL,
Bigtable, and Firestore. You can also check out
these codelabs for Cloud SQL and Spanner, along
with this demo video walking through the app
migration to Google Cloud.
Posted in Databases—AI & Machine Learning—
Application Development—Cloud SQL—
Spanner
Related articles


---
*Page 8*


Cloud Blog Contact sales Get started for free
Databases Data Analytics
Google (Spanner) Ranks #1 for What’s new with Google Data
Lightweight Transactions Use Cloud
Case in Gartner® Critical
By The Google Cloud Data Analytics, BI, and
Capabilities Report
Database teams • 3-minute read
By Jagan R. Athreya • 5-minute read
Databases Databases
Spanner in 2025: Innovations Introducing managed connection
powering intelligent, multi-model pooling in AlloyDB — scale
AI applications further, connect faster
By Shubhankar Chatterjee • 10-minute read By Emir Okan • 8-minute read
Follow us


---
*Page 9*


Cloud Blog Contact sales Get started for free
Google Cloud Google Cloud Products Privacy Terms
Help English