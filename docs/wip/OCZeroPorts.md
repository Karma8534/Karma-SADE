# OCZeroPorts

*Converted from: OCZeroPorts.PDF*



---
*Page 1*


Open in app
Search Write
Member-only story
I Deployed OpenClaw
With Zero Public Ports.
Here is the Tailscale
Setup That Actually
Works
60-Minute DIY Guide: Secure OpenClaw
Production Setup on Hetzner Cloud + Docker
+ Tailsclae
Reza Rezvani Following 9 min read · Feb 6, 2026
119 3
The email from Maor Dayan’s security scan arrived
on a Thursday: 42,665 OpenClaw instances


---
*Page 2*


exposed to the public internet. 93.4% had
authentication bypasses. Eight were completely
open — no password, no token, full shell access.
Secured Deployment of OpenClaw AI Assistant on Hetzner Cloud VPS |
Image By Gemini 3 Pro ©
I’d deployed my OpenClaw instance three days
earlier. I wasn’t in that list, but only because I’d
taken a different approach: zero public ports,
Tailscale-only access, every connection through an
encrypted mesh network. No one from the
internet could reach my gateway. Not because I’d


---
*Page 3*


configured a firewall rule correctly — because
there was nothing to reach.
Note: AI tools assisted with structuring this guide. The
deployment architecture, security configurations, and
troubleshooting steps come from my production
OpenClaw instance running on Hetzner Cloud.
This guide documents that setup. Not the
theoretical “best practices” version — the one I am
actually running in production on a Hetzner VPS,
controlling via Telegram from my phone, and
using daily with Claude Code.
What You’re Building
By the end of this guide (~60 minutes), you’ll have:
OpenClaw running on Hetzner Cloud
(€5.29/month for CX22: 2 vCPU, 4GB RAM)
Zero public attack surface — accessible only
through Tailscale mesh network


---
*Page 4*


Telegram integration for mobile control from
anywhere
Production security: SSH keys only, UFW
firewall, secrets isolation, auto-updates
Working configuration for Claude Code
integration
Prerequisites:
Basic terminal comfort (you will paste commands,
but I will explain what they do)
Credit card for Hetzner (~€5/month) and
Anthropic API (~$10–30/month for light use)
60 minutes of focused time
The Architecture: Why Tailscale Changes
Everything
Most OpenClaw guides expose port 18789 to the
internet, then add authentication as a band-aid.
That’s backwards. Better approach: make the
service unreachable, then selectively grant access.


---
*Page 5*


Zero Trust Architecture Using Tailscale | Image by Gemini 3 Pro /
Concept by Alireza Rezvani ©
Traditional deployment:
Internet → Firewall → Port 18789 → OpenClaw Gateway
↑


---
*Page 6*


Authentication happens here (if configured)
42,665 exposed instances suggest this fails often
Tailscale deployment:
Internet → [nothing exposed]
Tailscale mesh network:
Your phone/laptop ←→ VPS running OpenClaw
↑
Zero-trust network, WireGuard encrypted
No public ports, no firewall rules to misconfigur
Cost breakdown:
Hetzner CX22: €5.29/month (2 vCPU, 4GB RAM,
40GB SSD)
Tailscale: Free for personal use (up to 100
devices)
Anthropic API: ~$10–30/month for light use (~50
messages/day)


---
*Page 7*


Total: ~€15–20/month for production-grade
setup
Compare to DigitalOcean’s recommended
$24/month droplet or buying a $600 Mac Mini.
Step 1: Provision Hetzner VPS (10
minutes)
Create a Hetzner Cloud account at hetzner.com.
You’ll need to verify identity (EU regulations).
1.1: Generate SSH Key (If You Don’t Have
One)
On your local machine:
# Generate SSH key pair
ssh-keygen -t ed25519 -C "xyz-hetzner"
# When prompted for file location, accept default (~/
# Set a passphrase (optional but recommended)
# Display public key (you'll need this next)
cat ~/.ssh/id_ed25519.pub


---
*Page 8*


