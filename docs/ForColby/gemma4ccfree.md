Imagine running Claude Code with Google's Gemma 4 coding model on an Nvidia GPU — does it get any better?

Google Gemma 4 is the latest AI coding model that is blowing up, so I tried it on Claude Code.

And I was not disappointed.

If you read my previous Gemma 4 release article, you know I was already excited about the new Google Open-Source coding model.

But I couldn’t fully test it since running the 31B model locally requires serious hardware.

That changed this week.

Ollama now runs Gemma 4 in the cloud through their partnership with NVIDIA on Blackwell GPUs. One command and you’re coding with a model that scores 80% on LiveCodeBench and 89.2% on AIME 2026.

We are slowly moving away from complex hardware to run new AI models, thanks to Ollama, as I reviewed their Ollama Launch feature.

For Gemma 4, you just ollama launch claude --model gemma4:31b-cloud and you're running it.

I spent a few hours testing this combination

The 256K context window handles large codebases without chunking
The native function calling works with Claude Code’s agentic workflows
And the Apache 2.0 license means no restrictions.
In this article, I’ll walk you through the setup, run real coding tests, and share my honest experience with this combination.

But just a quick reminder:

If you are new to my content, you missed my year of Claude Code updates, where I covered every new feature, tip, and trick. Check out the complete list of Claude Code tutorials here. Follow me here on Medium and my Claude Code Masterclass newsletter so you don’t miss new updates.

Gemma 4 Perfect Built for Claude Code
Press enter or click to view image in full size

Google built Gemma 4 from the same research behind Gemini 3. The difference is you can run it yourself — locally or through Ollama Cloud.

Claude Code users:

Press enter or click to view image in full size

The 31B model puts up serious benchmarks:

LiveCodeBench v6: 80% — that’s open-source SOTA for coding
AIME 2026: 89.2% — up from Gemma 3’s 20.8% on the same test
Codeforces ELO: 2150 — competitive programming level
MMLU Pro: 85.2% — strong general reasoning
For context, these numbers were frontier-class from proprietary models a few months ago.

Context Window
Press enter or click to view image in full size

The 31B and 26B models support 256K tokens. The smaller E2B and E4B edge models go up to 128K.

In practice, you can pass entire codebases in a single prompt without chunking. Multi-file refactoring becomes much smoother when the model can see everything at once.

Native Function Calling
Gemma 4 supports structured tool use out of the box.

This is important for Claude Code’s agentic workflows; the model can call external tools, APIs, and execute multi-step operations fast and easily.

Apache 2.0 License
Unlike previous Gemma releases with custom licenses,

Gemma 4 ships under Apache 2.0. There are no restrictions on commercial use, fine-tuning, or deployment. Similar terms as Qwen and most of the open-weight ecosystem.

Ollama Cloud Gemma 4 Claude Code
Press enter or click to view image in full size

This is exactly what developers without high-end GPUs need.

Running the 31B model locally requires 20GB+ VRAM. The 26B MoE needs 18GB. Not everyone has that hardware.

Press enter or click to view image in full size

Ollama partnered with NVIDIA to run Gemma 4 on Blackwell GPUs in the cloud. You get the full 31B model without the hardware requirements.

The setup is one command:

ollama launch claude --model gemma4:31b-cloud
Press enter or click to view image in full size

Cloud models run at full context length automatically. You don’t need to configure context settings like you would for local models.

Setting Up Gemma 4 with Claude Code
Gemma 4 is available on Ollama with cloud integration. One command gets you running.

Prerequisites
Before we start, make sure you have:

Ollama v0.15+ installed
Claude Code v2.1+ installed
Ollama Cloud account
Step 1: Install Ollama
If you don’t have Ollama installed:

Mac:

brew install ollama
Linux:

curl -fsSL https://ollama.com/install.sh | sh
Windows: Download the installer from ollama.com and run it.

Verify installation:

ollama --version
Press enter or click to view image in full size

Step 2: Install Claude Code
If you already have Claude Code installed, skip to Step 3.

Mac/Linux:

curl -fsSL https://claude.ai/install.sh | bash
Windows PowerShell:

irm https://claude.ai/install.ps1 | iex
Verify installation:

claude --version
Press enter or click to view image in full size

You should see version 2.1.92 or newer.

Step 3: Pull Gemma 4 Cloud Model
ollama pull gemma4:31b-cloud
Press enter or click to view image in full size

