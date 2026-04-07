# GitHub - miantiao-me_cloud-claw_ Run OpenClaw with One Click on Cloudflare Containers to Create Your Personal Agent

*Converted from: GitHub - miantiao-me_cloud-claw_ Run OpenClaw with One Click on Cloudflare Containers to Create Your Personal Agent.PDF*



---
*Page 1*


miantiao-me/cloud-claw
Public
Run OpenClaw with One Click on Cloudflare Containers to Create Your Personal Agent
MIT license
158 stars 24 forks Branches Tags Activity
Star Notifications
Code Issues 1
… 1Branch 0Tags Go to file Go to file Code
miantiao-me feat: enhance WebSocket handling and session management in proxyCdp
e4880d1 · 3 days ago
.vscode chore: init 2 weeks ago
src feat: enhance WebSocket handling … 3 days ago
.dockerignore chore: init 2 weeks ago
.editorconfig chore: init 2 weeks ago
.env.example feat: add Cloudflare Browser CDP … last week
.gitignore chore: init 2 weeks ago
.oxfmtrc.json chore: init 2 weeks ago
AGENTS.md feat: add Cloudflare Browser CDP … last week
Dockerfile feat: add Cloudflare Browser CDP … last week
LICENSE chore: add MIT License 3 days ago
README.md chore: add postinstall lint hook last week
README.zh-CN.md feat: add Cloudflare Browser CDP … last week
package.json chore: add postinstall lint hook last week
pnpm-lock.yaml feat: add Cloudflare Browser CDP … last week
pnpm-workspace.yaml chore: init 2 weeks ago
tsconfig.json chore: init 2 weeks ago
worker-configuration.d.ts feat: add Cloudflare Browser CDP … last week


---
*Page 2*


wrangler.jsonc feat: add Cloudflare Browser CDP … last week
README MIT license
Cloud Claw (Cloudflare + OpenClaw)
Cloud Claw is a containerized AI assistant that runs OpenClaw on Cloudflare Workers + Containers.
A Worker handles routing and auth, forwards requests to a singleton container running an OpenClaw
gateway instance, and proxies Chrome DevTools Protocol (CDP) sessions via Cloudflare Browser Rendering.
English | 简体中⽂
Tech Stack
Runtime: Cloudflare Workers + Containers
Language: TypeScript (ES2024)
Package Manager: pnpm
Container Specs: 1 vCPU, 4GB RAM, 8GB disk
Browser: Cloudflare Browser Rendering (remote CDP)
Core Libraries:
: Workers standard library
cloudflare:workers
: Container management
@cloudflare/containers
Container Base:
nikolaik/python-nodejs:python3.12-nodejs22-bookworm
Storage: TigrisFS for S3/R2 mounting
Quick Start
Prerequisites
Node.js (v22+)
pnpm (v10.28.2+)
Wrangler CLI ( )
npm i -g wrangler
Install Dependencies
pnpm install


---
*Page 3*


Local Development
Start the local development server:
pnpm dev
Linting
Run formatter (oxfmt) and linter (oxlint):
pnpm lint
Generate Type Definitions
If you modify bindings in , regenerate the type file:
wrangler.jsonc
pnpm cf-typegen
Deployment
Deploy code to Cloudflare's global network:
pnpm deploy
Project Structure
.
├── src/
│ ├── index.ts # Workers entry point, routing, basic auth
│ ├── container.ts # AgentContainer class (extends Container), WebSocket
gateway
│ └── cdp.ts # Chrome DevTools Protocol proxy (chunked binary WebSocket
framing)
├── Dockerfile # Container image: OpenClaw gateway + TigrisFS S3 mount
├── worker-configuration.d.ts # Auto-generated Cloudflare binding types (DO NOT
EDIT)
├── wrangler.jsonc # Wrangler configuration (containers, bindings, placement)
├── tsconfig.json # TypeScript configuration
└── package.json
Data Persistence (S3/R2)
The container has built-in support for S3-compatible storage (such as Cloudflare R2, AWS S3). It uses
to mount object storage as a local filesystem for persistent data storage.
TigrisFS