Copy the entire output (starts with ssh-ed25519).
1.2: Create the Server
In Hetzner Cloud Console:
1. Create Project → Name it “OpenClaw” or similar
2. Add Server →
Location: Falkenstein (FSN1) or Nuremberg
(NBG1) for EU, Ashburn (ASH) for US
Image: Ubuntu 24.04 LTS
Type: CX22 (2 vCPU, 4GB RAM) — €5.29/month
Networking: IPv4 only (IPv6 optional)
SSH Keys: Paste your public key from step 1.1
Backups: Optional (adds €1/month, recommended
for production)
3. Create & Buy Now
Wait 30–60 seconds for provisioning. Note the IPv4
address shown in the server list.


---
*Page 9*


1.3: Initial Connection
# Replace with your server's IP address
ssh root@YOUR_SERVER_IP
# First connection will ask to verify fingerprint
# Type 'yes' and press Enter
You’re now root on your VPS. Everything from here
runs on the server.
Step 2: Install Tailscale (5 minutes)
Tailscale creates a private mesh network. Your VPS
will get a stable internal IP (100.x.x.x) accessible
only by devices you authorize.
# Add Tailscale's package repository
curl -fsSL https://tailscale.com/install.sh | sh
# Authenticate this machine to your Tailscale network
# This will print a URL - open it in your browser to
tailscale up
# Verify connection
tailscale status
# You should see your VPS listed with a 100.x.x.x IP


---
*Page 10*


Important: Copy the Tailscale IP (100.x.x.x
format). You’ll use this to access OpenClaw.
2.1: Install Tailscale on Your Local Machine
On your laptop/desktop:
macOS: brew install tailscale then sudo
tailscale up
Linux: Same script as server: curl -fsSL
https://tailscale.com/install.sh | sh
Windows: Download from
tailscale.com/download
Mobile: Install Tailscale app from App Store /
Play Store
After installing, run tailscale up and authenticate.
All your devices now share a private network.
Step 3: Install Docker (5 minutes)
OpenClaw runs in Docker for isolation and easier
updates.


---
*Page 11*


# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
# Verify installation
docker --version
# Should show: Docker version 25.x.x or similar
# Install Docker Compose
apt install docker-compose-plugin
# Verify
docker compose version
# Should show: Docker Compose version v2.x.x
Step 4: Install OpenClaw (15 minutes)
4.1: Clone Repository and Create
Directories
# Clone OpenClaw repository
git clone https://github.com/openclaw/openclaw.git
cd openclaw
# Create persistent data directories
# These survive container restarts
mkdir -p /root/.openclaw
mkdir -p /root/.openclaw/workspace


---
*Page 12*


# Set ownership to container user (UID 1000)
chown -R 1000:1000 /root/.openclaw
4.2: Configure Environment Variables
Create .env file with secrets:
# Generate secure gateway token
GATEWAY_TOKEN=$(openssl rand -hex 32)
# Create .env file
cat > .env << EOF
# OpenClaw Configuration
OPENCLAW_CONFIG_DIR=/root/.openclaw
OPENCLAW_WORKSPACE_DIR=/root/.openclaw/workspace
OPENCLAW_GATEWAY_BIND=loopback
OPENCLAW_GATEWAY_PORT=18789
OPENCLAW_GATEWAY_TOKEN=${GATEWAY_TOKEN}
# Anthropic API (get from console.anthropic.com)
ANTHROPIC_API_KEY=your_api_key_here
# Optional: Google services password (for Gmail/Calen
GOG_KEYRING_PASSWORD=
# Container environment
XDG_CONFIG_HOME=/home/node/.config
NODE_ENV=production
EOF
# Secure the file
chmod 600 .env
# Display your gateway token (save this!)
echo "Your gateway token: ${GATEWAY_TOKEN}"


---
*Page 13*