Cloud models register quickly since inference happens on NVIDIA’s Blackwell GPUs remotely.

Step 4: Launch Claude Code with Gemma 4
Here’s the command:

ollama launch claude --model gemma4:31b-cloud
Press enter or click to view image in full size

Ollama handles the API configuration behind the scenes. You do not need to export environment variables or set base URLs manually.

Step 5: Verify the Setup
Once Claude Code is running, check the status:

/status
Press enter or click to view image in full size

You should see:

Model: gemma4:31b-cloud
Anthropic base URL: http://127.0.0.1:11434
Auth token: ANTHROPIC_AUTH_TOKEN
Step 5: Test Prompt
Once you confirm you are using the Gemma 4 model, you can now run a test prompt :

Press enter or click to view image in full size

Understanding the Cloud Model
Gemma 4 on Ollama Cloud runs remotely, not locally.

Here’s what that means:

gemma4:31b-cloud: Runs on NVIDIA Blackwell GPUs via Ollama’s cloud
256K context window: Full context length, no configuration needed
No local GPU required: The heavy lifting happens on NVIDIA’s servers
Your code and prompts are sent to the cloud for processing. Keep this in mind if you’re working on proprietary codebases.

Local Model Option
If you have the hardware and prefer local inference:

# For laptops (10GB+ VRAM)

ollama pull gemma4:e4b
ollama launch claude --model gemma4:e4b

# For workstations (18GB+ VRAM)

ollama pull gemma4:26b
ollama launch claude --model gemma4:26b

# For maximum quality (20GB+ VRAM)

ollama pull gemma4:31b
ollama launch claude --model gemma4:31b
Local models give you privacy and zero latency, but require significant VRAM.

For a complete Ollama Launch guide, check my previous article: I Tested (New) Ollama Launch For Claude Code, Codex, OpenCode (No More Configs)

Practical Coding Tests
I ran a few tests to see how Gemma 4 performs in real coding scenarios.

Test 1: Complex App Build (One-Shot)
Same approach as my previous GLM articles.

Here’s my prompt:

Build me a real-time task tracker with:
- Add tasks with title, priority, due date, and tags
- Dashboard showing tasks by priority (bar chart) and completion rate (progress ring)
- Filter tasks by priority, tags, and date range
- Mark complete with animation
- Dark/light mode toggle
- Clean, modern UI with Tailwind
- Save to local storage
Press enter or click to view image in full size

Gemma 4 activated autopilot mode and used a planner agent to decompose the task before writing any code.

Press enter or click to view image in full size

It chose Vite + React + Tailwind + Recharts as the stack. Then it asked a clarifying question about what “real-time” meant — UI state only, cross-tab sync, or cloud sync.

Press enter or click to view image in full size

This wasn’t something I asked for. The model broke down a complex request into phases and asked for clarification before proceeding.

After selecting UI State Only, Gemma 4 built out the full application.

Components were well-organized
The charts rendered correctly
Dark mode worked on the first try.
One-shot for a working app with charts, filtering, animations, and local storage persistence. The code structure was clean, and the Tailwind classes followed consistent patterns.

Test 2: Multi-File Operations
The 256K context window should help with multi-file refactoring.

I asked Gemma 4 to refactor an existing JavaScript project to TypeScript:

Refactor this project to use TypeScript instead of JavaScript.
Update all files, add proper types, and make sure everything still works.
Gemma 4 maintained context across all files. When it updated the type definitions in one file, it remembered those types when updating imports in other files.

Test 3: Terminal Operations
I tested the terminal-based coding capability:

Set up a new Node.js project with TypeScript, ESLint, Prettier, and Jest.
Configure all the config files properly and add npm scripts for dev, build, test, and lint.
The tsconfig.json, .eslintrc, .prettierrc, and jest.config.js all worked together without conflicts.

Observations
A few things stood out during testing:

Autopilot Planning: Gemma 4 breaks down complex tasks into phases. It uses planning agents to decompose requirements before writing code.
Clarifying Questions: The model asks smart questions when requirements are ambiguous.
Code Quality: The generated code is clean. Components are well-organized.
Context Retention: Multi-file operations work smoothly.
Speed: Cloud inference is fast.
Final Thoughts
Gemma 4 on Claude Code delivers speed and good performance. Google shipped a serious open-source coding model.

The benchmarks translate to real performance. The Ollama Cloud integration removes the hardware barrier.

If you’ve been waiting for a Google model that works well with Claude Code, this is it.

