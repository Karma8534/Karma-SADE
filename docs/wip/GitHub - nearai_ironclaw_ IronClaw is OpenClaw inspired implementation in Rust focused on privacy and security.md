# GitHub - nearai_ironclaw_ IronClaw is OpenClaw inspired implementation in Rust focused on privacy and security

*Converted from: GitHub - nearai_ironclaw_ IronClaw is OpenClaw inspired implementation in Rust focused on privacy and security.PDF*



---
*Page 1*


nearai/ironclaw
Public
IronClaw is OpenClaw inspired implementation in Rust focused on privacy and security
Apache-2.0, MIT licenses found
150 stars 13 forks Branches Tags Activity
Star Notifications
Code Issues 1
4Branches 0Tags Go to file Go to file Code
elliotBraem Fixes build, adds missing sse event and correct command (#11)
202665a · 4 hours ago
.claude/commands feat: Add Google Suite & Telegra… yesterday
channels-src Fixes build, adds missing sse ev… 4 hours ago
docker Docker file for sandbox 5 days ago
docs Rebrand to IronClaw with securi… 5 days ago
migrations Add heartbeat integration, plann… last week
src Fixes build, adds missing sse ev… 4 hours ago
tests Add WebSocket gateway and co… yesterday
tools-src feat: Add Google Suite & Telegra… yesterday
wit Add Telegram typing indicator vi… 4 days ago
.env.example Fixes build, adds missing sse ev… 4 hours ago
.gitignore Initial implementation of the ag… last week
AGENTS.md Codex/feature parity pr hook (#6) yesterday
CLAUDE.md feat: Add Google Suite & Telegra… yesterday
CONTRIBUTING.md Codex/feature parity pr hook (#6) yesterday
Cargo.lock Add WebSocket gateway and co… yesterday
Cargo.toml Add WebSocket gateway and co… yesterday


---
*Page 2*


FEATURE_PARITY.md Rebrand to IronClaw with securi… 5 days ago
LICENSE-APACHE Split LICENSE into LICENSE-MIT… 4 days ago
LICENSE-MIT Split LICENSE into LICENSE-MIT… 4 days ago
README.md Fixes build, adds missing sse ev… 4 hours ago
ironclaw.png Add README with IronClaw bra… last week
README More
IronClaw
Your secure personal AI assistant, always on your side
Philosophy • Features • Installation • Configuration • Security • Architecture
Philosophy
IronClaw is built on a simple principle: your AI assistant should work for you, not against you.
In a world where AI systems are increasingly opaque about data handling and aligned with corporate
interests, IronClaw takes a different approach:
Your data stays yours - All information is stored locally, encrypted, and never leaves your control
Transparency by design - Open source, auditable, no hidden telemetry or data harvesting
Self-expanding capabilities - Build new tools on the fly without waiting for vendor updates
Defense in depth - Multiple security layers protect against prompt injection and data exfiltration
IronClaw is the AI assistant you can actually trust with your personal and professional life.


---
*Page 3*


Features
Security First
WASM Sandbox - Untrusted tools run in isolated WebAssembly containers with capability-based
permissions
Credential Protection - Secrets are never exposed to tools; injected at the host boundary with
leak detection
Prompt Injection Defense - Pattern detection, content sanitization, and policy enforcement
Endpoint Allowlisting - HTTP requests only to explicitly approved hosts and paths
Always Available
Multi-channel - REPL, HTTP webhooks, and extensible WASM channels (Telegram, Slack, and
more)
Heartbeat System - Proactive background execution for monitoring and maintenance tasks
Parallel Jobs - Handle multiple requests concurrently with isolated contexts
Self-repair - Automatic detection and recovery of stuck operations
Self-Expanding
Dynamic Tool Building - Describe what you need, and IronClaw builds it as a WASM tool
MCP Protocol - Connect to Model Context Protocol servers for additional capabilities
Plugin Architecture - Drop in new WASM tools and channels without restarting
Persistent Memory
Hybrid Search - Full-text + vector search using Reciprocal Rank Fusion
Workspace Filesystem - Flexible path-based storage for notes, logs, and context
Identity Files - Maintain consistent personality and preferences across sessions
Installation
Prerequisites
Rust 1.85+
PostgreSQL 15+ with pgvector extension
NEAR AI account (authentication handled via setup wizard)
Build


---
*Page 4*


# Clone the repository
git clone https://github.com/nearai/ironclaw.git
cd ironclaw
# Build
cargo build --release
# Run tests
cargo test
Database Setup
# Create database
createdb ironclaw
# Enable pgvector
psql ironclaw -c "CREATE EXTENSION IF NOT EXISTS vector;"
Configuration
Run the setup wizard to configure IronClaw:
ironclaw onboard
The wizard handles database connection, NEAR AI authentication (via browser OAuth), and secrets
encryption (using your system keychain). All settings are saved to .
~/.ironclaw/settings.toml
Security
IronClaw implements defense in depth to protect your data and prevent misuse.
WASM Sandbox
All untrusted tools run in isolated WebAssembly containers:
Capability-based permissions - Explicit opt-in for HTTP, secrets, tool invocation
Endpoint allowlisting - HTTP requests only to approved hosts/paths
Credential injection - Secrets injected at host boundary, never exposed to WASM code
Leak detection - Scans requests and responses for secret exfiltration attempts
Rate limiting - Per-tool request limits to prevent abuse
Resource limits - Memory, CPU, and execution time constraints


---
*Page 5*


WASM ──► Allowlist ──► Leak Scan ──► Credential ──► Execute ──► Leak Scan
──► WASM
Validator (request) Injector Request (response)
Prompt Injection Defense
External content passes through multiple security layers:
Pattern-based detection of injection attempts
Content sanitization and escaping
Policy rules with severity levels (Block/Warn/Review/Sanitize)
Tool output wrapping for safe LLM context injection
Data Protection
All data stored locally in your PostgreSQL database
Secrets encrypted with AES-256-GCM
No telemetry, analytics, or data sharing
Full audit log of all tool executions
Architecture
┌─────────────────────────────────────────────────────────────────┐
│ Channels │
│ ┌──────┐ ┌──────┐ ┌──────────────┐ │
│ │ REPL │ │ HTTP │ │ WASM Channels│ │
│ └──┬───┘ └──┬───┘ └──────┬───────┘ │
│ └─────────┴─────────────┘ │
│ │ │
│ ┌────▼────┐ │
│ │ Router │ Intent classification │
│ └────┬────┘ │
│ │ │
│ ┌──────────▼──────────┐ │
│ │ Scheduler │ Parallel job management │
│ └──────────┬──────────┘ │
│ │ │
│ ┌───────────────┼───────────────┐ │
│ ▼ ▼ ▼ │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│ │ Worker │ │ Worker │ │ Worker │ LLM reasoning │
│ └────┬────┘ └────┬────┘ └────┬────┘ │
│ └───────────────┼───────────────┘ │
│ │ │
│ ┌──────────▼──────────┐ │
│ │ Tool Registry │ │


---
*Page 6*


│ │ ┌───────────────┐ │ │
│ │ │ Built-in │ │ │
│ │ │ MCP │ │ │
│ │ │ WASM Sandbox │ │ │
│ │ └───────────────┘ │ │
│ └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
Core Components
Component Purpose
Agent Loop Main message handling and job coordination
Router Classifies user intent (command, query, task)
Scheduler Manages parallel job execution with priorities
Worker Executes jobs with LLM reasoning and tool calls
Workspace Persistent memory with hybrid search
Safety Layer Prompt injection defense and content sanitization
Usage
# First-time setup (configures database, auth, etc.)
ironclaw onboard
# Start interactive REPL
cargo run
# With debug logging
RUST_LOG=ironclaw=debug cargo run
Development
# Format code
cargo fmt
# Lint
cargo clippy --all --benches --tests --examples --all-features
# Run tests
createdb ironclaw_test
cargo test


---
*Page 7*


# Run specific test
cargo test test_name
OpenClaw Heritage
IronClaw is a Rust reimplementation inspired by OpenClaw. See FEATURE_PARITY.md for the
complete tracking matrix.
Key differences:
Rust vs TypeScript - Native performance, memory safety, single binary
WASM sandbox vs Docker - Lightweight, capability-based security
PostgreSQL vs SQLite - Production-ready persistence
Security-first design - Multiple defense layers, credential protection
License
Licensed under either of:
Releases
No releases published
Packages
No packages published
Contributors 4
ilblackdragonIllia Polosukhin
claudeClaude
serrrfiratfirat.sertgoz
elliotBraemElliot Braem
Languages
Rust97.3% JavaScript1.1% CSS0.8% PLpgSQL0.5% HTML0.2% Shell0.1%