CRITICAL: Replace your_api_key_here with your
actual Anthropic API key from
console.anthropic.com.
4.3: Create Docker Compose
Configuration
cat > docker-compose.yml << 'EOF'
services:
openclaw-gateway:
build: .
restart: unless-stopped
env_file:
- .env
environment:
- HOME=/home/node
- NODE_ENV=production
- TERM=xterm-256color
volumes:
- ${OPENCLAW_CONFIG_DIR}:/home/node/.openclaw
- ${OPENCLAW_WORKSPACE_DIR}:/home/node/.opencla
ports:
# Bind ONLY to localhost - Tailscale Serve will
- "127.0.0.1:${OPENCLAW_GATEWAY_PORT}:18789"
command: >
sh -c "pnpm install --frozen-lockfile &&
pnpm build &&
node dist/index.js gateway
--bind ${OPENCLAW_GATEWAY_BIND}


---
*Page 14*


--port ${OPENCLAW_GATEWAY_PORT}"
EOF
4.4: Build and Launch
# Build the container (first time: 5-10 minutes)
docker compose build
# Start OpenClaw
docker compose up -d
# Verify it's running
docker compose ps
# Should show: openclaw-gateway ... Up
# Check logs
docker compose logs -f openclaw-gateway
# Press Ctrl+C to exit logs when you see "Gateway lis
Step 5: Configure Tailscale Serve (5
minutes)
Tailscale Serve exposes localhost:18789 through
your Tailscale network with HTTPS and automatic
certificates.


---
*Page 15*


# Expose OpenClaw through Tailscale
tailscale serve https / http://127.0.0.1:18789
# Verify configuration
tailscale serve status
# Should show: https://<your-machine>.ts.net => http:
Access your OpenClaw dashboard:
From any device on your Tailscale network, open:
https://<your-vps-name>.ts.net/?token=<YOUR_GATEWAY_T
Replace <your-vps-name> with your VPS hostname
(shown in tailscale serve status) and
<YOUR_GATEWAY_TOKEN> with the token from step 4.2.
Step 6: Configure Telegram Integration
(10 minutes)
Control OpenClaw from your phone via Telegram.
6.1: Create Telegram Bot


---
*Page 16*


1. Open Telegram and message @BotFather
2. Send /newbot
3. Choose a name (e.g., “My OpenClaw Assistant”)
4. Choose a username (must end in bot, e.g.,
myopenclaw_bot)
5. Copy the token BotFather gives you (format:
123456:ABC-DEF...)
6.2: Connect OpenClaw to Telegram
In OpenClaw dashboard (opened in step 5):
1. Go to Settings → Channels
2. Click Add Channel → Select Telegram
3. Paste your bot token
4. Click Save
5. The page will show a pairing code
6.3: Pair Your Telegram Account
1. Open Telegram and message your bot (the
username you chose)


---
*Page 17*


2. Send /start
3. Send the pairing code shown in dashboard
4. Bot replies: “Device paired successfully”
Security: Add your Telegram user ID to the
allowlist:
In dashboard → Settings → Channels → Telegram →
Allowlist → Add your user ID (shown when you
message the bot).
Now you can message your bot from anywhere:
“Check my calendar”, “Summarize my inbox”, etc.
Step 7: Security Hardening (10 minutes)
7.1: Configure UFW Firewall
# Default deny incoming
ufw default deny incoming
ufw default allow outgoing
# Allow SSH (port 22)
ufw allow 22/tcp


---
*Page 18*


# Allow Tailscale (port 41641 UDP)
ufw allow 41641/udp
# Enable firewall
ufw enable
# Verify status
ufw status verbose
Important: Port 18789 (OpenClaw gateway) should
NOT appear in ufw status. It's only accessible via
Tailscale.
7.2: Install Fail2Ban (Brute Force
Protection)
# Install fail2ban
apt install fail2ban -y
# Create local configuration
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 1h
findtime = 10m
maxretry = 5
[sshd]
enabled = true
port = 22


---
*Page 19*


logpath = %(sshd_log)s
backend = systemd
EOF
# Start and enable
systemctl enable fail2ban
systemctl start fail2ban
# Verify
fail2ban-client status sshd
7.3: Enable Automatic Security Updates
# Install unattended-upgrades
apt install unattended-upgrades -y
# Configure
cat > /etc/apt/apt.conf.d/50unattended-upgrades << 'E
Unattended-Upgrade::Allowed-Origins {
"${distro_id}:${distro_codename}-security";
};
Unattended-Upgrade::Automatic-Reboot "false";
Unattended-Upgrade::Mail "root";
EOF
# Enable automatic updates
dpkg-reconfigure -plow unattended-upgrades
What Works (and What Doesn’t Yet)


