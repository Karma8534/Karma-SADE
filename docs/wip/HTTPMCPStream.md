# HTTPMCPStream

*Converted from: HTTPMCPStream.pdf*



---
*Page 1*


3/27/26, 4:10 PM Implementing MCP with Streamable HTTP Transport in prod | by DhanushKumar | Mar, 2026 | Artificial Intelligence in Plain English
Artificial Intelligence in Pla…
Implementing MCP with Streamable
HTTP Transport in prod
Overview :
DhanushKumar Follow 16 min read · 5 days ago
19 1
The Model Context Protocol (MCP) is an open standard introduced by
Anthropic in late 2024 to connect AI systems with external data and services.
It provides a JSON-RPC 2.0 based message protocol that explicitly separates
tool invocation from natural language prompts. In practice, an MCP Host
(for example an AI assistant or IDE) embeds an MCP Client, which speaks a
uniform JSON-RPC format to one or more MCP Servers. Each MCP Server
exposes a specific capability (such as a database query, file system access,
or web API) and mediates access to underlying resources. This design is
often likened to a “USB-C for AI” — a universal adapter that lets any AI agent
call any tool through the same protocol. By late 2025, MCP support had
rapidly become widespread across the industry, with major AI platforms
(OpenAI’s ChatGPT, Google DeepMind, Microsoft Copilot, etc.)
implementing the standard.
Under the hood, MCP formalizes communication and lifecycle phases. A
client first sends an initialize JSON-RPC request declaring its version and
capabilities; the server responds with its own capabilities and a session ID
(if session state is used). After this handshake, the client can send
tools/list requests to discover available tools, and tools/call requests to
invoke them. Each response is a JSON object with content (an array of result
blocks) and an isError flag according to the schema. MCP defines standard
transports: a local subprocess mode using STDIO, and a streamable HTTP
mode (HTTP POST with optional SSE for streaming).In HTTP mode, the
server exposes a single endpoint (e.g., /mcp) that accepts POST request
carrying JSON-RPC messages and can optionally return a streaming SSE
responses. Implementations must validate Origin, bind only to localhost by
default, and require authentication to prevent DNS rebinding or
unauthorized access.
https://medium.com/ai-in-plain-english/implementing-mcp-with-streamable-http-transport-in-prod-23ca9c6731ca 1/16


---
*Page 2*