---
*Page 4*


Environment Variables
To enable data persistence, configure the following environment variables in the container runtime
environment:
Variable Description Required Default
S3 API endpoint address Yes -
S3_ENDPOINT
Bucket name Yes -
S3_BUCKET
Access Key ID Yes -
S3_ACCESS_KEY_ID
Access Key Secret Yes -
S3_SECRET_ACCESS_KEY
Storage region No
S3_REGION auto
Whether to use Path Style access No
S3_PATH_STYLE false
Path prefix within the bucket (subdirectory) No (root)
S3_PREFIX
Additional mount arguments for TigrisFS No -
TIGRISFS_ARGS
Gateway access token (for Web UI authentication) Yes -
OPENCLAW_GATEWAY_TOKEN
Worker's public URL (for CDP proxy config) Yes -
WORKER_URL
How It Works
1. Mount Point: On container startup, the S3 bucket is mounted to .
/data
2. Workspace: The actual workspace is located at .
/data/workspace
3. OpenClaw Config: OpenClaw configuration files are stored in to ensure state
/data/.openclaw
persistence.
4. Initialization:
If the S3 bucket (or specified prefix path) is empty, the container automatically initializes the preset
directory structure.
If S3 configuration is missing, the container falls back to non-persistent local directory mode.
Web UI Initialization
After the first startup, OpenClaw needs to be initialized via the Web UI. Visit the deployed URL (e.g.,
) and follow the on-screen instructions to complete setup.
https://your-worker.workers.dev
Browser Rendering (CDP Proxy)
Cloud Claw integrates Cloudflare Browser Rendering to provide headless browser capabilities to the AI
assistant via the Chrome DevTools Protocol (CDP).
How It Works


---
*Page 5*


1. OpenClaw connects to the Worker's CDP proxy endpoint ( ) using
/cloudflare.browser/{token}
WebSocket.
2. The Worker acquires a browser session from Cloudflare's Browser Rendering API and proxies CDP
messages between OpenClaw and the remote browser.
3. Binary framing: CDP messages are chunked with a 4-byte length header to handle large payloads over
Cloudflare's WebSocket infrastructure.
Configuration
The CDP proxy is automatically configured when and are set. The
WORKER_URL OPENCLAW_GATEWAY_TOKEN
OpenClaw container generates a browser profile pointing to:
{WORKER_URL}/cloudflare.browser/{OPENCLAW_GATEWAY_TOKEN}
Authentication is handled via the token in the URL path — no additional setup required.
Container Lifecycle
By default, the container automatically sleeps after 10 minutes of inactivity to save resources. You can
customize this behavior:
Keep Container Always Running
To prevent the container from sleeping, modify :
src/container.ts
export class AgentContainer extends Container {
sleepAfter = 'never' // Never sleep (default: '10m')
// ...
}
Activity-Based Keep-Alive (Default)
The current implementation uses smart keep-alive: the container stays active during AI conversations and
sleeps during idle periods. This is achieved by calling when chat events are
renewActivityTimeout()
received:
// In watchContainer() - resets the sleep timer on each chat completion
if (frame.event === 'chat' && frame.payload?.state === 'final') {
this.renewActivityTimeout()
}
Available Options
Value Behavior
sleepAfter
Container runs indefinitely
'never'


---
*Page 6*


Value Behavior
sleepAfter
Sleep after 10 minutes of inactivity (default)
'10m'
Sleep after 1 hour of inactivity
'1h'
Sleep after 30 seconds of inactivity
'30s'
Note: When sleeping, the container state is preserved. It will automatically wake up on the next request,
but cold start may take a few seconds.
Development Guidelines
Fordetaileddevelopmentguidelines codestyle andAIagentbehaviorstandards pleasereferto
Releases
No releases published
Packages
No packages published
Languages
TypeScript71.2% Dockerfile28.8%