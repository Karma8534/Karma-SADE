---
source: https://platform.claude.com/docs/en/build-with-claude/overview
scraped: 2026-03-23
section: build-with-claude
---

# Features overview

Explore Claude's advanced features and capabilities.

---

Claude's API surface is organized into five areas:

- **Model capabilities:** Control how Claude reasons and formats responses.
- **Tools:** Let Claude take actions on the web or in your environment.
- **Tool infrastructure:** Handles discovery and orchestration at scale.
- **Context management:** Keeps long-running sessions efficient.
- **Files and assets:** Manage the documents and data you provide to Claude.

If you're new, start with [model capabilities](#model-capabilities) and [tools](#tools). Return to the other sections when you're ready to optimize cost, latency, or scale.

## Feature availability

Features on the Claude Platform are assigned one of the following availability classifications per platform (shown in the Availability column of each table below). Not all features pass through every stage. A feature may enter at any classification and may skip stages.

| Classification | Description |
|----------------|-------------|
| **Beta** | Preview features used for gathering feedback and iterating on a less mature use case. Availability may be limited, including through sign-up requirements or waitlists, and may not be publicly announced. Features may change significantly or be discontinued based on feedback. Not guaranteed for ongoing production use. Breaking changes are possible with notice, and some platform-specific limitations may apply. Beta features have a beta header. |
| **Generally available (GA)** | Feature is stable, fully supported, and recommended for production use. Should not have a beta header or other indicator that the feature is in a preview state. Covered by standard API versioning guarantees. |
| **Deprecated** | Feature is still functional but no longer recommended. A migration path and removal timeline are provided. |
| **Retired** | Feature is no longer available. |

## Model capabilities

Ways to steer Claude and Claude's direct outputs, including response format, reasoning depth, and input modalities.

| Feature | Description |
|---------|-------------|
| Context windows | Up to 1M tokens for processing large documents, extensive codebases, and long conversations. |
| Adaptive thinking | Let Claude dynamically decide when and how much to think. The recommended thinking mode for Opus 4.6. Use the effort parameter to control thinking depth. |
| Batch processing | Process large volumes of requests asynchronously for cost savings. Send batches with a large number of queries per batch. Batch API calls cost 50% less than standard API calls. |
| Citations | Ground Claude's responses in source documents. With Citations, Claude can provide detailed references to the exact sentences and passages it uses to generate responses, leading to more verifiable, trustworthy outputs. |
| Data residency | Control where model inference runs using geographic controls. Specify `"global"` or `"us"` routing per request via the `inference_geo` parameter. |
| Effort | Control how many tokens Claude uses when responding with the effort parameter, trading off between response thoroughness and token efficiency. Supported on Opus 4.6 and Opus 4.5. |
| Extended thinking | Enhanced reasoning capabilities for complex tasks, providing transparency into Claude's step-by-step thought process before delivering its final answer. |
| PDF support | Process and analyze text and visual content from PDF documents. |
| Search results | Enable natural citations for RAG applications by providing search results with proper source attribution. Achieve web search-quality citations for custom knowledge bases and tools. |
| Structured outputs | Guarantee schema conformance with two approaches: JSON outputs for structured data responses, and strict tool use for validated tool inputs. |

## Tools

Built-in tools that Claude invokes via `tool_use`. Server-side tools are run by the platform; client-side tools are implemented and executed by you.

### Server-side tools

| Feature | Description |
|---------|-------------|
| Code execution | Run code in a sandboxed environment for advanced data analysis, calculations, and file processing. Free when used with web search or web fetch. |
| Web fetch | Retrieve full content from specified web pages and PDF documents for in-depth analysis. |
| Web search | Augment Claude's comprehensive knowledge with current, real-world data from across the web. |

### Client-side tools

| Feature | Description |
|---------|-------------|
| Bash | Execute bash commands and scripts to interact with the system shell and perform command-line operations. |
| Computer use | Control computer interfaces by taking screenshots and issuing mouse and keyboard commands. |
| Memory | Enable Claude to store and retrieve information across conversations. Build knowledge bases over time, maintain project context, and learn from past interactions. |
| Text editor | Create and edit text files with a built-in text editor interface for file manipulation tasks. |

## Tool infrastructure

Infrastructure that supports discovering, orchestrating, and scaling tool use.

| Feature | Description |
|---------|-------------|
| Agent Skills | Extend Claude's capabilities with Skills. Use pre-built Skills (PowerPoint, Excel, Word, PDF) or create custom Skills with instructions and scripts. Skills use progressive disclosure to efficiently manage context. |
| Fine-grained tool streaming | Stream tool use parameters without buffering/JSON validation, reducing latency for receiving large parameters. |
| MCP connector | Connect to remote MCP servers directly from the Messages API without a separate MCP client. |
| Programmatic tool calling | Enable Claude to call your tools programmatically from within code execution containers, reducing latency and token consumption for multi-tool workflows. |
| Tool search | Scale to thousands of tools by dynamically discovering and loading tools on-demand using regex-based search, optimizing context usage and improving tool selection accuracy. |

## Context management

Infrastructure for controlling and optimizing Claude's context window.

| Feature | Description |
|---------|-------------|
| Compaction | Server-side context summarization for long-running conversations. When context approaches the window limit, the API automatically summarizes earlier parts of the conversation. Supported on Opus 4.6 and Sonnet 4.6. |
| Context editing | Automatically manage conversation context with configurable strategies. Supports clearing tool results when approaching token limits and managing thinking blocks in extended thinking conversations. |
| Automatic prompt caching | Simplify prompt caching to a single API parameter. The system automatically caches the last cacheable block in your request, moving the cache point forward as conversations grow. |
| Prompt caching (5m) | Provide Claude with more background knowledge and example outputs to reduce costs and latency. |
| Prompt caching (1hr) | Extended 1-hour cache duration for less frequently accessed but important context, complementing the standard 5-minute cache. |
| Token counting | Token counting enables you to determine the number of tokens in a message before sending it to Claude, helping you make informed decisions about your prompts and usage. |

## Files and assets

Manage files and assets for use with Claude.

| Feature | Description |
|---------|-------------|
| Files API | Upload and manage files to use with Claude without re-uploading content with each request. Supports PDFs, images, and text files. |