3/27/26, 4:10 PM Implementing MCP with Streamable HTTP Transport in prod | by DhanushKumar | Mar, 2026 | Artificial Intelligence in Plain English
A core best practice is to use MCP Gateway — a reverse proxy and registry
that stis between AI clients and MCP servers. The gateway provides a single
entry point (for example, mcp.mycompany.com) under which all tool
endpoints are namespaced (e.g., /crm/* for a CRM server, /db/* for a
database server).This simplifies client config and centralizes control : a
gateway can maintain a service registry (often with UI 0 so new tools are
discovered dynamically. It also allows centralized load balancing , health
checking and unified policy enforcement : with one gateway you can apply
authentication , rate limits , logging for every tool call, rather than each
server handling it separately .In fact , ByteBridge notes that production MCP
deployments should be designed around a gateway architecture to keep things
organized; all MCP requests from clients should funnel through this
controlled entry point, making security, monitoring, and scaling far more
tractable. Open-source gateways (often built on NGINX or FastAPI) and
commercial offerings (such as Peta by ByteBridge) already provide these
features, including secret management and human-in-the-loop approvals.
MCP in Prod :
The MCP offers a streamable HTTP transport that turns the MCP server into
a standard web API. Instead of using the older stdio transport (which only
works for local processess), streamble HTTP allows any MCP server to be
hosted like a normal web service. In practice, the server listens on a HTTP(s)
endpoint (e.g., /mcp), and then the client communication via HTTP POST
and Server-sent Events (SSE) .As one practitioner notes, using
transport="streamable-http" makes your MCP server “production-ready” it
can be deployed anywhere , scales like a REST API and maintains real time
bidirectional communication over HTTP .This solves the limitations of stdio
(desktop-only , no web support) by fitting into the existing cloud infra.
Under streamable HTTP, the MCP session begin with an HTTP initialize
request. .The server responds with a JSON payload and also sets an MCP-
Session-Id header, establishing a session .The client then makes all further
calls with that MCP-Session-Id header . To receive asynchronous events (such
as progress updates or multi-part results), the client also opens a separate
HTTP GET to a designated SSE endpoint (often the same /mcp path).In effect
, the client has two connections: a POST channel for sending requests and a
https://medium.com/ai-in-plain-english/implementing-mcp-with-streamable-http-transport-in-prod-23ca9c6731ca 2/16


---
*Page 3*


3/27/26, 4:10 PM Implementing MCP with Streamable HTTP Transport in prod | by DhanushKumar | Mar, 2026 | Artificial Intelligence in Plain English
long-lived GET (Accept : text/event-stream) for receivin SSE messages.The
server can choose to answer each POST with either a direct JSON response
(for quick operations) or switch to SSE mode ( Content-Type: text/event-
stream) to push multiple updates. This pattern is detailed in the spec : an SSE
stream allows sending a sequence of JSON messages ,each prefixed with id:
<num>, followed by newline and JSON content. In summary , streamable
HTTP is session-based and full duplex : the client constantly polls the GET
SSE stream ,while sending new instructions via POST .
End to End Architecture with Streamable HTTP
A typical prod setup uses a standard web architecture. The AI Agent ( MCP
Client) and the MCP servers sit behind an API gateway or ingress .For
example, there might ocnfigure a gateway with one hostname
(api.example.com) and route /mcp to your MCP server service. The MCP
server itself listens on port 8000(HTTP) .The agent initiates an MCP session
by POSTing to https://api.example.com/mcp, receiving a session ID , and then
opens an SSE Stream on the same path.The gateway should support sticky
sessions or properly route SSE connections to the same backend .Behing the
scences , load balancers or kubernetes can run multiple replicas .Becuase
SSE connections are long-lived , use HTTP/2 or HTTP/1.1 with keep-alive and
consider increasing timeout and max connections .Crucially ,treat each MCP
server as any stateful microsservices : log each request with session ID ,
monitor open SSE connections and ensure the network allows bidirectional
streaming.
https://medium.com/ai-in-plain-english/implementing-mcp-with-streamable-http-transport-in-prod-23ca9c6731ca 3/16


---
*Page 4*


3/27/26, 4:10 PM Implementing MCP with Streamable HTTP Transport in prod | by DhanushKumar | Mar, 2026 | Artificial Intelligence in Plain English
Security and reliability aspects are like any web API. USe HTTPS/TLS so that
both the POST requests and SSE responses are encrypted.Validate the Origin
header on the server to mitigate CSRF on the SSE endpoint . Aunthenticate
every request : intial MCP implementations often lacked authentication (one
“admin” token for all) which is dangerous in multi-tenant use .In prod, issue
each client a JWT or OAuth2 Toke, and uses FastMCP’s a built-in OAuth
support if needed.For example , the PythonFastMCP class allows to plugin a
TokenVerifier that checks bearer tokens according to the MCP auth
spec.Enfore fine-grained authorizations :only allow each agent to call the
tools it should (role-based access) .Configure rate -limiting on the gateway to
precent a runaway agent from overloading tools .
Load balancing works as usual : you can run multiple MCP server instances
behind a load balancer or kubernetes service .Ensure each server instances
can share workload ; streaming mode doesn’t preclude horizontal scaling. It
may need session affinity for the SSE stream or use a sticky session cookie.
Alternatively , it can centralize state (e.g., put all the session state in Redis) so
any instance can pick up where another left off.For high availability , place
health checks on /health or /ready endpoints (exposes by FastMCP or
custom) .Monitor the application with standard tools : log each tool
invocation (with session ID , tool name, params , result) and emit metrics
(requests sec, SSE streas open, error rates) to cloudwatch.In brief, observer
MCP servers the same way you would any HTTP microservice.
In summary, the MCP architecture in production typically involves AI agent
clients connecting to a central gateway, which routes requests to individual
MCP server microservices. Each server handles a specific resource or API.
All components communicate via JSON-RPC over TCP or HTTP/SSE with
clearly defined JSON schemas. The gateway abstracts away complexity (and
can act as a policy enforcement point), while MCP servers focus on exposing
business logic or data. This modular design enables scalability and security:
new tools are just new servers registered with the gateway, without changing
the AI client.
https://medium.com/ai-in-plain-english/implementing-mcp-with-streamable-http-transport-in-prod-23ca9c6731ca 4/16


---
*Page 5*


3/27/26, 4:10 PM Implementing MCP with Streamable HTTP Transport in prod | by DhanushKumar | Mar, 2026 | Artificial Intelligence in Plain English
MCP Streamable HTTP — Production Workflow Diagram
+-----------------------+
| AI AGENT / LLM |
| (LangGraph / Backend) |
+----------+------------+
|
| 1. JSON-RPC POST (initialize)
v
+-----------------------------+
| API GATEWAY / LOAD BALANCER |
| (Auth, Rate Limit, Routing) |
+-------------+---------------+
|
v
+-----------------------------+
| MCP SERVER |
https://medium.com/ai-in-plain-english/implementing-mcp-with-streamable-http-transport-in-prod-23ca9c6731ca 5/16


---
*Page 6*


3/27/26, 4:10 PM Implementing MCP with Streamable HTTP Transport in prod | by DhanushKumar | Mar, 2026 | Artificial Intelligence in Plain English
| - Tool Registry |
| - Session Manager |
| - Execution Engine |
+------+----------------------+
|
| 2. Open SSE Stream (GET /events)
v
+-----------------------------+
| STREAM CHANNEL (SSE) |
| (Server → Client Updates) |
+-----------------------------+
|
| 3. Tool Invocation
v
+-----------------------------+
| EXECUTION LAYER |
|-----------------------------|
| External APIs |
| Vector DB (RAG) |
| Databases |
| ML Models / Services |
+-----------------------------+
|
| 4. Streaming Results
v
+-----------------------------+
| STREAM RESPONSE (SSE) |
| Partial + Final Outputs |
+-----------------------------+
|
v
+-----------------------+
| AI AGENT |
| (Consumes Stream) |
+-----------------------+
MCP STDIO — Local Workflow Diagram
+--------------------------+
| AI AGENT / CLIENT |
| (Claude Desktop / IDE) |
+------------+-------------+
|
| Spawn Process
v
+-----------------------------+
| MCP SERVER |
| (Local Subprocess) |
+-------------+---------------+
|
-------------------------
| | |
v v v
+--------+ +--------+ +--------+
| stdin | | stdout | | stderr |
| (req) | | (resp) | | (logs) |
+--------+ +--------+ +--------+
|
| Tool Execution
v
+-----------------------------+
| LOCAL EXECUTION LAYER |
https://medium.com/ai-in-plain-english/implementing-mcp-with-streamable-http-transport-in-prod-23ca9c6731ca 6/16


---
*Page 7*


3/27/26, 4:10 PM Implementing MCP with Streamable HTTP Transport in prod | by DhanushKumar | Mar, 2026 | Artificial Intelligence in Plain English
|-----------------------------|
| File System |
| Local APIs |
| CLI Tools |
| Local Databases |
+-----------------------------+
|
| Response via stdout
v
+--------------------------+
| AI AGENT / CLIENT |
+--------------------------+
End-to-End MCP Server Example (Python)
To illustrate a concrete implementation, consider building a production-
grade MCP server in Python. The official MCP Python SDK provides a
convenient framework (e.g. FastMCP) that fully implements the protocol and
transports. Below is a simplified example of a file-system MCP server. This
server runs over HTTP (SSE-enabled) and exposes two tools: list_files and
read_file, confined to a secure base directory. It includes error handling
and enforces path restrictions to prevent unauthorized access.
import os
from pathlib import Path
from typing import List
from mcp.server.fastmcp import FastMCP
# Define the base directory (workspace) for file operations
BASE_DIR = Path("./workspace").resolve()
if not BASE_DIR.exists():
BASE_DIR.mkdir()
mcp = FastMCP(name="FileServer", json_response=True)
@mcp.tool()
def list_files() -> dict:
"""List files in the base directory."""
try:
entries = [f.name for f in BASE_DIR.iterdir() if f.is_file()]
text = "Files: " + ", ".join(entries)
# Return content as per MCP spec: array of {type, text}
return {"content": [{"type": "text", "text": text}], "isError": False}
except Exception as e:
error_text = f"Error listing files: {e}"
return {"content": [{"type": "text", "text": error_text}], "isError": True}
@mcp.tool()
def read_file(path: str) -> dict:
"""
Read the contents of a file within the base directory.
Returns the file text or an error if access is invalid.
"""
# Resolve the requested path securely within BASE_DIR
target = (BASE_DIR / path).resolve()
# Security check: ensure target is a subpath of BASE_DIR
if not str(target).startswith(str(BASE_DIR)):
return {"content": [{"type": "text", "text": "Access denied"}], "isError": T
if not target.exists():
return {"content": [{"type": "text", "text": f"File '{path}' not found"}], "
try:
content = target.read_text(encoding="utf-8")
return {"content": [{"type": "text", "text": content}], "isError": False}
https://medium.com/ai-in-plain-english/implementing-mcp-with-streamable-http-transport-in-prod-23ca9c6731ca 7/16


---
*Page 8*


3/27/26, 4:10 PM Implementing MCP with Streamable HTTP Transport in prod | by DhanushKumar | Mar, 2026 | Artificial Intelligence in Plain English
except Exception as e:
return {"content": [{"type": "text", "text": f"Read error: {e}"}], "isError"
if __name__ == "__main__":
# Run the MCP server on port 8000 with Streamable HTTP transport
# (the SDK handles HTTP+SSE as per MCP spec).
mcp.run(transport="streamable-http", port=8000)
This code uses FastMCP, which under the hood manages JSON-RPC framing
and lifecycle.It declares each tool with the @mcp.tool() decorator and returns
results that match the MCP schema (an object with content and isError).
The example enforces security by requiring that any file path lies under
BASE_DIR; otherwise it returns an "Access denied" error. This prevents
directory traversal and data leakage. In a real system, each tool would
include thorough input validation and exception handling as shown. By
using the SDK and structured JSON responses, this server is immediately
compatible with any MCP client or gateway.
A client (e.g. an AI host) would first call the initialize method to negotiate
protocol version and capabilities, then use tools/list to see list_files and
read_file, and finally issue tools/call requests like:
{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "read_file",
 
and the server would reply with a result object containing the file content or
error text .The protocol ensures every message is well-typed and that erros
are reported formally (e.g. JSON-RPC error for method not found, or an
isError: true in the result for execution errors).
Deployment and Infrastructure
 
In production, MCP servers should be containerized and orchestrated like
any critical microservice. The example Python server above can be packaged
with a minimal Dockerfile. For instance, using a slim Python base image and
adding a non-root user enhances security. A sample Dockerfile might be:
# Dockerfile
FROM python:3.11-slim AS base
# Create a dedicated user for MCP server
RUN groupadd -g 1001 mcpuser && useradd -u 1001 -g mcpuser mcpuser
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
# Copy application code
COPY . .
# Run as non-root for security
USER mcpuser
https://medium.com/ai-in-plain-english/implementing-mcp-with-streamable-http-transport-in-prod-23ca9c6731ca 8/16


---
*Page 9*


3/27/26, 4:10 PM Implementing MCP with Streamable HTTP Transport in prod | by DhanushKumar | Mar, 2026 | Artificial Intelligence in Plain English
EXPOSE 8000
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
This container runs the server on port 8000, as the non-root mcpuser user. A
healthcheck (not shown) should verify the /health endpoint regularly. When
running in Kubernetes, we deploy this container with a Deployment spec.
For example, we would define several replicas behind a Service, enable
rolling updates, and enforce strict Pod security. A snippet:
apiVersion: apps/v1
kind: Deployment
metadata:
name: mcp-fileserver
namespace: ai-agents
spec:
replicas: 3
strategy:
type: RollingUpdate
rollingUpdate:
maxSurge: 1
maxUnavailable: 0
selector:
matchLabels:
app: mcp-fileserver
template:
metadata:
labels:
app: mcp-fileserver
spec:
serviceAccountName: mcp-service-account
securityContext:
runAsNonRoot: true
runAsUser: 1001
fsGroup: 1001
containers:
- name: fileserver
image: myregistry/mcp-fileserver:v1
ports:
- containerPort: 8000
resources:
requests:
cpu: 100m
memory: 128Mi
limits:
cpu: 500m
memory: 256Mi
livenessProbe:
httpGet:
path: /health
port: 8000
initialDelaySeconds: 15
periodSeconds: 20
readinessProbe:
httpGet:
path: /ready
port: 8000
initialDelaySeconds: 5
periodSeconds: 10
env:
- name: PYTHONUNBUFFERED
value: "1"
https://medium.com/ai-in-plain-english/implementing-mcp-with-streamable-http-transport-in-prod-23ca9c6731ca 9/16


---
*Page 10*


3/27/26, 4:10 PM Implementing MCP with Streamable HTTP Transport in prod | by DhanushKumar | Mar, 2026 | Artificial Intelligence in Plain English
This Kubernetes configuration runs 3 pods of the MCP server with a rolling
update strategy. It sets runAsNonRoot and a fixed runAsUser for security,
mounts no sensitive volumes, and includes liveness/readiness probes.
These practices (non-root user, resource quotas, health checks) are advised
for production MCP containers.Horizontal Pod Autoscaling (based on CPU
or custom metrics) can be added to scale pods automatically. The MCP
Gateway itself would similarly run behind a Service or Ingress.
Networking-wise, one can expose the gateway on the public API (securely
behind an API gateway or ingress controller) while binding internal MCP
servers to localhost or a secure overlay network. Wildcard DNS or a service
mesh can route e.g. mcp.company.com/file/ to the file server and .../db/ to a
database tool. Each service should use TLS and token-based auth (see
below).
Observability, Monitoring, and Reliability
MCP services must be treated as mission-critical microservices. This means
robust observability and metrics. ByteBridge emphasizes “logging at every
layer” and correlating logs with unique request or trace IDs. In practice,
instrument each component (AI client, gateway, each MCP server) to log
every tool invocation: include timestamps, tool name, parameters (redacting
secrets), session or user IDs, and results or errors. Push these logs to a
centralized aggregator (ELK, Splunk, or cloud logging). Use structured
logging (JSON lines) so that logs from different services can be easily joined.
Expose Prometheus-style metrics for key KPIs: request counts per tool,
latency percentiles, error rates, active sessions, SSE connection counts, etc.
For instance, monitor “tools_called” counters, “tool_latency_seconds”
histograms, and track token usage per session. Health-check endpoints
should return OK when the server is ready. Use distributed tracing
(OpenTelemetry) if possible to visualize end-to-end flows from the user
query through the LLM to tool calls. This instrumentation helps quickly
pinpoint failures (authentication error vs. network vs. code bug).
Testing and debugging tools are important. One can build an “MCP
Inspector” CLI (or use existing ones) to simulate client behavior, test
registrations, and validate auth flows. In pre-production, enable verbose
logging of prompts, tool calls, and intermediate results (as long as data
privacy is controlled). For production, consider audit-logging every action
(which agent/tool/user did what) in an immutable store or SIEM for
compliance. In summary, treat MCP like any distributed service: set up
dashboards, alerts on error spikes, and end-to-end tracing, so that one can
see whether an issue was with the LLM’s request, the gateway, or a specific
tool service.
Security, Multi-tenancy, and Advanced Concepts
https://medium.com/ai-in-plain-english/implementing-mcp-with-streamable-http-transport-in-prod-23ca9c6731ca 10/16


---
*Page 11*


3/27/26, 4:10 PM Implementing MCP with Streamable HTTP Transport in prod | by DhanushKumar | Mar, 2026 | Artificial Intelligence in Plain English
Running AI agents on real data poses unique security challenges. Out-of-the-
box, early MCP implementations had minimal security (often no auth) and
relied on a single admin token. In production, strong authentication and
authorization are mandatory. Each client/agent should authenticate (e.g.
present a user or API JWT) on every call; do not use a single master key for
all users. Configure the gateway to validate tokens (OAuth 2.1 or similar) and
extract the user identity. Implement role-based access control (RBAC) such
that only authorized users or agents may invoke certain tools or data.
ByteBridge warns of the “confused deputy” problem when one token is
shared — the server cannot tell one end-user from another, so an attacker or
malicious agent could abuse elevated rights. Instead, issue scoped, short-
lived tokens per user or session, and have the gateway or servers check
permissions (for example, only the HR role can call /payroll/* tools).
Data context must also be isolated per user or session. If the MCP server is
multi-tenant (serving many users), design it so that each request includes a
tenant ID or user ID, and enforce filtering at the database/API level. For
instance, if using one “search_documents” tool for all users, add a user_id
field to queries or maintain separate databases per tenant. ByteBridge
advises that session data (conversation history, memory) should never mix
between users. For stateful tools that hold memory or caches, you may need
to run separate instances per user or partition memory by user ID. Test
thoroughly: ensure one user’s session cannot retrieve another’s data or crash
their context.
Credentials and secrets must never flow through the untrusted LLM client.
The base MCP spec (as of 2024) did not provide a way for servers to obtain
third-party OAuth tokens securely, leading to insecure workarounds. Recent
proposals (and implementations by vendors like Arcade) fix this via
elicitation. In essence, if a tool needs OAuth credentials (e.g. to call Gmail or
GitHub), the server returns an ElicitationRequired response with a special
URL mode. The client then opens a browser to that URL, letting the user
authenticate; the server receives the callback and obtains the token on the
server side. Because the flow uses a browser redirect, the LLM client never
sees the secret token — it only receives a confirmation after completion.
This “URL elicitation” pattern enforces clear trust boundaries and has
become part of the 2025 MCP spec. We recommend using the latest MCP
SDK and enabling the elicitation capability; for example, in Python one
can raise UrlElicitationRequiredError with parameters as shown in the SDK
example.
Encryption-in-transit is a must: run all MCP HTTP endpoints over TLS, even
internally. Validate the HTTP Origin header on SSE connections to avoid
CSRF. On a local client (e.g. desktop app) you should still use localhost
binding rather than wildcard. For secret management, do not hardcode API
https://medium.com/ai-in-plain-english/implementing-mcp-with-streamable-http-transport-in-prod-23ca9c6731ca 11/16


---
*Page 12*


3/27/26, 4:10 PM Implementing MCP with Streamable HTTP Transport in prod | by DhanushKumar | Mar, 2026 | Artificial Intelligence in Plain English
keys in tool code. Instead, use a secrets vault (AWS Secrets Manager,
HashiCorp Vault, etc.) that the server accesses at runtime. Per-session short-
lived credentials (via OAuth refresh tokens) are safest. Implement per-tool
quotas and rate-limits in the gateway or server to prevent abuse; for
example, allow at most N calls per minute per user to heavy APIs. Set
sensible timeouts on each call so one misbehaving tool doesn’t hang the
client.
Another advanced consideration is context longevity. MCP sessions may
hold context or memory. ByteBridge notes that stuffing too much context
into LLM prompts is costly and risky. Instead of appending lengthy
document data into every message, use dedicated memory stores. For
example, an MCP memory server (such as an open-source “postg-mem”
backed by PostgreSQL) can retain conversation history or knowledge graphs.
The agent writes important facts to this store and reads them back by query,
rather than carrying them in prompt tokens. This externalizes long-term
memory and keeps prompt sizes small. Similarly, if the protocol’s streaming
transport (SSE) is not suitable for your environment, you might use stateless
HTTP calls with an external session database (e.g. Redis) to remember
conversation state between POSTs. Just ensure that any session store uses
strong encryption at rest, and that sessions are invalidated after timeout to
limit exposure.
Best Practices and Next Steps
In summary, a production MCP deployment involves solid software
engineering and DevOps discipline. Use modern ML tooling: containerize
each server, orchestrate with Kubernetes or serverless in a secure VPC, and
use automated CI/CD. Require TLS everywhere and authenticate all
connections. Leverage the MCP specification fully: implement session
headers, version negotiation, and capabilities so you can evolve without
breaking clients. Keep the MCP SDK up to date. Enforce a human-in-the-loop
for critical actions (the MCP spec even provides notifications/prompts that
clients should use to ask user confirmation for sensitive ops). Continuously
audit and test: for example, simulate a malicious agent trying to break out of
the context or access unauthorized tools.
For end-to-end validation, one can integrate the MCP setup with an agent
framework. For instance, an AI can be tasked to call these file tools and
verify the outputs. The MCP Python SDK even includes an “inspector” CLI
for testing servers. Monitoring should include not just infrastructure metrics
but also ML-specific telemetry: how many tool calls per query, how often the
model requests elicitation, etc. Finally, always be prepared to iterate: as real
users begin to rely on MCP-integrated AI features, gather feedback on
performance, cost, and accuracy.
https://medium.com/ai-in-plain-english/implementing-mcp-with-streamable-http-transport-in-prod-23ca9c6731ca 12/16


---
*Page 13*


3/27/26, 4:10 PM Implementing MCP with Streamable HTTP Transport in prod | by DhanushKumar | Mar, 2026 | Artificial Intelligence in Plain English
Implementing MCP in production unlocks powerful AI features (e.g. real-
time data lookup, automated actions), but it also demands robust
architecture. By following best practices in cloud deployments, applying
thorough observability and security measures, and using the growing
ecosystem of MCP tools and gateways, teams can build scalable, reliable AI-
enabled applications. The example code and patterns above show one path
from concept to production-ready MCP service. With this foundation, the
next steps are to add more tools (e.g. database, search, or API integration
servers), implement end-user authentication, and refine multi-agent
workflows — always validating each component under load and attack
models. This layered, infrastructure-as-code approach ensures your MCP
application can handle real-world complexity while keeping user data safe
and performance high.
A message from our Founder
Hey, Sunil here. I wanted to take a moment to thank you for reading until the
end and for being a part of this community. Did you know that our team run
these publications as a volunteer effort to over 3.5m monthly readers? We
don’t receive any funding, we do this to support the community.
If you want to show some love, please take a moment to follow me on
LinkedIn, TikTok, Instagram. You can also subscribe to our weekly
newsletter. And before you go, don’t forget to clap and follow the writer!
Mcp Server Mcp Protocol Model Context Protocol Anthropic Claude Agents
Published in Artificial Intelligence in Plain English
Follow
41K followers · Last published 3 hours ago
New AI, ML and Data Science articles every day. Follow to join our 3.5M+ monthly
readers.
Written by DhanushKumar
Follow
1.1K followers · 69 following
A guy who is curious to learn and blog ... Data Science @Deloitte AI | Data
Science | Azure AI
Responses (1)
https://medium.com/ai-in-plain-english/implementing-mcp-with-streamable-http-transport-in-prod-23ca9c6731ca 13/16


---
*Page 14*


3/27/26, 4:10 PM Implementing MCP with Streamable HTTP Transport in prod | by DhanushKumar | Mar, 2026 | Artificial Intelligence in Plain English
Rae Steele
What are your thoughts?
Sowbaranic Rajhe/him
4 days ago
Amazing Content 👏
Please do read my blogs and follow my page for amazing content on geopolitics and tech corporate news.
Reply
More from the list: "System design overview "
Curated byM Redinger
Open in app
In.Net Pr…bySukhpin… syarif Tom Smykowski InLevel Up C
LSINeaQrc Ghot a Brain Idiomatic Go Design 🤖 Agentic Engineering Write My Advanced
Transplant in .NET 10 — … Patterns Every Backend… Workflow: I Built a Code-… Workflow
· Sep 18, 2025 · Mar 5 · Mar 15 · Mar 7
View list
More from DhanushKumar and Artificial Intelligence in Plain
English
DhanushKumar InArtificial Intelligence in Plain En… byFaisal haq…
RAG with LLaMA Using Ollama: A Why Claude Opus 4.6 Changes
Deep Dive into Retrieval-… Everything: The Dawn of “Vibe…
The landscape of AI is evolving rapidly, and Anthropic’s most intelligent model yet isn’t
Retrieval-Augmented Generation (RAG)… just an upgrade — it’s a fundamental shift in…
Nov 30, 2024 128 5 Feb 6 691 17
https://medium.com/ai-in-plain-english/implementing-mcp-with-streamable-http-transport-in-prod-23ca9c6731ca 14/16


---
*Page 15*


3/27/26, 4:10 PM Implementing MCP with Streamable HTTP Transport in prod | by DhanushKumar | Mar, 2026 | Artificial Intelligence in Plain English
InArtificial Intelligence in Plain En…byPump Para… InStackademicbyDhanushKumar
I Handed milo My Portfolio 38 Days Azure AI Foundry — Multi-Agent
Ago. I Haven’t Touched It Since. Orchestration and Workflows
Here’s what happens when you stop trading Azure AI Foundry (formerly Azure AI Studio) is
and just let the AI run. Microsoft’s end-to-end platform for building,…
Feb 23 196 5 Mar 16 13 2
See all from DhanushKumar See all from Artificial Intelligence in Plain English
Recommended from Medium
InTowards AIbyDivy Yadav A B Vijay Kumar
LLM Observability: The Missing Building Deep Agents
Layer in Most Production AI…
In this blog, I will share my experience
For developers who shipped an LLM building Autonomous, Memory-Rich, Multi-…
application and want to understand what is…
Mar 14 135 2 Mar 14 64 1
Pankaj Najeeb Khan
Context Management for AI Agents
https://medium.com/ai-in-plain-english/implementing-mcp-with-streamable-http-transport-in-prod-23ca9c6731ca 15/16


---
*Page 16*


3/27/26, 4:10 PM Implementing MCP with Streamable HTTP Transport in prod | by DhanushKumar | Mar, 2026 | Artificial Intelligence in Plain English
When Too Many Tools Become Too
When you typically use an LLM, you exchange
Much Context: A Deep Dive into… a few messages back and forth, get your…
Your agent has access to twelve MCP servers,
eighty callable tools and it just picked the… Oct 19, 2025 2
Mar 15 106
Abhirup Pal InFuture Of QAbyEkin Gün Öncü
🚀 Databricks AI Dev Kit in Claude Your MCP Sucks. Here’s How to Fix
Code (Desktop + CLI + VS Code) … It.
I’ve been using the Databricks AI Dev Kit with I wrote a piece last week arguing that MCP
Claude Code daily, and the setup tripped me… isn’t dead, people are just using it wrong.
Mar 15 23 1 6d ago 104
See more recommendations
https://medium.com/ai-in-plain-english/implementing-mcp-with-streamable-http-transport-in-prod-23ca9c6731ca 16/16