---
*Page 20*


Production-Ready Features
After three weeks running this setup, here’s what
works reliably:
Telegram integration: Message from anywhere,
responses feel instant. The mobile control is
genuinely useful — I have debugged production
issues from coffee shops.
Claude Code workflows: Point OpenClaw at a
GitHub repo, ask it to analyze code or generate
documentation. The Tailscale network means
Claude Code on my laptop and OpenClaw on the
VPS share context seamlessly.
24/7 availability: Set up heartbeat checks,
scheduled tasks, monitoring. The VPS doesn’t
sleep. I have run multi-hour research tasks that
would timeout on my laptop.
Cost efficiency: €5.29/month beats buying
hardware, and Hetzner’s bandwidth is generous
(20TB/month included).


---
*Page 21*


Current Limitations (Honest Assessment)
The OpenClaw team has done remarkable work,
but some rough edges remain. These aren’t
dealbreakers — just things to know:
Session management issues: GitHub issue #2624
documents random session resets where
OpenClaw “forgets” previous context. I’ve seen this
3–4 times in production. Workaround: explicit
memory writes (write this to memory/notes.md)
before long tasks.
Memory plugin unavailability: Running openclaw
status shows Memory: enabled (plugin memory-core)
· unavailable. The memory search feature exists
but doesn't initialize consistently. The team is
aware; expect fixes in upcoming releases.
Opus 4.6 compatibility: As of OpenClaw 2026.1.30,
Claude Opus 4.5 works fine but Opus 4.6 isn’t fully
supported yet. If you’re on Opus 4.6, you’ll see


---
*Page 22*


“model not found” errors. Stick with Sonnet 4.5 or
Opus 4.5 until the next release.
Token limit errors with embeddings: If using
memory search with OpenAI embeddings, chunks
occasionally exceed the 8192-token limit (GitHub
issue #5696). Workaround: switch to Anthropic
embeddings or disable session memory indexing.
These issues don’t stop daily use, but they’re worth
knowing about. The OpenClaw project moves fast
— by the time you read this, several may be
resolved.
Troubleshooting Guide
Gateway Won’t Start
# Check logs
docker compose logs openclaw-gateway
# Common issues:
# 1. Missing API key
cat .env | grep ANTHROPIC_API_KEY


---
*Page 23*


# 2. Port conflict (something else on 18789)
sudo lsof -i :18789
# 3. Build failure
docker compose build --no-cache
docker compose up -d
Can’t Access Dashboard via Tailscale
# Verify Tailscale is running
tailscale status
# Verify Serve configuration
tailscale serve status
# Should show https://<machine>.ts.net => http://127.
# Test localhost connection from VPS
curl -I http://127.0.0.1:18789
# Should return HTTP 200 (ignoring 401 auth error)
# Regenerate Serve config
tailscale serve reset
tailscale serve https / http://127.0.0.1:18789
Telegram Bot Not Responding
# Check channel status in dashboard
# Settings → Channels → Telegram → Status should sh


---
*Page 24*


# Verify bot token
# Send /start to your bot in Telegram
# If no response, token is invalid - create new bot w
# Check OpenClaw logs
docker compose logs -f openclaw-gateway | grep telegr
Memory/Session Reset Issues
# Check session status
docker compose exec openclaw-gateway openclaw status
# Force memory flush
docker compose exec openclaw-gateway openclaw session
# Manual session restart (last resort)
docker compose restart openclaw-gateway
Production Checklist
Before considering this “production-ready”:
[ ] Run security audit: openclaw doctor --deep
[ ] Verify firewall: ufw status shows only SSH +
Tailscale


---
*Page 25*


[ ] Test recovery: docker compose restart
succeeds
[ ] Backup secrets: Copy .env to secure location
(1Password, encrypted drive)
[ ] Document Tailscale IP: Save tailscale status
output
[ ] Test remote access: Access dashboard from
phone/laptop via Tailscale
[ ] Configure backups: Hetzner snapshots
(€1/month) or rsync to external storage
[ ] Monitor logs: docker compose logs -f shows
no repeated errors
[ ] Test Telegram: Send “what’s my IP” or simple
query, verify response
What You’ve Actually Built
You’re running a production-grade AI assistant
with:


---
*Page 26*


Zero public attack surface: No ports exposed to
the internet
Mobile control: Telegram from anywhere with
cell signal
End-to-end encryption: WireGuard (Tailscale) +
HTTPS
Cost-effective: ~€20/month total (VPS + API)
Scalable: Upgrade to CX32 (8GB RAM) when
needed
This is not the quickest setup — DigitalOcean’s 1-
click is faster. But it is the setup I trust enough to
use every day. The one that survives the “would I
recommend this to a client” test.
OpenClaw is evolving rapidly. Expect rough edges.
Expect breaking changes. Also expect the most
interesting AI assistant project happening right
now. Peter Steinberger and the team are shipping
fast, and the community is building 1,700+ skills.


---
*Page 27*


Just ship it with your eyes open.
What’s your production deployment strategy?
Running locally, cloud VPS, or waiting for hosted
offerings? Drop your setup in the comments — I’m
curious what patterns are emerging.
Openclaw AI Agent Ai Assistant Openclaw Security
Openclaw Setup
Written by Reza Rezvani
Following
4.4K followers · 76 following
As CTO of a Berlin AI MedTech startup, I tackle
daily challenges in healthcare tech. With 2
decades in tech, I drive innovations in human
motion analysis.
Responses (3)


---
*Page 28*


To respond to this story,
get the free Medium app.
Raul Casari
Feb 9
Hi! Thanks for the guide, it's really helpful. I have a technical question: in
your docker-compose.yml, the command block runs pnpm install and
pnpm build again at runtime. Since the Dockerfile already performs these
steps during the image build… more
3
Jay Klein
Feb 6
This is priceless. Most of the articles out there are either saying (or
believing) “there is no security problem with openclaw” while others say
“avoid at all cost due to security problems”. Only a few like this article
actually tells you what/why/how to fix. Thanks!
3 1 reply
Kelemen Balázs
Feb 8
Huge thanks! I needed to add CI=true to the docker-compose.yaml for
docker to start running


---
*Page 29*


More from Reza Rezvani
Reza Rezvani Reza Rezvani
141 Claude Code Claude Sonnet 4.6: I
A t Th S t Th T t d It A i t O
After 6 months building I Tested Claude Sonnet 4.6
t i d ti h ’ A i t O 4 6 All N
Jan 25 Feb 20
Reza Rezvani Reza Rezvani
These 4 Claude Code OpenClaw / Moltbot
F t S M t IDENTITY d H I
Hot reload, hooks frontmatter, SOUL.md defines who your AI
ild d i i d i IDENTITY d d fi h
Jan 12 Jan 30


---
*Page 30*


See all from Reza Rezvani
Recommended from Medium
Gustavo Garcia Phil | Rentier Digital Automation
OpenClaw and Voice AI Spotify Built “Honk” to
R l C di I B il
So, OpenClaw (previously
Last week, Spotify’s co-CEO
Cl db t M ltb t) i
t ld W ll St t th t hi b t
Feb 6 Feb 20
In by In by
AWS in Plain English Vivek V Coding Nexus Minervee


---
*Page 31*


I’ve Been a Costco Ok OpenClaw But I’m
M b f 25 Y Sidi With Th
The whole thing runs OpenClaw TypeScript to Go
l f d d ll R f t Th t Sl h d
Feb 13 Feb 18
Milvus In by
CodeX MayhemCode
Step-by-Step Guide to
OpenAI Acquires
S tti U O Cl
O Cl H
Peter Steinberger spent a
k d b ildi thi
Feb 3 Feb 18
See more recommendations